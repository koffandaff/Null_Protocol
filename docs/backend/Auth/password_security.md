# 🔒 Password Security

This document covers password hashing, storage, OTP generation, and password recovery in Fsociety.

---

## Table of Contents

- [Password Hashing with bcrypt](#password-hashing-with-bcrypt)
- [Password Storage](#password-storage)
- [Password Verification](#password-verification)
- [Forgot Password Flow](#forgot-password-flow)
- [OTP Generation](#otp-generation)
- [Password Reset](#password-reset)
- [Security Best Practices](#security-best-practices)

---

## Password Hashing with bcrypt

### What is bcrypt?

**bcrypt** is a password-hashing function designed by Niels Provos and David Mazières. It's based on the Blowfish cipher and incorporates a salt to protect against rainbow table attacks.

### Why bcrypt?

| Feature | Benefit |
|---------|---------|
| **Salted** | Each password has unique hash |
| **Adaptive** | Cost factor can be increased over time |
| **Slow** | Designed to be computationally expensive |
| **Time-tested** | Industry standard since 1999 |

### Hash Password Code

```python
# service/Auth_Service.py

import bcrypt

def hash_password(self, password: str) -> str:
    """Hash password using bcrypt"""
    try:
        # Generate salt (random bytes)
        salt = bcrypt.gensalt()
        
        # Hash password with salt
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        
        # Return as string for database storage
        return hashed.decode('utf-8')
    except Exception as e:
        raise ValueError(f"Password hashing failed: {str(e)}")
```

### bcrypt Hash Format

```
$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4r5KjD3.k7Kj6ej2
|__|__|______________________|______________________________|
 │   │           │                        │
 │   │           │                        └── Hash (31 chars)
 │   │           └── Salt (22 chars)
 │   └── Cost factor (12 = 2^12 iterations)
 └── Algorithm identifier ($2b$ = bcrypt)
```

---

## Password Storage

### Database Schema

```sql
-- users table
CREATE TABLE users (
    id TEXT PRIMARY KEY,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,  -- bcrypt hash stored here
    password_changed_at DATETIME,
    ...
);
```

### Storage Flow

```
User Input          bcrypt.gensalt()       bcrypt.hashpw()        Database
    │                     │                      │                    │
"Password123"  ──▶  Generate Salt  ──▶  Hash + Salt  ──▶  $2b$12$...
```

---

## Password Verification

### How Verification Works

```python
def verify_password(self, plain_password: str, hashed_password: str) -> bool:
    """Verify password using bcrypt"""
    try:
        return bcrypt.checkpw(
            plain_password.encode('utf-8'),
            hashed_password.encode('utf-8')
        )
    except Exception:
        return False
```

### Verification Process

1. Extract salt from stored hash (first 29 characters)
2. Hash input password with extracted salt
3. Compare resulting hash with stored hash
4. Return True if match, False otherwise

```
Stored Hash: $2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4r5KjD3.k7Kj6ej2
                   |_______________|
                   Extract Salt

User Input: "Password123"
            + Salt from hash
            = Hash with same salt
            
Compare: Generated Hash == Stored Hash?
```

---

## Forgot Password Flow

### Complete Flow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                    PASSWORD RECOVERY FLOW                        │
└─────────────────────────────────────────────────────────────────┘

   User                Frontend               Backend              Database
    │                     │                     │                     │
    │──Enter Email───────▶│                     │                     │
    │                     │──POST /forgot-pw───▶│                     │
    │                     │                     │──Get User by Email─▶│
    │                     │                     │◀──User Found────────│
    │                     │                     │                     │
    │                     │                     │──Generate 6-digit OTP
    │                     │                     │──Hash OTP (SHA256)──▶│
    │                     │                     │                     │
    │◀──────OTP printed to console (mock email)─│                     │
    │                     │                     │                     │
    │──Enter OTP─────────▶│                     │                     │
    │                     │──POST /verify-otp──▶│                     │
    │                     │◀──── OTP Valid ─────│                     │
    │                     │                     │                     │
    │──New Password──────▶│                     │                     │
    │                     │──POST /reset-pw────▶│                     │
    │                     │                     │──Verify OTP Again───│
    │                     │                     │──Hash New Password──│
    │                     │                     │──Update User────────▶│
    │                     │                     │──Delete Reset Token─▶│
    │                     │◀──── Success ───────│                     │
```

---

## OTP Generation

### 6-Digit OTP Generation

```python
# service/Auth_Service.py

def request_password_reset(self, email: str) -> bool:
    """Generate 6-digit OTP and print to console (Mock Email)"""
    user = self.user_repo.get_by_email(email)
    if not user:
        # Return True to prevent user enumeration
        return True
    
    import secrets
    import hashlib
    
    # Generate 6-digit OTP using cryptographically secure random
    otp = ''.join([str(secrets.randbelow(10)) for _ in range(6)])
    
    # Store SHA256 hash for verification (never store plain OTP)
    token_hash = hashlib.sha256(otp.encode()).hexdigest()
    
    # OTP expires in 10 minutes
    expires_at = datetime.utcnow() + timedelta(minutes=10)
    
    # Save to database
    self.user_repo.create_reset_token(user.id, token_hash, expires_at)
    
    # MOCK EMAIL SENDER (prints to console)
    print("\n" + "="*50)
    print(f" [EMAIL SERVICE] OTP Requested for {email}")
    print(f" [OTP CODE] {otp}")
    print("="*50 + "\n")
    
    return True
```

### Why Hash the OTP?

| Security Concern | Solution |
|------------------|----------|
| Database breach | Attacker only sees hash, not OTP |
| OTP interception | Short lifespan (10 min) |
| Brute force | Rate limiting (3/60s) |

---

## Password Reset

### Reset Process

```python
def reset_password(self, email: str, otp: str, new_password: str) -> None:
    """Reset password using Email + OTP"""
    import hashlib
    
    # 1. Verify User exists
    user = self.user_repo.get_by_email(email)
    if not user:
        raise ValueError("Invalid Email or OTP")

    # 2. Get stored token
    token_data = self.user_repo.get_user_reset_token(user.id)
    if not token_data:
        raise ValueError("No reset requested or expired")
        
    # 3. Verify OTP hash matches
    input_hash = hashlib.sha256(otp.encode()).hexdigest()
    if input_hash != token_data['token_hash']:
        raise ValueError("Invalid OTP")

    # 4. Check expiry
    if token_data['expires_at'] < datetime.utcnow():
        self.user_repo.delete_reset_token(token_data['token_hash'])
        raise ValueError("OTP has expired")
        
    # 5. Update password
    new_hash = self.hash_password(new_password)
    self.user_repo.update(user.id, {
        'password_hash': new_hash,
        'password_changed_at': datetime.utcnow()
    })
    
    # 6. Invalidate token (one-time use)
    self.user_repo.delete_reset_token(token_data['token_hash'])
```

---

## Security Best Practices

### Rate Limiting

```python
# routers/Auth_Router.py

@router.post('/forgot-password')
async def forgot_password(
    request: PasswordResetRequest,
    auth_service: AuthService = Depends(get_auth_service),
    _ = Depends(limiter.limit(limit=3, window=60))  # 3 requests per minute
):
```

### User Enumeration Prevention

```python
# Always return same response whether user exists or not
return {"message": "If the email exists, a reset link has been sent."}
```

### Password Change Tracking

```python
# Track when password was last changed
self.user_repo.update(user_id, {
    'password_hash': new_hash,
    'password_changed_at': datetime.utcnow()
})
```

---

## Related Documentation

- [Overview](./overview.md)
- [JWT Tokens](./jwt_tokens.md)
- [Admin Roles](./admin_roles.md)
