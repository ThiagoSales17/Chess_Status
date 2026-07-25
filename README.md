# ♟️ Chess Discord Rich Presence

Show your Chess.com stats directly on your Discord profile in real time!

![Discord Rich Presence Preview](github_preview.png)

```
🟢 YourName
   ♟️ | Chess stats
   Wins 5 | Losses 5 | Draws 2
```

---

## ✨ Features

### 🔧 Bug Fixes
- **Username case-insensitive** — `Twg2000` vs `twg2000` works correctly
- **Error handling** — InvalidID and network errors handled separately
- **RPC cleanup** — Socket IPC closes properly on crash (SIGINT/SIGTERM)
- **Retry/backoff** — Exponential backoff for Chess.com API failures

### 🟡 Game Modes & Stats
- **Multiple game modes** — Rapid, Blitz, Bullet, Daily
- **Interactive mode selection** — Menu in terminal to switch modes
- **Detailed stats** — Rating, Wins, Losses, Draws, Win Rate
- **Country flags** — Shows player's country with flag emoji
- **Avatar display** — Your Chess.com profile picture in Discord
- **Last online** — Shows when player was last active
- **Followers count** — Display follower count
- **League display** — Current league with icons
- **Live game detection** — Shows "Playing vs opponent" when in a game
- **Rating history** — ASCII chart showing rating changes
- **Rating notifications** — Detects and displays rating changes

### 🟢 Advanced Features
- **Config via .env or CLI** — Save settings in `.env` file or use arguments
- **Hot reload** — Change settings without restarting
- **Multi-account** — Monitor multiple players at once
- **Leaderboard** — Compare stats with friends
- **Streamer mode** — Extra info when streaming
- **GUI mode** — Tkinter interface for easy configuration

---

## 📋 Requirements

- Python 3.10+
- Discord Desktop App (must be running)
- A Chess.com account
- A Discord Application ID

---

## 📦 Installation

**1. Clone the repository**
```bash
git clone https://github.com/ThiagoSales17/Chess_Status.git
cd Chess_Status
```

**2. Create virtual environment**
```bash
python3 -m venv env
source env/bin/activate
```

**3. Install dependencies**
```bash
pip install -r requirements.txt
```

---

## ⚙️ Setup

<p align="center">
  <img src="github_preview1.png" alt="Discord Developer Portal" width="90%">
</p>

### Discord Application ID
1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Click **New Application** and name it (e.g. `Chess Stats`)
3. Copy the **Application ID**

### Rich Presence Image (Optional)
1. In the Developer Portal go to **Rich Presence** → **Art Assets**
2. Upload an image and name it `chess`

---

## 🚀 Usage

### Terminal Mode
```bash
./chess.sh
```

### GUI Mode
```bash
./chess-gui.sh
```

### Manual
```bash
python3 main.py
```

### Command Line Arguments
```bash
python3 main.py --username twg2000 --appid 1234567890
python3 main.py --game-mode blitz --interval 10
python3 main.py --multi-account user1 user2
python3 main.py --streamer
python3 main.py --gui
```

### Environment Variables (.env)
```env
CHESS_USERNAME=twg2000
DISCORD_APP_ID=1234567890
GAME_MODE=rapid
UPDATE_INTERVAL=15
MULTI_ACCOUNT=user1,user2
STREAMER_MODE=true
```

---

## 📁 Project Structure

```
Chess_Status/
├── main.py           # Entry point, game loop
├── config.py         # Config: argparse + .env + hot reload
├── chess_api.py      # Chess.com API wrapper with cache
├── models.py         # Dataclasses for player data
├── presence.py       # Discord RPC management
├── utils.py          # Helpers, rating tracker, leaderboard
├── gui.py            # Tkinter GUI interface
├── chess.sh          # Terminal startup script
├── chess-gui.sh      # GUI startup script
├── requirements.txt  # Python dependencies
├── .env.example      # Config template
└── LICENSE           # MIT License
```

---

## 🛠️ Built With

- [requests](https://docs.python-requests.org/) — Fetch data from Chess.com API
- [pypresence](https://pypresence.dev/) — Update Discord Rich Presence
- [Chess.com API](https://www.chess.com/news/view/published-data-api) — Public chess stats
- [Tkinter](https://docs.python.org/3/library/tkinter.html) — GUI interface

---

## 📄 License

MIT License — feel free to use and modify!

---

## 🙏 Acknowledgments

- [Chess.com](https://www.chess.com) for the public API
- [Discord](https://discord.com) for Rich Presence support
- Original project by [Saul-Goodman6](https://github.com/Saul-Goodman6/Chess_Status)
