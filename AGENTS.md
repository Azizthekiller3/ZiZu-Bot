# AGENTS.md — ZiZubot™ Project Context

This file gives AI coding agents (Claude, Copilot, Cursor, etc.) the full
context needed to work on this repo without re-investigating things that have
already been resolved.

---

## What this project is

**ZiZubot™** is a Telegram auto-filter bot written in Python 3.11 using the
[Pyrogram](https://docs.pyrogram.org/) MTProto client.  
Users type a movie/show name in a Telegram group; the bot replies with matching
files stored in MongoDB.  
It also supports inline search, IMDB lookups, shortlink monetisation, channel
indexing, broadcast, group management, auto-approve, and a built-in keep-alive
web server for free-tier hosting (Koyeb).

**Original base:** [KuttuBot by GouthamSER](https://github.com/GouthamSER/KuttuBot)  
**Deployed on:** Koyeb free tier (Docker, via `Dockerfile`)  
**Python runtime:** 3.11  
**Database:** MongoDB Atlas (Motor async driver + umongo ODM)

---

## Repo layout

```
ZiZu-Bot/
├── AGENTS.md               ← you are here
├── README.md               ← quick-start and feature overview
├── Dockerfile              ← Docker image used by Koyeb/Railway
├── Procfile                ← worker entry-point
├── railway.toml            ← Railway deployment config
└── ZiZubot/                ← ALL bot source lives here
    ├── AGENTS.md           ← condensed context for bot-folder agents
    ├── bot.py              ← Bot subclass + startup logic + web server
    ├── info.py             ← reads ALL env vars; import from here everywhere
    ├── utils.py            ← shared helpers + `temp` in-memory state class
    ├── Script.py           ← all user-facing message templates (one class)
    ├── .env.example        ← canonical env var reference (copy → .env)
    ├── requirements.txt    ← Python dependencies
    ├── start.sh            ← local run script (installs deps + starts bot)
    ├── logging.conf        ← logging configuration
    ├── assets/             ← static assets (default bot logo etc.)
    ├── database/
    │   ├── ia_filterdb.py      ← Media ODM model + file index CRUD
    │   ├── users_chats_db.py   ← users, chats, ban/unban, settings
    │   ├── filters_mdb.py      ← manual keyword filters per group
    │   ├── connections_mdb.py  ← user↔group connection preferences
    │   └── shortlink_db.py     ← shortlink usage tracking
    └── plugins/
        ├── __init__.py         ← empty; marks plugins/ as a package
        ├── auto_approve.py     ← auto-approve join requests + welcome DM
        ├── banned.py           ← banned-user and disabled-chat filters
        ├── broadcast.py        ← /broadcast command
        ├── channel.py          ← indexes media posted to CHANNELS
        ├── commands.py         ← /start, /help, /about
        ├── connection.py       ← /connect, /disconnect (user↔group)
        ├── etc.py              ← /link shortlink generator
        ├── filters.py          ← manual filter CRUD (/filter, /filters, /del)
        ├── index.py            ← /index, /cancel (bulk channel indexing)
        ├── inline.py           ← inline query handler (@bot <query>)
        ├── misc.py             ← /id, /info, /gifid + cb handlers
        ├── mov_ser_latest.py   ← IMDB search helper
        ├── p_ttishow.py        ← group join/leave, /ban, /unban, /users, /chats
        ├── pm_filter.py        ← core auto-filter handler (DM delivery flow)
        ├── shortlink.py        ← shortlink bypass / callback handler
        └── webcode.py          ← aiohttp health-check web server (GET /)
```

---

## Architecture

### Startup (`bot.py`)
1. `Bot.start()` loads banned users/chats from MongoDB into `temp.BANNED_USERS`
   and `temp.BANNED_CHATS` (in-memory lists for fast filter checks).
2. Pyrogram auto-loads every module in `plugins/` as handlers.
3. An aiohttp web server starts on `$PORT` (default 8000) to serve `GET /` for
   Koyeb health checks.
4. A keep-alive loop pings `$PUBLIC_URL/` every 4 minutes.
5. A 24-hour restart task calls `os.execv` to recycle memory.

### Config (`info.py`)
**Always import config from `info.py`** — never read `os.environ` directly in
plugins.  
`_require_str()` and `_require_int()` raise `EnvironmentError` with a clear
message if a required var is missing.

### Database (`database/`)
All DB modules expose an `async` API on a single `db` singleton.  
Motor (async pymongo wrapper) is used throughout — every DB call must be
`await`-ed.  
`ia_filterdb.py` also defines the `Media` umongo document model and
`ensure_indexes()` which must be called at startup.

### In-memory state (`utils.py → temp`)
```python
class temp:
    BANNED_USERS = []   # list of banned user IDs — populated from DB at startup
    BANNED_CHATS = []   # list of disabled chat IDs — populated from DB at startup
    ME = None           # bot's own user ID
    U_NAME = None       # bot username
    B_NAME = None       # bot display name
    MELCOW = {}         # stores the last welcome message per group (for deletion)
    SETTINGS = {}       # per-group settings cache {chat_id: settings_dict}
    CANCEL = False      # broadcast cancellation flag
    CURRENT = int(os.environ.get("SKIP", 2))
```

### Banned/disabled fast filters (`plugins/banned.py`)
`banned_user` and `disabled_group` are Pyrogram custom filters created with
`filters.create()`. They check the in-memory `temp` lists — no DB round-trip.

---

## Coding conventions

1. **Never use `print()` in bot code.** Use `logger = logging.getLogger(__name__)`
   and `logger.info/warning/error/exception`.

2. **Never shadow Python builtins.** The parameter name `filter` was renamed to
   `db_filter` throughout the codebase (Pyrogram uses `filter` as a builtin-ish
   name). Use `db_filter` for any variable that holds a database filter dict.

3. **All env vars come from `info.py`.** Do not call `os.environ.get()` directly
   in plugins or database modules.

4. **All DB calls are async.** Motor returns coroutines — always `await` them.

5. **Python 3.11 f-string rule:** You cannot have a raw (un-escaped) newline
   inside a regular `f"..."` or `"..."` string. Use `\n` for line breaks, or
   use triple-quoted strings `f"""..."""`. This has bitten this codebase
   multiple times (see Bug History below).

6. **`list.remove()` must be guarded.** `temp.BANNED_CHATS` and
   `temp.BANNED_USERS` are populated at startup from DB. If the bot restarted
   after a ban was applied, an ID may be in the DB but not in the in-memory list.
   Always wrap `.remove()` in `try/except ValueError`.

7. **Blocking calls must be offloaded.** `imdb.search_movie()` and
   `imdb.get_movie()` are synchronous — use `await asyncio.to_thread(...)`.

---

## Environment variables

See `ZiZubot/.env.example` for the full annotated reference.

### Required (bot will refuse to start without these)
| Variable | Description |
|---|---|
| `API_ID` | Telegram API ID from my.telegram.org |
| `API_HASH` | Telegram API Hash |
| `BOT_TOKEN` | Bot token from @BotFather |
| `ADMINS` | Space-separated Telegram user ID(s) |
| `DATABASE_URI` | MongoDB Atlas connection string |
| `LOG_CHANNEL` | Channel ID for bot logs (bot must be admin) |

### Strongly recommended
| Variable | Description | Default |
|---|---|---|
| `PUBLIC_URL` | Public HTTPS URL of deployment — enables keep-alive self-ping | *(disabled)* |
| `CHANNELS` | Space-separated channel IDs to index files from | *(none)* |
| `SUPPORT_CHAT` | Support group username (without @) | `ZiZuBot_support` |

### Feature flags (all optional)
`P_TTI_SHOW_OFF`, `IMDB`, `SINGLE_BUTTON`, `SPELL_CHECK_REPLY`,
`PROTECT_CONTENT`, `MELCOW_NEW_USERS`, `PUBLIC_FILE_STORE`,
`LONG_IMDB_DESCRIPTION`, `USE_CAPTION_FILTER`, `CACHE_TIME`,
`MAX_LIST_ELM`, `AUTO_APPROVE`, `WELCOME_DM`

---

## Bug history (35 bugs fixed — do not re-investigate)

All bugs below have been fixed and committed. The fixes are in `main`.

### Pattern: raw newline inside non-triple-quoted string (SyntaxError)
Python 3.11 raises `SyntaxError: unterminated string literal` when a regular
`f"..."` or `"..."` string contains a literal newline (i.e. the source line
ends before the closing quote). **All instances have been fixed** using `\n`
escape sequences. Files affected and now clean:
- `plugins/auto_approve.py` — 2 occurrences (welcome DM text, /approve_status reply)
- `plugins/banned.py` — 2 occurrences (ban reply, group-ban text)

### Pattern: `filter=True` keyword argument (TypeError at runtime)
Pyrogram filter methods do not accept `filter=True`. The codebase had 5 calls
passing this as a kwarg after a variable rename (`filter` → `db_filter`).
**All 5 fixed in `plugins/pm_filter.py`.**

### Pattern: unguarded `list.remove()` (ValueError at runtime)
`temp.BANNED_CHATS.remove()` and `temp.BANNED_USERS.remove()` crash with
`ValueError` if the bot restarted after a ban was applied (ID in DB but not
in the in-memory list). **Fixed in `plugins/p_ttishow.py`** — wrapped in
`try/except ValueError`.

### Pattern: blocking sync call on async event loop (freezes bot)
`imdb.search_movie()` and `imdb.get_movie()` are synchronous. Calling them
directly blocks the entire asyncio event loop. **Fixed in `utils.py`** —
offloaded with `await asyncio.to_thread(imdb.search_movie, ...)`.

### Pattern: `print()` instead of logger (silent error drops)
Several places used `print(traceback.format_exc())` instead of
`logger.exception()`. **Fixed in `plugins/etc.py`** and other locations.

### Other individual fixes (sessions 1–2)
- `database/ia_filterdb.py` — renamed `filter` param to `db_filter` (shadowed builtin)
- `database/users_chats_db.py` — various async/Motor fixes
- `bot.py` — port-busy retry loop; keep-alive loop; auto-delete restart message
- `info.py` — `_require_str`/`_require_int` helpers; removed dead `auth_channel` var
- `utils.py` — `list_to_str` trailing comma fix; `asyncio.to_thread` for IMDB
- `plugins/index.py` — FloodWait on `get_chat` now returns error instead of falling through
- `plugins/p_ttishow.py` — removed duplicate `/stats` handler that conflicted with `etc.py`

---

## How to make changes safely

1. **Always AST-parse Python files before committing:**
   ```python
   import ast
   ast.parse(open("file.py").read())  # raises SyntaxError if broken
   ```

2. **Test imports mentally:** Check that every name imported at the top of a
   file is actually defined/exported by its source module.

3. **After any change to `database/` files**, run `pnpm --filter @workspace/db run push`
   (or equivalent) to ensure schema changes are reflected.

4. **The in-memory `temp` lists are populated once at startup.** Any plugin that
   mutates `temp.BANNED_USERS` or `temp.BANNED_CHATS` must also update MongoDB
   and guard `.remove()` calls.

5. **Pyrogram handler precedence:** Handlers are loaded in filesystem order.
   Avoid duplicate command handlers across plugins — the first one registered
   wins silently.

---

## Running locally

```bash
cd ZiZubot
cp .env.example .env
# edit .env with your values
bash start.sh
```

## Docker / Koyeb

```bash
# Build
docker build -t zizubot .
# Run (pass env vars)
docker run --env-file ZiZubot/.env zizubot
```

Set `PUBLIC_URL` to your Koyeb service URL to enable the keep-alive self-ping.

---

## Dependency notes

| Package | Purpose |
|---|---|
| `pyrotgfork` | Pyrogram fork with extra MTProto features |
| `tgcrypto` | Fast AES for Pyrogram (required) |
| `motor==3.3.2` | Async MongoDB driver |
| `pymongo[srv]==4.6.0` | MongoDB client (Motor depends on this) |
| `umongo==3.1.0` | MongoDB ODM (used for `Media` model) |
| `marshmallow==3.18.0` | Serialisation (umongo dependency) |
| `cinemagoer` | IMDB data (installed from GitHub, not PyPI) |
| `aiohttp==3.9.5` | Async HTTP — health-check server + keep-alive ping |
| `bs4` | HTML parsing for Google spell-check fallback |
| `psutil` | System metrics (used in /stats) |
