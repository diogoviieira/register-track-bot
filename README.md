# Telegram Expense Tracker Bot

A Python-based Telegram bot that helps you track your daily expenses and automatically saves them to an Excel file.

## Features

- 💬 Interactive conversation-based expense logging
- 📊 Multiple expense categories (Food, Transport, Shopping, Bills, Entertainment, Health, Other)
- 💰 Track amount and description for each expense
- 📅 Automatic date and time stamping
- 📈 View today's expenses
- 📉 Get expense summary by category
- 📑 All data saved to Excel file for easy analysis

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
cd c:\repos\expense_bot
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

## Usage

### Bot Commands

- `/start` - Start the bot and add your first expense
- `/add` - Add a new expense
- `/view` - View all expenses for today
- `/summary` - Get a summary of today's expenses by category
- `/cancel` - Cancel the current operation

### Adding an Expense

1. Send `/add` to the bot
2. Select a category from the keyboard
3. Enter the amount (numbers only)
4. Provide a brief description
5. Done! Your expense is saved

### Example Conversation

```
You: /add
Bot: Let's add a new expense! 💰
     Please select a category:
     [Food] [Transport]
     [Shopping] [Bills]
     [Entertainment] [Health]
     [Other]

You: Food
Bot: Category: Food
     Now, enter the amount (numbers only):

You: 25.50
Bot: Amount: $25.50
     Please provide a brief description:

You: Lunch at restaurant
Bot: ✅ Expense saved successfully!
     📋 Category: Food
     💵 Amount: $25.50
     📝 Description: Lunch at restaurant
```

## Excel File Format

The bot creates an `expenses.xlsx` file with the following columns:

| Date       | Time     | Category | Amount | Description           |
|------------|----------|----------|--------|-----------------------|
| 2025-11-17 | 14:30:15 | Food     | 25.50  | Lunch at restaurant   |
| 2025-11-17 | 18:45:22 | Transport| 15.00  | Taxi to office        |

## Tips

- The bot automatically creates the Excel file on first run
- All expenses are timestamped automatically
- You can open the Excel file anytime to analyze your spending
- Use `/summary` to quickly see where your money is going
- The bot supports multiple users - each can add their own expenses

## Troubleshooting

**Bot doesn't respond:**
- Make sure the bot is running (`python bot.py`)
- Check that your token is set correctly
- Verify you have internet connection

**Excel file errors:**
- Make sure the `expenses.xlsx` file isn't open in Excel while the bot is running
- Check file permissions in the directory

**Installation issues:**
- Update pip: `python -m pip install --upgrade pip`
- Install packages one by one if needed

## Customization

You can easily customize the bot by editing `bot.py`:

- **Add more categories**: Modify the `CATEGORIES` list
- **Change Excel file name**: Update the `EXCEL_FILE` variable
- **Add new features**: Extend the bot with additional commands
- **Modify date format**: Change the `strftime` format strings

## Future Enhancements

Ideas for extending the bot:
- Monthly expense reports
- Budget limits with alerts
- Export to different file formats
- Multi-user support with separate files
- Expense editing and deletion
- Charts and visualizations
- Recurring expense tracking

Enjoy tracking your expenses! 💰📊
