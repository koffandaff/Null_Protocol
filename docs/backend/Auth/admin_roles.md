# 👑 Admin Roles & Permissions

This document covers role-based access control, admin dashboard features, and permission management.

---

## Table of Contents

- [Role System](#role-system)
- [Admin Identification](#admin-identification)
- [Protected Admin Routes](#protected-admin-routes)
- [Admin Dashboard Features](#admin-dashboard-features)
- [Admin Service Methods](#admin-service-methods)
- [SQL Console Security](#sql-console-security)

---

## Role System

### User Roles

| Role | Permissions |
|------|-------------|
| `user` | Standard access to security tools |
| `admin` | Full access + user management + SQL console |

### Role Storage

```sql
-- users table
CREATE TABLE users (
    id TEXT PRIMARY KEY,
    email TEXT UNIQUE,
    role TEXT DEFAULT 'user',  -- 'user' or 'admin'
    is_active BOOLEAN DEFAULT TRUE,
    ...
);
```

---

## Admin Identification

### In JWT Token

```python
# service/Auth_Service.py - Login

token_payload = {
    'sub': user['id'], 
    'email': user['email'],
    'role': user.get('role', 'user')  # Role included in token
}
```

### Token Payload Example

```json
{
  "sub": "550e8400-e29b-41d4-a716-446655440000",
  "email": "admin@fsociety.com",
  "role": "admin",
  "exp": 1704067200,
  "type": "access"
}
```

---

## Protected Admin Routes

### Admin Dependency

```python
# routers/dependencies.py

async def get_admin_user(
    current_user: dict = Depends(get_current_user)
) -> dict:
    """Dependency to ensure user is admin"""
    if current_user.get('role') != 'admin':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user
```

### Using in Routes

```python
# routers/Admin_Router.py

@router.get('/users')
async def get_all_users(
    admin_user: dict = Depends(get_admin_user),  # Only admins
    db: Session = Depends(get_db)
):
    ...
```

---

## Admin Dashboard Features

### Features Overview

```
┌─────────────────────────────────────────────────────┐
│                 ADMIN DASHBOARD                      │
├─────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌───────────┐ │
│  │ User Stats   │  │ Activity Log │  │ Charts    │ │
│  │ - Total      │  │ - Recent     │  │ - Logins  │ │
│  │ - Active     │  │ - Filter     │  │ - Signups │ │
│  │ - Admins     │  │ - Search     │  │ - Scans   │ │
│  └──────────────┘  └──────────────┘  └───────────┘ │
│                                                      │
│  ┌──────────────────────────────────────────────┐   │
│  │           USER MANAGEMENT                     │   │
│  │ - View all users                              │   │
│  │ - Enable/Disable accounts                     │   │
│  │ - Change roles (admin/user)                   │   │
│  │ - Search by username/email                    │   │
│  │ - Export PDF manifest                         │   │
│  └──────────────────────────────────────────────┘   │
│                                                      │
│  ┌──────────────────────────────────────────────┐   │
│  │           SQL CONSOLE                         │   │
│  │ - Execute raw SQL queries                     │   │
│  │ - View results in table format               │   │
│  │ - Export results to PDF                       │   │
│  └──────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────┘
```

### Statistics Endpoint

```python
# routers/Admin_Router.py

@router.get('/stats')
async def get_platform_stats(
    admin_user: dict = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    admin_service = AdminService(db)
    return admin_service.get_platform_stats()
```

### Stats Response

```json
{
  "users": {
    "total": 152,
    "active": 145,
    "admins": 3,
    "new_today": 5,
    "new_this_week": 23
  },
  "activities": {
    "total": 4521,
    "today": 89,
    "logins_today": 45,
    "scans_today": 32
  }
}
```

---

## Admin Service Methods

### User Management

```python
# service/Admin_Service.py

class AdminService:
    def get_all_users(self, limit: int, offset: int, search: str):
        """Get paginated user list with optional search"""
        
    def toggle_user_status(self, user_id: str, is_active: bool):
        """Enable or disable user account"""
        
    def change_user_role(self, user_id: str, new_role: str):
        """Change user role (user/admin)"""
        
    def get_platform_stats(self):
        """Get dashboard statistics"""
        
    def search_activities(self, filters: dict):
        """Search activity logs with filters"""
```

### Toggle User Status

```python
def toggle_user_status(self, target_user_id: str, is_active: bool) -> dict:
    """Enable or disable a user account"""
    user = self.user_repo.get_by_id(target_user_id)
    if not user:
        raise ValueError("User not found")
    
    self.user_repo.update(target_user_id, {'is_active': is_active})
    
    # Log the action
    action = 'enable_user' if is_active else 'disable_user'
    self.activity_repo.log_activity(
        user_id=target_user_id,
        action=action,
        details={'admin_action': True}
    )
    
    return {'message': f'User {"enabled" if is_active else "disabled"}'}
```

---

## SQL Console Security

### Allowed Operations

The SQL console allows admins to execute raw SQL queries. Security is maintained through:

1. **Role Check**: Only admins can access
2. **Read Operations**: SELECT queries are safe
3. **Write Operations**: INSERT/UPDATE/DELETE with caution
4. **Audit Trail**: All SQL executions are logged

### SQL Execution Endpoint

```python
# routers/Admin_Router.py

@router.post('/sql')
async def execute_sql(
    request: SQLRequest,
    admin_user: dict = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Execute SQL query (admin only)"""
    admin_service = AdminService(db)
    return admin_service.execute_sql(request.query)
```

### SQL Service Method

```python
def execute_sql(self, query: str) -> dict:
    """Execute raw SQL query and return results"""
    try:
        result = self.db.execute(text(query))
        
        if query.strip().upper().startswith('SELECT'):
            columns = list(result.keys())
            rows = [list(row) for row in result.fetchall()]
            return {
                'success': True,
                'columns': columns,
                'rows': rows,
                'row_count': len(rows),
                'message': f'{len(rows)} rows returned'
            }
        else:
            self.db.commit()
            return {
                'success': True,
                'columns': [],
                'rows': [],
                'row_count': result.rowcount,
                'message': f'{result.rowcount} rows affected'
            }
    except Exception as e:
        return {
            'success': False,
            'columns': [],
            'rows': [],
            'row_count': 0,
            'message': str(e)
        }
```

---

## Frontend Admin Check

### Checking Admin Role

```javascript
// frontend/js/auth.js

static getCurrentUser() {
    return JSON.parse(localStorage.getItem('user'));
}

static isAdmin() {
    const user = this.getCurrentUser();
    return user && user.role === 'admin';
}
```

### Protected UI Elements

```javascript
// frontend/js/views/admin.js

// Only show admin panel link if user is admin
if (Auth.isAdmin()) {
    document.getElementById('admin-link').style.display = 'block';
}
```

---

## Related Documentation

- [Overview](./overview.md)
- [JWT Tokens](./jwt_tokens.md)
- [Password Security](./password_security.md)
