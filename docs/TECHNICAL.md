# 📝 Technical Notes

## Architecture Overview

### Database Migration (Excel → SQLite)

This bot was migrated from Excel-based storage to SQLite for improved reliability and performance.

#### Why SQLite?

| Benefit | Description |
|---------|-------------|
| **ACID Compliance** | Guaranteed data integrity with automatic transactions |
| **Concurrent Access** | Multiple users can read simultaneously |
| **Performance** | Indexed queries, no file parsing overhead |
| **Reliability** | Journal-based recovery from crashes |
| **Portability** | Single file, no external database server |

#### Schema Design

```sql
CREATE TABLE expenses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    date TEXT NOT NULL,
    time TEXT NOT NULL,
    category TEXT NOT NULL,
    subcategory TEXT NOT NULL,
    amount REAL NOT NULL,
    description TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_expenses_user_date ON expenses(user_id, date);
CREATE INDEX idx_incomes_user_date ON incomes(user_id, date);
```

#### Multi-User Isolation

Every query includes `WHERE user_id = ?` to ensure complete data separation:

```python
# All queries filter by user_id
cursor.execute("""
    SELECT * FROM expenses 
    WHERE user_id = ? AND date = ?
    ORDER BY time DESC
""", (user_id, date))
```

**Security**: Users cannot access or modify other users' data. Verified with comprehensive test suite.

## Code Structure

### Entry Point

`run_bot.py` - Launches the bot with proper Python path configuration

```python
# Adds src/ to path and imports bot.py
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
from bot import main
```

### Main Bot Logic

`src/bot.py` - Contains all bot logic (~1200 lines)

- **Conversation handlers** - Manage multi-step interactions
- **Database layer** - Thread-safe connections with context managers
- **Command handlers** - Process user commands
- **State management** - Track conversation states

### Utilities

- `utils/db_browser.py` - Interactive 10-command database browser
- `utils/view_db.py` - Quick database statistics viewer
- `utils/cleanup_db.py` - Safe data cleanup with confirmations

### Tests

- `tests/test_multiuser.py` - Verifies user data isolation
- `tests/test_bot_features.py` - Feature integration tests

## Performance Characteristics

### Memory Usage

- **Idle**: ~20-30 MB RAM
- **Active**: ~40-50 MB RAM (during conversations)
- **Database**: Thread-local connections (1 per thread)

### Database Growth

Typical usage (1 user, 10 expenses/day):
- **Monthly**: ~100 KB
- **Yearly**: ~1-5 MB
- **10 years**: ~10-50 MB

### Response Times

| Operation | Time |
|-----------|------|
| Simple command | <100ms |
| Database query | <50ms |
| Monthly summary | <200ms |
| Category aggregation | <150ms |

## Deployment Architecture

```
┌─────────────────────┐
│   Telegram API      │
│  (Cloud Service)    │
└──────────┬──────────┘
           │
           │ HTTPS
           │
┌──────────▼──────────┐
│   Raspberry Pi      │
│  ┌──────────────┐   │
│  │ Systemd      │   │
│  │ Service      │   │
│  │  ├─ Bot      │   │
│  │  └─ SQLite   │   │
│  └──────────────┘   │
│  ┌──────────────┐   │
│  │ Filesystem   │   │
│  │  data/       │   │
│  │  ├─ DB       │   │
│  │  └─ Backups  │   │
│  └──────────────┘   │
└─────────────────────┘
```

## Thread Safety

### Database Connections

```python
# Thread-local storage ensures each thread has its own connection
thread_local = threading.local()

@contextmanager
def get_db_connection():
    if not hasattr(thread_local, 'connection'):
        thread_local.connection = sqlite3.connect(DB_FILE)
        thread_local.connection.row_factory = sqlite3.Row
    
    try:
        yield thread_local.connection
        thread_local.connection.commit()
    except Exception as e:
        thread_local.connection.rollback()
        raise
```

### Conversation States

Telegram's `ConversationHandler` manages state per user automatically.

## Future Considerations

### Scalability

Current design supports:
- **Users**: Hundreds (limited by Raspberry Pi resources)
- **Entries**: Millions (SQLite can handle >1TB databases)
- **Queries**: Concurrent reads, sequential writes

### Extensibility

Easy to add:
- New commands (add handler)
- New categories (update dictionaries)
- New tables (migrations)
- Export formats (utilities)
- Web interface (Flask/FastAPI)

### Migration Path

If outgrowing SQLite:
1. Export to CSV
2. Import to PostgreSQL/MySQL
3. Update connection logic
4. Deploy on cloud service

## Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| python-telegram-bot | 22.5 | Telegram Bot API wrapper |
| sqlite3 | built-in | Database engine |

Minimal dependencies = easier maintenance and deployment.

## License

MIT License - See [LICENSE](../LICENSE) file.

---

**Technical questions?** Open an [issue](https://github.com/diogoviieira/register-track-bot/issues) or [discussion](https://github.com/diogoviieira/register-track-bot/discussions).
