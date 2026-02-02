# 🔑 JWT Tokens - Access & Refresh Token System

This document explains how JWT tokens are generated, validated, and managed in Fsociety.

---

## Table of Contents

- [What is JWT?](#what-is-jwt)
- [Token Types](#token-types)
- [Token Generation](#token-generation)
- [Token Storage](#token-storage)
- [Token Validation](#token-validation)
- [Refresh Flow](#refresh-flow)
- [Code Examples](#code-examples)

---

## What is JWT?

**JSON Web Token (JWT)** is a compact, URL-safe means of representing claims to be transferred between two parties. JWTs are signed using a secret key (HMAC) or a public/private key pair (RSA).

### JWT Structure

```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c
|_______________|  |_____________________________|  |___________________________|
     Header                   Payload                      Signature
```

---

## Token Types

### Access Token
| Property | Value |
|----------|-------|
| **Purpose** | Authenticate API requests |
| **Lifespan** | 15 minutes |
| **Storage** | Client localStorage |
| **Sent via** | `Authorization: Bearer <token>` header |

### Refresh Token
| Property | Value |
|----------|-------|
| **Purpose** | Obtain new access tokens |
| **Lifespan** | 7 days |
| **Storage** | HttpOnly cookie + Database |
| **Sent via** | Cookie (automatic) |

---

## Token Generation

### Environment Variables

```env
# backend/.env
SECRET_KEY=your-super-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7
```

### Access Token Creation

```python
# service/Auth_Service.py

def create_access_token(self, payload_data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token"""
    payload = payload_data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire)
    
    payload.update({'exp': expire, 'type': 'access'})
    access_token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
    return access_token
```

### Refresh Token Creation

```python
def create_refresh_token(self, data: dict) -> str:
    """Create JWT refresh token"""
    payload = data.copy()
    expire = datetime.utcnow() + timedelta(days=self.refresh_token_expire)
    payload.update({'exp': expire, 'type': 'refresh'})
    refresh_token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
    return refresh_token
```

### Token Payload Contents

```json
{
  "sub": "user_id_uuid",
  "email": "user@example.com",
  "role": "user",
  "exp": 1704067200,
  "type": "access"
}
```

---

## Token Storage

### Access Token (Client-Side)

```javascript
// frontend/js/auth.js

static async login(email, password) {
    const response = await Api.post('/auth/login', { email, password });
    
    // Store access token in localStorage
    localStorage.setItem('access_token', response.access_token);
    localStorage.setItem('user', JSON.stringify(response.user));
    
    return response.user;
}
```

### Refresh Token (Server-Side)

```python
# routers/Auth_Router.py - Login endpoint

response.set_cookie(
    key="refresh_token",
    value=result["refresh_token"],
    httponly=True,      # JavaScript cannot access
    secure=False,       # Set True for HTTPS in production
    samesite="lax",     # CSRF protection
    max_age=7 * 24 * 60 * 60  # 7 days
)
```

### Refresh Token in Database

```python
# Stored in users table
self.user_repo.save_refresh_token(user['id'], refresh_token, expires_at)
```

---

## Token Validation

### Access Token Verification

```python
# service/Auth_Service.py

def verify_token(self, token: str, token_type: str = 'access') -> Optional[dict]:
    """Verify JWT token"""
    try:
        payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
        
        # Ensure token type matches
        if payload.get('type') != token_type:
            return None
        
        return payload
    except JWTError:
        return None
```

### Protected Route Dependency

```python
# routers/dependencies.py

async def get_current_user(
    request: Request,
    db: Session = Depends(get_db)
) -> dict:
    """Dependency to get current authenticated user"""
    
    # Extract token from Authorization header
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    token = auth_header.split(' ')[1]
    
    # Verify token
    auth_service = AuthService(db)
    user = auth_service.get_current_user(token)
    
    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    return user
```

---

## Refresh Flow

### When Access Token Expires

```
┌──────────────────────────────────────────────────────────────────┐
│ 1. API call fails with 401 (token expired)                       │
│ 2. Frontend intercepts error                                      │
│ 3. Frontend calls POST /api/auth/refresh (cookie sent auto)      │
│ 4. Backend validates refresh token from cookie + DB              │
│ 5. New access token returned                                      │
│ 6. Frontend retries original request with new token             │
└──────────────────────────────────────────────────────────────────┘
```

### Frontend Auto-Refresh

```javascript
// frontend/js/api.js

async refreshToken() {
    try {
        const response = await fetch(`${this.baseUrl}/auth/refresh`, {
            method: 'POST',
            credentials: 'include'  // Send cookies
        });
        
        if (response.ok) {
            const data = await response.json();
            localStorage.setItem('access_token', data.access_token);
            return data.access_token;
        }
        return null;
    } catch (error) {
        return null;
    }
}
```

### Backend Refresh Endpoint

```python
# routers/Auth_Router.py

@router.post('/refresh', response_model=Token)
async def refresh_token(
    request: Request,
    response: Response,
    auth_service: AuthService = Depends(get_auth_service)
):
    """Refresh access token using refresh token from cookie"""
    refresh_token = request.cookies.get("refresh_token")
    
    if not refresh_token:
        raise HTTPException(status_code=401, detail="Refresh token missing")
    
    new_access_token = auth_service.refresh_access_token(refresh_token)
    if not new_access_token:
        raise HTTPException(status_code=401, detail="Invalid Refresh Token")
    
    return Token(access_token=new_access_token)
```

---

## Code Examples

### Complete Login Flow

```python
# service/Auth_Service.py

def login_user(self, email: str, password: str) -> dict:
    """Login user and return tokens"""
    # 1. Authenticate
    user = self.authenticate_user(email, password)
    if not user:
        raise ValueError("Invalid credentials")
    
    # 2. Create token payload
    token_payload = {
        'sub': user['id'], 
        'email': user['email'],
        'role': user.get('role', 'user')
    }
    
    # 3. Generate tokens
    access_token = self.create_access_token(token_payload)
    refresh_token = self.create_refresh_token(token_payload)

    # 4. Save refresh token to database
    expires_at = datetime.utcnow() + timedelta(days=self.refresh_token_expire)
    self.user_repo.save_refresh_token(user['id'], refresh_token, expires_at)
    
    # 5. Update last login
    self.user_repo.update_last_login(user['id'])
    
    # 6. Log activity
    self.activity_repo.log_activity(
        user_id=user['id'],
        action='login',
        details={'email': user['email']}
    )

    return {
        'access_token': access_token,
        'refresh_token': refresh_token,
        'token_type': 'bearer',
        'user': { ... }
    }
```

---

## Security Considerations

1. **Secret Key**: Must be long, random, and kept secret
2. **HTTPS**: Required in production for secure cookie transmission
3. **Token Rotation**: Refresh tokens are invalidated on logout
4. **Database Validation**: Refresh tokens verified against stored value
5. **Short Lifespan**: Access tokens expire quickly (15 min)

---

## Related Documentation

- [Overview](./overview.md)
- [Password Security](./password_security.md)
- [Admin Roles](./admin_roles.md)
