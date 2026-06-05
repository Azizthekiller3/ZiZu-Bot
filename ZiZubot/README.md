# ZiZubot™

A powerful Telegram auto-filter bot — rebranded from KuttuBot. Supports auto-filter, manual filters, IMDB info, spell-check, inline search, file store, broadcast, indexing, ban/unban, per-group settings, force-subscribe, auto-approve join requests, and shortlink monetization.

---

## Quick Deploy

```bash
git clone https://github.com/Azizthekiller3/ZiZu-Bot
cd ZiZu-Bot/ZiZubot
cp .env.example .env
nano .env           # fill in your values
bash start.sh
```

---

## Prerequisites

| Requirement | How to get it |
|-------------|--------------|
| Python 3.11+ |  |
| pip |  |
| MongoDB Atlas (free) | [mongodb.com/atlas](https://www.mongodb.com/atlas/database) |
| Telegram API credentials | [my.telegram.org](https://my.telegram.org) → API Development Tools |
| Bot token | [@BotFather](https://t.me/BotFather) →  |

---

## Step-by-Step Setup

### 1 — Clone the repo
```bash
git clone https://github.com/Azizthekiller3/ZiZu-Bot
cd ZiZu-Bot/ZiZubot
```

### 2 — Copy and fill the config
```bash
cp .env.example .env
nano .env
```

Fill in every **required** value (see table below). Save with , exit with .

### 3 — Run the bot
```bash
bash start.sh
```

The script automatically installs all Python dependencies and starts the bot.

---

## Environment Variables

Copy  to  and set these values.

### Required

| Variable | Description | Example |
|----------|-------------|---------|
|  | Telegram API ID from my.telegram.org |  |
|  | Telegram API Hash from my.telegram.org |  |
|  | Bot token from @BotFather |  |
|  | Your Telegram user ID(s), space-separated |  |
|  | MongoDB Atlas connection string |  |
|  | Channel ID where the bot sends logs (bot must be admin) |  |

### Optional but Recommended

| Variable | Description | Default |
|----------|-------------|---------|
|  | Your public HTTPS URL — enables the keep-alive self-ping every 4 min to prevent free-tier hosts (Koyeb, Render) from sleeping. Set to your service URL, e.g.  | *(empty — keep-alive disabled)* |
|  | Pyrogram session name |  |
|  | Channel ID(s) to index files from, space-separated | *(empty)* |
|  | Force-subscribe channel ID | *(none)* |
|  | Username of your support group |  |
|  | MongoDB database name |  |
|  | MongoDB collection name for indexed files |  |
|  | Channel to receive index requests | same as  |
|  | Channel(s) for file-store feature | *(empty)* |

### Feature Flags

| Variable | Description | Default |
|----------|-------------|---------|
|  | Send files to user PM instead of group |  |
|  | Show IMDB info on search results |  |
|  | Single-column file buttons |  |
|  | Suggest spelling corrections |  |
|  | Enable forward-protection on files |  |
|  | Send welcome video to new group members |  |
|  | Allow anyone to use file-store links |  |
|  | Show full IMDB plot |  |
|  | Search within file captions too |  |
|  | Inline query cache time in seconds |  |
|  | Max cast/crew items to show | *(full list)* |
|  | Auto-approve join requests (/) |  |
|  | Send DM when auto-approving (/) |  |

### Captions & Templates

| Variable | Description |
|----------|-------------|
|  | Caption template for files. Supports , ,  |
|  | Caption template for batch files |
|  | Template for IMDB result messages. Supports , , , , , etc. |

---

## Hosting

### Koyeb (recommended free-tier)

1. Fork this repo
2. Create a new Koyeb service → **Deploy from GitHub**
3. Set **Dockerfile** as the builder (detected automatically)
4. Add all required environment variables in Koyeb → Settings → Variables
5. **Important:** also set  to your Koyeb service URL (e.g. ) — this enables the keep-alive ping that prevents the free-tier instance from sleeping
6. Click **Deploy**

### Railway

1. Fork this repo
2. Create a new Railway project → **Deploy from GitHub repo**
3. Set all environment variables in Railway → Variables
4. Railway uses the included  and  automatically
5. Set  to your Railway public domain

### VPS (Ubuntu/Debian)

```bash
git clone https://github.com/Azizthekiller3/ZiZu-Bot
cd ZiZu-Bot/ZiZubot
cp .env.example .env && nano .env
screen -S zizubot
bash start.sh
# Ctrl+A then D to detach
```

### Local / Replit

Add all variables as environment secrets, then run  or .

---

## Admin Commands

### General
| Command | Description |
|---------|-------------|
|  | Show database statistics (files, users, chats, DB size) |
|  | List all bot users |
|  | List all connected chats |
|  | Ban a user |
|  | Unban a user |
|  | Leave a chat |
|  | Disable bot in a chat |
|  | Re-enable a disabled chat |
|  | Broadcast a message to all users (reply to a message) |
|  | Live server CPU/RAM/disk usage |

### Indexing
| Command | Description |
|---------|-------------|
|  | Index a channel — forward a message from it or send the channel link |
|  | Set message offset for indexing |
|  | Delete a specific file from the database |

### Auto-Approve
| Command | Description |
|---------|-------------|
|  | Enable auto-approve join requests |
|  | Disable auto-approve join requests |
|  | Enable welcome DM on approval |
|  | Disable welcome DM on approval |
|  | Show current auto-approve settings |

### Shortlink & Monetization
| Command | Description |
|---------|-------------|
|  | Set shortlink service (e.g. publicearn.com) |
|  | Check shortlink config |
|  | How many times per day users must verify (0 = off) |
|  | Disable shortlink and send files directly |

---

## How Shortlink Monetization Works

1. Create an account on a shortener like [publicearn.com](https://publicearn.com)
2. Copy your API key from their dashboard
3. Send your bot: 
4. Send: 
5. Every file request now goes through the ad shortlink — you earn money, users still get their files

---

## How to Index Files

1. Make the bot an admin in your file channel
2. Forward any message from that channel to the bot in PM
3. The bot asks you to confirm — click **Yes**
4. The bot indexes all files up to that message ID

---

## Project Structure

```
ZiZubot/
├── bot.py                  # Main entry point + keep-alive web server
├── info.py                 # All config / env var parsing
├── utils.py                # Shared helpers (IMDB, subscriptions, etc.)
├── Script.py               # All message text templates
├── start.sh                # Local startup script
├── requirements.txt        # Python dependencies
├── .env.example            # Config template — copy to .env
├── assets/
│   └── zizubot_logo.jpg
├── database/
│   ├── ia_filterdb.py      # Indexed file collection + search
│   ├── users_chats_db.py   # Users, chats, ban status
│   ├── filters_mdb.py      # Manual keyword filters
│   ├── connections_mdb.py  # PM ↔ group connections
│   └── shortlink_db.py     # Shortlink config per group
└── plugins/
    ├── commands.py         # /start, file delivery, verify flow
    ├── pm_filter.py        # Auto-filter, spell-check, all callbacks
    ├── filters.py          # Manual filter CRUD commands
    ├── shortlink.py        # Shortlink commands
    ├── index.py            # Channel indexing
    ├── broadcast.py        # /broadcast command
    ├── etc.py              # /ping, /usage, /id, /info, /stats
    ├── misc.py             # Settings, IMDB, connections
    ├── channel.py          # Auto-save media from indexed channels
    ├── p_ttishow.py        # New group join, leave/disable/enable/ban
    ├── auto_approve.py     # Join request auto-approval
    ├── banned.py           # Banned user/chat filter
    ├── connection.py       # /connect /disconnect /connections
    ├── inline.py           # Inline query handler
    ├── mov_ser_latest.py   # /movies and /series latest list
    └── webcode.py          # Health-check HTTP endpoint
```

---

## Updating

```bash
git pull
bash start.sh
```

On Koyeb/Railway: just push to GitHub — it redeploys automatically if connected.

---

## License

This bot is based on [KuttuBot](https://github.com/GouthamSER/KuttuBot). Rebranded as **ZiZubot™**.
