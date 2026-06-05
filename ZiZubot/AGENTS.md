# AGENTS.md — ZiZubot™ Bot Source

> Full project context is in [`/AGENTS.md`](../AGENTS.md) at the repo root.
> This file is a quick-reference for agents working inside the `ZiZubot/` folder.

---

## Entry point

```
bot.py          ← run this (or via start.sh / Docker CMD)
```

## File roles

| File / Folder | Purpose |
|---|---|
| `bot.py` | `Bot(Client)` subclass — startup, web server, keep-alive, restart |
| `info.py` | **Single source of truth for all config.** Reads env vars; always import from here |
| `utils.py` | Shared helpers + `temp` class (in-memory banned lists, settings cache) |
| `Script.py` | All user-facing message strings as class attributes |
| `database/ia_filterdb.py` | `Media` ODM model + file search/index CRUD |
| `database/users_chats_db.py` | Users, chats, ban/unban, group settings |
| `database/filters_mdb.py` | Manual keyword→reply filters per group |
| `database/connections_mdb.py` | User↔group connection preferences |
| `database/shortlink_db.py` | Shortlink usage tracking |
| `plugins/` | One file per feature; Pyrogram auto-loads all of them |

## Plugin map

| Plugin | Handles |
|---|---|
| `pm_filter.py` | Core auto-filter — matches user queries to indexed files |
| `index.py` | `/index`, `/cancel` — bulk channel indexing |
| `channel.py` | Saves media posted to `CHANNELS` to the index |
| `inline.py` | `@bot <query>` inline search |
| `commands.py` | `/start`, `/help`, `/about` |
| `filters.py` | `/filter`, `/filters`, `/del` — manual keyword filters |
| `connection.py` | `/connect`, `/disconnect` — user↔group linking |
| `p_ttishow.py` | Group join/leave events; `/ban`, `/unban`, `/users`, `/chats`, `/disable`, `/enable`, `/leave` |
| `banned.py` | Pyrogram custom filters `banned_user` and `disabled_group` |
| `broadcast.py` | `/broadcast` |
| `misc.py` | `/id`, `/info`, `/gifid` + callback button handlers |
| `etc.py` | `/link` shortlink generator |
| `shortlink.py` | Shortlink bypass callback |
| `auto_approve.py` | Auto-approve join requests; `/approve_on/off`, `/welcome_on/off` |
| `p_ttishow.py` | New-member welcome, chat enable/disable |
| `webcode.py` | `GET /` health-check web server |

## Must-know rules

### 1. No raw newlines in f-strings (Python 3.11)
```python
# WRONG — SyntaxError in Python 3.11
text = f"Line one
Line two"

# CORRECT
text = f"Line one\nLine two"
# or
text = f"""Line one
Line two"""
```
This bug crashed the bot 4 times across `auto_approve.py` and `banned.py`.
All fixed — do not reintroduce.

### 2. Use `logger`, never `print()`
```python
import logging
logger = logging.getLogger(__name__)
logger.exception(e)   # not print(traceback.format_exc())
```

### 3. Never use `filter` as a variable name
The builtin `filter` is also a Pyrogram keyword. Use `db_filter` for any
dict that is passed to Motor/pymongo as a query filter.

### 4. Guard `list.remove()` on temp lists
```python
# WRONG — raises ValueError if bot restarted after the ban
temp.BANNED_CHATS.remove(chat_id)

# CORRECT
try:
    temp.BANNED_CHATS.remove(chat_id)
except ValueError:
    pass
```

### 5. Offload blocking IMDB calls
```python
# WRONG — freezes the event loop
result = imdb.search_movie(title)

# CORRECT
result = await asyncio.to_thread(imdb.search_movie, title)
```

### 6. All config comes from `info.py`
Never call `os.environ.get()` directly in plugins. Import the constant from
`info.py` instead.

### 7. All DB calls are async
Motor returns coroutines. Every call to `db.*` must be `await`-ed.

## Required env vars

```
API_ID          Telegram API ID
API_HASH        Telegram API Hash
BOT_TOKEN       Bot token from @BotFather
ADMINS          Space-separated admin user IDs
DATABASE_URI    MongoDB Atlas connection string
LOG_CHANNEL     Log channel ID (bot must be admin)
```

See `.env.example` for the complete annotated list of all variables.

## Run locally

```bash
cp .env.example .env
# fill in .env
bash start.sh
```

## Bugs already fixed (do not re-investigate)

35 bugs fixed across 4 sessions. See [`/AGENTS.md`](../AGENTS.md) §Bug History
for the full list. Key patterns that are fully resolved:
- `SyntaxError` from raw newlines in f-strings — **all instances fixed**
- `filter=True` kwarg TypeError in `pm_filter.py` — **fixed**
- Unguarded `list.remove()` in `p_ttishow.py` — **fixed**
- Blocking IMDB calls in `utils.py` — **fixed**
- Duplicate `/stats` handler conflict — **fixed**
