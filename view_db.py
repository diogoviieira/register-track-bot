"""View database contents"""
import sqlite3

conn = sqlite3.connect('finance_tracker.db')
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

print("\n📊 DATABASE CONTENTS")
print("=" * 50)

# Count totals
cursor.execute('SELECT COUNT(*) as count FROM expenses')
exp_count = cursor.fetchone()['count']
cursor.execute('SELECT COUNT(*) as count FROM incomes')
inc_count = cursor.fetchone()['count']

print(f'\nTotal Expenses: {exp_count}')
print(f'Total Incomes: {inc_count}')

# Show expenses
print('\n=== EXPENSES (Last 10) ===')
cursor.execute('SELECT * FROM expenses ORDER BY date DESC, time DESC LIMIT 10')
expenses = cursor.fetchall()
if expenses:
    for exp in expenses:
        print(f'  [{exp["date"]} {exp["time"]}] User:{exp["user_id"]}')
        print(f'    {exp["category"]} > {exp["subcategory"]} | €{exp["amount"]:.2f}')
        print(f'    "{exp["description"]}"')
        print()
else:
    print('  No expenses yet\n')

# Show incomes
print('=== INCOMES (Last 10) ===')
cursor.execute('SELECT * FROM incomes ORDER BY date DESC, time DESC LIMIT 10')
incomes = cursor.fetchall()
if incomes:
    for inc in incomes:
        print(f'  [{inc["date"]} {inc["time"]}] User:{inc["user_id"]}')
        print(f'    {inc["category"]} > {inc["subcategory"]} | €{inc["amount"]:.2f}')
        print(f'    "{inc["description"]}"')
        print()
else:
    print('  No incomes yet\n')

# Show users
print('=== UNIQUE USERS ===')
cursor.execute('SELECT DISTINCT user_id FROM expenses UNION SELECT DISTINCT user_id FROM incomes')
users = cursor.fetchall()
if users:
    for user in users:
        cursor.execute('SELECT COUNT(*) as count FROM expenses WHERE user_id = ?', (user['user_id'],))
        exp_c = cursor.fetchone()['count']
        cursor.execute('SELECT COUNT(*) as count FROM incomes WHERE user_id = ?', (user['user_id'],))
        inc_c = cursor.fetchone()['count']
        
        # Get latest activity
        cursor.execute('SELECT MAX(date) as last_date FROM expenses WHERE user_id = ?', (user['user_id'],))
        last_exp = cursor.fetchone()['last_date']
        
        print(f'  User {user["user_id"]}:')
        print(f'    - {exp_c} expenses, {inc_c} incomes')
        print(f'    - Last activity: {last_exp or "N/A"}')
        print()
else:
    print('  No users yet\n')

# Show monthly summary
print('=== MONTHLY SUMMARY (November 2025) ===')
cursor.execute('''
    SELECT category, subcategory, SUM(amount) as total, COUNT(*) as count
    FROM expenses
    WHERE date LIKE '2025-11%'
    GROUP BY category, subcategory
    ORDER BY total DESC
''')
monthly = cursor.fetchall()
if monthly:
    total_month = 0
    for row in monthly:
        total_month += row['total']
        print(f'  {row["category"]} > {row["subcategory"]}: €{row["total"]:.2f} ({row["count"]} entries)')
    print(f'\n  Total November Expenses: €{total_month:.2f}')
else:
    print('  No expenses in November yet')

conn.close()
print("\n" + "=" * 50)
