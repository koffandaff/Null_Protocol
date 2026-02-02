# 🐍 SQLAlchemy ORM

This document explains how we use SQLAlchemy for database operations in Fsociety.

---

## Table of Contents

- [What is SQLAlchemy?](#what-is-sqlalchemy)
- [Setup](#setup)
- [Models](#models)
- [CRUD Operations](#crud-operations)
- [Relationships](#relationships)
- [Session Management](#session-management)
- [Code Examples](#code-examples)

---

## What is SQLAlchemy?

**SQLAlchemy** is Python's most popular ORM (Object-Relational Mapper). It allows you to:

- Define database tables as Python classes
- Perform CRUD operations without writing raw SQL
- Handle relationships between tables automatically
- Write database-agnostic code

### Why SQLAlchemy?

| Feature | Benefit |
|---------|---------|
| **ORM** | Write Python, not SQL |
| **Migrations** | Schema versioning with Alembic |
| **Security** | Prevents SQL injection |
| **Portability** | Switch databases easily |

---

## Setup

### Engine Configuration

```python
# database/engine.py

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Database URL (easily swappable)
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./data/fsociety.db")

# Create engine
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},  # Required for SQLite + FastAPI
        echo=False  # Set True for SQL debugging
    )
else:
    engine = create_engine(
        DATABASE_URL,
        pool_size=10,
        max_overflow=20,
        pool_pre_ping=True
    )

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()
```

### Enable Foreign Keys (SQLite)

```python
# SQLite has foreign keys disabled by default
from sqlalchemy import event

@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()
```

---

## Models

### Defining a Model

```python
# database/models.py

from sqlalchemy import Column, String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from database.engine import Base
import uuid
from datetime import datetime

def generate_uuid():
    return str(uuid.uuid4())

class User(Base):
    __tablename__ = "users"
    
    # Primary Key
    id = Column(String(36), primary_key=True, default=generate_uuid)
    
    # Unique Constraints
    email = Column(String(255), unique=True, nullable=False, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    
    # Regular Columns
    password_hash = Column(Text, nullable=False)
    role = Column(String(20), default="user")
    is_active = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)
    
    # Relationships
    activities = relationship("ActivityLog", back_populates="user", cascade="all, delete-orphan")
```

### Column Types

| SQLAlchemy | SQLite | PostgreSQL | Usage |
|------------|--------|------------|-------|
| `String(n)` | TEXT | VARCHAR(n) | Fixed-length text |
| `Text` | TEXT | TEXT | Unlimited text |
| `Integer` | INTEGER | INTEGER | Numbers |
| `Boolean` | INTEGER | BOOLEAN | True/False |
| `DateTime` | TEXT | TIMESTAMP | Dates/times |
| `JSON` | TEXT | JSONB | Structured data |
| `Float` | REAL | DOUBLE | Decimals |

---

## CRUD Operations

### CREATE - Insert New Record

```python
# database/repositories/user_repository.py

def create(self, user_data: dict) -> User:
    """Create a new user"""
    user = User(
        email=user_data['email'],
        username=user_data['username'],
        password_hash=user_data['password_hash'],
        full_name=user_data.get('full_name'),
        role=user_data.get('role', 'user'),
        is_active=True
    )
    
    self.db.add(user)       # Stage for insert
    self.db.commit()        # Execute insert
    self.db.refresh(user)   # Reload from DB (get generated ID)
    
    return user
```

### READ - Query Records

```python
# Get by ID
def get_by_id(self, user_id: str) -> Optional[User]:
    return self.db.query(User).filter(User.id == user_id).first()

# Get by unique field
def get_by_email(self, email: str) -> Optional[User]:
    return self.db.query(User).filter(User.email == email).first()

# Get all with pagination
def get_all(self, limit: int = 100, offset: int = 0) -> List[User]:
    return self.db.query(User).offset(offset).limit(limit).all()

# Get with filters
def get_active_admins(self) -> List[User]:
    return self.db.query(User).filter(
        User.role == 'admin',
        User.is_active == True
    ).all()

# Search with LIKE
def search(self, query: str) -> List[User]:
    search_term = f"%{query}%"
    return self.db.query(User).filter(
        (User.username.ilike(search_term)) |
        (User.email.ilike(search_term))
    ).all()
```

### UPDATE - Modify Records

```python
def update(self, user_id: str, update_data: dict) -> Optional[User]:
    """Update user fields"""
    user = self.get_by_id(user_id)
    if not user:
        return None
    
    # Update only provided fields
    for key, value in update_data.items():
        if hasattr(user, key):
            setattr(user, key, value)
    
    self.db.commit()
    self.db.refresh(user)
    return user

# Alternative: Bulk update
def disable_many(self, user_ids: List[str]) -> int:
    result = self.db.query(User).filter(
        User.id.in_(user_ids)
    ).update({'is_active': False}, synchronize_session='fetch')
    
    self.db.commit()
    return result  # Number of rows updated
```

### DELETE - Remove Records

```python
def delete(self, user_id: str) -> bool:
    """Delete a user (cascades to related tables)"""
    user = self.get_by_id(user_id)
    if not user:
        return False
    
    self.db.delete(user)
    self.db.commit()
    return True

# Bulk delete
def delete_inactive(self) -> int:
    result = self.db.query(User).filter(
        User.is_active == False
    ).delete(synchronize_session='fetch')
    
    self.db.commit()
    return result
```

---

## Relationships

### One-to-One

```python
# User has one UserStats
class User(Base):
    stats = relationship("UserStats", back_populates="user", uselist=False)

class UserStats(Base):
    user_id = Column(String(36), ForeignKey("users.id"), primary_key=True)
    user = relationship("User", back_populates="stats")
```

### One-to-Many

```python
# User has many ActivityLogs
class User(Base):
    activities = relationship("ActivityLog", back_populates="user", cascade="all, delete-orphan")

class ActivityLog(Base):
    user_id = Column(String(36), ForeignKey("users.id"))
    user = relationship("User", back_populates="activities")
```

### Accessing Related Data

```python
# Get user with all their scans
user = db.query(User).filter(User.id == user_id).first()

# Access related records (lazy loaded)
for scan in user.network_scans:
    print(scan.target, scan.status)

# Eager loading (single query)
from sqlalchemy.orm import joinedload

user = db.query(User).options(
    joinedload(User.network_scans)
).filter(User.id == user_id).first()
```

---

## Session Management

### FastAPI Dependency

```python
# database/engine.py

def get_db():
    """Dependency for FastAPI routes"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Usage in router
from fastapi import Depends
from database.engine import get_db

@router.get('/users')
async def get_users(db: Session = Depends(get_db)):
    users = db.query(User).all()
    return users
```

### Context Manager (Outside FastAPI)

```python
from contextlib import contextmanager

@contextmanager
def get_db_context():
    """For non-FastAPI usage"""
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()

# Usage
with get_db_context() as db:
    users = db.query(User).all()
```

---

## Code Examples

### Complete Repository Pattern

```python
# database/repositories/user_repository.py

from sqlalchemy.orm import Session
from database.models import User
from typing import Optional, List

class UserRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, data: dict) -> User:
        user = User(**data)
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user
    
    def get_by_id(self, id: str) -> Optional[User]:
        return self.db.query(User).filter(User.id == id).first()
    
    def get_by_email(self, email: str) -> Optional[User]:
        return self.db.query(User).filter(User.email == email).first()
    
    def update(self, id: str, data: dict) -> Optional[User]:
        user = self.get_by_id(id)
        if user:
            for key, value in data.items():
                setattr(user, key, value)
            self.db.commit()
        return user
    
    def delete(self, id: str) -> bool:
        user = self.get_by_id(id)
        if user:
            self.db.delete(user)
            self.db.commit()
            return True
        return False
```

### Using in Service Layer

```python
# service/Auth_Service.py

class AuthService:
    def __init__(self, db: Session):
        self.db = db
        self.user_repo = UserRepository(db)
    
    def register_user(self, user_data: dict) -> dict:
        # Check if exists
        if self.user_repo.get_by_email(user_data['email']):
            raise ValueError("User already exists")
        
        # Hash password
        user_data['password_hash'] = self.hash_password(user_data['password'])
        del user_data['password']
        
        # Create user
        user = self.user_repo.create(user_data)
        
        return user.to_dict()
```

---

## Related Documentation

- [Database Schema](./schema.md)
- [Commands](./commands.md)
- [Viva Questions](./viva_questions.md)
