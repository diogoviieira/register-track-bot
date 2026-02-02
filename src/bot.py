import logging
import sys
import signal
import re
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    filters,
    ContextTypes,
)
from datetime import datetime, timedelta
import os
import math
import sqlite3
import io
from contextlib import contextmanager
import threading
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer

# Configure logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=getattr(logging, LOG_LEVEL, logging.INFO),
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Reduce telegram library verbosity
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("telegram").setLevel(logging.WARNING)

# Conversation states
CATEGORY, SUBCATEGORY, AMOUNT, DESCRIPTION, DATE_INPUT, EDIT_FIELD, PDF_PERIOD, PDF_MONTH, PDF_YEAR, SUMMARY_PERIOD, SUMMARY_MONTH, SUMMARY_YEAR, SUMMARY_DAY = range(13)

# Database file path
DB_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "finance_tracker.db")

# Thread-local storage for database connections
thread_local = threading.local()

# Database column names
class DBColumns:
    ID = "id"
    DATE = "date"
    TIME = "time"
    CATEGORY = "category"
    SUBCATEGORY = "subcategory"
    AMOUNT = "amount"
    DESCRIPTION = "description"

# Month mappings (English, Portuguese, and numbers)
MONTH_MAPPINGS = {
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

MONTH_NAMES = {
    '01': 'January', '02': 'February', '03': 'March',
    '04': 'April', '05': 'May', '06': 'June',
    '07': 'July', '08': 'August', '09': 'September',
    '10': 'October', '11': 'November', '12': 'December'
}

# Validation constants
MAX_AMOUNT = 999999

# Common prompts
DATE_FORMAT_PROMPT = (
    "📅 Enter the date {action} (format: DD/MM/YY)\n\n"
    "Example: 15/11/25\n"
    "Or type /cancel to abort."
)

# Main categories
CATEGORIES = [
    ["Home", "Car"],
    ["Lazer", "Travel"],
    ["Needs", "Health"],
    ["Streaming", "Subscriptions"],
    ["Others", "Incomes"]
]

# Subcategories for each main category
SUBCATEGORIES = {
    "Home": [
        ["Rent", "Light"],
        ["Water", "Net"],
        ["Groceries", "Me Mimei"],
        ["Other"]
    ],
    "Car": [
        ["Fuel", "Insurance"],
        ["Maintenance", "Parking"],
        ["Via Verde", "Other"]
    ],
    "Lazer": [
        ["Dining Out", "Movies/Shows"],
        ["Hobbies", "Coffees"],
        ["Other"]
    ],
    "Travel": [
        ["Flights", "Hotels"],
        ["Transportation", "Food"],
        ["Activities", "Other"]
    ],
    "Streaming": [
        ["Prime", "Netflix"],
        ["Disney+", "Crunchyroll"]
    ],
    "Subscriptions": [
        ["Patreon", "iCloud"],
        ["Spotify", "F1 TV"],
        ["Telemóvel", "Other"]
    ],
    "Needs": [
        ["Clothing", "Personal Care"],
        ["Other"]
    ],
    "Health": [
        ["Doctor", "Pharmacy"],
        ["Hospital_Urgency", "Gym"],
        ["Supplements", "Other"]
    ],
    "Others": [
        ["Gifts", "Pet"],
        ["Mi Mimei", "Maomao"],
        ["Other"]
    ],
    "Incomes": [
        ["Refeição", "Subsídio"],
        ["Bónus", "Salary"],
        ["Interest", "Others"]
    ]
}

# Categories/subcategories that don't need description input
# Description will be auto-filled as "Category - Subcategory"
AUTO_DESCRIPTION = {
    "Home": ["Rent", "Light", "Water", "Net", "Groceries"],
    "Car": ["Fuel", "Insurance", "Via Verde"],
    "Health": ["Doctor", "Pharmacy", "Gym", "Other"],
    "Streaming": "all",  # All subcategories in Streaming
    "Subscriptions": "all",  # All subcategories in Subscriptions
    "Incomes": ["Refeição", "Subsídio", "Bónus", "Salary"]
}


def should_skip_description(category: str, subcategory: str) -> bool:
    """Check if description should be auto-filled for this category/subcategory"""
    if category not in AUTO_DESCRIPTION:
        return False
    
    auto_subs = AUTO_DESCRIPTION[category]
    if auto_subs == "all":
        return True
    
    return subcategory in auto_subs


def get_today_date() -> str:
    """Get today's date in YYYY-MM-DD format"""
    return datetime.now().strftime("%Y-%m-%d")


@contextmanager
def get_db_connection():
    """Get thread-safe database connection with automatic commit/rollback"""
    # Use thread-local storage to ensure each thread has its own connection
    if not hasattr(thread_local, "connection"):
        thread_local.connection = sqlite3.connect(DB_FILE, check_same_thread=False)
        thread_local.connection.row_factory = sqlite3.Row
    
    conn = thread_local.connection
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise


def format_success_message(category: str, subcategory: str, amount: float, description: str, target_date: str = None, is_income: bool = False) -> str:
    """Format a standardized success message for saved expenses/incomes"""
    date_msg = f" for {target_date}" if target_date else ""
    entry_type = "Income" if is_income else "Expense"
    emoji = "💵" if is_income else "💸"
    next_cmd = "/add" if not is_income else "/add"
    
    return (
        f"✅ {entry_type} saved successfully{date_msg}!\n\n"
        f"📋 Category: {category}\n"
        f"🏷️ Subcategory: {subcategory}\n"
        f"{emoji} Amount: €{amount:.2f}\n"
        f"📝 Description: {description}\n\n"
        f"Use {next_cmd} to add another entry or /view to see today's entries.\n"
        "Use /help to see all available commands."
    )


async def handle_error(update: Update, error: Exception, operation: str, logger_instance=logger):
    """Centralized error handling for operations"""
    logger_instance.error(f"Error {operation}: {error}")
    await update.message.reply_text(f"Error {operation}. Please try again.")


def format_expense_line(row) -> str:
    """Format a single expense line for display from database row"""
    return f"• {row['category']} > {row['subcategory']}: €{row['amount']:.2f} - {row['description']}"


def format_expense_numbered(index: int, row) -> str:
    """Format a numbered expense line for selection lists"""
    return f"{index}. {row['category']} > {row['subcategory']}: €{row['amount']:.2f} - {row['description']}"


def get_week_dates():
    """Get start and end dates for the current week (Monday to Sunday)"""
    today = datetime.now()
    start_of_week = today - timedelta(days=today.weekday())
    end_of_week = start_of_week + timedelta(days=6)
    return start_of_week.strftime("%Y-%m-%d"), end_of_week.strftime("%Y-%m-%d")


def get_month_dates():
    """Get start and end dates for the current month"""
    today = datetime.now()
    start_of_month = today.replace(day=1)
    # Get last day of month
    if today.month == 12:
        end_of_month = today.replace(year=today.year + 1, month=1, day=1) - timedelta(days=1)
    else:
        end_of_month = today.replace(month=today.month + 1, day=1) - timedelta(days=1)
    return start_of_month.strftime("%Y-%m-%d"), end_of_month.strftime("%Y-%m-%d")


def get_year_dates():
    """Get start and end dates for the current year"""
    today = datetime.now()
    start_of_year = today.replace(month=1, day=1)
    end_of_year = today.replace(month=12, day=31)
    return start_of_year.strftime("%Y-%m-%d"), end_of_year.strftime("%Y-%m-%d")


def get_entries_for_period(start_date: str, end_date: str, user_id: int, table: str = "expenses"):
    """Get entries between two dates for a user"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(f"""
            SELECT * FROM {table}
            WHERE user_id = ? AND date >= ? AND date <= ?
            ORDER BY date DESC, time DESC
        """, (user_id, start_date, end_date))
        return cursor.fetchall()


def get_available_months(user_id: int) -> list:
    """Get list of months that have data for a user (from both expenses and incomes)"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        # Get unique year-month combinations from both tables
        cursor.execute("""
            SELECT DISTINCT substr(date, 1, 7) as month FROM expenses WHERE user_id = ?
            UNION
            SELECT DISTINCT substr(date, 1, 7) as month FROM incomes WHERE user_id = ?
            ORDER BY month DESC
        """, (user_id, user_id))
        results = cursor.fetchall()
        return [row[0] for row in results]  # Returns list like ['2026-01', '2025-12', ...]


def get_available_years(user_id: int) -> list:
    """Get list of years that have data for a user"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT DISTINCT substr(date, 1, 4) as year FROM expenses WHERE user_id = ?
            UNION
            SELECT DISTINCT substr(date, 1, 4) as year FROM incomes WHERE user_id = ?
            ORDER BY year DESC
        """, (user_id, user_id))
        results = cursor.fetchall()
        return [row[0] for row in results]  # Returns list like ['2026', '2025', ...]


