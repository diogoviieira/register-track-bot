"""Interactive SQLite Database Browser for finance_tracker.db"""
import sqlite3
import sys

DB_FILE = 'finance_tracker.db'

def show_help():
    """Display help menu"""
    print("\n" + "="*60)
    print("📊 FINANCE TRACKER DATABASE BROWSER")
    print("="*60)
    print("\nAvailable commands:")
    print("  1  - View all expenses")
    print("  2  - View all incomes")
    print("  3  - View by user ID")
    print("  4  - View monthly summary")
    print("  5  - View database schema")
    print("  6  - Count all records")
    print("  7  - Search expenses by category")
    print("  8  - View user statistics")
    print("  9  - Custom SQL query")
    print("  10 - Export to CSV")
    print("  h  - Show this help")
    print("  q  - Quit")
    print("="*60 + "\n")

def get_connection():
    """Get database connection"""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def view_expenses():
    """View all expenses"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM expenses ORDER BY date DESC, time DESC LIMIT 50')
    rows = cursor.fetchall()
    
    if not rows:
        print("No expenses found.")
        return
    
    print(f"\n{'='*80}")
    print(f"EXPENSES (Last 50)")
    print(f"{'='*80}")
    for row in rows:
        print(f"\nID: {row['id']} | User: {row['user_id']} | Date: {row['date']} {row['time']}")
        print(f"  {row['category']} > {row['subcategory']}")
        print(f"  Amount: €{row['amount']:.2f}")
        print(f"  Description: {row['description']}")
    print(f"{'='*80}\n")
    conn.close()

def view_incomes():
    """View all incomes"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM incomes ORDER BY date DESC, time DESC LIMIT 50')
    rows = cursor.fetchall()
    
    if not rows:
        print("No incomes found.")
        return
    
    print(f"\n{'='*80}")
    print(f"INCOMES (Last 50)")
    print(f"{'='*80}")
    for row in rows:
        print(f"\nID: {row['id']} | User: {row['user_id']} | Date: {row['date']} {row['time']}")
        print(f"  {row['category']} > {row['subcategory']}")
        print(f"  Amount: €{row['amount']:.2f}")
        print(f"  Description: {row['description']}")
    print(f"{'='*80}\n")
    conn.close()

def view_by_user():
    """View data for specific user"""
    user_id = input("Enter user ID: ").strip()
    if not user_id.isdigit():
        print("Invalid user ID")
        return
    
    user_id = int(user_id)
    conn = get_connection()
    cursor = conn.cursor()
    
    # Get expenses
    cursor.execute('SELECT * FROM expenses WHERE user_id = ? ORDER BY date DESC', (user_id,))
    expenses = cursor.fetchall()
    
    # Get incomes
    cursor.execute('SELECT * FROM incomes WHERE user_id = ? ORDER BY date DESC', (user_id,))
    incomes = cursor.fetchall()
    
    print(f"\n{'='*80}")
    print(f"USER {user_id} DATA")
    print(f"{'='*80}")
    
    print(f"\nEXPENSES ({len(expenses)}):")
    if expenses:
        for exp in expenses:
            print(f"  [{exp['date']}] {exp['category']} > {exp['subcategory']}: €{exp['amount']:.2f}")
    else:
        print("  No expenses")
    
    print(f"\nINCOMES ({len(incomes)}):")
    if incomes:
        for inc in incomes:
            print(f"  [{inc['date']}] {inc['category']} > {inc['subcategory']}: €{inc['amount']:.2f}")
    else:
        print("  No incomes")
    
    total_expenses = sum(row['amount'] for row in expenses)
    total_incomes = sum(row['amount'] for row in incomes)
    
    print(f"\nTOTALS:")
    print(f"  Expenses: €{total_expenses:.2f}")
    print(f"  Incomes: €{total_incomes:.2f}")
    print(f"  Balance: €{total_incomes - total_expenses:.2f}")
    print(f"{'='*80}\n")
    
    conn.close()

