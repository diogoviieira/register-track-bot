# 💰 Telegram Finance Tracker Bot

A Telegram bot for tracking personal expenses and incomes with multi-user support and SQLite database storage.

## 📁 Project Structure

```
register-track-bot/
├── src/                    # Main bot source code
│   └── bot.py             # Telegram bot implementation
├── utils/                  # Database management utilities
│   ├── db_browser.py      # Interactive database browser
│   ├── view_db.py         # Quick database viewer
│   └── cleanup_db.py      # Database cleanup utility
├── tests/                  # Test files
│   ├── test_multiuser.py  # Multi-user isolation tests
│   └── test_bot_features.py
├── docs/                   # Documentation
│   ├── README.md          # This file (linked from root)
│   ├── DEPLOY.md          # Deployment guide
│   ├── MIGRATION.md       # Migration documentation
│   ├── CONTRIBUTING.md    # Contribution guidelines
│   └── Commands.md        # Bot commands reference
├── config/                 # Configuration files
│   ├── register-bot.service  # Systemd service
│   └── .env.example       # Environment variables template
├── data/                   # Data directory (excluded from git)
│   ├── finance_tracker.db # SQLite database
│   ├── expenses.xlsx      # Legacy Excel files (backup)
│   ├── incomes.xlsx
│   └── REPORTS/           # Generated reports
├── run_bot.py             # Bot launcher script
├── requirements.txt       # Python dependencies
└── LICENSE

```

## 🚀 Quick Start

### Local Development

1. **Clone the repository**
   ```bash
   git clone https://github.com/diogoviieira/register-track-bot.git
   cd register-track-bot
   ```

2. **Install dependencies**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Set up environment**
   ```bash
   cp config/.env.example .env
   # Edit .env and add your TELEGRAM_BOT_TOKEN
   ```

4. **Run the bot**
   ```bash
   python run_bot.py
   ```

### Raspberry Pi Deployment

See [docs/DEPLOY.md](docs/DEPLOY.md) for complete deployment instructions.

## 📊 Database Management

### Interactive Browser
```bash
python utils/db_browser.py
```
Features: view records, search, filter by user, monthly summaries, export to CSV

### Quick View
```bash
python utils/view_db.py
```
Shows: total counts, recent entries, user statistics, monthly summary

### Cleanup Utility
```bash
python utils/cleanup_db.py
```
Options: delete test users, delete by date range, delete all data, vacuum database

## 🔑 Features

- 💸 Track expenses and incomes
- 📅 Date-based organization
- 📂 Category and subcategory system
- 👥 Multi-user support with data isolation
- 🔍 Search and filter capabilities
- 📊 Monthly summaries and statistics
- 🗄️ SQLite database (no Excel files)
- 🔐 Secure user data separation
- 🛠️ Database management utilities

## 📝 Bot Commands

- `/start` - Start the bot
- `/expense` - Register a new expense
- `/income` - Register a new income
- `/view` - View your entries
- `/help` - Show help message

See [docs/Commands.md](docs/Commands.md) for detailed command reference.

## 🧪 Testing

```bash
# Run multi-user isolation tests
python tests/test_multiuser.py
```

## 🤝 Contributing

See [docs/CONTRIBUTING.md](docs/CONTRIBUTING.md) for contribution guidelines.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🔗 Links

- **Documentation**: [docs/](docs/)
- **Deployment Guide**: [docs/DEPLOY.md](docs/DEPLOY.md)
- **Migration Guide**: [docs/MIGRATION.md](docs/MIGRATION.md)
