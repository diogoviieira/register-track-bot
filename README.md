# 💰 Telegram Finance Tracker Bot

> A production-ready Telegram bot for personal finance management with multi-user support, built for reliability and ease of use.

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Telegram Bot](https://img.shields.io/badge/Telegram-Bot-blue.svg?logo=telegram)](https://core.telegram.org/bots)

## ✨ Features

- 💬 **Conversational Interface** - Natural conversation flow for logging expenses
- 🏷️ **Smart Categorization** - Pre-defined categories with auto-descriptions for common expenses
- 📊 **Multi-User Support** - Isolated data per user with secure access control
- 💾 **SQLite Database** - Lightweight, reliable, and perfect for 24/7 operation
- 🔍 **Powerful Queries** - View, edit, and analyze your expenses by date or month
- 📈 **Monthly Summaries** - Track spending patterns with category breakdowns
- 🛠️ **Management Tools** - Interactive browser, viewer, and cleanup utilities included
- 🚀 **Production Ready** - Systemd service configuration for Raspberry Pi deployment

## 🚀 Quick Start

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

# Set your bot token
export TELEGRAM_BOT_TOKEN="your_bot_token_here"  # Linux/Mac
# Windows: $env:TELEGRAM_BOT_TOKEN="your_bot_token_here"

# Run the bot
python run_bot.py

# Or without activating venv (use full path):
# .venv/Scripts/python run_bot.py  (Windows)
# .venv/bin/python run_bot.py      (Linux/Mac)
```

> **Windows Note**: If you get "running scripts is disabled", either:
> - Use full path: `.venv\Scripts\python.exe run_bot.py`
> - Or enable scripts once: `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`

## 📁 Project Structure

```
register-track-bot/
├── src/bot.py              # Main bot logic
├── utils/                  # Database management tools
├── tests/                  # Test suite
├── docs/                   # Documentation
├── config/                 # Configuration files
├── data/                   # Database storage (auto-created)
└── run_bot.py              # Entry point
```

## 📖 Usage

### Basic Commands

```
/start      - Start the bot and see available commands
/add    - Log a new expense
/income     - Record income
/view       - View entries for today or specific date
/month      - View monthly summary
/edit       - Modify existing entries
/delete     - Remove entries
/help       - Show all commands
```

### Example Workflow

1. Start a conversation: `/add`
2. Select category (e.g., "Home", "Car", "Food")
3. Choose subcategory (e.g., "Rent", "Fuel", "Groceries")
4. Enter amount: `45.50`
5. Add description or skip (auto-filled for common items)
6. Done! ✅

### Monthly Overview

```
/month november
```

Get instant summaries with category breakdowns and totals.

## 🏗️ Architecture

- **Bot Framework**: python-telegram-bot 22.5
- **Database**: SQLite with optimized indexes
- **Design**: Conversation-based state management
- **Security**: User ID-based data isolation
- **Performance**: Thread-safe connections, ~20-30MB RAM

## 🛠️ Database Tools

Three built-in utilities for database management:

| Tool | Purpose | Use Case |
|------|---------|----------|
| `db_browser.py` | Interactive browser | Query, search, export to CSV |
| `view_db.py` | Quick viewer | Check stats and recent entries |
| `cleanup_db.py` | Data cleanup | Remove test data, optimize DB |

```bash
python utils/db_browser.py  # Full-featured browser
python utils/view_db.py     # Quick overview
python utils/cleanup_db.py  # Maintenance
```

## 🎯 Key Highlights

### Production Ready
- ✅ Systemd service for 24/7 uptime on Raspberry Pi
- ✅ Automatic restart on failure
- ✅ Comprehensive logging and monitoring

### Developer Friendly
- Clean, modular codebase
- Well-documented functions
- Comprehensive test suite
- Easy to extend and customize

### User Experience
- Intuitive conversation flow
- Smart auto-completion
- European date format support (DD/MM/YY)
- Multi-language month recognition

## 🚢 Deployment

Designed for Raspberry Pi but works anywhere Python runs.

### Raspberry Pi Setup

```bash
# Clone and install
git clone https://github.com/diogoviieira/register-track-bot.git
cd register-track-bot
pip3 install -r requirements.txt

# Configure service
sudo cp config/register-bot.service /etc/systemd/system/
sudo systemctl enable register-bot.service
sudo systemctl start register-bot.service
```

📖 **Full guide**: [docs/DEPLOY.md](docs/DEPLOY.md)

### Docker (Coming Soon)

```bash
docker run -e TELEGRAM_BOT_TOKEN=your_token diogoviieira/finance-tracker
```

## 🧪 Testing

```bash
python tests/test_multiuser.py  # Multi-user isolation
python tests/test_bot_features.py  # Feature tests
```

## 📚 Documentation

- [Deployment Guide](docs/DEPLOY.md) - Raspberry Pi setup and systemd configuration
- [Migration Notes](docs/MIGRATION.md) - Excel to SQLite migration details
- [Contributing](docs/CONTRIBUTING.md) - Guidelines for contributors
- [Commands Reference](docs/Commands.md) - Complete command documentation

## 🤝 Contributing

Contributions are welcome! Please read [CONTRIBUTING.md](docs/CONTRIBUTING.md) first.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 💬 Support

Found a bug? Have a feature request? [Open an issue](https://github.com/diogoviieira/register-track-bot/issues)

---

<p align="center">Made with ❤️ for personal finance management</p>
<p align="center">Built with Python • Telegram Bot API • SQLite</p>
