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
CATEGORY, SUBCATEGORY, AMOUNT, DESCRIPTION, DATE_INPUT, EDIT_FIELD = range(6)

# Excel file path
EXCEL_FILE = "expenses.xlsx"

# Main categories
CATEGORIES = [
    ["Home", "Car"],
    ["Lazer", "Travel"],
    ["Needs", "Health"],
    ["Streaming", "Subscriptions"],
    ["Others"]
]

# Subcategories for each main category
SUBCATEGORIES = {
    "Home": [
        ["Rent", "Light"],
        ["Water", "Net"],
        ["Me Mimei", "Other"]
    ],
    "Car": [
        ["Fuel", "Insurance"],
        ["Maintenance", "Parking"],
        ["Via Verde", "Other"]
    ],
    "Lazer": [
        ["Entertainment", "Dining Out"],
        ["Movies/Shows", "Hobbies"],
        ["Coffees", "Other"]
    ],
    "Travel": [
        ["Flights", "Hotels"],
        ["Transportation", "Food"],
        ["Activities", "Other"]
    ],
    "Streaming": [
        ["Prime", "Netflix"],
        ["Disney+", "HBO"]
    ],
    "Subscriptions": [
        ["Patreon", "iCloud"],
        ["Spotify", "F1 TV"],
        ["Telemóvel"]
    ],
    "Needs": [
        ["Groceries", "Clothing"],
        ["Personal Care", "Setup"],
        ["Other"]
    ],
    "Health": [
        ["Doctor", "Pharmacy"],
        ["Hospital", "Gym"],
        ["Supplements", "Other"]
    ],
    "Others": [
        ["Gifts", "Pet"],
        ["Mi Mimei", "Other"]
    ]
}

# Categories/subcategories that don't need description input
# Description will be auto-filled as "Category - Subcategory"
AUTO_DESCRIPTION = {
    "Home": ["Rent", "Light", "Water", "Net"],
    "Car": ["Fuel", "Insurance", "Via Verde"],
    "Streaming": "all",  # All subcategories in Streaming
    "Subscriptions": "all"  # All subcategories in Subscriptions
}


def should_skip_description(category: str, subcategory: str) -> bool:
    """Check if description should be auto-filled for this category/subcategory"""
    if category not in AUTO_DESCRIPTION:
        return False
    
    auto_subs = AUTO_DESCRIPTION[category]
    if auto_subs == "all":
        return True
    
    return subcategory in auto_subs


def init_excel():
    """Initialize Excel file if it doesn't exist"""
    if not os.path.exists(EXCEL_FILE):
        wb = Workbook()
        ws = wb.active
        ws.title = "Expenses"
        ws.append(["Date", "Time", "Category", "Subcategory", "Amount", "Description"])
        wb.save(EXCEL_FILE)
        logger.info(f"Created new Excel file: {EXCEL_FILE}")


