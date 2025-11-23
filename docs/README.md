# Telegram Expense Tracker Bot

A Python-based Telegram bot that helps you track your daily expenses and incomes. Designed for 24/7 operation on Raspberry Pi with SQLite database storage.

## Features

- 💬 Interactive conversation-based expense logging
- 📊 Multiple expense categories with subcategories (Home, Car, Lazer, Travel, Needs, Health, Streaming, Subscriptions, Others)
- 💰 Separate income tracking (Salary, Refeição, Subsídio, Bónus, Others)
- 🎯 Smart auto-description for recurring expenses (rent, utilities, subscriptions, etc.)
- 📅 European date format (DD/MM/YY) support
- 📈 View expenses for today, specific dates, or entire months
- 📉 Get expense summaries by category
- ✏️ Edit expenses (amount or description) from any date
- 🗑️ Delete expenses from any date
- 💾 SQLite database storage (lightweight, no external server needed)
- 🔄 Perfect for 24/7 operation on Raspberry Pi
- 🚀 Low resource usage (~20-30MB RAM)

## Setup Instructions

### 1. Create Your Telegram Bot

1. Open Telegram and search for `@BotFather`
2. Send `/newbot` command
3. Follow the instructions:
   - Choose a name for your bot (e.g., "My Expense Tracker")
   - Choose a username (must end in 'bot', e.g., "myexpense_tracker_bot")
4. Copy the API token provided by BotFather

### 2. Install Dependencies

```powershell
cd c:\repos\register-track-bot
pip install -r requirements.txt
```

**Or use the virtual environment:**
```powershell
cd c:\repos\register-track-bot
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 3. Set Your Bot Token

Set the token as an environment variable:

**Windows (PowerShell):**
```powershell
$env:TELEGRAM_BOT_TOKEN = "your-token-here"
```

**Or permanently:**
```powershell
setx TELEGRAM_BOT_TOKEN "your-token-here"
```

**Linux/Mac:**
```bash
export TELEGRAM_BOT_TOKEN="your-token-here"
```

### 4. Run the Bot

```powershell
python bot.py
```

**Or if using virtual environment:**
```powershell
C:\repos\register-track-bot\.venv\Scripts\python.exe bot.py
```

## Usage

### Bot Commands

**Today's Expenses:**
- `/start` - Start the bot and see all available commands
- `/add` - Add expense for today
- `/view` - View today's expenses
- `/summary` - Get today's expense summary by category
- `/delete` - Delete an expense from today

**Specific Date Operations:**
- `/add_d` - Add expense for a specific date (DD/MM/YY format)
- `/view_d` - View expenses for a specific date
- `/edit_d` - Edit expense from a specific date
- `/delete_d` - Delete expense from a specific date

**Edit & Manage:**
- `/edit` - Edit an expense from today (amount or description)

**Monthly Overview:**
- `/month <name>` - View all expenses for a month (e.g., `/month november` or `/month 11`)
- `/income <month>` - View all incomes for a month (e.g., `/income november` or `/income 11`)

**Other:**
- `/help` - Show all available commands
- `/cancel` - Cancel the current operation

### Adding an Expense (Today)

1. Send `/add` to the bot
2. Select a main category (Home, Car, Lazer, Travel, etc.)
3. Select a subcategory
4. Enter the amount (numbers only)
5. Provide a description (or skip if auto-description applies)
6. Done! Your expense is saved

### Adding an Expense for a Specific Date

1. Send `/add_d` to the bot
2. Enter date in DD/MM/YY format (e.g., `15/11/25`)
3. Follow the same steps as adding today's expense

### Viewing Monthly Expenses

```
You: /month november
Bot: 📊 Expenses for November 2025:

     📋 By Category:
       • Car > Fuel: €150.00
       • Home > Rent: €800.00
       • Streaming > Netflix: €13.99

     💰 Total: €963.99
     📝 3 expense(s) recorded
```

### Example Conversation

```
You: /add
Bot: Let's add a new expense! 💰
     Please select a category:
     [Home] [Car]
     [Lazer] [Travel]
     [Needs] [Health]
     [Streaming] [Subscriptions]
     [Others]

You: Car
Bot: Category: Car
     Please select a subcategory:
     [Fuel] [Insurance]
     [Maintenance] [Parking]
     [Via Verde] [Other]

You: Fuel
Bot: Subcategory: Fuel
     Now, enter the amount (numbers only):

You: 45.50
Bot: ✅ Expense saved successfully!
     📋 Category: Car
     🏷️ Subcategory: Fuel
     💵 Amount: €45.50
     📝 Description: Car - Fuel
```

### Auto-Description Categories

For these categories/subcategories, the bot automatically fills the description (no need to type it):
- **Home**: Rent, Light, Water, Net
- **Car**: Fuel, Insurance, Via Verde
- **Streaming**: All subcategories (Prime, Netflix, Disney+, HBO)
- **Subscriptions**: All subcategories (Patreon, iCloud, Spotify, F1 TV, Telemóvel)

### Editing an Expense

**Edit from today:**
```
You: /edit
Bot: ✏️ Today's Expenses (2025-11-18):

     1. Car > Fuel: €45.50 - Car - Fuel
     2. Lazer > Coffees: €3.50 - Morning coffee
     
     Reply with the number (1-2) to edit, or /cancel to abort.

You: 2
Bot: ✏️ Editing expense:
     📋 Category: Lazer
     🏷️ Subcategory: Coffees
     💵 Amount: €3.50
     📝 Description: Morning coffee
     
     What would you like to edit?
     Reply with:
     • 'amount' - Change the amount
     • 'description' - Change the description
     • /cancel - Cancel editing

