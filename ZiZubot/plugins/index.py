import logging
import asyncio
from pyrogram import Client, filters, enums
from pyrogram.errors import FloodWait
from pyrogram.errors.exceptions.bad_request_400 import ChannelInvalid, ChatAdminRequired, UsernameInvalid, UsernameNotModified
from info import ADMINS
from info import INDEX_REQ_CHANNEL as LOG_CHANNEL
from database.ia_filterdb import save_file
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from utils import temp
import re
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
lock = asyncio.Lock()


@Client.on_callback_query(filters.regex(r'^index'))
async def index_files(bot, query):
    if query.data.startswith('index_cancel'):
        temp.CANCEL = True
        return await query.answer("Cancelling Indexing")
    _, raju, chat, lst_msg_id, from_user = query.data.split("#")
    if raju == 'reject':
        await query.message.delete()
        await bot.send_message(int(from_user),
                               f'Your Submission for indexing {chat} has been decliened by our moderators.',
                               reply_to_message_id=int(lst_msg_id))
        return

    if lock.locked():
        return await query.answer('Wait until previous process complete.', show_alert=True)
    msg = query.message

    await query.answer('Processing...⏳', show_alert=True)
    if int(from_user) not in ADMINS:
        await bot.send_message(int(from_user),
                               f'Your Submission for indexing {chat} has been accepted by our moderators and will be added soon.',
                               reply_to_message_id=int(lst_msg_id))
    await msg.edit(
        "Starting Indexing",
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton('Cancel', callback_data='index_cancel')]]
        )
    )
    try:
        chat = int(chat)
    except:
        chat = chat
    await index_files_to_db(int(lst_msg_id), chat, msg, bot)


