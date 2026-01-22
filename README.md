# 💰 Telegram Finance Tracker Bot

A Telegram bot for personal finance tracking with multi-user support. Track expenses and income through natural conversation, view monthly summaries, and manage your finances easily.

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg?logo=docker)](https://www.docker.com/)

## ✨ Features

- 💬 Conversational interface for logging expenses and income
- 🏷️ Smart categorization with auto-suggestions
- 📊 Multi-user support with isolated data
- 💾 SQLite database for reliability
- 📈 Monthly summaries and analytics
- 🔍 Query and edit past transactions
- 🐳 Docker ready for 24/7 operation

## 🚀 Quick Start

### Docker Deployment (Recommended)

```bash
# Clone and configure
git clone https://github.com/diogoviieira/register-track-bot.git
cd register-track-bot
cp .env.example .env

# Add your bot token to .env
nano .env

# Deploy
docker compose up -d
```

### Local Development

```bash
# Clone the repository
git clone https://github.com/diogoviieira/register-track-bot.git
cd register-track-bot

# Set up virtual environment (recommended)
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# Windows PowerShell: .venv\Scripts\Activate.ps1
# Windows CMD: .venv\Scripts\activate.bat

# Install dependencies
pip install -r requirements.txt

```bash
# Install dependencies
pip install -r requirements.txt

# Set your bot token
export TELEGRAM_BOT_TOKEN="your_token_here"

# Run
python run_bot.py
```

## 📖 Usage

**Available Commands:**
- `/start` - Start the bot
- `/add` - Log an expense
- `/income` - Record income
- `/view` - View entries (today or specific date)
- `/month` - Monthly summary
- `/edit` - Modify entries
- `/delete` - Remove entries
- `/help` - Show all commands

**Example:**
1. `/add` → Select category → Choose subcategory
2. Enter amount: `45.50`
3. Add description (optional)
4. Done! ✅

## 🏗️ Tech Stack

- **Framework**: python-telegram-bot 21.7
- **Database**: SQLite (thread-safe)
- **Deployment**: Docker + Docker Compose
- **Requirements**: Python 3.8+

## 📦 Environment Variables

```env
TELEGRAM_BOT_TOKEN=your_bot_token_here  # Required
LOG_LEVEL=INFO                          # Optional (DEBUG, INFO, WARNING, ERROR)
TZ=Europe/Lisbon                        # Optional (timezone)
```

## 🐳 Docker Details

The bot runs as a non-root user with:
- Auto-restart on failure
- Health checks every 60s
- Log rotation (max 30MB)
- Resource limits (256MB RAM, 50% CPU)

**Common Commands:**
```bash
docker compose up -d              # Start
docker compose logs -f            # View logs
docker compose restart            # Restart
docker compose down               # Stop
```

## 📝 License

MIT License - see [LICENSE](LICENSE) file

## 🤝 Contributing

Contributions are welcome! Feel free to open issues or submit pull requests.
- Intuitive conversation flow
- Smart auto-completion
- European date format support (DD/MM/YY)
- Multi-language month recognition

## 🚢 Deployment

### 🐳 Docker (Recommended for 24/7)

**Best for**: Production servers, home servers, VPS, Raspberry Pi

```bash
# Quick deploy (5 minutes)
cp .env.example .env && nano .env  # Add your TELEGRAM_BOT_TOKEN
docker compose up -d
```

**Features**: Auto-restart, health monitoring, resource limits, log rotation, security hardening

**Docs**: [Docker Guide](docs/DEPLOY-DOCKER.md) | [Quick Start](QUICKSTART-DOCKER.md) | [Quick Reference](QUICK-REFERENCE.md)

---

### 🍓 Traditional Deployment

Optimized for 24/7 operation on Linux, Windows, or cloud platforms.

### Ubuntu / Debian (Recommended)

```bash
# Quick setup
sudo apt update && sudo apt install python3 python3-venv git -y
---

<p align="center">Made with ❤️ for personal finance tracking</p>