def monthly_summary():
    """Show monthly summary"""
    year_month = input("Enter year-month (YYYY-MM) or press Enter for current: ").strip()
    if not year_month:
        from datetime import datetime
        year_month = datetime.now().strftime("%Y-%m")
    
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT category, subcategory, SUM(amount) as total, COUNT(*) as count
        FROM expenses
        WHERE date LIKE ?
        GROUP BY category, subcategory
        ORDER BY total DESC
    ''', (f"{year_month}%",))
    
    rows = cursor.fetchall()
    
    print(f"\n{'='*80}")
    print(f"MONTHLY SUMMARY - {year_month}")
    print(f"{'='*80}")
    
    if rows:
        grand_total = 0
        for row in rows:
            print(f"{row['category']:15} > {row['subcategory']:20} €{row['total']:8.2f} ({row['count']} entries)")
            grand_total += row['total']
        print(f"{'-'*80}")
        print(f"{'TOTAL':37} €{grand_total:8.2f}")
    else:
        print("No expenses for this month")
    
    print(f"{'='*80}\n")
    conn.close()

def show_schema():
    """Show database schema"""
    conn = get_connection()
    cursor = conn.cursor()
    
    print(f"\n{'='*80}")
    print("DATABASE SCHEMA")
    print(f"{'='*80}")
    
    # Show expenses table
    cursor.execute("PRAGMA table_info(expenses)")
    print("\nEXPENSES TABLE:")
    for col in cursor.fetchall():
        print(f"  {col['name']:15} {col['type']:10} {'NOT NULL' if col['notnull'] else ''} {'PRIMARY KEY' if col['pk'] else ''}")
    
    # Show incomes table
    cursor.execute("PRAGMA table_info(incomes)")
    print("\nINCOMES TABLE:")
    for col in cursor.fetchall():
        print(f"  {col['name']:15} {col['type']:10} {'NOT NULL' if col['notnull'] else ''} {'PRIMARY KEY' if col['pk'] else ''}")
    
    # Show indexes
    cursor.execute("SELECT name, sql FROM sqlite_master WHERE type='index' AND sql IS NOT NULL")
    indexes = cursor.fetchall()
    if indexes:
        print("\nINDEXES:")
        for idx in indexes:
            print(f"  {idx['name']}")
    
    print(f"{'='*80}\n")
    conn.close()

def count_records():
    """Count all records"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT COUNT(*) as count FROM expenses')
    exp_count = cursor.fetchone()['count']
    
    cursor.execute('SELECT COUNT(*) as count FROM incomes')
    inc_count = cursor.fetchone()['count']
    
    cursor.execute('SELECT COUNT(DISTINCT user_id) as count FROM (SELECT user_id FROM expenses UNION SELECT user_id FROM incomes)')
    user_count = cursor.fetchone()['count']
    
    print(f"\n{'='*60}")
    print("RECORD COUNTS")
    print(f"{'='*60}")
    print(f"  Expenses: {exp_count}")
    print(f"  Incomes:  {inc_count}")
    print(f"  Users:    {user_count}")
    print(f"{'='*60}\n")
    
    conn.close()

def search_category():
    """Search expenses by category"""
    category = input("Enter category name (or part of it): ").strip()
    
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM expenses 
        WHERE category LIKE ? OR subcategory LIKE ?
        ORDER BY date DESC
    ''', (f'%{category}%', f'%{category}%'))
    
    rows = cursor.fetchall()
    
    print(f"\n{'='*80}")
    print(f"SEARCH RESULTS - '{category}'")
    print(f"{'='*80}")
    
    if rows:
        for row in rows:
            print(f"[{row['date']}] User:{row['user_id']} | {row['category']} > {row['subcategory']}: €{row['amount']:.2f}")
    else:
        print("No results found")
    
    print(f"{'='*80}\n")
    conn.close()

