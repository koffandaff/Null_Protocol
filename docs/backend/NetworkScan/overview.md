# 🔍 Network Scanning Module

This document explains how network scanning works in Fsociety.

---

## Overview

The Network Scanning module provides reconnaissance capabilities for security professionals:

- **Port Scanning**: Discover open ports on target systems
- **Service Detection**: Identify running services and versions
- **OS Fingerprinting**: Detect target operating system

---

## Architecture

```
Frontend                 Backend                    External
┌──────────┐      ┌─────────────────┐      ┌──────────────┐
│ ScanView │ ───▶ │ Scan_Router.py  │ ───▶ │ Target Host  │
│          │      │                 │      │              │
│ POST /   │      │ Scan_Service.py │      │ Ports: 1-65535
│ network  │      │                 │      └──────────────┘
└──────────┘      │ network_tools.py│
                  └─────────────────┘
```

---

## Files

| File | Purpose |
|------|---------|
| `routers/Scan_Router.py` | API endpoints |
| `service/Scan_Service.py` | Business logic |
| `utils/network_tools.py` | Low-level scanning |
| `model/Scan_Model.py` | Pydantic schemas |

---

## API Endpoints

### Start Network Scan
```http
POST /api/scans/network
Authorization: Bearer <token>
Content-Type: application/json

{
  "target": "192.168.1.1",
  "scan_type": "quick",
  "ports": "1-1024"
}
```

### Response
```json
{
  "scan_id": "uuid",
  "status": "running",
  "started_at": "2024-01-01T12:00:00"
}
```

### Get Scan Results
```http
GET /api/scans/{scan_id}
Authorization: Bearer <token>
```

---

## Scan Types

| Type | Ports | Description |
|------|-------|-------------|
| `quick` | 1-1024 | Common ports only |
| `full` | 1-65535 | All ports (slow) |
| `custom` | User-defined | Specific port range |

---

## Code Flow

```python
# routers/Scan_Router.py
@router.post('/network')
async def start_network_scan(request: ScanRequest, user = Depends(get_current_user)):
    scan_service = ScanService(db)
    result = await scan_service.run_network_scan(
        user_id=user['id'],
        target=request.target,
        scan_type=request.scan_type
    )
    return result

# service/Scan_Service.py
async def run_network_scan(self, user_id, target, scan_type):
    # 1. Check cache
    cache_key = cache_tools.get_key('network', target)
    cached = cache_tools.get(cache_key)
    if cached:
        return cached
    
    # 2. Perform scan
    results = await network_tools.scan_ports(target, scan_type)
    
    # 3. Save to database
    scan = self.scan_repo.create({
        'user_id': user_id,
        'target': target,
        'results': results
    })
    
    # 4. Cache results
    cache_tools.set(cache_key, results)
    
    return results
```

---

## Security Considerations

1. **Input Validation**: Target must be valid IP or hostname
2. **Rate Limiting**: Prevent scan abuse
3. **Caching**: Avoid repeated scans of same target
4. **Logging**: All scans recorded in activity log

---

## Related Documentation

- [Security Audit](../SecurityAudit/overview.md)
- [Caching](../Caching_RateLimiting/caching.md)