def save_expense(category: str, subcategory: str, amount: float, description: str, custom_date: str = None):
    """Save expense to Excel file with optional custom date"""
    try:
        wb = openpyxl.load_workbook(EXCEL_FILE)
        ws = wb.active
        
        if custom_date:
            date_str = custom_date
        else:
            date_str = datetime.now().strftime("%Y-%m-%d")
        
        time_str = datetime.now().strftime("%H:%M:%S")
        
        ws.append([date_str, time_str, category, subcategory, amount, description])
        wb.save(EXCEL_FILE)
        logger.info(f"Saved expense: {category} > {subcategory} - €{amount} on {date_str}")
        return True
    except Exception as e:
        logger.error(f"Error saving expense: {e}")
        return False


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Start the conversation and ask for expense category"""
    await update.message.reply_text(
        "Hi! I'm your Daddy, i will register your money moves. 📊\n\n"
        "I'll help you not wasting all your money on Putas e Vinho verde.\n\n"
        "Commands:\n"
        "/add - Add expense for today\n"
        "/add_d - Add expense for a specific date\n"
        "/view - View today's expenses\n"
        "/view_d - View expenses for a specific date\n"
        "/month - View expenses for a specific month\n"
        "/summary - Get today's summary\n"
        "/edit - Edit an expense from today\n"
        "/edit_d - Edit an expense from a specific date\n"
        "/delete - Delete today's expense\n"
        "/delete_d - Delete expense from a specific date\n"
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
    """Store category and ask for subcategory"""
    selected_category = update.message.text
    context.user_data["category"] = selected_category
    
    # Get subcategories for the selected category
    if selected_category in SUBCATEGORIES:
        subcats = SUBCATEGORIES[selected_category]
        await update.message.reply_text(
            f"Category: {selected_category}\n\n"
            "Please select a subcategory:",
            reply_markup=ReplyKeyboardMarkup(subcats, one_time_keyboard=True),
        )
        return SUBCATEGORY
    else:
        # If no subcategories defined, skip to amount
        await update.message.reply_text(
            f"Category: {selected_category}\n\n"
            "Now, enter the amount (numbers only):",
            reply_markup=ReplyKeyboardRemove(),
        )
        return AMOUNT


async def subcategory(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Store subcategory and ask for amount"""
    selected_subcategory = update.message.text
    context.user_data["subcategory"] = selected_subcategory
    
    # Check if this category/subcategory should skip description
    category = context.user_data["category"]
    if should_skip_description(category, selected_subcategory):
        context.user_data["skip_description"] = True
    
    await update.message.reply_text(
        f"Subcategory: {selected_subcategory}\n\n"
        "Now, enter the amount (numbers only):",
        reply_markup=ReplyKeyboardRemove(),
    )
    return AMOUNT


