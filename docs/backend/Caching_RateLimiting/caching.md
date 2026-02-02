# 📦 Caching System

This document explains how caching works in Fsociety, what we cache, and why.

---

## Table of Contents

- [What is Caching?](#what-is-caching)
- [Implementation](#implementation)
- [Cache Storage](#cache-storage)
- [Cache Operations](#cache-operations)
- [What We Cache](#what-we-cache)
- [What We Don't Cache](#what-we-dont-cache)
- [Configuration](#configuration)
- [Code Examples](#code-examples)

---

## What is Caching?

**Caching** is a technique of storing frequently accessed data in a fast-access storage layer to reduce response times and server load.

### Benefits

| Benefit | Description |
|---------|-------------|
| **Speed** | Cached responses return instantly |
| **Reduced Load** | Fewer database/API calls |
| **Cost Savings** | Less external API usage |
| **Consistency** | Same scan results for repeated queries |

---

## Implementation

We use an **in-memory LRU (Least Recently Used) cache** implemented with Python's `OrderedDict`.

### Architecture

```
Client Request
      │
      ▼
┌─────────────────┐     Cache Hit?     ┌──────────────────┐
│   Endpoint      │ ─────────────────▶ │   CacheTools     │
│   (Router)      │                    │   (In-Memory)    │
└─────────────────┘                    └──────────────────┘
      │                                        │
      │ Cache Miss                             │ Hit
      ▼                                        ▼
┌─────────────────┐                   ┌──────────────────┐
│   Service       │                   │   Return Cached  │
│   (Actual Work) │                   │   Response       │
└─────────────────┘                   └──────────────────┘
      │
      ▼
Store in Cache
```

---

## Cache Storage

### Where is Cache Stored?

The cache is stored **in-memory** in the Python process. This means:

| Characteristic | Value |
|----------------|-------|
| **Location** | RAM of the server |
| **Persistence** | None (lost on restart) |
| **Speed** | Fastest possible (nanoseconds) |
| **Sharing** | Single process only |
| **Size Limit** | Configurable (default 500 entries) |

### Data Structure

```python
# collections.OrderedDict maintains insertion order
self.cache = OrderedDict()

# Each entry structure:
{
    'key': 'md5_hash_of_params',
    'value': {
        'value': { ... scan results ... },
        'timestamp': 1704067200.123,
        'created_at': '2024-01-01T12:00:00'
    }
}
```

---

## Cache Operations

### Key Generation

```python
def get_key(self, scan_type: str, target: str, params: Dict = None) -> str:
    """Generate unique cache key from scan parameters"""
    key_data = {
        'scan_type': scan_type,    # e.g., 'network', 'security'
        'target': target,           # e.g., 'example.com'
        'params': params or {}      # e.g., {'ports': '1-1000'}
    }
    
    # Sort params for consistent keys
    key_str = json.dumps(key_data, sort_keys=True)
    return hashlib.md5(key_str.encode()).hexdigest()
```

### Get from Cache

```python
def get(self, key: str) -> Optional[Dict]:
    """Get value from cache"""
    if not settings.CACHE_ENABLED:
        return None
    
    if key in self.cache:
        entry = self.cache[key]
        
        # Check if expired
        if time.time() - entry['timestamp'] > self.ttl:
            del self.cache[key]
            self.misses += 1
            return None
        
        # Move to end (most recently used)
        self.cache.move_to_end(key)
        self.hits += 1
        return entry['value']
    
    self.misses += 1
    return None
```

### Set in Cache

```python
def set(self, key: str, value: Dict) -> None:
    """Set value in cache"""
    if not settings.CACHE_ENABLED:
        return
    
    # Remove expired entries first
    self._cleanup()
    
    # Add new entry
    self.cache[key] = {
        'value': value,
        'timestamp': time.time(),
        'created_at': datetime.utcnow().isoformat()
    }
    
    # Move to end (most recently used)
    self.cache.move_to_end(key)
    
    # Enforce size limit (LRU eviction)
    if len(self.cache) > self.max_size:
        self.cache.popitem(last=False)  # Remove oldest
```

---

## What We Cache

| Scan Type | Reason | TTL |
|-----------|--------|-----|
| **Network Scans** | Port scans are slow, results stable | 5 min |
| **Security Audits** | SSL/Headers don't change frequently | 5 min |
| **DNS Lookups** | DNS records update slowly | 10 min |
| **WHOIS Data** | Domain info rarely changes | 30 min |

### Example Usage in Service

```python
# service/Scan_Service.py

async def run_network_scan(self, target: str, params: Dict) -> Dict:
    # 1. Generate cache key
    cache_key = cache_tools.get_key('network', target, params)
    
    # 2. Check cache
    cached = cache_tools.get(cache_key)
    if cached:
        cached['from_cache'] = True
        return cached
    
    # 3. Perform actual scan (slow)
    result = await self._do_network_scan(target, params)
    
    # 4. Store in cache
    cache_tools.set(cache_key, result)
    
    return result
```

---

## What We Don't Cache

| Data Type | Reason |
|-----------|--------|
| **User Data** | Privacy concerns, must be real-time |
| **Auth Tokens** | Security risk, short-lived |
| **Activity Logs** | Must reflect current state |
| **File Hashes** | Files may change between scans |
| **AI Chat Responses** | Each response should be unique |

---

## Configuration

### Environment Settings

```python
# config/settings.py

class Settings:
    CACHE_ENABLED: bool = True
    CACHE_TTL: int = 300        # 5 minutes
    MAX_CACHE_SIZE: int = 500   # 500 entries
```

### Cache Statistics

```python
def get_stats(self) -> Dict:
    """Get cache performance statistics"""
    return {
        'enabled': settings.CACHE_ENABLED,
        'total_entries': len(self.cache),
        'max_size': self.max_size,
        'ttl_seconds': self.ttl,
        'hits': self.hits,
        'misses': self.misses,
        'hit_rate': round(hits / total, 3),
        'memory_bytes': memory_estimate,
    }
```

---

## Code Examples

### Complete Cache Workflow

```python
from utils.cache_tools import cache_tools

# 1. Generate key
key = cache_tools.get_key('security', 'https://example.com')

# 2. Try cache first
cached_result = cache_tools.get(key)
if cached_result:
    return cached_result  # Fast return!

# 3. Do expensive operation
result = perform_security_audit('https://example.com')

# 4. Store for next time
cache_tools.set(key, result)

return result
```

### Clearing Cache

```python
# Clear all cache
cache_tools.clear()

# Clear specific type
cache_tools.clear(cache_type='network')
```

---

## Related Documentation

- [Rate Limiting](./rate_limiting.md)
- [Database](../Database/overview.md)
