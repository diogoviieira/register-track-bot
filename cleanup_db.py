"""Safe database cleanup utility"""
import sqlite3

DB_FILE = 'finance_tracker.db'

def get_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def show_users():
    """Show all users in database"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT DISTINCT user_id FROM expenses 
        UNION 
        SELECT DISTINCT user_id FROM incomes
        ORDER BY user_id
    ''')
    
    users = cursor.fetchall()
    
    print("\n📊 Users in database:")
    print("="*60)
    for user in users:
        uid = user['user_id']
        cursor.execute('SELECT COUNT(*) as count FROM expenses WHERE user_id = ?', (uid,))
        exp_count = cursor.fetchone()['count']
        cursor.execute('SELECT COUNT(*) as count FROM incomes WHERE user_id = ?', (uid,))
        inc_count = cursor.fetchone()['count']
        
        print(f"User {uid}: {exp_count} expenses, {inc_count} incomes")
    print("="*60)
    
    conn.close()
    return [user['user_id'] for user in users]

def delete_test_users():
    """Delete test users (12345, 67890)"""
    print("\n🗑️  Deleting test users (12345, 67890)...")
    
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('DELETE FROM expenses WHERE user_id IN (12345, 67890)')
    exp_deleted = cursor.rowcount
    
    cursor.execute('DELETE FROM incomes WHERE user_id IN (12345, 67890)')
    inc_deleted = cursor.rowcount
    
    conn.commit()
    conn.close()
    
    print(f"✅ Deleted {exp_deleted} expenses and {inc_deleted} incomes")

def delete_specific_user():
    """Delete specific user"""
    users = show_users()
    
    user_id = input("\nEnter user ID to delete (or 'cancel'): ").strip()
    
    if user_id.lower() == 'cancel':
        print("Cancelled")
        return
    
    if not user_id.isdigit():
        print("❌ Invalid user ID")
        return
    
    user_id = int(user_id)
    
    if user_id not in users:
        print(f"❌ User {user_id} not found")
        return
    
    confirm = input(f"⚠️  Delete ALL data for user {user_id}? (yes/no): ").strip().lower()
    
    if confirm != 'yes':
        print("Cancelled")
        return
    
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('DELETE FROM expenses WHERE user_id = ?', (user_id,))
    exp_deleted = cursor.rowcount
    
    cursor.execute('DELETE FROM incomes WHERE user_id = ?', (user_id,))
    inc_deleted = cursor.rowcount
    
    conn.commit()
    conn.close()
    
    print(f"✅ Deleted {exp_deleted} expenses and {inc_deleted} incomes for user {user_id}")

def delete_all_data():
    """Delete all data (keep tables)"""
    print("\n⚠️  WARNING: This will delete ALL expenses and incomes!")
    print("The tables will remain, but all data will be lost.")
    
    confirm = input("Type 'DELETE ALL' to confirm: ").strip()
    
    if confirm != 'DELETE ALL':
        print("Cancelled")
        return
    
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('DELETE FROM expenses')
    exp_deleted = cursor.rowcount
    
    cursor.execute('DELETE FROM incomes')
    inc_deleted = cursor.rowcount
    
    conn.commit()
    conn.close()
    
    print(f"✅ Deleted {exp_deleted} expenses and {inc_deleted} incomes")
    print("Tables are intact and bot will work normally")

def delete_by_date():
    """Delete entries before a specific date"""
    date = input("\nDelete entries before date (YYYY-MM-DD): ").strip()
    
    # Simple validation
    if len(date) != 10 or date[4] != '-' or date[7] != '-':
        print("❌ Invalid date format. Use YYYY-MM-DD")
        return
    
    conn = get_connection()
    cursor = conn.cursor()
    
    # Preview what will be deleted
    cursor.execute('SELECT COUNT(*) as count FROM expenses WHERE date < ?', (date,))
    exp_count = cursor.fetchone()['count']
    
    cursor.execute('SELECT COUNT(*) as count FROM incomes WHERE date < ?', (date,))
    inc_count = cursor.fetchone()['count']
    
    print(f"\n📊 Will delete:")
    print(f"  {exp_count} expenses")
    print(f"  {inc_count} incomes")
    
    confirm = input(f"\nConfirm deletion? (yes/no): ").strip().lower()
    
    if confirm != 'yes':
        print("Cancelled")
        conn.close()
        return
    
    cursor.execute('DELETE FROM expenses WHERE date < ?', (date,))
    cursor.execute('DELETE FROM incomes WHERE date < ?', (date,))
    
    conn.commit()
    conn.close()
    
    print("✅ Deleted successfully")

def vacuum_database():
    """Optimize database (reclaim space)"""
    print("\n🔧 Running VACUUM to optimize database...")
    
    import os
    before_size = os.path.getsize(DB_FILE)
    
    conn = get_connection()
    conn.execute('VACUUM')
    conn.close()
    
    after_size = os.path.getsize(DB_FILE)
    saved = before_size - after_size
    
    print(f"✅ Database optimized!")
    print(f"  Before: {before_size:,} bytes")
    print(f"  After:  {after_size:,} bytes")
    print(f"  Saved:  {saved:,} bytes")

def main():
    """Main menu"""
    while True:
        print("\n" + "="*60)
        print("🗑️  DATABASE CLEANUP UTILITY")
        print("="*60)
        print("\n1. Show all users")
        print("2. Delete test users (12345, 67890)")
        print("3. Delete specific user")
        print("4. Delete entries before date")
        print("5. Delete ALL data (keep tables)")
        print("6. Optimize database (VACUUM)")
        print("q. Quit")
        print("\n⚠️  Always backup database before cleanup!")
        
        choice = input("\nChoice> ").strip().lower()
        
        try:
            if choice == 'q':
                print("Goodbye! 👋")
                break
            elif choice == '1':
                show_users()
            elif choice == '2':
                delete_test_users()
            elif choice == '3':
                delete_specific_user()
            elif choice == '4':
                delete_by_date()
            elif choice == '5':
                delete_all_data()
            elif choice == '6':
                vacuum_database()
            else:
                print(f"Unknown option: {choice}")
        
        except KeyboardInterrupt:
            print("\n\nUse 'q' to quit")
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == '__main__':
    main()