You: amount
Bot: Current amount: €3.50
     Enter the new amount (numbers only):

You: 4.50
Bot: ✅ Expense updated successfully!
     📋 Category: Lazer
     🏷️ Subcategory: Coffees
     💵 Amount: €4.50
     📝 Description: Morning coffee
```

**Edit from a specific date:**
1. Send `/edit_d`
2. Enter date in DD/MM/YY format
3. Select the expense number to edit
4. Choose what to edit (amount or description)
5. Enter the new value

### Deleting an Expense

**Delete from today:**
```
You: /delete
Bot: 🗑️ Today's Expenses (2025-11-18):

     1. Car > Fuel: €45.50 - Car - Fuel
     2. Home > Rent: €800.00 - Home - Rent
     
     Reply with the number (1-2) to delete, or /cancel to abort.

You: 1
Bot: ✅ Deleted expense:
     📋 Category: Car
     🏷️ Subcategory: Fuel
     💵 Amount: €45.50
     📝 Description: Car - Fuel
```

**Delete from a specific date:**
1. Send `/delete_d`
2. Enter date in DD/MM/YY format
3. Select the expense number to delete

## Database Structure

The bot creates a `finance_tracker.db` SQLite database with two tables:

**Expenses Table:**
| id | date       | time     | category | subcategory | amount | description    | created_at          |
|----|------------|----------|----------|-------------|--------|----------------|---------------------|
| 1  | 2025-11-17 | 14:30:15 | Car      | Fuel        | 45.50  | Car - Fuel     | 2025-11-17 14:30:15 |
| 2  | 2025-11-17 | 18:45:22 | Home     | Rent        | 800.00 | Home - Rent    | 2025-11-17 18:45:22 |
| 3  | 2025-11-18 | 10:15:00 | Lazer    | Coffees     | 3.50   | Morning coffee | 2025-11-18 10:15:00 |

**Incomes Table:**
| id | date       | time     | category | subcategory | amount  | description          | created_at          |
|----|------------|----------|----------|-------------|---------|----------------------|---------------------|
| 1  | 2025-11-01 | 09:00:00 | Incomes  | Salary      | 2000.00 | Incomes - Salary     | 2025-11-01 09:00:00 |
| 2  | 2025-11-15 | 12:00:00 | Incomes  | Refeição    | 150.00  | Incomes - Refeição   | 2025-11-15 12:00:00 |

## Tips

- The bot automatically creates the database on first run
- All expenses and incomes are timestamped automatically
- Expenses and incomes are stored in separate tables
- Use SQLite browser to analyze your data (optional)
- Use `/summary` to quickly see where your money is going
- Use `/income <month>` to track your monthly income
- Database is lightweight and grows slowly (~100MB per year)
- The bot supports multiple users - each can add their own expenses

## Troubleshooting

**Bot doesn't respond:**
- Make sure the bot is running (`python bot.py`)
- Check that your token is set correctly
- Verify you have internet connection

**Database errors:**
- Check file permissions for `finance_tracker.db`
- Ensure the bot has write permissions to the directory
- Restart the bot if database is locked

**Installation issues:**
- Update pip: `python -m pip install --upgrade pip`
- Install packages one by one if needed

## Available Categories & Subcategories

- **Home**: Rent, Light, Water, Net, Me Mimei, Other
- **Car**: Fuel, Insurance, Maintenance, Parking, Via Verde, Other
- **Lazer**: Entertainment, Dining Out, Movies/Shows, Hobbies, Coffees, Other
- **Travel**: Flights, Hotels, Transportation, Food, Activities, Other
- **Streaming**: Prime, Netflix, Disney+, HBO
- **Subscriptions**: Patreon, iCloud, Spotify, F1 TV, Telemóvel
- **Needs**: Groceries, Clothing, Personal Care, Setup, Other
- **Health**: Doctor, Pharmacy, Hospital_Urgency, Gym, Supplements, Other
- **Others**: Gifts, Pet, Mi Mimei, Other
- **Incomes**: Refeição, Subsídio, Bónus, Salary, Others

## Customization

You can easily customize the bot by editing `bot.py`:

- **Add/modify categories**: Edit the `CATEGORIES` and `SUBCATEGORIES` dictionaries
- **Change auto-description rules**: Modify the `AUTO_DESCRIPTION` dictionary
- **Change database file name**: Update the `DB_FILE` variable
- **Add new features**: Extend the bot with additional commands
- **Currency symbol**: Change `€` to your preferred currency
- **Backup database**: Use SQLite backup commands or simple file copy

## Database Management

View database contents using SQLite:
```bash
# Install SQLite (if needed)
sudo apt install sqlite3 -y

# Open database
sqlite3 finance_tracker.db

# View expenses
SELECT * FROM expenses ORDER BY date DESC LIMIT 10;

# View incomes
SELECT * FROM incomes ORDER BY date DESC LIMIT 10;

# Get monthly totals
SELECT strftime('%Y-%m', date) as month, SUM(amount) as total 
FROM expenses 
GROUP BY month 
ORDER BY month DESC;
```

**Backup database:**
```bash
# Create backup
cp finance_tracker.db finance_backup_$(date +%Y%m%d).db

# Or use SQLite backup
sqlite3 finance_tracker.db ".backup finance_backup.db"
```

## Future Enhancements

Potential features to add:
- Budget limits with alerts
- Export to CSV/PDF
- Charts and visualizations
- Recurring expense templates
- Year-over-year comparisons
- Web dashboard interface
- Automated backups to cloud storage

Enjoy tracking your expenses! 💰📊

---