def get_month_date_range(year_month: str) -> tuple:
    """Get start and end dates for a specific month (YYYY-MM format)"""
    year, month = int(year_month[:4]), int(year_month[5:7])
    start_date = f"{year_month}-01"
    # Get last day of month
    if month == 12:
        end_date = f"{year}-12-31"
    else:
        next_month = datetime(year, month + 1, 1)
        last_day = (next_month - timedelta(days=1)).day
        end_date = f"{year_month}-{last_day:02d}"
    return start_date, end_date


def get_year_date_range(year: str) -> tuple:
    """Get start and end dates for a specific year"""
    return f"{year}-01-01", f"{year}-12-31"


def format_month_for_display(year_month: str) -> str:
    """Format YYYY-MM to readable format like 'January 2026'"""
    year, month = year_month[:4], year_month[5:7]
    month_names = {
        '01': 'January', '02': 'February', '03': 'March', '04': 'April',
        '05': 'May', '06': 'June', '07': 'July', '08': 'August',
        '09': 'September', '10': 'October', '11': 'November', '12': 'December'
    }
    return f"{month_names.get(month, month)} {year}"


def generate_pdf_report(expenses: list, incomes: list, period_name: str, start_date: str, end_date: str) -> io.BytesIO:
    """Generate a PDF report with expenses and incomes"""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=20*mm, bottomMargin=20*mm)
    styles = getSampleStyleSheet()
    elements = []
    
    # Title style
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        spaceAfter=20,
        alignment=1  # Center
    )
    
    # Header style
    header_style = ParagraphStyle(
        'CustomHeader',
        parent=styles['Heading2'],
        fontSize=14,
        spaceAfter=10,
        textColor=colors.darkblue
    )
    
    # Add title
    title = Paragraph(f"📊 Financial Report - {period_name}", title_style)
    elements.append(title)
    
    # Add period info
    period_info = Paragraph(f"Period: {start_date} to {end_date}", styles['Normal'])
    elements.append(period_info)
    elements.append(Spacer(1, 10*mm))
    
    # Calculate totals
    total_expenses = sum(row['amount'] for row in expenses) if expenses else 0
    total_incomes = sum(row['amount'] for row in incomes) if incomes else 0
    balance = total_incomes - total_expenses
    
    # Summary section
    summary_header = Paragraph("💰 Summary", header_style)
    elements.append(summary_header)
    
    summary_data = [
        ['Category', 'Amount'],
        ['Total Incomes', f"€{total_incomes:.2f}"],
        ['Total Expenses', f"€{total_expenses:.2f}"],
        ['Balance', f"€{balance:.2f}"]
    ]
    
    summary_table = Table(summary_data, colWidths=[100*mm, 50*mm])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.darkblue),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        ('BACKGROUND', (0, 1), (-1, 1), colors.lightgreen),
        ('BACKGROUND', (0, 2), (-1, 2), colors.lightsalmon),
        ('BACKGROUND', (0, 3), (-1, 3), colors.lightyellow if balance >= 0 else colors.lightcoral),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
    ]))
    elements.append(summary_table)
    elements.append(Spacer(1, 10*mm))
    
    # Expenses by category
    if expenses:
        expenses_header = Paragraph("📉 Expenses by Category", header_style)
        elements.append(expenses_header)
        
        # Group by category
        category_totals = {}
        for row in expenses:
            cat = row['category']
            category_totals[cat] = category_totals.get(cat, 0) + row['amount']
        
        cat_data = [['Category', 'Total']]
        for cat, total in sorted(category_totals.items(), key=lambda x: x[1], reverse=True):
            cat_data.append([cat, f"€{total:.2f}"])
        
        cat_table = Table(cat_data, colWidths=[100*mm, 50*mm])
        cat_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.coral),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.whitesmoke, colors.white]),
        ]))
        elements.append(cat_table)
        elements.append(Spacer(1, 8*mm))
        
        # Detailed expenses
        expenses_detail_header = Paragraph("📋 Expense Details", header_style)
        elements.append(expenses_detail_header)
        
        exp_data = [['Date', 'Category', 'Subcategory', 'Amount', 'Description']]
        for row in expenses:
            exp_data.append([
                row['date'],
                row['category'],
                row['subcategory'],
                f"€{row['amount']:.2f}",
                row['description'][:25] + '...' if len(row['description']) > 25 else row['description']
            ])
        
        exp_table = Table(exp_data, colWidths=[25*mm, 30*mm, 30*mm, 22*mm, 43*mm])
        exp_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkred),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.whitesmoke, colors.white]),
        ]))
        elements.append(exp_table)
        elements.append(Spacer(1, 10*mm))
    
    # Incomes section
    if incomes:
        incomes_header = Paragraph("📈 Income Details", header_style)
        elements.append(incomes_header)
        
        inc_data = [['Date', 'Category', 'Subcategory', 'Amount', 'Description']]
        for row in incomes:
            inc_data.append([
                row['date'],
                row['category'],
                row['subcategory'],
                f"€{row['amount']:.2f}",
                row['description'][:25] + '...' if len(row['description']) > 25 else row['description']
            ])
        
        inc_table = Table(inc_data, colWidths=[25*mm, 30*mm, 30*mm, 22*mm, 43*mm])
        inc_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkgreen),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.honeydew, colors.white]),
        ]))
        elements.append(inc_table)
    
    # Footer
    elements.append(Spacer(1, 15*mm))
    footer = Paragraph(f"Generated on {datetime.now().strftime('%Y-%m-%d %H:%M')}", 
                       ParagraphStyle('Footer', parent=styles['Normal'], fontSize=8, textColor=colors.grey, alignment=1))
    elements.append(footer)
    
    # Build PDF
    doc.build(elements)
    buffer.seek(0)
    return buffer


