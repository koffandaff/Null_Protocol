# 🛡️ Security Audit Module

This document explains how security auditing works in Fsociety.

---

## Overview

The Security Audit module analyzes websites for vulnerabilities:

- **SSL/TLS Analysis**: Certificate validation, protocol versions
- **Security Headers**: CSP, HSTS, X-Frame-Options, etc.
- **Vulnerability Checks**: Common misconfigurations

---

## Architecture

```
Frontend                 Backend                    External
┌──────────┐      ┌──────────────────┐      ┌──────────────┐
│ AuditView│ ───▶ │ Security_Router  │ ───▶ │ Target URL   │
│          │      │                  │      │              │
│ POST /   │      │ Security_Service │      │ HTTPS Server │
│ audit    │      │                  │      └──────────────┘
└──────────┘      │ security_tools   │
                  └──────────────────┘
```

---

## Files

| File | Purpose |
|------|---------|
| `routers/Security_Router.py` | API endpoints |
| `service/Security_Service.py` | Business logic |
| `utils/security_tools.py` | SSL/Header checks |
| `model/Security_Model.py` | Pydantic schemas |

---

## API Endpoints

### Run Security Audit
```http
POST /api/security/audit
Authorization: Bearer <token>
Content-Type: application/json

{
  "url": "https://example.com"
}
```

### Response
```json
{
  "ssl": {
    "valid": true,
    "issuer": "Let's Encrypt",
    "expires_at": "2024-06-01",
    "protocol_version": "TLSv1.3"
  },
  "headers": {
    "strict-transport-security": "max-age=31536000",
    "content-security-policy": "default-src 'self'",
    "x-frame-options": "DENY"
  },
  "risk_level": "low",
  "score": 85
}
```

---

## Security Checks

### SSL/TLS Analysis

| Check | Description |
|-------|-------------|
| Certificate Validity | Is cert expired? |
| Issuer | Trusted CA? |
| Protocol Version | TLS 1.2+ required |
| Certificate Chain | Complete chain? |

### Security Headers

| Header | Purpose | Missing Risk |
|--------|---------|--------------|
| `Strict-Transport-Security` | Force HTTPS | Medium |
| `Content-Security-Policy` | XSS prevention | High |
| `X-Frame-Options` | Clickjacking prevention | Medium |
| `X-Content-Type-Options` | MIME sniffing | Low |
| `X-XSS-Protection` | Browser XSS filter | Low |

---

## Code Flow

```python
# utils/security_tools.py

async def analyze_ssl(url: str) -> dict:
    """Analyze SSL/TLS configuration"""
    import ssl
    import socket
    
    hostname = urlparse(url).hostname
    context = ssl.create_default_context()
    
    with socket.create_connection((hostname, 443)) as sock:
        with context.wrap_socket(sock, server_hostname=hostname) as ssock:
            cert = ssock.getpeercert()
            
            return {
                'valid': True,
                'issuer': dict(cert['issuer']),
                'subject': dict(cert['subject']),
                'expires_at': cert['notAfter'],
                'protocol': ssock.version()
            }

async def check_headers(url: str) -> dict:
    """Check security headers"""
    import httpx
    
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        
        security_headers = [
            'strict-transport-security',
            'content-security-policy',
            'x-frame-options',
            'x-content-type-options'
        ]
        
        return {
            header: response.headers.get(header)
            for header in security_headers
        }
```

---

## Risk Scoring

| Score | Level | Meaning |
|-------|-------|---------|
| 90-100 | ✅ Low | Excellent security |
| 70-89 | ⚠️ Medium | Some improvements needed |
| 50-69 | 🔶 High | Significant issues |
| 0-49 | 🔴 Critical | Major vulnerabilities |

---

## Related Documentation

- [Network Scan](../NetworkScan/overview.md)
- [Phishing Detection](../Phishing/overview.md)
