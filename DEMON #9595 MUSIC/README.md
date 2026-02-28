# ✦ Aesthetic Music Bot

A playful, aesthetic Discord music bot built with `discord.py` and `yt-dlp`.

## Features
- 🎵 Play music from YouTube search or URLs
- 📜 Queue management with pagination
- 🔁 Loop modes: off / single / queue
- 🔀 Shuffle
- 🎨 Beautiful embeds with progress bars and playful messages
- 🎛️ Button controls on now-playing cards
- ⚡ Hybrid commands (both `!prefix` and `/slash`)

## Commands

| Command | Aliases | Description |
|---------|---------|-------------|
| `!play <query>` | `!p` | Play a song or add to queue |
| `!skip` | `!s` | Skip current song |
| `!pause` | — | Pause playback |
| `!resume` | `!r` | Resume playback |
| `!queue [page]` | `!q` | View the queue |
| `!nowplaying` | `!np` | Show current track |
| `!loop [off/single/queue]` | — | Set loop mode |
| `!shuffle` | — | Shuffle the queue |
| `!volume <0-100>` | `!vol` | Set volume |
| `!remove <position>` | — | Remove from queue |
| `!clear` | — | Clear the queue |
| `!lyrics [query]` | — | Look up lyrics |
| `!leave` | `!dc` | Disconnect the bot |
| `!ping` | — | Check latency |

## Deploying on Railway

1. Push this repo to GitHub
2. Go to [railway.app](https://railway.app) → **New Project** → **Deploy from GitHub repo**
3. Select this repo
4. In the **Variables** tab, add:
   - `DISCORD_TOKEN` = your bot token
5. Railway will auto-detect `nixpacks.toml` and install FFmpeg ✅
6. The `Procfile` tells Railway to run `python main.py` as a **worker** (not a web server)

## Local Development

```bash
# 1. Clone the repo
git clone <your-repo-url>
cd <repo>

# 2. Install dependencies
pip install -r requirements.txt

# 3. Create your .env file
cp .env.example .env
# Edit .env and add your DISCORD_TOKEN

# 4. Run the bot
python main.py
```

> ⚠️ **Never commit your `.env` file or bot token!** It's already in `.gitignore`.

## Requirements
- Python 3.11+
- FFmpeg (auto-installed on Railway via `nixpacks.toml`)