async def pdf_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start PDF export conversation"""
    # Clear any previous conversation state
    context.user_data.clear()
    
    keyboard = [
        ["📅 This Week", "📆 Choose Month"],
        ["📊 Choose Year", "❌ Cancel"]
    ]
    
    await update.message.reply_text(
        "📄 *PDF Export*\n\n"
        "Choose the period for your financial report:",
        parse_mode="Markdown",
        reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    )
    return PDF_PERIOD


async def handle_pdf_period(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle PDF period selection"""
    choice = update.message.text.strip()
    user_id = update.effective_user.id
    
    if "Cancel" in choice:
        await update.message.reply_text("❌ PDF export cancelled.", reply_markup=ReplyKeyboardRemove())
        return ConversationHandler.END
    
    # Week - generate immediately
    if "Week" in choice:
        start_date, end_date = get_week_dates()
        period_name = "This Week"
        return await generate_and_send_pdf(update, user_id, start_date, end_date, period_name)
    
    # Month - show available months
    elif "Month" in choice:
        available_months = get_available_months(user_id)
        
        if not available_months:
            await update.message.reply_text(
                "📭 No data found. Start tracking your expenses first!",
                reply_markup=ReplyKeyboardRemove()
            )
            return ConversationHandler.END
        
        # Create keyboard with available months (max 12 for display)
        keyboard = []
        for i in range(0, min(len(available_months), 12), 2):
            row = [format_month_for_display(available_months[i])]
            if i + 1 < len(available_months):
                row.append(format_month_for_display(available_months[i + 1]))
            keyboard.append(row)
        keyboard.append(["❌ Cancel"])
        
        # Store mapping for later use
        context.user_data['month_mapping'] = {
            format_month_for_display(m): m for m in available_months
        }
        
        await update.message.reply_text(
            "📆 *Select Month*\n\n"
            "Choose a month with recorded data:",
            parse_mode="Markdown",
            reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
        )
        return PDF_MONTH
    
    # Year - show available years
    elif "Year" in choice:
        available_years = get_available_years(user_id)
        
        if not available_years:
            await update.message.reply_text(
                "📭 No data found. Start tracking your expenses first!",
                reply_markup=ReplyKeyboardRemove()
            )
            return ConversationHandler.END
        
        # Create keyboard with available years
        keyboard = []
        for i in range(0, len(available_years), 2):
            row = [f"📊 {available_years[i]}"]
            if i + 1 < len(available_years):
                row.append(f"📊 {available_years[i + 1]}")
            keyboard.append(row)
        keyboard.append(["❌ Cancel"])
        
        await update.message.reply_text(
            "📊 *Select Year*\n\n"
            "Choose a year with recorded data:",
            parse_mode="Markdown",
            reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
        )
        return PDF_YEAR
    
    else:
        await update.message.reply_text("❌ Invalid option. Please try again with /pdf")
        return ConversationHandler.END


async def handle_pdf_month(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle month selection for PDF"""
    choice = update.message.text.strip()
    user_id = update.effective_user.id
    
    if "Cancel" in choice:
        await update.message.reply_text("❌ PDF export cancelled.", reply_markup=ReplyKeyboardRemove())
        context.user_data.pop('month_mapping', None)
        return ConversationHandler.END
    
    # Get the YYYY-MM format from mapping
    month_mapping = context.user_data.get('month_mapping', {})
    year_month = month_mapping.get(choice)
    
    if not year_month:
        await update.message.reply_text("❌ Invalid month. Please try again with /pdf")
        return ConversationHandler.END
    
    start_date, end_date = get_month_date_range(year_month)
    period_name = choice  # Already formatted like "January 2026"
    
    context.user_data.pop('month_mapping', None)
    return await generate_and_send_pdf(update, user_id, start_date, end_date, period_name)


async def handle_pdf_year(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle year selection for PDF"""
    choice = update.message.text.strip()
    user_id = update.effective_user.id
    
    if "Cancel" in choice:
        await update.message.reply_text("❌ PDF export cancelled.", reply_markup=ReplyKeyboardRemove())
        return ConversationHandler.END
    
    # Extract year from choice (e.g., "📊 2026" -> "2026")
    year = choice.replace("📊 ", "").strip()
    
    if not year.isdigit() or len(year) != 4:
        await update.message.reply_text("❌ Invalid year. Please try again with /pdf")
        return ConversationHandler.END
    
    start_date, end_date = get_year_date_range(year)
    period_name = year
    
    return await generate_and_send_pdf(update, user_id, start_date, end_date, period_name)


async def generate_and_send_pdf(update: Update, user_id: int, start_date: str, end_date: str, period_name: str):
    """Generate and send PDF report"""
    await update.message.reply_text("⏳ Generating PDF report...", reply_markup=ReplyKeyboardRemove())
    
    try:
        # Get data
        expenses = get_entries_for_period(start_date, end_date, user_id, "expenses")
        incomes = get_entries_for_period(start_date, end_date, user_id, "incomes")
        
        if not expenses and not incomes:
            await update.message.reply_text(f"📭 No data found for {period_name}.")
            return ConversationHandler.END
        
        # Generate PDF
        pdf_buffer = generate_pdf_report(expenses, incomes, period_name, start_date, end_date)
        
        # Create filename
        filename = f"finance_report_{period_name.lower().replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.pdf"
        
        # Send PDF
        await update.message.reply_document(
            document=pdf_buffer,
            filename=filename,
            caption=f"📊 *Financial Report - {period_name}*\n\n"
                   f"📅 Period: {start_date} to {end_date}\n"
                   f"📉 Expenses: {len(expenses)} entries\n"
                   f"📈 Incomes: {len(incomes)} entries",
            parse_mode="Markdown"
        )
        
        logger.info(f"PDF report generated for user {user_id}: {period_name}")
        
    except Exception as e:
        logger.error(f"Error generating PDF: {e}")
        await update.message.reply_text("❌ Error generating PDF. Please try again.")
    
    return ConversationHandler.END


def get_entries_for_date(target_date: str, user_id: int, table: str = "expenses"):
    """Load entries (expenses or incomes) for a specific date and user from database"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(f"""
            SELECT * FROM {table}
            WHERE user_id = ? AND date = ?
            ORDER BY time DESC
        """, (user_id, target_date))
        return cursor.fetchall()


def init_database():
    """Initialize SQLite database with expenses and incomes tables"""
    # Ensure data directory exists
    data_dir = os.path.dirname(DB_FILE)
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Create expenses table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                date TEXT NOT NULL,
                time TEXT NOT NULL,
                category TEXT NOT NULL,
                subcategory TEXT NOT NULL,
                amount REAL NOT NULL,
                description TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create incomes table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS incomes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                date TEXT NOT NULL,
                time TEXT NOT NULL,
                category TEXT NOT NULL,
                subcategory TEXT NOT NULL,
                amount REAL NOT NULL,
                description TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create indexes for better query performance
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_expenses_user_date ON expenses(user_id, date)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_incomes_user_date ON incomes(user_id, date)")
        
        logger.debug(f"Database initialized: {DB_FILE}")


def save_expense(category: str, subcategory: str, amount: float, description: str, user_id: int, custom_date: str = None):
    """Save expense or income to database for specific user"""
    # Determine if this is an income or expense
    is_income = (category == "Incomes")
    table = "incomes" if is_income else "expenses"
    
    try:
        if custom_date:
            date_str = custom_date
        else:
            date_str = datetime.now().strftime("%Y-%m-%d")
        
        time_str = datetime.now().strftime("%H:%M:%S")
        
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(f"""
                INSERT INTO {table} (user_id, date, time, category, subcategory, amount, description)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (user_id, date_str, time_str, category, subcategory, amount, description))
            
            entry_type = "income" if is_income else "expense"
            logger.debug(f"Saved {entry_type} for user {user_id}: {category} > {subcategory} - €{amount} on {date_str}")
            return True
    except Exception as e:
        entry_type = "income" if is_income else "expense"
        logger.error(f"Error saving {entry_type}: {e}")
        return False


