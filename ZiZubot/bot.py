import logging,sys,os,asyncio
import logging.config

# Get logging configurations
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

async def schedule_restart():
    await asyncio.sleep(86400)  # 24 hours
    os.execv(sys.executable, ['python'] + sys.argv)

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
        logging.info(f"{me.first_name} with for Pyrogram v{__version__} (Layer {layer}) started on {me.username}.")
        logging.info(LOG_STR)
        # FIX: wrap LOG_CHANNEL message so a bad channel ID doesn't crash before webserver starts
        try:
            await self.send_message(chat_id=LOG_CHANNEL, text=script.RESTART_TXT)
        except Exception as e:
            logging.warning(f"Could not send restart message to LOG_CHANNEL ({LOG_CHANNEL}): {e}")
        print("ZiZuBot™ is running!")

        client = webserver.AppRunner(await bot_run())
        await client.setup()
        bind_address = "0.0.0.0"
        port = int(environ.get("PORT", 8000))
        await webserver.TCPSite(client, bind_address, port).start()
        logging.info(f"Web health-check running on port {port}")
        asyncio.create_task(schedule_restart())

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

        Parameters:
            chat_id: Unique identifier or username of the target chat.
            limit:   ID of the last message to fetch (inclusive upper bound).
            offset:  ID of the first message to fetch (default 0).
        """
        current = offset
        while True:
            # FIX: was current+new_diff+1 (off-by-one — fetched one extra per batch)
            new_diff = min(200, limit - current)
            if new_diff <= 0:
                return
            ids = list(range(current, current + new_diff))
            # FIX: handle FloodWait inside the generator so it doesn't abort indexing
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