@Client.on_message((filters.forwarded | (filters.regex(r"(https://)?(t\.me/|telegram\.me/|telegram\.dog/)(c/)?(\d+|[a-zA-Z_0-9]+)/(\d+)$") & filters.text)) & filters.private & filters.incoming)
async def send_for_index(bot, message):
    if message.text:
        regex = re.compile(r"(https://)?(t\.me/|telegram\.me/|telegram\.dog/)(c/)?(\d+|[a-zA-Z_0-9]+)/(\d+)$")
        match = regex.match(message.text)
        if not match:
            return await message.reply('Invalid link')
        chat_id = match.group(4)
        last_msg_id = int(match.group(5))
        if chat_id.isnumeric():
            chat_id = int(("-100" + chat_id))
    elif message.forward_from_chat and message.forward_from_chat.type == enums.ChatType.CHANNEL:
        last_msg_id = message.forward_from_message_id
        chat_id = message.forward_from_chat.username or message.forward_from_chat.id
    else:
        return
    try:
        await bot.get_chat(chat_id)
    except ChannelInvalid:
        return await message.reply('This may be a private channel / group. Make me an admin over there to index the files.')
    except (UsernameInvalid, UsernameNotModified):
        return await message.reply('Invalid Link specified.')
    except FloodWait as fw:
        # FIX: previously the code slept for fw.value seconds and then fell
        # through to get_messages without re-verifying the chat — meaning an
        # unresolved chat_id was used for indexing.  Tell the user to retry
        # instead so the full flow runs cleanly after the rate limit clears.
        logger.warning(f"FloodWait {fw.value}s on get_chat during index request from {message.from_user.id}")
        return await message.reply(
            f'⏳ Telegram is rate-limiting requests right now. Please try again in <b>{fw.value} seconds</b>.',
            parse_mode=enums.ParseMode.HTML
        )
    except Exception as e:
        logger.exception(e)
        return await message.reply('Something went wrong fetching that chat. Make sure the bot is a member/admin there.')
    try:
        k = await bot.get_messages(chat_id, last_msg_id)
    except:
        return await message.reply('Make Sure That Iam An Admin In The Channel, if channel is private')
    if k.empty:
        return await message.reply('This may be group and iam not a admin of the group.')

    if message.from_user.id in ADMINS:
        buttons = [
            [
                InlineKeyboardButton('Yes',
                                     callback_data=f'index#accept#{chat_id}#{last_msg_id}#{message.from_user.id}')
            ],
            [
                InlineKeyboardButton('close', callback_data='close_data'),
            ]
        ]
        reply_markup = InlineKeyboardMarkup(buttons)
        return await message.reply(
            f'Do you Want To Index This Channel/ Group ?\n\nChat ID/ Username: <code>{chat_id}</code>\nLast Message ID: <code>{last_msg_id}</code>',
            reply_markup=reply_markup)

    if type(chat_id) is int:
        try:
            link = (await bot.create_chat_invite_link(chat_id)).invite_link
        except ChatAdminRequired:
            return await message.reply('Make sure iam an admin in the chat and have permission to invite users.')
    else:
        link = f"@{message.forward_from_chat.username}"
    buttons = [
        [
            InlineKeyboardButton('Accept Index',
                                 callback_data=f'index#accept#{chat_id}#{last_msg_id}#{message.from_user.id}')
        ],
        [
            InlineKeyboardButton('Reject Index',
                                 callback_data=f'index#reject#{chat_id}#{message.id}#{message.from_user.id}'),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(buttons)
    await bot.send_message(LOG_CHANNEL,
                           f'#IndexRequest\n\nBy : {message.from_user.mention} (<code>{message.from_user.id}</code>)\nChat ID/ Username - <code> {chat_id}</code>\nLast Message ID - <code>{last_msg_id}</code>\nInviteLink - {link}',
                           reply_markup=reply_markup)
    await message.reply('ThankYou For the Contribution, Wait For My Moderators to verify the files.')


@Client.on_message(filters.command('setskip') & filters.user(ADMINS))
async def set_skip_number(bot, message):
    if ' ' in message.text:
        _, skip = message.text.split(" ")
        try:
            skip = int(skip)
        except:
            return await message.reply("Skip number should be an integer.")
        await message.reply(f"Successfully set SKIP number as {skip}")
        temp.CURRENT = int(skip)
    else:
        await message.reply("Give me a skip number")


def _index_summary(total_files, duplicate, deleted, no_media, unsupported, errors):
    return (
        f"✅ Saved: <code>{total_files}</code>\n"
        f"♻️ Duplicates skipped: <code>{duplicate}</code>\n"
        f"🗑 Deleted messages skipped: <code>{deleted}</code>\n"
        f"🚫 Non-media skipped: <code>{no_media + unsupported}</code> "
        f"(Unsupported: <code>{unsupported}</code>)\n"
        f"⚠️ Errors: <code>{errors}</code>"
    )


async def index_files_to_db(lst_msg_id, chat, msg, bot):
    total_files = 0
    duplicate = 0
    errors = 0
    deleted = 0
    no_media = 0
    unsupported = 0
    async with lock:
        current = temp.CURRENT
        temp.CANCEL = False

        while True:
            flood_hit = False
            try:
                async for message in bot.iter_messages(chat, lst_msg_id, temp.CURRENT):
                    if temp.CANCEL:
                        await msg.edit(
                            "❌ <b>Indexing Cancelled</b>\n\n" + _index_summary(total_files, duplicate, deleted, no_media, unsupported, errors)
                        )
                        return
                    current += 1
                    if current % 20 == 0:
                        can = [[InlineKeyboardButton('Cancel', callback_data='index_cancel')]]
                        try:
                            await msg.edit_text(
                                text=(
                                    f"⏳ <b>Indexing…</b>  (<code>{current}</code> fetched)\n\n"
                                    + _index_summary(total_files, duplicate, deleted, no_media, unsupported, errors)
                                ),
                                reply_markup=InlineKeyboardMarkup(can)
                            )
                        except FloodWait as fw:
                            await asyncio.sleep(fw.value)
                        except Exception:
                            pass
                    if message.empty:
                        deleted += 1
                        continue
                    elif not message.media:
                        no_media += 1
                        continue
                    elif message.media not in [enums.MessageMediaType.VIDEO, enums.MessageMediaType.AUDIO, enums.MessageMediaType.DOCUMENT]:
                        unsupported += 1
                        continue
                    media = getattr(message, message.media.value, None)
                    if not media:
                        unsupported += 1
                        continue
                    media.file_type = message.media.value
                    media.caption = message.caption
                    try:
                        aynav, vnay = await save_file(media)
                    except FloodWait as fw:
                        logger.warning(f"FloodWait {fw.value}s while saving file — sleeping")
                        await asyncio.sleep(fw.value)
                        try:
                            aynav, vnay = await save_file(media)
                        except Exception:
                            errors += 1
                            continue
                    if aynav:
                        total_files += 1
                    elif vnay == 0:
                        duplicate += 1
                    elif vnay == 2:
                        errors += 1

            except FloodWait as fw:
                wait_secs = fw.value + 5
                logger.warning(f"FloodWait {fw.value}s during indexing — auto-resuming from msg {current} after {wait_secs}s")
                temp.CURRENT = current
                flood_hit = True
                try:
                    await msg.edit(
                        f"⏸ <b>Rate limit hit — auto-resuming in {wait_secs}s…</b>\n\n"
                        + _index_summary(total_files, duplicate, deleted, no_media, unsupported, errors)
                        + f"\n\n<i>Resuming from message ID <code>{current}</code></i>"
                    )
                except Exception:
                    pass
                await asyncio.sleep(wait_secs)

            except Exception as e:
                logger.exception(e)
                await msg.edit(
                    f"❌ <b>Indexing stopped due to an error.</b>\n\n"
                    + _index_summary(total_files, duplicate, deleted, no_media, unsupported, errors)
                )
                return

            if not flood_hit:
                break

        await msg.edit(
            "✅ <b>Indexing Complete!</b>\n\n"
            + _index_summary(total_files, duplicate, deleted, no_media, unsupported, errors)
        )
