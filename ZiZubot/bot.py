import logging, sys, os, asyncio
import logging.config

logging.config.fileConfig('logging.conf')
logging.getLogger().setLevel(logging.INFO)
logging.getLogger("pyrogram").setLevel(logging.ERROR)
logging.getLogger("imdbpy").setLevel(logging.ERROR)

from pyrogram import Client, __version__
from pyrogram.raw.all import layer
from pyrogram.errors import FloodWait
from database.ia_filterdb import Media
from database.users_chats_db import db
from info import SESSION, API_ID, API_HASH, BOT_TOKEN, LOG_STR, LOG_CHANNEL
from utils import temp
from typing import Union, Optional, AsyncGenerator
from pyrogram import types
from Script import script

from plugins.webcode import bot_run
from os import environ
from aiohttp import web as webserver
import aiohttp


async def _auto_delete_msg(msg, delay: int = 5):
    """Delete a message after `delay` seconds, silently ignoring errors."""
    await asyncio.sleep(delay)
    try:
        await msg.delete()
    except Exception:
        pass


async def schedule_restart():
    await asyncio.sleep(86400)  # 24 hours
    os.execv(sys.executable, ['python'] + sys.argv)


async def keep_alive_loop(port: int):
    """Ping our own health endpoint every 4 minutes to prevent Koyeb from sleeping."""
    public_url = environ.get('PUBLIC_URL', '').rstrip('/')
    local_url = f"http://localhost:{port}/"
    ping_url = (public_url + '/') if public_url else local_url
    await asyncio.sleep(60)
    async with aiohttp.ClientSession() as session:
        while True:
            try:
                async with session.get(ping_url, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                    logging.info(f"Keep-alive ping -> {ping_url} [{resp.status}]")
            except Exception as e:
                logging.warning(f"Keep-alive ping failed: {e}")
            await asyncio.sleep(240)


class Bot(Client):

    def __init__(self):
        super().__init__(
            name=SESSION,
            api_id=API_ID,
            api_hash=API_HASH,
            bot_token=BOT_TOKEN,
            workers=50,
            plugins={"root": "plugins"},
            sleep_threshold=5,
        )

    async def start(self):
        b_users, b_chats = await db.get_banned()
        temp.BANNED_USERS = b_users
        temp.BANNED_CHATS = b_chats
        await super().start()
        await Media.ensure_indexes()
        me = await self.get_me()
        temp.ME = me.id
        temp.U_NAME = me.username
        temp.B_NAME = me.first_name
        self.username = '@' + me.username
        logging.info(f"{me.first_name} with Pyrogram v{__version__} (Layer {layer}) started on {me.username}.")
        logging.info(LOG_STR)

        # Send restart notification and auto-delete it after 5 seconds
        try:
            restart_msg = await self.send_message(chat_id=LOG_CHANNEL, text=script.RESTART_TXT)
            asyncio.create_task(_auto_delete_msg(restart_msg, delay=5))
        except Exception as e:
            logging.warning(f"Could not send restart message to LOG_CHANNEL ({LOG_CHANNEL}): {e}")

        logging.info("ZiZuBot is running!")

        # Start the health-check web server.
        # FIX: wrapped in retry loop — if the port is still bound by the dying
        # previous process (OSError: Address already in use), we wait and retry
        # instead of crashing and triggering another restart loop.
        port = int(environ.get("PORT", 8000))
        runner = webserver.AppRunner(await bot_run())
        await runner.setup()
        for attempt in range(1, 6):
            try:
                site = webserver.TCPSite(runner, "0.0.0.0", port)
                await site.start()
                logging.info(f"Web health-check running on port {port}")
                break
            except OSError as e:
                if attempt < 5:
                    logging.warning(f"Port {port} busy (attempt {attempt}/5), retrying in 3s: {e}")
                    await asyncio.sleep(3)
                else:
                    logging.error(f"Could not bind to port {port} after 5 attempts: {e}")
                    # Continue running — the bot itself works even without the health endpoint

        asyncio.create_task(schedule_restart())
        asyncio.create_task(keep_alive_loop(port))

    async def stop(self, *args):
        await super().stop()
        logging.info("Bot stopped. Bye.")

    async def iter_messages(
        self,
        chat_id: Union[int, str],
        limit: int,
        offset: int = 0,
    ) -> Optional[AsyncGenerator["types.Message", None]]:
        """Iterate through a chat sequentially, fetching in batches of up to 200.
        Handles FloodWait internally so indexing is never aborted by rate limits.
        """
        current = offset
        while True:
            new_diff = min(200, limit - current)
            if new_diff <= 0:
                return
            ids = list(range(current, current + new_diff))
            try:
                messages = await self.get_messages(chat_id, ids)
            except FloodWait as fw:
                logging.warning(f"FloodWait {fw.value}s in iter_messages — sleeping then retrying batch")
                await asyncio.sleep(fw.value + 2)
                try:
                    messages = await self.get_messages(chat_id, ids)
                except Exception as e:
                    logging.error(f"iter_messages batch failed after FloodWait retry: {e}")
                    return
            except Exception as e:
                logging.error(f"iter_messages get_messages error: {e}")
                return
            for message in messages:
                yield message
                current += 1


app = Bot()
app.run()
