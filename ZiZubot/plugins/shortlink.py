import logging
import asyncio
import secrets
import aiohttp
from urllib.parse import quote

from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from info import ADMINS
from database.shortlink_db import (
    get_shortlink_config,
    set_shortlink_config,
    set_daily_verify,
    get_daily_verify,
    needs_verify,
    increment_verify,
)

logger = logging.getLogger(__name__)

# In-memory token store: {token: (ident, file_id, user_id)}
VERIFY_TOKENS: dict = {}


# ── Shortlink API ──────────────────────────────────────────────────────────────

async def get_short_link(long_url: str) -> str | None:
    """
    Shorten `long_url` using the configured shortener service.
    Returns the shortened URL or None if not configured / API fails.
    """
    cfg = await get_shortlink_config()
    if not cfg or not cfg.get("domain") or not cfg.get("api_key"):
        return None

    domain  = cfg["domain"].rstrip("/")
    api_key = cfg["api_key"]
    encoded = quote(long_url, safe="")
    api_url = f"https://{domain}/api?api={api_key}&url={encoded}"

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(api_url, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                data = await resp.json(content_type=None)
        # Most shorteners use one of these key names
        short = (
            data.get("shortenedUrl")
            or data.get("short_url")
            or data.get("shortlink")
            or data.get("short")
            or data.get("result")
        )
        return short or None
    except Exception as e:
        logger.exception(f"Shortlink API error: {e}")
        return None


async def make_verify_link(bot_username: str, ident: str, file_id: str, user_id: int) -> str | None:
    """
    Generate a unique token, store it, shorten the bot deep link.
    Returns the shortened URL to send to the user, or None.
    """
    token = secrets.token_urlsafe(12)
    VERIFY_TOKENS[token] = (ident, file_id, user_id)

    # Deep link user lands on after completing the shortlink
    deep_link = f"https://t.me/{bot_username}?start=verify_{token}"
    short = await get_short_link(deep_link)
    if not short:
        # API failed — clean up token
        VERIFY_TOKENS.pop(token, None)
    return short


async def consume_token(token: str, user_id: int):
    """
    Validate and consume a verify token.
    Returns (ident, file_id) if valid and belongs to user_id, else (None, None).
    """
    entry = VERIFY_TOKENS.get(token)
    if not entry:
        return None, None
    ident, file_id, orig_user = entry
    if orig_user != 0 and orig_user != user_id:
        return None, None
    VERIFY_TOKENS.pop(token, None)
    await increment_verify(user_id)
    return ident, file_id


# ── Admin Commands ─────────────────────────────────────────────────────────────

@Client.on_message(filters.command("shortlink") & filters.user(ADMINS) & filters.private)
async def cmd_set_shortlink(client, message):
    args = message.command[1:]
    if len(args) < 2:
        return await message.reply_text(
            "<b>❗ Usage:</b>\n"
            "<code>/shortlink &lt;domain&gt; &lt;api_key&gt;</code>\n\n"
            "<b>Example:</b>\n"
            "<code>/shortlink publicearn.com 837b7a64653d1b435f5e20a237840f51d0c1ce</code>",
            parse_mode=enums.ParseMode.HTML
        )
    domain, api_key = args[0], args[1]
    # Strip angle brackets in case user copied the example format: /shortlink <domain> <api_key>
    domain = domain.strip("<>")
    api_key = api_key.strip("<>")
    # Strip http/https prefix if user pasted full URL
    domain = domain.replace("https://", "").replace("http://", "").rstrip("/")
    await set_shortlink_config(domain, api_key)
    await message.reply_text(
        f"✅ <b>Shortlink configured!</b>\n\n"
        f"🔗 <b>Domain :</b> <code>{domain}</code>\n"
        f"🔑 <b>API Key :</b> <code>{api_key[:8]}{'*' * (len(api_key) - 8)}</code>",
        parse_mode=enums.ParseMode.HTML
    )


@Client.on_message(filters.command("shortlink_status") & filters.user(ADMINS))
async def cmd_shortlink_status(client, message):
    cfg = await get_shortlink_config()
    daily = await get_daily_verify()
    if not cfg or not cfg.get("domain"):
        return await message.reply_text(
            "❌ <b>No shortlink configured.</b>\n\n"
            "Use <code>/shortlink &lt;domain&gt; &lt;api_key&gt;</code> to set one.",
            parse_mode=enums.ParseMode.HTML
        )
    key = cfg.get("api_key", "")
    masked = key[:6] + "*" * max(0, len(key) - 6)
    await message.reply_text(
        f"📊 <b>Shortlink Status</b>\n\n"
        f"{'━' * 26}\n"
        f"🌐 <b>Domain        :</b> <code>{cfg['domain']}</code>\n"
        f"🔑 <b>API Key       :</b> <code>{masked}</code>\n"
        f"📅 <b>Daily Verify  :</b> <code>{daily}x per day</code>\n"
        f"{'━' * 26}",
        parse_mode=enums.ParseMode.HTML
    )


@Client.on_message(filters.command("set_daily_verify") & filters.user(ADMINS))
async def cmd_set_daily_verify(client, message):
    args = message.command[1:]
    if not args or not args[0].isdigit():
        return await message.reply_text(
            "<b>❗ Usage:</b> <code>/set_daily_verify &lt;number&gt;</code>\n\n"
            "<b>Example:</b> <code>/set_daily_verify 2</code>\n\n"
            "<i>Sets how many times per day a user must complete the shortlink.</i>",
            parse_mode=enums.ParseMode.HTML
        )
    count = int(args[0])
    if count < 0 or count > 10:
        return await message.reply_text("❌ Value must be between 0 and 10.")
    await set_daily_verify(count)
    if count == 0:
        await message.reply_text("✅ <b>Shortlink verification disabled.</b> Files will be sent directly.", parse_mode=enums.ParseMode.HTML)
    else:
        await message.reply_text(
            f"✅ <b>Daily verify set to <code>{count}x</code> per day.</b>",
            parse_mode=enums.ParseMode.HTML
        )


@Client.on_message(filters.command("remove_shortlink") & filters.user(ADMINS))
async def cmd_remove_shortlink(client, message):
    from database.shortlink_db import _cfg_col
    await _cfg_col.delete_one({"_id": "config"})
    await message.reply_text("✅ <b>Shortlink removed.</b> Files will now be sent directly.", parse_mode=enums.ParseMode.HTML)
