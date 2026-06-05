import os
import asyncio
import logging
from pyrogram.enums import ParseMode
from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram.errors.exceptions.bad_request_400 import MessageTooLong, PeerIdInvalid
from info import ADMINS, LOG_CHANNEL, SUPPORT_CHAT, MELCOW_NEW_USERS
from database.users_chats_db import db
from database.ia_filterdb import Media
from utils import get_size, temp, get_settings
from Script import script
from pyrogram.errors import ChatAdminRequired, FloodWait

logger = logging.getLogger(__name__)


@Client.on_message(filters.new_chat_members & filters.group)
async def save_group(bot, message):
    r_j_check = [u.id for u in message.new_chat_members]
    if temp.ME in r_j_check:
        if not await db.get_chat(message.chat.id):
            total = await bot.get_chat_members_count(message.chat.id)
            r_j = message.from_user.mention if message.from_user else "Anonymous"
            await bot.send_message(
                LOG_CHANNEL,
                script.LOG_TEXT_G.format(
                    message.chat.title,
                    message.chat.id,
                    total,
                    r_j
                )
            )
            await db.add_chat(message.chat.id, message.chat.title)
        if message.chat.id in temp.BANNED_CHATS:
            buttons = [[
                InlineKeyboardButton(
                    '\U0001d61a\U0001d600\U0001d617\U0001d617\U0001d60e\U0001d625\U0001d614',
                    url=f'https://t.me/{SUPPORT_CHAT}'
                )
            ]]
            reply_markup = InlineKeyboardMarkup(buttons)
            k = await message.reply(
                text='<b>CHAT NOT ALLOWED \U0001f41e\n\n\U0001d499\U0001d500 \U0001d49d\U0001d497\U0001d49c\U0001d4c3\U0001d4c8\U0001d4c2 \U0001d499\U0001d4d0\U0001d4c2 \U0001d4c7\U0001d4d4\U0001d4c2\U0001d4c2\U0001d4c7\U0001d4c2\U0001d4c8\U0001d4ca\U0001d4d4\U0001d4c2 \U0001d499\U0001d4d4 \U0001d4a1\U0001d4c7\U0001d4c7\U0001d4c2\U0001d4c8\U0001d4ca !IF YOU WANT TO KNOW MORE ABOUT IT CONTACT OWNER...</b>',
                reply_markup=reply_markup
            )
            try:
                await k.pin()
            except:
                pass
            await bot.leave_chat(message.chat.id)
            return
        buttons = [[
            InlineKeyboardButton(
                '\U0001d499\U0001d4de\U0001d4e6 \U0001d4a3\U0001d4de \U0001d4ca\U0001d4c2\U0001d4d4 \U0001d499\U0001d4d4',
                url=f"https://t.me/{temp.U_NAME}?start=help"
            ),
            InlineKeyboardButton(
                '\U0001f4e2 UPDATES \U0001f4e2',
                url='https://t.me/wudixh1'
            )
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await message.reply_text(
            text=f"<b>\u203a\u203a THANKS TO ADD ME TO YOUR GROUP. {message.chat.title} \u2763\ufe0f\n\u203a\u203a DON'T FORGET TO MAKE ME ADMIN.\n\u203a\u203a IS ANY DOUBTS ABOUT USING ME CLICK BELOW BUTTON..\u26a1\u26a1.</b>",
            reply_markup=reply_markup
        )
    else:
        settings = await get_settings(message.chat.id)
        if settings["welcome"]:
            for u in message.new_chat_members:
                if (temp.MELCOW).get('welcome') is not None:
                    try:
                        await (temp.MELCOW['welcome']).delete()
                    except:
                        pass
                try:
                    temp.MELCOW['welcome'] = await message.reply_video(
                        video="https://graph.org/file/481bbbcad81cb1b2f741c.mp4",
                        caption=f"<b>\u029cey, {u.mention} \U0001f44b\U0001f3fb\n"
                                f"welcome to our group {message.chat.title}\n\n"
                                f"you can find movies / series / animes etc. from here.\n"
                                f"enjoy \U0001f609</b>",
                        reply_markup=InlineKeyboardMarkup(
                            [[
                                InlineKeyboardButton(
                                    '\u27a1\ufe0fgroup rules\u2b05\ufe0f',
                                    url='https://youtube.com/@im_goutham_josh'
                                )
                            ]]
                        )
                    )
                except Exception:
                    temp.MELCOW['welcome'] = await message.reply_text(
                        f"\U0001f44b Welcome {u.mention} to **{message.chat.title}**\n\n"
                        f"Enjoy your stay \U0001f60a"
                    )


@Client.on_message(filters.command('leave') & filters.user(ADMINS))
async def leave_a_chat(bot, message):
    if len(message.command) == 1:
        return await message.reply('Give me a chat id')
    chat = message.command[1]
    try:
        chat = int(chat)
    except:
        chat = chat
    try:
        buttons = [[
            InlineKeyboardButton('SUPPORT', url=f'https://t.me/{SUPPORT_CHAT}')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await bot.send_message(
            chat_id=chat,
            text='<b>Hello Friends, \nMy admin has told me to leave from group so i go! If you wanna add me again contact my support group.</b>',
            reply_markup=reply_markup,
        )
        await bot.leave_chat(chat)
        await message.reply(f"left the chat `{chat}`")
    except FloodWait as fw:
        await asyncio.sleep(fw.value)
        await message.reply("Done (had to wait for rate limit).")
    except Exception as e:
        logger.exception(e)
        await message.reply('Failed to leave that chat. Check the chat ID and try again.')


@Client.on_message(filters.command('disable') & filters.user(ADMINS))
async def disable_chat(bot, message):
    if len(message.command) == 1:
        return await message.reply('Give me a chat id')
    r = message.text.split(None)
    if len(r) > 2:
        reason = message.text.split(None, 2)[2]
        chat = message.text.split(None, 2)[1]
    else:
        chat = message.command[1]
        reason = "No reason Provided"
    try:
        chat_ = int(chat)
    except:
        return await message.reply('Give Me A Valid Chat ID')
    cha_t = await db.get_chat(int(chat_))
    if not cha_t:
        return await message.reply("Chat Not Found In DB")
    if cha_t['is_disabled']:
        return await message.reply(f"This chat is already disabled:\nReason-<code> {cha_t['reason']} </code>")
    await db.disable_chat(int(chat_), reason)
    temp.BANNED_CHATS.append(int(chat_))
    await message.reply('Chat Successfully Disabled')
    try:
        buttons = [[
            InlineKeyboardButton('SUPPORT', url=f'https://t.me/{SUPPORT_CHAT}')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await bot.send_message(
            chat_id=chat_,
            text=f'<b>Hello Friends, \nMy admin has told me to leave from group so i go! If you wanna add me again contact my support group.</b> \nReason : <code>{reason}</code>',
            reply_markup=reply_markup)
        await bot.leave_chat(chat_)
    except FloodWait as fw:
        await asyncio.sleep(fw.value)
    except Exception as e:
        logger.exception(e)


@Client.on_message(filters.command('enable') & filters.user(ADMINS))
async def re_enable_chat(bot, message):
    if len(message.command) == 1:
        return await message.reply('Give me a chat id')
    chat = message.command[1]
    try:
        chat_ = int(chat)
    except:
        return await message.reply('Give Me A Valid Chat ID')
    sts = await db.get_chat(int(chat))
    if not sts:
        return await message.reply("Chat Not Found In DB !")
    if not sts.get('is_disabled'):
        return await message.reply('This chat is not yet disabled.')
    await db.re_enable_chat(int(chat_))
    try:
        temp.BANNED_CHATS.remove(int(chat_))
    except ValueError:
        pass  # already absent from in-memory list (bot restarted after ban)
    await message.reply("Chat Successfully re-enabled")


# FIX: removed duplicate /stats handler (get_ststs) that conflicted with the
# admin-guarded /stats in etc.py. The old version also called
# Media.count_documents() with no filter arg which raises TypeError in Motor.


@Client.on_message(filters.command('ban') & filters.user(ADMINS))
async def ban_a_user(bot, message):
    if len(message.command) == 1:
        return await message.reply('Give me a user id / username')
    r = message.text.split(None)
    if len(r) > 2:
        reason = message.text.split(None, 2)[2]
        chat = message.text.split(None, 2)[1]
    else:
        chat = message.command[1]
        reason = "No reason Provided"
    try:
        chat = int(chat)
    except:
        pass
    try:
        k = await bot.get_users(chat)
    except PeerIdInvalid:
        return await message.reply("This is an invalid user, make sure i have met him before.")
    except IndexError:
        return await message.reply("This might be a channel, make sure its a user.")
    except FloodWait as fw:
        await asyncio.sleep(fw.value)
        return await message.reply("Rate limited by Telegram. Please try again in a moment.")
    except Exception as e:
        logger.exception(e)
        return await message.reply('Failed to fetch user. Make sure the user ID or username is correct.')
    else:
        jar = await db.get_ban_status(k.id)
        if jar['is_banned']:
            return await message.reply(f"{k.mention} is already banned\nReason: {jar['ban_reason']}")
        await db.ban_user(k.id, reason)
        temp.BANNED_USERS.append(k.id)
        await message.reply(f"Successfully banned {k.mention}")


@Client.on_message(filters.command('unban') & filters.user(ADMINS))
async def unban_a_user(bot, message):
    if len(message.command) == 1:
        return await message.reply('Give me a user id / username')
    r = message.text.split(None)
    if len(r) > 2:
        reason = message.text.split(None, 2)[2]
        chat = message.text.split(None, 2)[1]
    else:
        chat = message.command[1]
        reason = "No reason Provided"
    try:
        chat = int(chat)
    except:
        pass
    try:
        k = await bot.get_users(chat)
    except PeerIdInvalid:
        return await message.reply("This is an invalid user, make sure i have met him before.")
    except IndexError:
        return await message.reply("This might be a channel, make sure its a user.")
    except FloodWait as fw:
        await asyncio.sleep(fw.value)
        return await message.reply("Rate limited by Telegram. Please try again in a moment.")
    except Exception as e:
        logger.exception(e)
        return await message.reply('Failed to fetch user. Make sure the user ID or username is correct.')
    else:
        jar = await db.get_ban_status(k.id)
        if not jar['is_banned']:
            return await message.reply(f"{k.mention} is not yet banned.")
        await db.remove_ban(k.id)
        try:
            temp.BANNED_USERS.remove(k.id)
        except ValueError:
            pass  # already absent from in-memory list (bot restarted after ban)
        await message.reply(f"Successfully unbanned {k.mention}")


@Client.on_message(filters.command('users') & filters.user(ADMINS))
async def list_users(bot, message):
    raju = await message.reply('Getting List Of Users')
    users = await db.get_all_users()
    out = "Users Saved In DB Are:\n\n"
    async for user in users:
        out += f"<a href=tg://user?id={user['id']}>{user['name']}</a>"
        if user['ban_status']['is_banned']:
            out += '( Banned User )'
        out += '\n'
    try:
        await raju.edit_text(out)
    except MessageTooLong:
        with open('users.txt', 'w+') as outfile:
            outfile.write(out)
        await message.reply_document('users.txt', caption="List Of Users")
        # FIX: clean up temp file after sending
        try:
            os.remove('users.txt')
        except OSError:
            pass


@Client.on_message(filters.command('chats') & filters.user(ADMINS))
async def list_chats(bot, message):
    raju = await message.reply('Getting List Of chats')
    chats = await db.get_all_chats()
    out = "Chats Saved In DB Are:\n\n"
    async for chat in chats:
        out += f"**Title:** `{chat['title']}`\n**- ID:** `{chat['id']}`"
        if chat['chat_status']['is_disabled']:
            out += '( Disabled Chat )'
        out += '\n'
    try:
        await raju.edit_text(out)
    except MessageTooLong:
        with open('chats.txt', 'w+') as outfile:
            outfile.write(out)
        await message.reply_document('chats.txt', caption="List Of Chats")
        # FIX: clean up temp file after sending
        try:
            os.remove('chats.txt')
        except OSError:
            pass
