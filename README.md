<p align="center">
  <img src="https://img.icons8.com/fluency/96/money-bag.png" alt="Finance Bot Logo" width="96"/>
</p>

<h1 align="center">💰 Telegram Finance Tracker Bot</h1>

<p align="center">
  <strong>A personal finance tracking bot for Telegram with multi-user support</strong>
</p>

<p align="center">
  <a href="https://www.python.org/downloads/"><img src="https://img.shields.io/badge/python-3.8+-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python 3.8+"/></a>
  <a href="https://www.docker.com/"><img src="https://img.shields.io/badge/Docker-Ready-2496ED?style=for-the-badge&logo=docker&logoColor=white" alt="Docker Ready"/></a>
  <a href="https://opensource.org/licenses/MIT"><img src="https://img.shields.io/badge/License-MIT-green?style=for-the-badge" alt="MIT License"/></a>
</p>

<p align="center">
  <a href="#-features">Features</a> •
  <a href="#-quick-start">Quick Start</a> •
  <a href="#-commands">Commands</a> •
  <a href="#-categories">Categories</a> •
  <a href="#-pdf-reports">PDF Reports</a> •
  <a href="#-tech-stack">Tech Stack</a>
</p>

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 💬 **Conversational UI** | Natural flow for logging expenses and income |
| 🏷️ **Smart Categories** | 10 categories with 50+ subcategories, auto-descriptions |
| 👥 **Multi-User** | Isolated data per Telegram user |
| 📄 **PDF Export** | Generate professional reports (week/month/year) |
| 📊 **Analytics** | Monthly summaries with category breakdowns |
| ✏️ **Full CRUD** | Add, view, edit, delete entries anytime |
| 📅 **Date Support** | Log expenses for any past date |
| 🐳 **Production Ready** | Docker deployment with auto-restart |

---

## 🚀 Quick Start

### Docker Deployment (Recommended)

```bash
# Clone repository
git clone https://github.com/diogoviieira/register-track-bot.git
cd register-track-bot

# Configure environment
cp .env.example .env
nano .env  # Add your TELEGRAM_BOT_TOKEN

# Deploy (runs 24/7 with auto-restart)
docker compose up -d

# View logs
docker compose logs -f
```

### Local Development

```bash
# Clone and setup
git clone https://github.com/diogoviieira/register-track-bot.git
cd register-track-bot
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install and run
pip install -r requirements.txt
export TELEGRAM_BOT_TOKEN="your_token_here"
python run_bot.py
```

---

## 📱 Commands

### Daily Operations

| Command | Description |
|---------|-------------|
| `/add` | Log a new expense for today |
| `/view` | View today's expenses |
| `/summary` | Get today's summary with totals |
| `/edit` | Edit an expense from today |
| `/delete` | Delete an expense from today |

### Date-Specific Operations

| Command | Description |
|---------|-------------|
| `/add_d` | Add expense for a specific date |
| `/view_d` | View expenses for a specific date |
| `/edit_d` | Edit expense from a specific date |
| `/delete_d` | Delete expense from a specific date |

### Reports & Analytics

| Command | Description |
|---------|-------------|
| `/month <name>` | View monthly expenses (e.g., `/month january`) |
| `/income <month>` | View monthly income (e.g., `/income january`) |
| `/pdf` | 📄 **Export PDF report** (week/month/year) |

### Utility

| Command | Description |
|---------|-------------|
| `/help` | Show all available commands |
| `/cancel` | Cancel current operation |

---

## 🏷️ Categories

<details>
<summary><strong>📋 View All Categories & Subcategories</strong></summary>

