# ZiZubot™ — Telegram Auto-Filter Bot

> A full-featured Telegram movie/file bot with auto-filter, IMDB lookup, shortlink monetisation, inline search, group management, and keep-alive hosting support.

Based on [KuttuBot](https://github.com/GouthamSER/KuttuBot) · Maintained by [@Azizthekiller3](https://github.com/Azizthekiller3)

---

## Quick Start

```bash
git clone https://github.com/Azizthekiller3/ZiZu-Bot
cd ZiZu-Bot/ZiZubot
cp .env.example .env
nano .env          # fill required values
bash start.sh
```

Or deploy with Docker (Koyeb / Railway / Render):

```bash
git clone https://github.com/Azizthekiller3/ZiZu-Bot
# Set environment variables in your platform dashboard — see ZiZubot/README.md
```

## 📖 Full Documentation

See **[ZiZubot/README.md](ZiZubot/README.md)** for:
- Complete environment variable reference
- Step-by-step local setup
- Koyeb, Railway, and VPS deployment guides
- Admin command list
- Shortlink monetisation setup
- How to index files from channels

## What it does

| Feature | Description |
|---------|-------------|
| 🎬 Auto-filter | Sends matching files when users type a movie/show name in a group |
| 🔍 Inline search | Works in any chat via  |
| 📚 Manual filters | Admins can set keyword → reply mappings |
| 🏷 IMDB info | Displays rating, genres, and plot with each result |
| 💸 Shortlink ads | Every file delivery goes through a shortlink so you earn money |
| 🔗 File store | Generate permanent bot links to any file |
| 📡 Channel indexer | Index an entire channel with one command |
| 👥 Group management | Ban, mute, force-subscribe, per-group settings |
| 📢 Broadcast | Send messages to all users at once |
| ✅ Auto-approve | Automatically approve channel join requests |

## Repo structure

```
ZiZu-Bot/
├── Dockerfile          # Docker image (used by Koyeb/Railway)
├── Procfile            # Heroku/Koyeb worker command
├── railway.toml        # Railway deployment config
└── ZiZubot/            # All bot source code
    ├── .env.example    # Config template — copy to .env
    ├── README.md       # Full setup and deployment docs
    ├── bot.py          # Entry point
    ├── info.py         # Environment variable parser
    ├── utils.py        # Shared helpers
    ├── Script.py       # All message templates
    ├── database/       # MongoDB collections
    └── plugins/        # Pyrogram message handlers
```

## Requirements

- Python 3.11+
- MongoDB Atlas (free tier works)
- Telegram API credentials from [my.telegram.org](https://my.telegram.org)
- A bot token from [@BotFather](https://t.me/BotFather)

## License

Based on the open-source [KuttuBot](https://github.com/GouthamSER/KuttuBot).