async def view_incomes_month(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """View incomes for a specific month"""
    try:
        # Parse the command to get month name or number
        message_text = update.message.text.lower()
        
        # Extract month from command (e.g., "/income november" or "/income 11")
        parts = message_text.split()
        if len(parts) < 2:
            await update.message.reply_text(
                "📅 Please specify a month.\n\n"
                "Examples:\n"
                "/income november\n"
                "/income 11\n"
                "/income novembro"
            )
            return
        
        month_input = parts[1]
        month_num = MONTH_MAPPINGS.get(month_input)
        
        if not month_num:
            await update.message.reply_text(
                "❌ Invalid month. Please use month name or number (1-12).\n\n"
                "Examples: /income november or /income 11"
            )
            return
        
        # Get current year
        current_year = datetime.now().year
        user_id = update.effective_user.id
        
        # Query incomes from database
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM incomes
                WHERE user_id = ? AND date LIKE ?
                ORDER BY date, time
            """, (user_id, f"{current_year}-{month_num}-%"))
            incomes = cursor.fetchall()
        
        if incomes:
            total = 0.0
            category_totals = {}
            
            for row in incomes:
                amount = row['amount']
                total += amount
                
                # Track subcategory totals (all are Incomes category)
                subcategory = row['subcategory']
                category_totals[subcategory] = category_totals.get(subcategory, 0) + amount
            
            message = f"💰 Incomes for {MONTH_NAMES[month_num]} {current_year}:\n\n"
            message += f"📋 By Type:\n"
            for subcat, subcat_total in sorted(category_totals.items()):
                message += f"  • {subcat}: €{subcat_total:.2f}\n"
            
            message += f"\n💵 Total Income: €{total:.2f}\n"
            message += f"📝 {len(incomes)} income(s) recorded"
        else:
            await update.message.reply_text(f"No incomes recorded for {month_input.capitalize()} {current_year}.")
            return
        
        await update.message.reply_text(message)
        
    except Exception as e:
        await handle_error(update, e, "viewing month incomes")


async def view_expenses_month(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """View expenses for a specific month"""
    try:
        # Parse the command to get month name or number
        message_text = update.message.text.lower()
        
        # Extract month from command (e.g., "/expense november" or "/expense 11")
        parts = message_text.split()
        if len(parts) < 2:
            await update.message.reply_text(
                "📅 Please specify a month.\n\n"
                "Examples:\n"
                "/expense november\n"
                "/expense 11\n"
                "/expense novembro"
            )
            return
        
        month_input = parts[1]
        month_num = MONTH_MAPPINGS.get(month_input)
        
        if not month_num:
            await update.message.reply_text(
                "❌ Invalid month. Please use month name or number (1-12).\n\n"
                "Examples: /expense november or /expense 11"
            )
            return
        
        # Get current year
        current_year = datetime.now().year
        user_id = update.effective_user.id
        
        # Query expenses from database
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM expenses
                WHERE user_id = ? AND date LIKE ?
                ORDER BY date, time
            """, (user_id, f"{current_year}-{month_num}-%"))
            expenses = cursor.fetchall()
        
        if expenses:
            total = 0.0
            category_totals = {}
            
            for row in expenses:
                amount = row['amount']
                total += amount
                
                # Track category > subcategory totals
                key = f"{row['category']} > {row['subcategory']}"
                category_totals[key] = category_totals.get(key, 0) + amount
            
            message = f"💸 Expenses for {MONTH_NAMES[month_num]} {current_year}:\n\n"
            message += f"📋 By Category:\n"
            for cat, cat_total in sorted(category_totals.items()):
                message += f"  • {cat}: €{cat_total:.2f}\n"
            
            message += f"\n💰 Total Expenses: €{total:.2f}\n"
            message += f"📝 {len(expenses)} expense(s) recorded"
        else:
            await update.message.reply_text(f"No expenses recorded for {month_input.capitalize()} {current_year}.")
            return
        
        await update.message.reply_text(message)
        
    except Exception as e:
        await handle_error(update, e, "viewing month expenses")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show help message with all available commands"""
    await update.message.reply_text(
        "📋 **Available Commands:**\n\n"
        "** Add Entries **\n"
        "/add - Add expense or income for today\n"
        "/add_d - Add expense or income for a specific date\n\n"
        "** View & Summary **\n"
        "/view - View today's expenses\n"
        "/summary - Interactive summary (day/month/year)\n\n"
        "** Edit & Delete (Today) **\n"
        "/edit - Edit an expense from today\n"
        "/delete - Delete an expense from today\n\n"
        "** Specific Date **\n"
        "/view_d - View expenses for a specific date\n"
        "/edit_d - Edit expense from a specific date\n"
        "/delete_d - Delete expense from a specific date\n\n"
        "** Quick Views by Month **\n"
        "/expense <month> - View expenses only for a month\n"
        "/income <month> - View incomes only for a month\n"
        "Example: /expense february or /income 2\n\n"
        "** Combined View **\n"
        "/month <name> - View summary (expenses + incomes + balance)\n"
        "Example: /month february or /month 2\n\n"
        "** Export **\n"
        "/pdf - Export PDF report (week/month/year)\n\n"
        "** Other **\n"
        "/cancel - Cancel current operation\n"
        "/help - Show this help message\n"
    )


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Start the conversation and ask for expense category"""
    await update.message.reply_text(
        "👋 Welcome to your Expense & Income Tracker! 📊\n\n"
        "I'll help you track your finances easily.\n\n"
        "Use /help to see all available commands.\n\n"
        "Let's add an entry! Please select a category:",
        reply_markup=ReplyKeyboardMarkup(CATEGORIES, one_time_keyboard=True),
    )
    return CATEGORY


