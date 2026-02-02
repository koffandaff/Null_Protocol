# ⏱️ Rate Limiting

This document explains rate limiting implementation in Fsociety to prevent abuse.

---

## Table of Contents

- [What is Rate Limiting?](#what-is-rate-limiting)
- [Implementation](#implementation)
- [How It Works](#how-it-works)
- [Protected Endpoints](#protected-endpoints)
- [Code Examples](#code-examples)
- [Customization](#customization)

---

## What is Rate Limiting?

**Rate limiting** restricts the number of requests a client can make in a given time window. This prevents:

| Attack Type | Description |
|-------------|-------------|
| **Brute Force** | Trying many passwords rapidly |
| **DoS** | Overwhelming the server with requests |
| **Spam** | Automated form submissions |
| **API Abuse** | Excessive API consumption |

---

## Implementation

We use a custom `SimpleRateLimiter` class that tracks requests by IP and endpoint.

### Class Structure

```python
# routers/limiter.py

class SimpleRateLimiter:
    """
    A simple in-memory rate limiter to prevent brute force and spam.
    Tracks requests by IP and endpoint.
    """
    def __init__(self):
        # Dictionary: (ip, endpoint) -> [timestamps]
        self.requests: Dict[Tuple[str, str], list] = defaultdict(list)
```

---

## How It Works

### Request Flow

```
Client Request
      │
      ▼
┌─────────────────┐
│ Check Rate Limit│
│  (IP + Endpoint)│
└─────────────────┘
      │
      ├── Under Limit ──────────▶ Process Request
      │                                  │
      │                                  ▼
      │                          Record Timestamp
      │
      └── Over Limit ───────────▶ 429 Too Many Requests
```

### Algorithm (Sliding Window)

```python
def is_rate_limited(self, ip: str, endpoint: str, limit: int, window: int) -> bool:
    """
    Check if the request should be limited.
    
    Args:
        ip: Client IP address
        endpoint: The API endpoint being accessed
        limit: Max requests allowed in the window
        window: Time window in seconds
    """
    now = time.time()
    key = (ip, endpoint)
    
    # Clean up old timestamps (sliding window)
    self.requests[key] = [t for t in self.requests[key] if now - t < window]
    
    # Check if limit exceeded
    if len(self.requests[key]) >= limit:
        return True  # Rate limited!
    
    # Record this request
    self.requests[key].append(now)
    return False
```

### Example Scenario

```
Window: 60 seconds, Limit: 3 requests

Time 0s:  Request 1 ✓ [0]
Time 10s: Request 2 ✓ [0, 10]
Time 20s: Request 3 ✓ [0, 10, 20]
Time 30s: Request 4 ✗ RATE LIMITED (3 in window)
Time 61s: Request 5 ✓ [10, 20, 61] (0 expired, under limit)
```

---

## Protected Endpoints

### Endpoint Limits

| Endpoint | Limit | Window | Reason |
|----------|-------|--------|--------|
| `/auth/forgot-password` | 3 | 60s | Prevent email spam |
| `/auth/verify-otp` | 5 | 300s | Prevent OTP brute force |
| `/auth/reset-password` | 5 | 300s | Prevent password guessing |
| `/auth/login` | 10 | 60s | Prevent credential stuffing |

### Usage as FastAPI Dependency

```python
# routers/Auth_Router.py

from routers.limiter import limiter

@router.post('/forgot-password')
async def forgot_password(
    request: PasswordResetRequest,
    auth_service: AuthService = Depends(get_auth_service),
    _ = Depends(limiter.limit(limit=3, window=60))  # <-- Rate limit
):
    ...
```

---

## Code Examples

### Complete Limiter Dependency

```python
# routers/limiter.py

def limit(self, limit: int, window: int):
    """Create FastAPI dependency for rate limiting"""
    async def dependency(request: Request):
        ip = request.client.host
        endpoint = request.url.path
        
        if self.is_rate_limited(ip, endpoint, limit, window):
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail={
                    "code": "RATE_LIMIT_EXCEEDED",
                    "message": f"Too many requests. Please try again after {window} seconds."
                }
            )
    return dependency

# Global instance
limiter = SimpleRateLimiter()
```

### Frontend Handling

```javascript
// frontend/js/api.js

async request(endpoint, options = {}) {
    const response = await fetch(...);
    
    if (response.status === 429) {
        const error = await response.json();
        Utils.showToast(error.detail.message, 'error');
        throw new Error('Rate limited');
    }
    
    return response.json();
}
```

---

## Customization

### Adjusting Limits

```python
# More strict limit
_ = Depends(limiter.limit(limit=1, window=300))  # 1 request per 5 min

# More lenient limit
_ = Depends(limiter.limit(limit=100, window=60))  # 100 requests per minute
```

### Per-User Rate Limiting

For authenticated endpoints, you can rate limit by user ID instead of IP:

```python
async def user_rate_limit(current_user: dict = Depends(get_current_user)):
    user_id = current_user['id']
    if limiter.is_rate_limited(user_id, '/api/scan', limit=10, window=60):
        raise HTTPException(status_code=429, detail="Scan limit exceeded")
```

---

## Storage Details

### Memory Structure

```python
# In-memory storage
self.requests = {
    ('192.168.1.1', '/api/auth/login'): [1704067200.1, 1704067201.5, 1704067203.8],
    ('192.168.1.2', '/api/auth/forgot-password'): [1704067100.0],
    ...
}
```

### Memory Management

- Old timestamps are cleaned on each check
- No persistent storage (resets on restart)
- Fast O(n) cleanup where n = timestamps in window

---

## Comparison: Why Not Redis?

| Feature | In-Memory | Redis |
|---------|-----------|-------|
| **Setup** | Zero config | Requires Redis server |
| **Speed** | Fastest | Fast (network hop) |
| **Persistence** | None | Optional |
| **Multi-instance** | No | Yes |
| **Complexity** | Simple | More complex |

For Fsociety (single-instance educational project), in-memory is ideal.

---

## Related Documentation

- [Caching](./caching.md)
- [Auth Overview](../Auth/overview.md)