| Category | Subcategories |
|----------|---------------|
| 🏠 **Home** | Rent, Light, Water, Net, Groceries, Me Mimei, Other |
| 🚗 **Car** | Fuel, Insurance, Maintenance, Parking, Via Verde, Other |
| 🎉 **Lazer** | Dining Out, Movies/Shows, Hobbies, Coffees, Other |
| ✈️ **Travel** | Flights, Hotels, Transportation, Food, Activities, Other |
| 📺 **Streaming** | Prime, Netflix, Disney+, Crunchyroll |
| 📱 **Subscriptions** | Patreon, iCloud, Spotify, F1 TV, Telemóvel, Other |
| 🛒 **Needs** | Clothing, Personal Care, Other |
| ⚕️ **Health** | Doctor, Pharmacy, Hospital_Urgency, Gym, Supplements, Other |
| 🎁 **Others** | Gifts, Pet, Mi Mimei, Maomao, Other |
| 💵 **Incomes** | Refeição, Subsídio, Bónus, Salary, Interest, Others |

</details>

---

## 📄 PDF Reports

Generate professional financial reports directly in Telegram:

```
/pdf → Choose period → Receive PDF file
```

**Options:**
- 📅 **This Week** - Current week (Monday to Sunday)
- 📆 **This Month** - Current month
- 📊 **This Year** - Full year report

**Report includes:**
- 💰 Summary (Total Income, Expenses, Balance)
- 📉 Expenses breakdown by category
- 📋 Detailed transaction tables
- 🎨 Color-coded sections (green = income, red = expenses)

---

## 🛠️ Tech Stack

| Technology | Purpose |
|------------|---------|
| ![Python](https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white) | Core language |
| ![Telegram](https://img.shields.io/badge/python--telegram--bot-26A5E4?style=flat-square&logo=telegram&logoColor=white) | Bot framework (v21.7) |
| ![SQLite](https://img.shields.io/badge/SQLite-003B57?style=flat-square&logo=sqlite&logoColor=white) | Database (thread-safe) |
| ![Docker](https://img.shields.io/badge/Docker-2496ED?style=flat-square&logo=docker&logoColor=white) | Containerization |
| ![ReportLab](https://img.shields.io/badge/ReportLab-PDF-red?style=flat-square) | PDF generation |

---

## 📁 Project Structure

```
register-track-bot/
├── 📄 src/bot.py          # Main bot logic (all commands)
├── 📄 run_bot.py          # Entry point
├── 📄 requirements.txt    # Python dependencies
├── 🐳 Dockerfile          # Container definition
├── 🐳 docker-compose.yml  # Orchestration config
├── 📄 .env.example        # Environment template
├── 📄 .gitignore          # Git ignore rules
└── 📄 LICENSE             # MIT License
```

---

## ⚙️ Configuration

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `TELEGRAM_BOT_TOKEN` | ✅ Yes | - | Bot token from [@BotFather](https://t.me/BotFather) |
| `LOG_LEVEL` | ❌ No | `INFO` | Logging level (DEBUG, INFO, WARNING, ERROR) |
| `TZ` | ❌ No | `UTC` | Timezone (e.g., `Europe/Lisbon`) |

### Docker Configuration

The container runs with:
- 🔄 Auto-restart on failure (`unless-stopped`)
- 🏥 Health checks every 60 seconds
- 📊 Resource limits (256MB RAM, 50% CPU)
- 📝 Log rotation (max 30MB)
- 🔒 Non-root user for security

---

## 🚀 Deployment

### Production (Docker)

```bash
# Start
docker compose up -d

# View logs
docker compose logs -f

# Restart
docker compose restart

# Stop
docker compose down

# Rebuild (after code changes)
docker compose up -d --build
```

### Update Workflow

```bash
# Pull latest changes
git pull origin main

# Rebuild and restart
docker compose up -d --build
```

---

## 📊 Usage Example

```
User: /add
Bot:  Select a category: [Home] [Car] [Lazer] ...

User: Home
Bot:  Select a subcategory: [Rent] [Light] [Groceries] ...

User: Groceries
Bot:  Enter the amount (€):

User: 45.50
Bot:  ✅ Expense saved successfully!
      📋 Category: Home
      🏷️ Subcategory: Groceries
      💵 Amount: €45.50
```

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

<p align="center">
  Made with ❤️ for personal finance management
  <br>
  <sub>Built with Python • Telegram Bot API • SQLite • Docker</sub>
</p>

