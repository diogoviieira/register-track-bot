import logging
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    filters,
    ContextTypes,
)
from datetime import datetime
import openpyxl
from openpyxl import Workbook
import os

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Conversation states
CATEGORY, AMOUNT, DESCRIPTION = range(3)

# Excel file path
EXCEL_FILE = "expenses.xlsx"

# Expense categories
CATEGORIES = [
    ["Food", "Transport"],
    ["Shopping", "Bills"],
    ["Entertainment", "Health"],
    ["Other"]
]


def init_excel():
    """Initialize Excel file if it doesn't exist"""
    if not os.path.exists(EXCEL_FILE):
        wb = Workbook()
        ws = wb.active
        ws.title = "Expenses"
        ws.append(["Date", "Time", "Category", "Amount", "Description"])
        wb.save(EXCEL_FILE)
        logger.info(f"Created new Excel file: {EXCEL_FILE}")


def save_expense(category: str, amount: float, description: str):
    """Save expense to Excel file"""
    try:
        wb = openpyxl.load_workbook(EXCEL_FILE)
        ws = wb.active
        
        now = datetime.now()
        date_str = now.strftime("%Y-%m-%d")
        time_str = now.strftime("%H:%M:%S")
        
        ws.append([date_str, time_str, category, amount, description])
        wb.save(EXCEL_FILE)
        logger.info(f"Saved expense: {category} - ${amount}")
        return True
    except Exception as e:
        logger.error(f"Error saving expense: {e}")
        return False


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Start the conversation and ask for expense category"""
    await update.message.reply_text(
        "Hi! I'm your Expense Tracker Bot. 📊\n\n"
        "I'll help you track your daily expenses.\n\n"
        "Commands:\n"
        "/add - Add a new expense\n"
        "/view - View today's expenses\n"
        "/summary - Get expense summary\n"
        "/cancel - Cancel current operation\n\n"
        "Let's add an expense! Please select a category:",
        reply_markup=ReplyKeyboardMarkup(CATEGORIES, one_time_keyboard=True),
    )
    return CATEGORY


async def add_expense(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Start adding a new expense"""
    await update.message.reply_text(
        "Let's add a new expense! 💰\n\n"
        "Please select a category:",
        reply_markup=ReplyKeyboardMarkup(CATEGORIES, one_time_keyboard=True),
    )
    return CATEGORY


async def category(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Store category and ask for amount"""
    context.user_data["category"] = update.message.text
    await update.message.reply_text(
        f"Category: {update.message.text}\n\n"
        "Now, enter the amount (numbers only):",
        reply_markup=ReplyKeyboardRemove(),
    )
    return AMOUNT


async def amount(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Store amount and ask for description"""
    try:
        amount_value = float(update.message.text)
        context.user_data["amount"] = amount_value
        await update.message.reply_text(
            f"Amount: ${amount_value:.2f}\n\n"
            "Please provide a brief description:"
        )
        return DESCRIPTION
    except ValueError:
        await update.message.reply_text(
            "Please enter a valid number for the amount:"
        )
        return AMOUNT


async def description(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Store description and save the expense"""
    context.user_data["description"] = update.message.text
    
    category = context.user_data["category"]
    amount = context.user_data["amount"]
    description = update.message.text
    
    if save_expense(category, amount, description):
        await update.message.reply_text(
            "✅ Expense saved successfully!\n\n"
            f"📋 Category: {category}\n"
            f"💵 Amount: ${amount:.2f}\n"
            f"📝 Description: {description}\n\n"
            "Use /add to add another expense or /view to see today's expenses."
        )
    else:
        await update.message.reply_text(
            "❌ Sorry, there was an error saving your expense. Please try again."
        )
    
    return ConversationHandler.END


async def view_expenses(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """View today's expenses"""
    try:
        wb = openpyxl.load_workbook(EXCEL_FILE)
        ws = wb.active
        
        today = datetime.now().strftime("%Y-%m-%d")
        expenses = []
        total = 0.0
        
        for row in ws.iter_rows(min_row=2, values_only=True):
            if row[0] == today:
                expenses.append(row)
                total += float(row[3])
        
        if expenses:
            message = f"📊 Today's Expenses ({today}):\n\n"
            for exp in expenses:
                message += f"• {exp[2]}: ${exp[3]:.2f} - {exp[4]}\n"
            message += f"\n💰 Total: ${total:.2f}"
        else:
            message = "No expenses recorded for today."
        
        await update.message.reply_text(message)
    except Exception as e:
        logger.error(f"Error viewing expenses: {e}")
        await update.message.reply_text("Error retrieving expenses.")


async def summary(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Get expense summary by category"""
    try:
        wb = openpyxl.load_workbook(EXCEL_FILE)
        ws = wb.active
        
        today = datetime.now().strftime("%Y-%m-%d")
        category_totals = {}
        
        for row in ws.iter_rows(min_row=2, values_only=True):
            if row[0] == today:
                category = row[2]
                amount = float(row[3])
                category_totals[category] = category_totals.get(category, 0) + amount
        
        if category_totals:
            message = f"📈 Today's Summary ({today}):\n\n"
            for cat, total in sorted(category_totals.items()):
                message += f"• {cat}: ${total:.2f}\n"
            message += f"\n💰 Grand Total: ${sum(category_totals.values()):.2f}"
        else:
            message = "No expenses recorded for today."
        
        await update.message.reply_text(message)
    except Exception as e:
        logger.error(f"Error getting summary: {e}")
        await update.message.reply_text("Error retrieving summary.")


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancel the conversation"""
    await update.message.reply_text(
        "Operation cancelled. Use /add to add a new expense.",
        reply_markup=ReplyKeyboardRemove(),
    )
    return ConversationHandler.END


def main():
    """Start the bot"""
    # Initialize Excel file
    init_excel()
    
    # Read bot token from environment variable or config
    BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    
    if not BOT_TOKEN:
        print("ERROR: Please set TELEGRAM_BOT_TOKEN environment variable")
        print("\nSteps to get your bot token:")
        print("1. Open Telegram and search for @BotFather")
        print("2. Send /newbot command")
        print("3. Follow the instructions to create your bot")
        print("4. Copy the token and set it as environment variable:")
        print("   Windows: setx TELEGRAM_BOT_TOKEN \"your-token-here\"")
        print("   Linux/Mac: export TELEGRAM_BOT_TOKEN=\"your-token-here\"")
        return
    
    # Create application
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Add conversation handler for adding expenses
    conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler("start", start),
            CommandHandler("add", add_expense),
        ],
        states={
            CATEGORY: [MessageHandler(filters.TEXT & ~filters.COMMAND, category)],
            AMOUNT: [MessageHandler(filters.TEXT & ~filters.COMMAND, amount)],
            DESCRIPTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, description)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
    
    application.add_handler(conv_handler)
    application.add_handler(CommandHandler("view", view_expenses))
    application.add_handler(CommandHandler("summary", summary))
    
    # Start the bot
    print("Bot is running... Press Ctrl+C to stop.")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