def user_stats():
    """Show user statistics"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT DISTINCT user_id FROM expenses 
        UNION 
        SELECT DISTINCT user_id FROM incomes
    ''')
    users = cursor.fetchall()
    
    print(f"\n{'='*80}")
    print("USER STATISTICS")
    print(f"{'='*80}")
    
    for user in users:
        uid = user['user_id']
        
        cursor.execute('SELECT COUNT(*) as count, SUM(amount) as total FROM expenses WHERE user_id = ?', (uid,))
        exp_data = cursor.fetchone()
        
        cursor.execute('SELECT COUNT(*) as count, SUM(amount) as total FROM incomes WHERE user_id = ?', (uid,))
        inc_data = cursor.fetchone()
        
        cursor.execute('SELECT MIN(date) as first, MAX(date) as last FROM expenses WHERE user_id = ?', (uid,))
        dates = cursor.fetchone()
        
        print(f"\nUser ID: {uid}")
        print(f"  Expenses: {exp_data['count']} entries, €{exp_data['total'] or 0:.2f} total")
        print(f"  Incomes:  {inc_data['count']} entries, €{inc_data['total'] or 0:.2f} total")
        print(f"  Active:   {dates['first']} to {dates['last']}")
    
    print(f"{'='*80}\n")
    conn.close()

def custom_query():
    """Execute custom SQL query"""
    print("\nEnter SQL query (or 'cancel' to abort):")
    query = input("SQL> ").strip()
    
    if query.lower() == 'cancel':
        return
    
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(query)
        
        if query.lower().startswith('select'):
            rows = cursor.fetchall()
            if rows:
                # Print column names
                print("\n" + " | ".join(rows[0].keys()))
                print("-" * 80)
                # Print rows
                for row in rows:
                    print(" | ".join(str(val) for val in row))
            else:
                print("No results")
        else:
            conn.commit()
            print(f"Query executed. Rows affected: {cursor.rowcount}")
        
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

def export_csv():
    """Export data to CSV"""
    import csv
    from datetime import datetime
    
    print("\nExport options:")
    print("1. All expenses")
    print("2. All incomes")
    print("3. Both")
    
    choice = input("Choice (1-3): ").strip()
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    conn = get_connection()
    cursor = conn.cursor()
    
    if choice in ['1', '3']:
        cursor.execute('SELECT * FROM expenses ORDER BY date DESC, time DESC')
        expenses = cursor.fetchall()
        
        filename = f'expenses_{timestamp}.csv'
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['ID', 'User ID', 'Date', 'Time', 'Category', 'Subcategory', 'Amount', 'Description'])
            for row in expenses:
                writer.writerow([row['id'], row['user_id'], row['date'], row['time'], 
                               row['category'], row['subcategory'], row['amount'], row['description']])
        print(f"✅ Exported {len(expenses)} expenses to {filename}")
    
    if choice in ['2', '3']:
        cursor.execute('SELECT * FROM incomes ORDER BY date DESC, time DESC')
        incomes = cursor.fetchall()
        
        filename = f'incomes_{timestamp}.csv'
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['ID', 'User ID', 'Date', 'Time', 'Category', 'Subcategory', 'Amount', 'Description'])
            for row in incomes:
                writer.writerow([row['id'], row['user_id'], row['date'], row['time'], 
                               row['category'], row['subcategory'], row['amount'], row['description']])
        print(f"✅ Exported {len(incomes)} incomes to {filename}")
    
    conn.close()

def main():
    """Main interactive loop"""
    show_help()
    
    while True:
        try:
            cmd = input("Command> ").strip().lower()
            
            if cmd == 'q' or cmd == 'quit':
                print("Goodbye! 👋")
                break
            elif cmd == 'h' or cmd == 'help':
                show_help()
            elif cmd == '1':
                view_expenses()
            elif cmd == '2':
                view_incomes()
            elif cmd == '3':
                view_by_user()
            elif cmd == '4':
                monthly_summary()
            elif cmd == '5':
                show_schema()
            elif cmd == '6':
                count_records()
            elif cmd == '7':
                search_category()
            elif cmd == '8':
                user_stats()
            elif cmd == '9':
                custom_query()
            elif cmd == '10':
                export_csv()
            else:
                print(f"Unknown command: {cmd}. Type 'h' for help.")
        
        except KeyboardInterrupt:
            print("\nUse 'q' to quit.")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == '__main__':
    main()
