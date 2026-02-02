# 🔐 Authentication System Overview

This document provides a comprehensive overview of the Fsociety authentication system.

---

## Table of Contents

- [Architecture](#architecture)
- [Authentication Flow](#authentication-flow)
- [Key Components](#key-components)
- [Security Features](#security-features)
- [Related Files](#related-files)

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     AUTHENTICATION FLOW                          │
└─────────────────────────────────────────────────────────────────┘
                              
  ┌──────────┐      ┌──────────────┐      ┌────────────────┐
  │  Client  │ ───▶ │ Auth_Router  │ ───▶ │  Auth_Service  │
  │ (Browser)│      │  (Endpoints) │      │ (Business Logic)│
  └──────────┘      └──────────────┘      └────────────────┘
       │                                          │
       │                                          ▼
       │                              ┌────────────────────┐
       │                              │  UserRepository    │
       │                              │  (SQLAlchemy ORM)  │
       │                              └────────────────────┘
       │                                          │
       │                                          ▼
       │                              ┌────────────────────┐
       │◀──────────────────────────── │   SQLite Database  │
       │      JWT + HttpOnly Cookie   └────────────────────┘
```

---

## Authentication Flow

### 1. User Registration (Signup)

```
Client                   Server
  │                         │
  │──POST /api/auth/signup─▶│
  │   {email, username,     │
  │    password, ...}       │
  │                         │
  │                    ┌────┴────┐
  │                    │ Validate │
  │                    │ & Hash   │
  │                    │ Password │
  │                    └────┬────┘
  │                         │
  │                    ┌────┴────┐
  │                    │  Store  │
  │                    │  in DB  │
  │                    └────┬────┘
  │                         │
  │◀──── UserResponse ──────│
```

### 2. User Login

```
Client                   Server
  │                         │
  │──POST /api/auth/login──▶│
  │   {email, password}     │
  │                         │
  │                    ┌────┴────┐
  │                    │ Verify  │
  │                    │Password │
  │                    └────┬────┘
  │                         │
  │                    ┌────┴────┐
  │                    │Generate │
  │                    │JWT tokens│
  │                    └────┬────┘
  │                         │
  │◀── access_token (body)──│
  │◀── refresh_token (cookie)│
```

### 3. Token Refresh

```
Client                   Server
  │                         │
  │──POST /api/auth/refresh─▶│
  │   (Cookie: refresh_token)│
  │                         │
  │                    ┌────┴────┐
  │                    │ Verify  │
  │                    │ Refresh │
  │                    │ Token   │
  │                    └────┬────┘
  │                         │
  │◀── new access_token ────│
```

---

## Key Components

### Files

| File | Purpose |
|------|---------|
| `routers/Auth_Router.py` | HTTP endpoints for authentication |
| `service/Auth_Service.py` | Business logic for auth operations |
| `model/Auth_Model.py` | Pydantic models for request/response |
| `routers/dependencies.py` | `get_current_user` dependency |
| `routers/limiter.py` | Rate limiting implementation |
| `database/repositories/user_repository.py` | Database operations |

### Service Methods

| Method | Description |
|--------|-------------|
| `hash_password()` | Hash password using bcrypt |
| `verify_password()` | Verify password against hash |
| `create_access_token()` | Generate JWT access token (15 min) |
| `create_refresh_token()` | Generate JWT refresh token (7 days) |
| `verify_token()` | Decode and validate JWT |
| `register_user()` | Create new user account |
| `login_user()` | Authenticate and return tokens |
| `refresh_access_token()` | Generate new access token |
| `logout()` | Invalidate refresh token |

---

## Security Features

### 1. Password Hashing (bcrypt)
- Uses Blowfish cipher with salt
- Computationally expensive to prevent brute force
- Salt is automatically generated and stored with hash

### 2. JWT Tokens
- **Access Token**: Short-lived (15 minutes), sent in Authorization header
- **Refresh Token**: Long-lived (7 days), stored in HttpOnly cookie

### 3. Rate Limiting
- Login: Standard rate limiting via global middleware
- Password Reset: 3 requests per 60 seconds
- OTP Verification: 5 requests per 300 seconds

### 4. SQL Injection Prevention
- All database operations use SQLAlchemy ORM
- Parameterized queries prevent injection attacks

### 5. Account Protection
- Disabled accounts cannot login
- Activity logging for audit trails

---

## Related Files

```
backend/
├── routers/
│   ├── Auth_Router.py      # Endpoints
│   ├── dependencies.py     # get_current_user
│   └── limiter.py          # Rate limiting
├── service/
│   └── Auth_Service.py     # Business logic
├── model/
│   └── Auth_Model.py       # Pydantic schemas
└── database/
    └── repositories/
        └── user_repository.py  # DB operations
```

---

## Next Steps

- [JWT Tokens Deep Dive](./jwt_tokens.md)
- [Password Security](./password_security.md)
- [Admin Roles & Permissions](./admin_roles.md)
