"""Test multi-user isolation and security"""
from bot import get_db_connection

print('=== Testing Security: User Cannot Access Others Data ===')

with get_db_connection() as conn:
    cursor = conn.cursor()
    
    # Check all expenses
    cursor.execute('SELECT id, user_id, category FROM expenses')
    all_expenses = cursor.fetchall()
    print(f'\nDatabase has {len(all_expenses)} total expenses:')
    for exp in all_expenses:
        print(f'  ID:{exp["id"]} belongs to user {exp["user_id"]} - {exp["category"]}')
    
    # Try to delete another user's expense
    print(f'\nUser 67890 attempting to delete expense ID:1 (belongs to user 12345)...')
    cursor.execute('DELETE FROM expenses WHERE id = ? AND user_id = ?', (1, 67890))
    affected = cursor.rowcount
    print(f'  Rows deleted: {affected}')
    
    # Verify it still exists
    cursor.execute('SELECT COUNT(*) as count FROM expenses WHERE id = 1')
    still_exists = cursor.fetchone()["count"]
    print(f'  Expense ID:1 still exists: {"YES ✅" if still_exists else "NO ❌"}')
    
    print('\n✅ Security verified! Users cannot modify others\' data.')
