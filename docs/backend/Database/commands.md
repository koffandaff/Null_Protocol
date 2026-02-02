# 🖥️ Database Commands

This document provides SQLite and SQLAlchemy commands for database inspection and management.

---

## Table of Contents

- [SQLite CLI Commands](#sqlite-cli-commands)
- [SQLAlchemy Commands](#sqlalchemy-commands)
- [Common Queries](#common-queries)
- [Maintenance Commands](#maintenance-commands)

---

## SQLite CLI Commands

### Opening the Database

```bash
# Windows
cd backend/data
sqlite3 fsociety.db

# Or specify full path
sqlite3 e:\Fsociety\backend\data\fsociety.db
```

### Basic SQLite Commands

```sql
-- Show all tables
.tables

-- Show table schema
.schema users
.schema network_scans

-- Show all schemas
.schema

-- Enable column headers in output
.headers on
.mode column

-- Exit SQLite
.quit
-- or
.exit
```

### Viewing Data

```sql
-- Count records
SELECT COUNT(*) FROM users;
SELECT COUNT(*) FROM activity_logs;

-- View all users (limited)
SELECT id, email, username, role, is_active FROM users LIMIT 10;

-- View recent activity
SELECT action, timestamp FROM activity_logs ORDER BY timestamp DESC LIMIT 20;

-- View table info (columns)
PRAGMA table_info(users);

-- View indexes
PRAGMA index_list(users);

-- View foreign keys
PRAGMA foreign_keys;
PRAGMA foreign_key_list(network_scans);
```

---

## SQLAlchemy Commands

### Python Shell Access

```bash
cd backend
python

>>> from database.engine import SessionLocal
>>> from database.models import User, ActivityLog, NetworkScan
>>> db = SessionLocal()
```

### Query Examples

```python
# Count all users
>>> db.query(User).count()
152

# Get all admins
>>> admins = db.query(User).filter(User.role == 'admin').all()
>>> for a in admins: print(a.email)
admin@fsociety.com
dhruvil@fsociety.com

# Find user by email
>>> user = db.query(User).filter(User.email == 'test@test.com').first()
>>> print(user.id if user else 'Not found')

# Get recent scans
>>> scans = db.query(NetworkScan).order_by(NetworkScan.started_at.desc()).limit(5).all()
>>> for s in scans: print(s.target, s.status)

# Close session when done
>>> db.close()
```

### Initialization Commands

```python
# Initialize database (creates tables)
from database.engine import init_db
init_db()

# Drop all tables (DANGER!)
from database.engine import drop_all_tables
drop_all_tables()

# Seed with initial data
from database.engine import get_db_context
from database.seed import seed_database

with get_db_context() as db:
    seed_database(db)
```

---

## Common Queries

### User Statistics

```sql
-- Users by role
SELECT role, COUNT(*) as count FROM users GROUP BY role;

-- Active vs Inactive users
SELECT is_active, COUNT(*) FROM users GROUP BY is_active;

-- Users registered per day (last 7 days)
SELECT DATE(created_at) as day, COUNT(*) 
FROM users 
WHERE created_at >= DATE('now', '-7 days')
GROUP BY DATE(created_at);

-- Most recent registrations
SELECT email, username, created_at 
FROM users 
ORDER BY created_at DESC 
LIMIT 10;
```

### Activity Analysis

```sql
-- Most common actions
SELECT action, COUNT(*) as count 
FROM activity_logs 
GROUP BY action 
ORDER BY count DESC;

-- Activity by user
SELECT u.email, COUNT(a.id) as actions
FROM users u
LEFT JOIN activity_logs a ON u.id = a.user_id
GROUP BY u.id
ORDER BY actions DESC
LIMIT 10;

-- Activity by hour today
SELECT strftime('%H', timestamp) as hour, COUNT(*)
FROM activity_logs
WHERE DATE(timestamp) = DATE('now')
GROUP BY hour;
```

### Scan Statistics

```sql
-- Scans by type
SELECT scan_type, COUNT(*) FROM network_scans GROUP BY scan_type;

-- Success rate
SELECT status, COUNT(*) FROM network_scans GROUP BY status;

-- Average scan duration
SELECT AVG(duration_ms) as avg_duration_ms FROM network_scans WHERE status = 'completed';

-- Top scanned targets
SELECT target, COUNT(*) as scans
FROM network_scans
GROUP BY target
ORDER BY scans DESC
LIMIT 10;
```

---

## Maintenance Commands

### Database Backup

```bash
# SQLite backup (CLI)
sqlite3 backend/data/fsociety.db ".backup backup_$(date +%Y%m%d).db"

# Windows PowerShell
Copy-Item backend/data/fsociety.db "backup_$(Get-Date -Format 'yyyyMMdd').db"
```

### Database Optimization

```sql
-- Analyze tables for query optimization
ANALYZE;

-- Vacuum to reclaim space
VACUUM;

-- Rebuild indexes
REINDEX;
```

### Checking Database Integrity

```sql
-- Check for corruption
PRAGMA integrity_check;

-- Check foreign key constraints
PRAGMA foreign_key_check;
```

### Clearing Old Data

```sql
-- Delete old activity logs (older than 30 days)
DELETE FROM activity_logs 
WHERE timestamp < DATE('now', '-30 days');

-- Delete completed scans older than 7 days
DELETE FROM network_scans 
WHERE status = 'completed' 
AND completed_at < DATE('now', '-7 days');
```

---

## Useful One-Liners

```bash
# Quick table count (Windows PowerShell)
sqlite3 backend/data/fsociety.db "SELECT 'users: ' || COUNT(*) FROM users"

# Export users to CSV
sqlite3 -header -csv backend/data/fsociety.db "SELECT * FROM users" > users.csv

# View database size
sqlite3 backend/data/fsociety.db "SELECT page_count * page_size as size FROM pragma_page_count(), pragma_page_size()"
```

---

## Related Documentation

- [Database Schema](./schema.md)
- [SQLAlchemy ORM](./sqlalchemy.md)
- [Viva Questions](./viva_questions.md)