async def amount(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Store amount and ask for description (or auto-save if description not needed)"""
    try:
        amount_value = float(update.message.text)
        context.user_data["amount"] = amount_value
        
        # Check if we should skip description
        if context.user_data.get("skip_description", False):
            # Auto-fill description and save directly
            category = context.user_data["category"]
            subcategory = context.user_data.get("subcategory", "N/A")
            description = f"{category} - {subcategory}"
            target_date = context.user_data.get("target_date")
            
            if save_expense(category, subcategory, amount_value, description, target_date):
                date_msg = f" for {target_date}" if target_date else ""
                await update.message.reply_text(
                    f"✅ Expense saved successfully{date_msg}!\n\n"
                    f"📋 Category: {category}\n"
                    f"🏷️ Subcategory: {subcategory}\n"
                    f"💵 Amount: €{amount_value:.2f}\n"
                    f"📝 Description: {description}\n\n"
                    "Use /add to add another expense or /view to see today's expenses."
                )
            else:
                await update.message.reply_text(
                    "❌ Sorry, there was an error saving your expense. Please try again."
                )
            
            context.user_data.clear()
            return ConversationHandler.END
        else:
            # Ask for description as usual
            await update.message.reply_text(
                f"Amount: €{amount_value:.2f}\n\n"
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
    subcategory = context.user_data.get("subcategory", "N/A")
    amount = context.user_data["amount"]
    description = update.message.text
    target_date = context.user_data.get("target_date")
    
    if save_expense(category, subcategory, amount, description, target_date):
        date_msg = f" for {target_date}" if target_date else ""
        await update.message.reply_text(
            f"✅ Expense saved successfully{date_msg}!\n\n"
            f"📋 Category: {category}\n"
            f"🏷️ Subcategory: {subcategory}\n"
            f"💵 Amount: €{amount:.2f}\n"
            f"📝 Description: {description}\n\n"
            "Use /add to add another expense or /view to see today's expenses."
        )
    else:
        await update.message.reply_text(
            "❌ Sorry, there was an error saving your expense. Please try again."
        )
    
    context.user_data.clear()
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
                total += float(row[4])  # Amount is now in column 4
        
        if expenses:
            message = f"📊 Today's Expenses ({today}):\n\n"
            for exp in expenses:
                message += f"• {exp[2]} > {exp[3]}: €{exp[4]:.2f} - {exp[5]}\n"
            message += f"\n💰 Total: €{total:.2f}"
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
                subcategory = row[3]
                amount = float(row[4])
                key = f"{category} > {subcategory}"
                category_totals[key] = category_totals.get(key, 0) + amount
        
        if category_totals:
            message = f"📈 Today's Summary ({today}):\n\n"
            for cat, total in sorted(category_totals.items()):
                message += f"• {cat}: €{total:.2f}\n"
            message += f"\n💰 Grand Total: €{sum(category_totals.values()):.2f}"
        else:
            message = "No expenses recorded for today."
        
        await update.message.reply_text(message)
    except Exception as e:
        logger.error(f"Error getting summary: {e}")
        await update.message.reply_text("Error retrieving summary.")


async def view_month_expenses(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """View expenses for a specific month"""
    try:
        # Parse the command to get month name or number
        message_text = update.message.text.lower()
        
        # Month mapping (English and Portuguese)
        months = {
            'january': '01', 'janeiro': '01', '1': '01',
            'february': '02', 'fevereiro': '02', '2': '02',
            'march': '03', 'março': '03', 'marco': '03', '3': '03',
            'april': '04', 'abril': '04', '4': '04',
            'may': '05', 'maio': '05', '5': '05',
            'june': '06', 'junho': '06', '6': '06',
            'july': '07', 'julho': '07', '7': '07',
            'august': '08', 'agosto': '08', '8': '08',
            'september': '09', 'setembro': '09', '9': '09',
            'october': '10', 'outubro': '10', '10': '10',
            'november': '11', 'novembro': '11', '11': '11',
            'december': '12', 'dezembro': '12', '12': '12'
        }
        
        # Extract month from command (e.g., "/month november" or "/month 11")
        parts = message_text.split()
        if len(parts) < 2:
            await update.message.reply_text(
                "📅 Please specify a month.\n\n"
                "Examples:\n"
                "/month november\n"
                "/month 11\n"
                "/month novembro"
            )
            return
        
        month_input = parts[1]
        month_num = months.get(month_input)
        
        if not month_num:
            await update.message.reply_text(
                "❌ Invalid month. Please use month name or number (1-12).\n\n"
                "Examples: /month november or /month 11"
            )
            return
        
        # Get current year
        current_year = datetime.now().year
        
        # Load expenses
        wb = openpyxl.load_workbook(EXCEL_FILE)
        ws = wb.active
        
        expenses = []
        total = 0.0
        category_totals = {}
        
        for row in ws.iter_rows(min_row=2, values_only=True):
            if row[0] and row[0].startswith(f"{current_year}-{month_num}"):
                expenses.append(row)
                total += float(row[4])
                
                # Track category totals
                key = f"{row[2]} > {row[3]}"
                category_totals[key] = category_totals.get(key, 0) + float(row[4])
        
        if expenses:
            # Month names for display
            month_names = {
                '01': 'January', '02': 'February', '03': 'March',
                '04': 'April', '05': 'May', '06': 'June',
                '07': 'July', '08': 'August', '09': 'September',
                '10': 'October', '11': 'November', '12': 'December'
            }
            
            message = f"📊 Expenses for {month_names[month_num]} {current_year}:\n\n"
            message += f"📋 By Category:\n"
            for cat, cat_total in sorted(category_totals.items()):
                message += f"  • {cat}: €{cat_total:.2f}\n"
            
            message += f"\n💰 Total: €{total:.2f}\n"
            message += f"📝 {len(expenses)} expense(s) recorded"
        else:
            await update.message.reply_text(f"No expenses recorded for {month_input.capitalize()} {current_year}.")
            return
        
        await update.message.reply_text(message)
        
    except Exception as e:
        logger.error(f"Error viewing month expenses: {e}")
        await update.message.reply_text("Error retrieving monthly expenses.")


async def delete_expense(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show today's expenses and allow user to delete one"""
    try:
        wb = openpyxl.load_workbook(EXCEL_FILE)
        ws = wb.active
        
        today = datetime.now().strftime("%Y-%m-%d")
        today_expenses = []
        
        # Collect today's expenses with their row numbers
        for idx, row in enumerate(ws.iter_rows(min_row=2, values_only=False), start=2):
            if row[0].value == today:
                today_expenses.append((idx, row))
        
        if not today_expenses:
            await update.message.reply_text("No expenses to delete for today.")
            return
        
        # Display expenses with numbers
        message = f"🗑️ Today's Expenses ({today}):\n\n"
        for i, (row_idx, row) in enumerate(today_expenses, start=1):
            message += f"{i}. {row[2].value} > {row[3].value}: €{row[4].value:.2f} - {row[5].value}\n"
        message += f"\nReply with the number (1-{len(today_expenses)}) to delete, or /cancel to abort."
        
        context.user_data["delete_expenses"] = today_expenses
        await update.message.reply_text(message)
        
    except Exception as e:
        logger.error(f"Error in delete_expense: {e}")
        await update.message.reply_text("Error retrieving expenses for deletion.")


async def handle_delete_number(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the deletion of an expense by number"""
    try:
        choice = int(update.message.text)
        expenses = context.user_data.get("delete_expenses", [])
        
        if not expenses or choice < 1 or choice > len(expenses):
            await update.message.reply_text(
                f"Invalid choice. Please enter a number between 1 and {len(expenses)}, or /cancel."
            )
            return
        
        # Get the row to delete
        row_idx, row = expenses[choice - 1]
        
        # Load workbook and delete the row
        wb = openpyxl.load_workbook(EXCEL_FILE)
        ws = wb.active
        ws.delete_rows(row_idx)
        wb.save(EXCEL_FILE)
        
        # Show confirmation
        await update.message.reply_text(
            f"✅ Deleted expense:\n\n"
            f"📋 Category: {row[2].value}\n"
            f"🏷️ Subcategory: {row[3].value}\n"
            f"💵 Amount: €{row[4].value:.2f}\n"
            f"📝 Description: {row[5].value}\n\n"
            "Expense has been removed."
        )
        
        # Clear the delete context
        context.user_data.pop("delete_expenses", None)
        
    except ValueError:
        await update.message.reply_text(
            "Please enter a valid number, or /cancel to abort."
        )
    except Exception as e:
        logger.error(f"Error deleting expense: {e}")
        await update.message.reply_text("Error deleting expense. Please try again.")


# Edit expense functions

async def edit_expense(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show today's expenses and allow user to edit one"""
    try:
        wb = openpyxl.load_workbook(EXCEL_FILE)
        ws = wb.active
        
        today = datetime.now().strftime("%Y-%m-%d")
        today_expenses = []
        
        for idx, row in enumerate(ws.iter_rows(min_row=2, values_only=False), start=2):
            if row[0].value == today:
                today_expenses.append((idx, row))
        
        if not today_expenses:
            await update.message.reply_text("No expenses to edit for today.")
            return
        
        message = f"✏️ Today's Expenses ({today}):\n\n"
        for i, (row_idx, row) in enumerate(today_expenses, start=1):
            message += f"{i}. {row[2].value} > {row[3].value}: €{row[4].value:.2f} - {row[5].value}\n"
        message += f"\nReply with the number (1-{len(today_expenses)}) to edit, or /cancel to abort."
        
        context.user_data["edit_expenses"] = today_expenses
        await update.message.reply_text(message)
        
    except Exception as e:
        logger.error(f"Error in edit_expense: {e}")
        await update.message.reply_text("Error retrieving expenses for editing.")


async def edit_expense_date(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Edit expense for a specific date"""
    await update.message.reply_text(
        "📅 Enter the date to edit an expense (format: DD/MM/YY)\n\n"
        "Example: 15/11/25\n"
        "Or type /cancel to abort."
    )
    context.user_data["editing_for_date"] = True
    return DATE_INPUT


async def show_edit_for_date(update: Update, context: ContextTypes.DEFAULT_TYPE, target_date: str):
    """Show expenses for a specific date and allow editing"""
    try:
        wb = openpyxl.load_workbook(EXCEL_FILE)
        ws = wb.active
        
        date_expenses = []
        
        for idx, row in enumerate(ws.iter_rows(min_row=2, values_only=False), start=2):
            if row[0].value == target_date:
                date_expenses.append((idx, row))
        
        if not date_expenses:
            await update.message.reply_text(f"No expenses to edit for {target_date}.")
            return
        
        message = f"✏️ Expenses for {target_date}:\n\n"
        for i, (row_idx, row) in enumerate(date_expenses, start=1):
            message += f"{i}. {row[2].value} > {row[3].value}: €{row[4].value:.2f} - {row[5].value}\n"
        message += f"\nReply with the number (1-{len(date_expenses)}) to edit, or /cancel to abort."
        
        context.user_data["edit_expenses"] = date_expenses
        await update.message.reply_text(message)
        
    except Exception as e:
        logger.error(f"Error in show_edit_for_date: {e}")
        await update.message.reply_text("Error retrieving expenses for editing.")


async def handle_edit_number(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the selection of an expense to edit"""
    try:
        choice = int(update.message.text)
        expenses = context.user_data.get("edit_expenses", [])
        
        if not expenses or choice < 1 or choice > len(expenses):
            await update.message.reply_text(
                f"Invalid choice. Please enter a number between 1 and {len(expenses)}, or /cancel."
            )
            return
        
        # Store the selected expense for editing
        row_idx, row = expenses[choice - 1]
        context.user_data["edit_row_idx"] = row_idx
        context.user_data["edit_expense_data"] = {
            "category": row[2].value,
            "subcategory": row[3].value,
            "amount": row[4].value,
            "description": row[5].value
        }
        context.user_data.pop("edit_expenses", None)
        
        # Show what can be edited
        await update.message.reply_text(
            f"✏️ Editing expense:\n\n"
            f"📋 Category: {row[2].value}\n"
            f"🏷️ Subcategory: {row[3].value}\n"
            f"💵 Amount: €{row[4].value:.2f}\n"
            f"📝 Description: {row[5].value}\n\n"
            "What would you like to edit?\n"
            "Reply with:\n"
            "• 'amount' - Change the amount\n"
            "• 'description' - Change the description\n"
            "• /cancel - Cancel editing"
        )
        
    except ValueError:
        await update.message.reply_text(
            "Please enter a valid number, or /cancel to abort."
        )
    except Exception as e:
        logger.error(f"Error selecting expense for edit: {e}")
        await update.message.reply_text("Error selecting expense. Please try again.")


async def handle_edit_field_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the choice of what field to edit"""
    choice = update.message.text.lower().strip()
    
    if choice == "amount":
        context.user_data["editing_field"] = "amount"
        current_amount = context.user_data["edit_expense_data"]["amount"]
        await update.message.reply_text(
            f"Current amount: €{current_amount:.2f}\n\n"
            "Enter the new amount (numbers only):"
        )
    elif choice == "description":
        context.user_data["editing_field"] = "description"
        current_desc = context.user_data["edit_expense_data"]["description"]
        await update.message.reply_text(
            f"Current description: {current_desc}\n\n"
            "Enter the new description:"
        )
    else:
        await update.message.reply_text(
            "Please reply with 'amount' or 'description', or /cancel to abort."
        )


async def handle_edit_value(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the new value for the edited field"""
    try:
        field = context.user_data.get("editing_field")
        new_value = update.message.text
        
        if field == "amount":
            new_value = float(new_value)
        
        # Load workbook and update the expense
        wb = openpyxl.load_workbook(EXCEL_FILE)
        ws = wb.active
        row_idx = context.user_data["edit_row_idx"]
        
        if field == "amount":
            ws.cell(row=row_idx, column=5).value = new_value  # Column 5 is Amount
            context.user_data["edit_expense_data"]["amount"] = new_value
        elif field == "description":
            ws.cell(row=row_idx, column=6).value = new_value  # Column 6 is Description
            context.user_data["edit_expense_data"]["description"] = new_value
        
        wb.save(EXCEL_FILE)
        
        # Show confirmation
        data = context.user_data["edit_expense_data"]
        await update.message.reply_text(
            f"✅ Expense updated successfully!\n\n"
            f"📋 Category: {data['category']}\n"
            f"🏷️ Subcategory: {data['subcategory']}\n"
            f"💵 Amount: €{data['amount']:.2f}\n"
            f"📝 Description: {data['description']}"
        )
        
        # Clear edit context
        context.user_data.pop("edit_row_idx", None)
        context.user_data.pop("edit_expense_data", None)
        context.user_data.pop("editing_field", None)
        
    except ValueError:
        await update.message.reply_text(
            "Please enter a valid number for the amount, or /cancel to abort."
        )
    except Exception as e:
        logger.error(f"Error updating expense: {e}")
        await update.message.reply_text("Error updating expense. Please try again.")


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancel the conversation"""
    await update.message.reply_text(
        "Operation cancelled. Use /add to add a new expense.",
        reply_markup=ReplyKeyboardRemove(),
    )
    context.user_data.clear()
    return ConversationHandler.END


# Date-specific functions

async def add_expense_date(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Start adding an expense for a specific date"""
    await update.message.reply_text(
        "📅 Enter the date for the expense (format: DD/MM/YY)\n\n"
        "Example: 15/11/25\n"
        "Or type /cancel to abort."
    )
    context.user_data["adding_for_date"] = True
    return DATE_INPUT


async def view_expenses_date(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """View expenses for a specific date"""
    await update.message.reply_text(
        "📅 Enter the date to view expenses (format: DD/MM/YY)\n\n"
        "Example: 15/11/25\n"
        "Or type /cancel to abort."
    )
    context.user_data["viewing_date"] = True
    return DATE_INPUT


async def delete_expense_date(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Delete expense for a specific date"""
    await update.message.reply_text(
        "📅 Enter the date to delete an expense (format: DD/MM/YY)\n\n"
        "Example: 15/11/25\n"
        "Or type /cancel to abort."
    )
    context.user_data["deleting_for_date"] = True
    return DATE_INPUT


async def handle_date_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle date input and route to appropriate action"""
    date_text = update.message.text.strip()
    
    # Validate date format (DD/MM/YY)
    try:
        parsed_date = datetime.strptime(date_text, "%d/%m/%y")
        date_str = parsed_date.strftime("%Y-%m-%d")  # Store internally as YYYY-MM-DD
    except ValueError:
        await update.message.reply_text(
            "❌ Invalid date format. Please use DD/MM/YY format.\n"
            "Example: 15/11/25\n\n"
            "Or type /cancel to abort."
        )
        return DATE_INPUT
    
    # Store the date
    context.user_data["target_date"] = date_str
    
    # Route based on what action was requested
    if context.user_data.get("adding_for_date"):
        context.user_data.pop("adding_for_date")
        await update.message.reply_text(
            f"📅 Adding expense for {date_str}\n\n"
            "Please select a category:",
            reply_markup=ReplyKeyboardMarkup(CATEGORIES, one_time_keyboard=True),
        )
        return CATEGORY
    
    elif context.user_data.get("viewing_date"):
        context.user_data.pop("viewing_date")
        await view_expenses_for_date(update, context, date_str)
        return ConversationHandler.END
    
    elif context.user_data.get("deleting_for_date"):
        context.user_data.pop("deleting_for_date")
        await show_delete_for_date(update, context, date_str)
        return ConversationHandler.END
    
    elif context.user_data.get("editing_for_date"):
        context.user_data.pop("editing_for_date")
        await show_edit_for_date(update, context, date_str)
        return ConversationHandler.END
    
    return ConversationHandler.END


async def view_expenses_for_date(update: Update, context: ContextTypes.DEFAULT_TYPE, target_date: str):
    """View expenses for a specific date"""
    try:
        wb = openpyxl.load_workbook(EXCEL_FILE)
        ws = wb.active
        
        expenses = []
        total = 0.0
        
        for row in ws.iter_rows(min_row=2, values_only=True):
            if row[0] == target_date:
                expenses.append(row)
                total += float(row[4])
        
        if expenses:
            message = f"📊 Expenses for {target_date}:\n\n"
            for exp in expenses:
                message += f"• {exp[2]} > {exp[3]}: €{exp[4]:.2f} - {exp[5]}\n"
            message += f"\n💰 Total: €{total:.2f}"
        else:
            message = f"No expenses recorded for {target_date}."
        
        await update.message.reply_text(message)
    except Exception as e:
        logger.error(f"Error viewing expenses for date: {e}")
        await update.message.reply_text("Error retrieving expenses.")


async def show_delete_for_date(update: Update, context: ContextTypes.DEFAULT_TYPE, target_date: str):
    """Show expenses for a specific date and allow deletion"""
    try:
        wb = openpyxl.load_workbook(EXCEL_FILE)
        ws = wb.active
        
        date_expenses = []
        
        for idx, row in enumerate(ws.iter_rows(min_row=2, values_only=False), start=2):
            if row[0].value == target_date:
                date_expenses.append((idx, row))
        
        if not date_expenses:
            await update.message.reply_text(f"No expenses to delete for {target_date}.")
            return
        
        message = f"🗑️ Expenses for {target_date}:\n\n"
        for i, (row_idx, row) in enumerate(date_expenses, start=1):
            message += f"{i}. {row[2].value} > {row[3].value}: €{row[4].value:.2f} - {row[5].value}\n"
        message += f"\nReply with the number (1-{len(date_expenses)}) to delete, or /cancel to abort."
        
        context.user_data["delete_expenses"] = date_expenses
        await update.message.reply_text(message)
        
    except Exception as e:
        logger.error(f"Error in show_delete_for_date: {e}")
        await update.message.reply_text("Error retrieving expenses for deletion.")


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
    
    # Add conversation handler for adding expenses (today or specific date)
    conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler("start", start),
            CommandHandler("add", add_expense),
            CommandHandler("add_d", add_expense_date),
        ],
        states={
            DATE_INPUT: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_date_input)],
            CATEGORY: [MessageHandler(filters.TEXT & ~filters.COMMAND, category)],
            SUBCATEGORY: [MessageHandler(filters.TEXT & ~filters.COMMAND, subcategory)],
            AMOUNT: [MessageHandler(filters.TEXT & ~filters.COMMAND, amount)],
            DESCRIPTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, description)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
    
    # Conversation handler for viewing specific date
    view_date_handler = ConversationHandler(
        entry_points=[CommandHandler("view_d", view_expenses_date)],
        states={
            DATE_INPUT: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_date_input)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
    
    # Conversation handler for deleting from specific date
    delete_date_handler = ConversationHandler(
        entry_points=[CommandHandler("delete_d", delete_expense_date)],
        states={
            DATE_INPUT: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_date_input)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
    
    # Conversation handler for editing from specific date
    edit_date_handler = ConversationHandler(
        entry_points=[CommandHandler("edit_d", edit_expense_date)],
        states={
            DATE_INPUT: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_date_input)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
    
    application.add_handler(conv_handler)
    application.add_handler(view_date_handler)
    application.add_handler(delete_date_handler)
    application.add_handler(edit_date_handler)
    application.add_handler(CommandHandler("view", view_expenses))
    application.add_handler(CommandHandler("month", view_month_expenses))
    application.add_handler(CommandHandler("summary", summary))
    application.add_handler(CommandHandler("edit", edit_expense))
    application.add_handler(CommandHandler("delete", delete_expense))
    
    # Combined handler for all non-conversation text input
    async def handle_text_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
        text = update.message.text.strip()
        
        # Priority 1: Editing field value
        if context.user_data.get("editing_field"):
            await handle_edit_value(update, context)
            return
        
        # Priority 2: Selecting what field to edit
        if context.user_data.get("edit_expense_data") and text.lower() in ["amount", "description"]:
            await handle_edit_field_choice(update, context)
            return
        
        # Priority 3: Selecting expense number to edit
        if context.user_data.get("edit_expenses") and text.isdigit():
            await handle_edit_number(update, context)
            return
        
        # Priority 4: Selecting expense number to delete
        if context.user_data.get("delete_expenses") and text.isdigit():
            await handle_delete_number(update, context)
            return
    
    application.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        handle_text_input
    ))
    
    # Start the bot
    print("Bot is running... Press Ctrl+C to stop.")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
