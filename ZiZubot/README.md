# ZiZubot™

A powerful Telegram auto-filter bot — rebranded from KuttuBot. Supports auto-filter, manual filters, IMDB info, spell-check, inline search, file store, broadcast, indexing, ban/unban, per-group settings, force-subscribe, auto-approve join requests, and shortlink monetization.

---

## Quick Deploy

```bash
git clone https://github.com/YOUR_USERNAME/ZiZubot
cd ZiZubot/ZiZubot
cp .env.example .env
nano .env           # fill in your values
bash start.sh
```

---

## Prerequisites

| Requirement | How to get it |
|-------------|--------------|
| Python 3.10+ | `sudo apt install python3` |
| pip | `sudo apt install python3-pip` |
| MongoDB Atlas (free) | [mongodb.com/atlas](https://www.mongodb.com/atlas/database) |
| Telegram API credentials | [my.telegram.org](https://my.telegram.org) → API Development Tools |
| Bot token | [@BotFather](https://t.me/BotFather) → `/newbot` |

---

## Step-by-Step Setup

### 1 — Clone the repo
```bash
git clone https://github.com/YOUR_USERNAME/ZiZubot
cd ZiZubot/ZiZubot
```

### 2 — Copy and fill the config
```bash
cp .env.example .env
nano .env
```

Fill in every **required** value (see table below). Save with `Ctrl+O`, exit with `Ctrl+X`.

### 3 — Run the bot
```bash
bash start.sh
```

The script automatically installs all Python dependencies and starts the bot.

---

## Environment Variables

Copy `.env.example` to `.env` and set these values.

### Required

| Variable | Description | Example |
|----------|-------------|---------|
| `API_ID` | Telegram API ID from my.telegram.org | `1234567` |
| `API_HASH` | Telegram API Hash from my.telegram.org | `abc123def456...` |
| `BOT_TOKEN` | Bot token from @BotFather | `123456:ABC-...` |
| `ADMINS` | Your Telegram user ID(s), space-separated | `987654321` |
| `DATABASE_URI` | MongoDB Atlas connection string | `mongodb+srv://user:pass@cluster.mongodb.net` |
| `LOG_CHANNEL` | Channel ID where the bot sends logs (bot must be admin) | `-1001234567890` |

### Optional but Recommended

| Variable | Description | Default |
|----------|-------------|---------|
| `CHANNELS` | Channel ID(s) to index files from, space-separated | *(empty)* |
| `AUTH_CHANNEL` | Force-subscribe channel ID | *(none)* |
| `SUPPORT_CHAT` | Username of your support group | `ZiZuBot_support` |
| `DATABASE_NAME` | MongoDB database name | `ZiZuBot` |
| `INDEX_REQ_CHANNEL` | Channel to receive index requests | same as `LOG_CHANNEL` |

### Feature Flags

| Variable | Description | Default |
|----------|-------------|---------|
| `P_TTI_SHOW_OFF` | Send files to user PM instead of group | `True` |
| `IMDB` | Show IMDB info on search results | `False` |
| `SINGLE_BUTTON` | Single-column file buttons | `True` |
| `SPELL_CHECK_REPLY` | Suggest spelling corrections | `True` |
| `PROTECT_CONTENT` | Enable forward-protection on files | `False` |
| `MELCOW_NEW_USERS` | Send welcome video to new group members | `True` |
| `PUBLIC_FILE_STORE` | Allow anyone to use file-store links | `False` |
| `LONG_IMDB_DESCRIPTION` | Show full IMDB plot | `False` |
| `USE_CAPTION_FILTER` | Search within file captions too | `False` |
| `CACHE_TIME` | Inline query cache time in seconds | `300` |

### Captions & Templates

| Variable | Description |
|----------|-------------|
| `CUSTOM_FILE_CAPTION` | Caption template for files. Supports `{file_name}`, `{file_size}`, `{file_caption}` |
| `BATCH_FILE_CAPTION` | Caption template for batch files |
| `IMDB_TEMPLATE` | Template for IMDB result messages. Supports `{title}`, `{year}`, `{rating}`, `{genres}`, `{url}`, etc. |

---

## Admin Commands

### General
| Command | Description |
|---------|-------------|
| `/stats` | Show database statistics |
| `/logs` | Get recent error logs |
| `/users` | List all bot users |
| `/chats` | List all connected chats |
| `/ban <user>` | Ban a user |
| `/unban <user>` | Unban a user |
| `/leave <chat_id>` | Leave a chat |
| `/disable <chat_id>` | Disable a chat |
| `/enable <chat_id>` | Re-enable a disabled chat |
| `/broadcast` | Broadcast a message to all users |
| `/channel` | List indexed channels |
| `/restart` | Restart the bot |

### Indexing
| Command | Description |
|---------|-------------|
| `/index` | Start indexing a channel (forward a message or send channel link) |
| `/setskip <n>` | Set message offset for indexing |
| `/delete` | Delete a file from DB |

### Shortlink & Monetization
| Command | Description |
|---------|-------------|
| `/shortlink <domain> <api_key>` | Set shortlink service (e.g. publicearn.com) |
| `/shortlink_status` | Check shortlink config |
| `/set_daily_verify <n>` | How many times per day users must verify (0 = off) |
| `/remove_shortlink` | Disable shortlink and send files directly |

---

## How Shortlink Monetization Works

1. Create an account on a shortener like [publicearn.com](https://publicearn.com), [omnifly.in](https://omnifly.in), or [shortslink.in](https://shortslink.in)
2. Copy your API key from their dashboard
3. Send your bot: `/shortlink publicearn.com YOUR_API_KEY`
4. Send: `/set_daily_verify 1`
5. Every file request now goes through the ad shortlink — you earn money, users still get their files

---

## How to Index Files

1. Make the bot an admin in your file channel
2. Forward any message from that channel to the bot in PM
3. The bot will ask you to confirm indexing
4. Click **Yes** — the bot indexes all files up to that message

OR send a channel link like: `https://t.me/c/1234567890/500`

---

## Project Structure

```
ZiZubot/
├── bot.py              # Main entry point
├── info.py             # All config / env vars
├── utils.py            # Shared utilities (IMDB, subscriptions, etc.)
├── Script.py           # All message templates
├── start.sh            # Universal startup script
├── requirements.txt    # Python dependencies
├── .env.example        # Config template (copy to .env)
├── assets/
│   └── zizubot_logo.jpg
├── database/
│   ├── ia_filterdb.py      # File index DB
│   ├── users_chats_db.py   # Users & chats DB
│   ├── filters_mdb.py      # Manual filters DB
│   ├── connections_mdb.py  # Group connections DB
│   └── shortlink_db.py     # Shortlink config DB
└── plugins/
    ├── commands.py     # /start and file delivery
    ├── pm_filter.py    # Auto-filter + all callbacks
    ├── filters.py      # Manual filter commands
    ├── shortlink.py    # Shortlink monetization
    ├── index.py        # Channel indexing
    ├── broadcast.py    # Broadcast
    ├── etc.py          # /ping, /usage, /id, /info
    ├── misc.py         # Settings, connections
    ├── channel.py      # Auto-save files from channels
    └── ...
```

---

## Updating

```bash
git pull
bash start.sh
```

---

## Hosting Options

| Platform | Notes |
|----------|-------|
| **VPS (Ubuntu/Debian)** | `bash start.sh` in a `screen` or `tmux` session |
| **Replit** | Add secrets via Replit Secrets panel |
| **Railway / Render** | Set env vars in the platform dashboard, run `python bot.py` |

---

## License

This bot is based on [KuttuBot](https://github.com/GouthamSER/KuttuBot). Rebranded as **ZiZubot™**.