async def add_expense(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Start adding a new expense"""
    # Clear any previous conversation state
    context.user_data.clear()
    
    await update.message.reply_text(
        "Let's add a new entry! 💰\n\n"
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
        
        # Validate amount
        if not math.isfinite(amount_value):
            await update.message.reply_text(
                "❌ Invalid amount. Please enter a valid number (use . as decimal separator):"
            )
            return AMOUNT
        
        if amount_value <= 0:
            await update.message.reply_text(
                "❌ Amount must be positive! Please enter a positive number:"
            )
            return AMOUNT
        
        if amount_value > MAX_AMOUNT:
            await update.message.reply_text(
                "❌ Amount too large! Please enter a reasonable amount:"
            )
            return AMOUNT
        
        context.user_data["amount"] = amount_value
        
        # Check if we should skip description
        if context.user_data.get("skip_description", False):
            # Auto-fill description and save directly
            category = context.user_data["category"]
            subcategory = context.user_data.get("subcategory", "N/A")
            description = f"{category} - {subcategory}"
            target_date = context.user_data.get("target_date")
            user_id = update.effective_user.id
            
            is_income = (category == "Incomes")
            if save_expense(category, subcategory, amount_value, description, user_id, target_date):
                await update.message.reply_text(
                    format_success_message(category, subcategory, amount_value, description, target_date, is_income)
                )
            else:
                await update.message.reply_text(
                    "❌ Sorry, there was an error saving your entry. Please try again."
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
            "Please enter a valid number for the amount (use . as decimal separator):"
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
    user_id = update.effective_user.id
    is_income = (category == "Incomes")
    
    if save_expense(category, subcategory, amount, description, user_id, target_date):
        await update.message.reply_text(
            format_success_message(category, subcategory, amount, description, target_date, is_income)
        )
    else:
        await update.message.reply_text(
            "❌ Sorry, there was an error saving your entry. Please try again."
        )
    
    context.user_data.clear()
    return ConversationHandler.END


async def view_expenses(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """View today's expenses for current user"""
    try:
        today = get_today_date()
        user_id = update.effective_user.id
        expenses = get_entries_for_date(today, user_id, "expenses")
        
        if expenses:
            total = sum(row['amount'] for row in expenses)
            message = f"📊 Today's Expenses ({today}):\n\n"
            for exp in expenses:
                message += format_expense_line(exp) + "\n"
            message += f"\n💰 Total: €{total:.2f}"
        else:
            message = "No expenses recorded for today."
        
        await update.message.reply_text(message)
    except Exception as e:
        await handle_error(update, e, "viewing expenses")


async def summary_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Start the summary conversation - show period selection"""
    # Clear any previous conversation state
    context.user_data.clear()
    
    keyboard = [
        ["📅 Today", "📆 Specific Day"],
        ["📊 Month", "📈 Year"],
        ["❌ Cancel"]
    ]
    
    await update.message.reply_text(
        "📊 *Financial Summary*\n\n"
        "Choose the period you want to view:",
        parse_mode="Markdown",
        reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    )
    return SUMMARY_PERIOD


async def handle_summary_period(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle summary period selection"""
    choice = update.message.text.strip()
    user_id = update.effective_user.id
    
    if "Cancel" in choice:
        await update.message.reply_text("❌ Summary cancelled.", reply_markup=ReplyKeyboardRemove())
        return ConversationHandler.END
    
    # Today - generate immediately
    if "Today" in choice:
        return await generate_and_send_summary(update, user_id, "today")
    
    # Specific Day - ask for date
    elif "Specific Day" in choice:
        await update.message.reply_text(
            "📅 *Select a Date*\n\n"
            "Enter the date in one of these formats:\n"
            "• `DD/MM` (current year)\n"
            "• `DD/MM/YYYY`\n"
            "• `YYYY-MM-DD`\n\n"
            "Example: `15/02` or `15/02/2026`",
            parse_mode="Markdown",
            reply_markup=ReplyKeyboardRemove()
        )
        return SUMMARY_DAY
    
    # Month - show available months
    elif "Month" in choice:
        available_months = get_available_months(user_id)
        
        if not available_months:
            await update.message.reply_text(
                "📭 No data found. Start tracking your finances first!",
                reply_markup=ReplyKeyboardRemove()
            )
            return ConversationHandler.END
        
        # Create keyboard with available months (max 12 for display)
        keyboard = []
        for i in range(0, min(len(available_months), 12), 2):
            row = [format_month_for_display(available_months[i])]
            if i + 1 < len(available_months):
                row.append(format_month_for_display(available_months[i + 1]))
            keyboard.append(row)
        keyboard.append(["❌ Cancel"])
        
        # Store mapping for later use
        context.user_data['summary_month_mapping'] = {
            format_month_for_display(m): m for m in available_months
        }
        
        await update.message.reply_text(
            "📆 *Select Month*\n\n"
            "Choose a month with recorded data:",
            parse_mode="Markdown",
            reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
        )
        return SUMMARY_MONTH
    
    # Year - show available years
    elif "Year" in choice:
        available_years = get_available_years(user_id)
        
        if not available_years:
            await update.message.reply_text(
                "📭 No data found. Start tracking your finances first!",
                reply_markup=ReplyKeyboardRemove()
            )
            return ConversationHandler.END
        
        # Create keyboard with available years
        keyboard = []
        for i in range(0, len(available_years), 2):
            row = [f"📊 {available_years[i]}"]
            if i + 1 < len(available_years):
                row.append(f"📊 {available_years[i + 1]}")
            keyboard.append(row)
        keyboard.append(["❌ Cancel"])
        
        await update.message.reply_text(
            "📊 *Select Year*\n\n"
            "Choose a year with recorded data:",
            parse_mode="Markdown",
            reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
        )
        return SUMMARY_YEAR
    
    else:
        await update.message.reply_text("❌ Invalid option. Please try again with /summary")
        return ConversationHandler.END


async def handle_summary_day(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle specific day input for summary"""
    date_input = update.message.text.strip()
    user_id = update.effective_user.id
    
    # Parse date in various formats
    target_date = None
    current_year = datetime.now().year
    
    try:
        # Try DD/MM format (current year)
        if re.match(r'^\d{1,2}/\d{1,2}$', date_input):
            day, month = date_input.split('/')
            target_date = f"{current_year}-{int(month):02d}-{int(day):02d}"
        # Try DD/MM/YYYY format
        elif re.match(r'^\d{1,2}/\d{1,2}/\d{4}$', date_input):
            day, month, year = date_input.split('/')
            target_date = f"{year}-{int(month):02d}-{int(day):02d}"
        # Try YYYY-MM-DD format
        elif re.match(r'^\d{4}-\d{2}-\d{2}$', date_input):
            target_date = date_input
        else:
            await update.message.reply_text(
                "❌ Invalid date format.\n\n"
                "Please use: `DD/MM`, `DD/MM/YYYY`, or `YYYY-MM-DD`\n"
                "Example: `15/02` or `15/02/2026`",
                parse_mode="Markdown"
            )
            return SUMMARY_DAY
        
        # Validate date exists
        datetime.strptime(target_date, "%Y-%m-%d")
        
    except ValueError:
        await update.message.reply_text(
            "❌ Invalid date. Please enter a valid date.",
            reply_markup=ReplyKeyboardRemove()
        )
        return SUMMARY_DAY
    
    return await generate_and_send_summary(update, user_id, "day", target_date)


async def handle_summary_month(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle month selection for summary"""
    choice = update.message.text.strip()
    user_id = update.effective_user.id
    
    if "Cancel" in choice:
        await update.message.reply_text("❌ Summary cancelled.", reply_markup=ReplyKeyboardRemove())
        context.user_data.pop('summary_month_mapping', None)
        return ConversationHandler.END
    
    # Get the YYYY-MM format from mapping
    month_mapping = context.user_data.get('summary_month_mapping', {})
    year_month = month_mapping.get(choice)
    
    if not year_month:
        await update.message.reply_text("❌ Invalid month. Please try again with /summary")
        return ConversationHandler.END
    
    context.user_data.pop('summary_month_mapping', None)
    return await generate_and_send_summary(update, user_id, "month", year_month)


async def handle_summary_year(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle year selection for summary"""
    choice = update.message.text.strip()
    user_id = update.effective_user.id
    
    if "Cancel" in choice:
        await update.message.reply_text("❌ Summary cancelled.", reply_markup=ReplyKeyboardRemove())
        return ConversationHandler.END
    
    # Extract year from choice (e.g., "📊 2026" -> "2026")
    year = choice.replace("📊 ", "").strip()
    
    if not year.isdigit() or len(year) != 4:
        await update.message.reply_text("❌ Invalid year. Please try again with /summary")
        return ConversationHandler.END
    
    return await generate_and_send_summary(update, user_id, "year", year)


async def generate_and_send_summary(update: Update, user_id: int, period_type: str, period_value: str = None) -> int:
    """Generate and send financial summary for the specified period"""
    try:
        # Determine date range based on period type
        if period_type == "today":
            start_date = end_date = get_today_date()
            period_name = f"Today ({start_date})"
        elif period_type == "day":
            start_date = end_date = period_value
            period_name = f"{period_value}"
        elif period_type == "month":
            start_date, end_date = get_month_date_range(period_value)
            period_name = format_month_for_display(period_value)
        elif period_type == "year":
            start_date, end_date = get_year_date_range(period_value)
            period_name = period_value
        else:
            await update.message.reply_text("❌ Invalid period type.", reply_markup=ReplyKeyboardRemove())
            return ConversationHandler.END
        
        # Get expenses grouped by category
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Expenses by category
            cursor.execute("""
                SELECT category, subcategory, SUM(amount) as total, COUNT(*) as count
                FROM expenses
                WHERE user_id = ? AND date >= ? AND date <= ?
                GROUP BY category, subcategory
                ORDER BY category, subcategory
            """, (user_id, start_date, end_date))
            expense_totals = cursor.fetchall()
            
            # Incomes by category
            cursor.execute("""
                SELECT category, subcategory, SUM(amount) as total, COUNT(*) as count
                FROM incomes
                WHERE user_id = ? AND date >= ? AND date <= ?
                GROUP BY category, subcategory
                ORDER BY category, subcategory
            """, (user_id, start_date, end_date))
            income_totals = cursor.fetchall()
        
        # Check if there's any data
        if not expense_totals and not income_totals:
            await update.message.reply_text(
                f"📭 No records found for {period_name}.",
                reply_markup=ReplyKeyboardRemove()
            )
            return ConversationHandler.END
        
        # Build message
        message = f"📊 *Summary for {period_name}*\n\n"
        
        # Expenses section
        if expense_totals:
            expense_grand_total = 0.0
            expense_count = 0
            message += "💸 *Expenses:*\n"
            for row in expense_totals:
                cat_key = f"{row['category']} > {row['subcategory']}"
                total = row['total']
                count = row['count']
                expense_grand_total += total
                expense_count += count
                message += f"  • {cat_key}: €{total:.2f} ({count})\n"
            message += f"  📝 *Total:* €{expense_grand_total:.2f} ({expense_count} entries)\n\n"
        else:
            expense_grand_total = 0.0
            message += "💸 *Expenses:* €0.00\n\n"
        
        # Incomes section
        if income_totals:
            income_grand_total = 0.0
            income_count = 0
            message += "💵 *Incomes:*\n"
            for row in income_totals:
                cat_key = f"{row['category']} > {row['subcategory']}"
                total = row['total']
                count = row['count']
                income_grand_total += total
                income_count += count
                message += f"  • {cat_key}: €{total:.2f} ({count})\n"
            message += f"  📝 *Total:* €{income_grand_total:.2f} ({income_count} entries)\n\n"
        else:
            income_grand_total = 0.0
            message += "💵 *Incomes:* €0.00\n\n"
        
        # Balance
        balance = income_grand_total - expense_grand_total
        balance_emoji = "📈" if balance >= 0 else "📉"
        balance_text = f"+€{balance:.2f}" if balance >= 0 else f"-€{abs(balance):.2f}"
        message += f"{balance_emoji} *Balance:* {balance_text}"
        
        await update.message.reply_text(message, parse_mode="Markdown", reply_markup=ReplyKeyboardRemove())
        
    except Exception as e:
        logger.error(f"Error generating summary: {e}")
        await update.message.reply_text("❌ Error generating summary. Please try again.", reply_markup=ReplyKeyboardRemove())
    
    return ConversationHandler.END


async def view_month_expenses(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """View expenses for a specific month"""
    try:
        # Parse the command to get month name or number
        message_text = update.message.text.lower()
        
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
        month_num = MONTH_MAPPINGS.get(month_input)
        
        if not month_num:
            await update.message.reply_text(
                "❌ Invalid month. Please use month name or number (1-12).\n\n"
                "Examples: /month november or /month 11"
            )
            return
        
        # Get current year
        current_year = datetime.now().year
        user_id = update.effective_user.id
        
        # Query expenses and incomes from database
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM expenses
                WHERE user_id = ? AND date LIKE ?
                ORDER BY date, time
            """, (user_id, f"{current_year}-{month_num}-%"))
            expenses = cursor.fetchall()
            
            cursor.execute("""
                SELECT * FROM incomes
                WHERE user_id = ? AND date LIKE ?
                ORDER BY date, time
            """, (user_id, f"{current_year}-{month_num}-%"))
            incomes = cursor.fetchall()
        
        if not expenses and not incomes:
            await update.message.reply_text(f"No records for {month_input.capitalize()} {current_year}.")
            return
        
        message = f"📊 Summary for {MONTH_NAMES[month_num]} {current_year}:\n\n"
        
        # Expenses section
        if expenses:
            expense_total = 0.0
            expense_categories = {}
            
            for row in expenses:
                amount = row['amount']
                expense_total += amount
                key = f"{row['category']} > {row['subcategory']}"
                expense_categories[key] = expense_categories.get(key, 0) + amount
            
            message += f"💸 Expenses:\n"
            for cat, cat_total in sorted(expense_categories.items()):
                message += f"  • {cat}: €{cat_total:.2f}\n"
            message += f"  📝 Total: €{expense_total:.2f} ({len(expenses)} entries)\n\n"
        else:
            expense_total = 0.0
            message += f"💸 Expenses: €0.00\n\n"
        
        # Incomes section
        if incomes:
            income_total = 0.0
            income_categories = {}
            
            for row in incomes:
                amount = row['amount']
                income_total += amount
                key = f"{row['category']} > {row['subcategory']}"
                income_categories[key] = income_categories.get(key, 0) + amount
            
            message += f"💵 Incomes:\n"
            for cat, cat_total in sorted(income_categories.items()):
                message += f"  • {cat}: €{cat_total:.2f}\n"
            message += f"  📝 Total: €{income_total:.2f} ({len(incomes)} entries)\n\n"
        else:
            income_total = 0.0
            message += f"💵 Incomes: €0.00\n\n"
        
        # Balance
        balance = income_total - expense_total
        balance_emoji = "📈" if balance >= 0 else "📉"
        message += f"{balance_emoji} Balance: €{balance:.2f}"
        
        await update.message.reply_text(message)
        
    except Exception as e:
        await handle_error(update, e, "viewing month expenses")


async def show_expenses_for_action(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    target_date: str,
    action: str,
    user_data_key: str
):
    """Generic function to show expenses for delete/edit actions for current user"""
    try:
        user_id = update.effective_user.id
        expenses = get_entries_for_date(target_date, user_id, "expenses")
        
        if not expenses:
            await update.message.reply_text(f"No expenses to {action} for {target_date}.")
            return
        
        # Build message with appropriate emoji
        emoji = {"delete": "🗑️", "edit": "✏️"}.get(action, "📋")
        message = f"{emoji} Expenses for {target_date}:\n\n"
        
        for i, row in enumerate(expenses, start=1):
            message += format_expense_numbered(i, row) + "\n"
        
        message += f"\nReply with the number (1-{len(expenses)}) to {action}, or /cancel to abort."
        
        context.user_data[user_data_key] = expenses
        await update.message.reply_text(message)
        
    except Exception as e:
        await handle_error(update, e, f"showing expenses for {action}")
        # Clean up on error
        context.user_data.pop(user_data_key, None)


async def delete_expense(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show today's expenses and allow user to delete one"""
    today = get_today_date()
    await show_expenses_for_action(update, context, today, "delete", "delete_expenses")


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
        row = expenses[choice - 1]
        expense_id = row['id']
        user_id = update.effective_user.id
        
        # Delete from database (with user_id check for security)
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM expenses WHERE id = ? AND user_id = ?", (expense_id, user_id))
        
        # Show confirmation
        await update.message.reply_text(
            f"✅ Deleted expense:\n\n"
            f"📋 Category: {row['category']}\n"
            f"🏷️ Subcategory: {row['subcategory']}\n"
            f"💵 Amount: €{row['amount']:.2f}\n"
            f"📝 Description: {row['description']}\n\n"
            "Expense has been removed."
        )
        
    except ValueError:
        await update.message.reply_text(
            "Please enter a valid number, or /cancel to abort."
        )
    except Exception as e:
        await handle_error(update, e, "deleting expense")
    finally:
        # Always clear the delete context
        context.user_data.pop("delete_expenses", None)


# Edit expense functions

async def edit_expense(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show today's expenses and allow user to edit one"""
    today = get_today_date()
    await show_expenses_for_action(update, context, today, "edit", "edit_expenses")


async def edit_expense_date(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Edit expense for a specific date"""
    # Clear any previous conversation state
    context.user_data.clear()
    context.user_data["editing_for_date"] = True
    
    await update.message.reply_text(
        DATE_FORMAT_PROMPT.format(action="to edit an expense")
    )
    return DATE_INPUT


async def show_edit_for_date(update: Update, context: ContextTypes.DEFAULT_TYPE, target_date: str):
    """Show expenses for a specific date and allow editing"""
    await show_expenses_for_action(update, context, target_date, "edit", "edit_expenses")


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
        row = expenses[choice - 1]
        context.user_data["edit_expense_id"] = row['id']
        context.user_data["edit_expense_data"] = {
            "category": row['category'],
            "subcategory": row['subcategory'],
            "amount": row['amount'],
            "description": row['description']
        }
        context.user_data.pop("edit_expenses", None)
        
        # Show what can be edited
        await update.message.reply_text(
            f"✏️ Editing expense:\n\n"
            f"📋 Category: {row['category']}\n"
            f"🏷️ Subcategory: {row['subcategory']}\n"
            f"💵 Amount: €{row['amount']:.2f}\n"
            f"📝 Description: {row['description']}\n\n"
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
        await handle_error(update, e, "selecting expense for edit")
        # Clean up on error
        context.user_data.pop("edit_expenses", None)
        context.user_data.pop("edit_expense_id", None)
        context.user_data.pop("edit_expense_data", None)


async def handle_edit_field_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the choice of what field to edit"""
    try:
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
    except Exception as e:
        await handle_error(update, e, "handling edit field choice")
        # Clean up on error
        context.user_data.pop("edit_expense_id", None)
        context.user_data.pop("edit_expense_data", None)
        context.user_data.pop("editing_field", None)


async def handle_edit_value(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the new value for the edited field"""
    try:
        field = context.user_data.get("editing_field")
        new_value = update.message.text
        
        if field == "amount":
            new_value = float(new_value)
            
            # Validate amount
            if not math.isfinite(new_value):
                await update.message.reply_text(
                    "❌ Invalid amount. Please enter a valid number:"
                )
                return
            
            if new_value <= 0:
                await update.message.reply_text(
                    "❌ Amount must be positive! Please enter a positive number:"
                )
                return
            
            if new_value > MAX_AMOUNT:
                await update.message.reply_text(
                    "❌ Amount too large! Please enter a reasonable amount:"
                )
                return
        
        # Update database (with user_id check for security)
        expense_id = context.user_data["edit_expense_id"]
        user_id = update.effective_user.id
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            if field == "amount":
                cursor.execute(
                    "UPDATE expenses SET amount = ? WHERE id = ? AND user_id = ?",
                    (new_value, expense_id, user_id)
                )
                context.user_data["edit_expense_data"]["amount"] = new_value
            elif field == "description":
                cursor.execute(
                    "UPDATE expenses SET description = ? WHERE id = ? AND user_id = ?",
                    (new_value, expense_id, user_id)
                )
                context.user_data["edit_expense_data"]["description"] = new_value
        
        # Show confirmation
        data = context.user_data["edit_expense_data"]
        await update.message.reply_text(
            f"✅ Expense updated successfully!\n\n"
            f"📋 Category: {data['category']}\n"
            f"🏷️ Subcategory: {data['subcategory']}\n"
            f"💵 Amount: €{data['amount']:.2f}\n"
            f"📝 Description: {data['description']}"
        )
        
    except ValueError:
        await update.message.reply_text(
            "Please enter a valid number for the amount, or /cancel to abort."
        )
    except Exception as e:
        await handle_error(update, e, "updating expense")
    finally:
        # Always clear edit context
        context.user_data.pop("edit_expense_id", None)
        context.user_data.pop("edit_expense_data", None)
        context.user_data.pop("editing_field", None)


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
    # Clear any previous conversation state
    context.user_data.clear()
    context.user_data["adding_for_date"] = True
    
    await update.message.reply_text(
        DATE_FORMAT_PROMPT.format(action="for the expense")
    )
    return DATE_INPUT


async def view_expenses_date(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """View expenses for a specific date"""
    # Clear any previous conversation state
    context.user_data.clear()
    context.user_data["viewing_date"] = True
    
    await update.message.reply_text(
        DATE_FORMAT_PROMPT.format(action="to view expenses")
    )
    return DATE_INPUT


async def delete_expense_date(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Delete expense for a specific date"""
    # Clear any previous conversation state
    context.user_data.clear()
    context.user_data["deleting_for_date"] = True
    
    await update.message.reply_text(
        DATE_FORMAT_PROMPT.format(action="to delete an expense")
    )
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
    """View expenses for a specific date for current user"""
    try:
        user_id = update.effective_user.id
        expenses = get_entries_for_date(target_date, user_id, "expenses")
        
        if expenses:
            total = sum(row['amount'] for row in expenses)
            message = f"📊 Expenses for {target_date}:\n\n"
            for exp in expenses:
                message += format_expense_line(exp) + "\n"
            message += f"\n💰 Total: €{total:.2f}"
        else:
            message = f"No expenses recorded for {target_date}."
        
        await update.message.reply_text(message)
    except Exception as e:
        await handle_error(update, e, "viewing expenses for date")


async def show_delete_for_date(update: Update, context: ContextTypes.DEFAULT_TYPE, target_date: str):
    """Show expenses for a specific date and allow deletion"""
    await show_expenses_for_action(update, context, target_date, "delete", "delete_expenses")


def main():
    """Start the bot"""
    # Validate required environment variables
    BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    
    if not BOT_TOKEN:
        logger.error("FATAL: TELEGRAM_BOT_TOKEN environment variable not set")
        logger.error("Get your token from @BotFather on Telegram")
        logger.error("Then set: export TELEGRAM_BOT_TOKEN='your-token-here'")
        sys.exit(1)
    
    if len(BOT_TOKEN) < 40 or ":" not in BOT_TOKEN:
        logger.error("FATAL: TELEGRAM_BOT_TOKEN appears to be invalid (wrong format)")
        sys.exit(1)
    
    # Initialize database
    try:
        init_database()
    except Exception as e:
        logger.error(f"FATAL: Failed to initialize database: {e}")
        sys.exit(1)
    
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
        allow_reentry=True,
    )
    
    # Conversation handler for viewing specific date
    view_date_handler = ConversationHandler(
        entry_points=[CommandHandler("view_d", view_expenses_date)],
        states={
            DATE_INPUT: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_date_input)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
        allow_reentry=True,
    )
    
    # Conversation handler for deleting from specific date
    delete_date_handler = ConversationHandler(
        entry_points=[CommandHandler("delete_d", delete_expense_date)],
        states={
            DATE_INPUT: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_date_input)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
        allow_reentry=True,
    )
    
    # Conversation handler for editing from specific date
    edit_date_handler = ConversationHandler(
        entry_points=[CommandHandler("edit_d", edit_expense_date)],
        states={
            DATE_INPUT: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_date_input)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
        allow_reentry=True,
    )
    
    # Conversation handler for PDF export
    pdf_handler = ConversationHandler(
        entry_points=[CommandHandler("pdf", pdf_command)],
        states={
            PDF_PERIOD: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_pdf_period)],
            PDF_MONTH: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_pdf_month)],
            PDF_YEAR: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_pdf_year)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
        allow_reentry=True,
    )
    
    # Conversation handler for Summary
    summary_handler = ConversationHandler(
        entry_points=[CommandHandler("summary", summary_command)],
        states={
            SUMMARY_PERIOD: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_summary_period)],
            SUMMARY_MONTH: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_summary_month)],
            SUMMARY_YEAR: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_summary_year)],
            SUMMARY_DAY: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_summary_day)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
        allow_reentry=True,
    )
    
    application.add_handler(conv_handler)
    application.add_handler(view_date_handler)
    application.add_handler(delete_date_handler)
    application.add_handler(edit_date_handler)
    application.add_handler(pdf_handler)
    application.add_handler(summary_handler)
    application.add_handler(CommandHandler("view", view_expenses))
    application.add_handler(CommandHandler("month", view_month_expenses))
    application.add_handler(CommandHandler("expense", view_expenses_month))
    application.add_handler(CommandHandler("income", view_incomes_month))
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
    
    # Handle unknown commands
    async def unknown_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text(
            "Use /help to see all available commands."
        )
    
    # Help command handler
    application.add_handler(CommandHandler("help", help_command))
    
    # Unknown command handler - must be last
    application.add_handler(MessageHandler(filters.COMMAND, unknown_command))
    
    # Setup graceful shutdown
    def signal_handler(sig, frame):
        logger.info("Shutdown signal received, stopping bot...")
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Global error handlers
    def handle_exception(exc_type, exc_value, exc_traceback):
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return
        logger.critical("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))
        sys.exit(1)
    
    sys.excepthook = handle_exception
    
    # Start the bot
    logger.info("Bot starting...")
    
    try:
        application.run_polling(allowed_updates=Update.ALL_TYPES, drop_pending_updates=True)
    except Exception as e:
        logger.critical(f"FATAL: Bot crashed: {e}", exc_info=True)
        sys.exit(1)
    finally:
        logger.info("Bot stopped")


if __name__ == "__main__":
    main()