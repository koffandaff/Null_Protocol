# ❓ Database Viva Questions

Common interview and viva questions related to database design and SQLAlchemy.

---

## Table of Contents

- [Basic Database Concepts](#basic-database-concepts)
- [SQLite Questions](#sqlite-questions)
- [SQLAlchemy Questions](#sqlalchemy-questions)
- [Schema Design Questions](#schema-design-questions)
- [Performance Questions](#performance-questions)

---

## Basic Database Concepts

### Q1: What is a relational database?
**Answer**: A relational database organizes data into tables (relations) with rows (records) and columns (attributes). Tables can be related through foreign keys. Examples: SQLite, PostgreSQL, MySQL.

### Q2: What is the difference between SQL and NoSQL?
**Answer**:
| SQL | NoSQL |
|-----|-------|
| Structured schema | Flexible schema |
| Tables with rows | Documents, key-value, graphs |
| ACID compliant | Eventually consistent |
| Vertical scaling | Horizontal scaling |
| Example: PostgreSQL | Example: MongoDB |

### Q3: What is normalization?
**Answer**: Normalization is the process of organizing data to reduce redundancy:
- **1NF**: Atomic values, no repeating groups
- **2NF**: 1NF + no partial dependencies
- **3NF**: 2NF + no transitive dependencies

### Q4: What is a primary key?
**Answer**: A primary key is a column (or combination) that uniquely identifies each row. In Fsociety, we use UUID strings as primary keys for security and portability.

### Q5: What is a foreign key?
**Answer**: A foreign key is a column that references the primary key of another table, establishing a relationship between tables.

```sql
-- Example: network_scans.user_id references users.id
user_id Column(String(36), ForeignKey("users.id"))
```

### Q6: What is an index?
**Answer**: An index is a data structure that speeds up queries on indexed columns. Like a book's index, it allows quick lookups without scanning all rows.

```sql
-- Creating an index
CREATE INDEX idx_users_email ON users(email);
```

---

## SQLite Questions

### Q7: Why did you choose SQLite for this project?
**Answer**:
1. **Zero configuration**: No server setup required
2. **Portable**: Single file database
3. **Perfect for development**: Quick prototyping
4. **Sufficient for single-user**: No concurrent write bottlenecks
5. **Easy migration**: Can switch to PostgreSQL via SQLAlchemy

### Q8: What are SQLite's limitations?
**Answer**:
- No concurrent writes (file-level locking)
- Limited to 281 TB database size
- No user management/permissions
- Limited data types (everything is TEXT internally)

### Q9: How do you enable foreign keys in SQLite?
**Answer**: Foreign keys are disabled by default in SQLite. Enable with:
```sql
PRAGMA foreign_keys = ON;
```
In Fsociety, we do this automatically on every connection using SQLAlchemy events.

### Q10: How do you backup SQLite?
**Answer**:
```bash
# Simple file copy (while not writing)
cp fsociety.db backup.db

# Using SQLite backup
sqlite3 fsociety.db ".backup backup.db"
```

---

## SQLAlchemy Questions

### Q11: What is an ORM?
**Answer**: ORM (Object-Relational Mapping) maps database tables to Python classes and rows to objects. Benefits:
- Write Python, not SQL
- Database-agnostic code
- Automatic SQL injection prevention
- Easier relationship handling

### Q12: What is the difference between Session and Engine?
**Answer**:
- **Engine**: Low-level database connection, manages connection pool
- **Session**: High-level interface for queries, handles transactions

### Q13: How does SQLAlchemy prevent SQL injection?
**Answer**: SQLAlchemy uses parameterized queries:
```python
# Safe (parameterized)
db.query(User).filter(User.email == email).first()

# Generates: SELECT * FROM users WHERE email = ?
# The email value is never interpolated into SQL string
```

### Q14: What is `relationship()` in SQLAlchemy?
**Answer**: `relationship()` defines how two models are related and enables easy navigation:
```python
# In User model
activities = relationship("ActivityLog", back_populates="user")

# Usage
user.activities  # Returns all activity logs for this user
```

### Q15: What is `cascade="all, delete-orphan"`?
**Answer**: Cascade rules define what happens to related records:
- **all**: Propagate save/update to children
- **delete-orphan**: Delete children when parent is deleted

### Q16: What is lazy loading vs eager loading?
**Answer**:
```python
# Lazy (default): Related data loaded when accessed
user = db.query(User).first()
user.activities  # SQL executed here

# Eager: Related data loaded in same query
from sqlalchemy.orm import joinedload
user = db.query(User).options(joinedload(User.activities)).first()
```

---

## Schema Design Questions

### Q17: Why use UUIDs instead of auto-increment integers?
**Answer**:
1. **Security**: IDs are not guessable
2. **Distributed**: Can generate without database
3. **Unique across systems**: No ID collisions on merge
4. **No enumeration attacks**: Can't guess user count

### Q18: Why store refresh_token in the users table?
**Answer**: Design decision for simplicity:
- One active refresh token per user
- Reduces joins on every /refresh call
- Alternative: Separate table for multi-device support

### Q19: Why use JSON columns for scan results?
**Answer**:
- Scan results have variable structure
- No schema changes for new result fields
- Easy serialization/deserialization
- SQLite stores as TEXT anyway

### Q20: How would you scale this database for millions of users?
**Answer**:
1. Migrate to PostgreSQL
2. Add read replicas
3. Partition activity_logs by date
4. Add Redis for caching
5. Use connection pooling
6. Add indexes on query patterns

---

## Performance Questions

### Q21: How do you optimize a slow query?
**Answer**:
1. Add indexes on filtered/sorted columns
2. Use EXPLAIN to analyze query plan
3. Paginate results (LIMIT/OFFSET)
4. Eager load related data if needed
5. Cache frequently accessed data

### Q22: What is N+1 query problem?
**Answer**: When you load N records and then make N additional queries for related data:
```python
# Problem (N+1 queries)
users = db.query(User).all()
for user in users:
    print(user.activities)  # Query for each user!

# Solution (1 query)
users = db.query(User).options(joinedload(User.activities)).all()
```

### Q23: When would you denormalize data?
**Answer**: When read performance is critical:
- Analytics/dashboards with aggregations
- Caching computed values (e.g., total_scans in user_stats)
- Trade-off: More storage, potential data inconsistency

### Q24: What is database connection pooling?
**Answer**: Reusing database connections instead of creating new ones for each request. Benefits:
- Faster connection time
- Limited concurrent connections
- Resource management

```python
engine = create_engine(url, pool_size=10, max_overflow=20)
```

---

## Related Documentation

- [Database Schema](./schema.md)
- [SQLAlchemy ORM](./sqlalchemy.md)
- [Commands](./commands.md)
