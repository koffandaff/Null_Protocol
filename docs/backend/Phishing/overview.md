# 🎣 Phishing Detection Module

This document explains how phishing detection works in Fsociety.

---

## Overview

The Phishing Detection module analyzes URLs and emails for phishing indicators:

- **URL Analysis**: Check for suspicious patterns, domain age, SSL validity
- **Email Analysis**: Parse email headers, check for spoofing
- **Risk Scoring**: Provide phishing probability score

---

## Detection Techniques

### URL Analysis

| Check | What It Detects |
|-------|-----------------|
| Domain Age | Newly registered domains |
| SSL Certificate | Missing or invalid certs |
| Known Blacklists | Known phishing domains |
| Typosquatting | Similar to legitimate domains |
| URL Length | Unusually long URLs |
| Suspicious TLDs | High-risk TLDs (.xyz, .tk) |

### Email Analysis

| Check | What It Detects |
|-------|-----------------|
| SPF Record | Sender authentication |
| DKIM Signature | Email integrity |
| DMARC Policy | Domain alignment |
| Reply-To Mismatch | Suspicious redirects |
| Urgent Language | Social engineering |

---

## API Endpoints

### Check URL
```http
POST /api/security/phishing/url
Authorization: Bearer <token>
Content-Type: application/json

{
  "url": "https://suspicious-site.com/login"
}
```

### Response
```json
{
  "url": "https://suspicious-site.com/login",
  "risk_level": "high",
  "score": 85,
  "indicators": [
    "Domain registered 2 days ago",
    "No SPF record found",
    "URL contains 'login' but not HTTPS"
  ],
  "verdict": "LIKELY_PHISHING"
}
```

---

## Code Flow

```python
# utils/phishing_tools.py

async def analyze_url(url: str) -> dict:
    """Analyze URL for phishing indicators"""
    indicators = []
    score = 0
    
    # 1. Check domain age
    domain_info = await get_whois(url)
    if domain_info['age_days'] < 30:
        indicators.append(f"Domain registered {domain_info['age_days']} days ago")
        score += 30
    
    # 2. Check SSL
    ssl_info = await check_ssl(url)
    if not ssl_info['valid']:
        indicators.append("Invalid or missing SSL certificate")
        score += 25
    
    # 3. Check blacklists
    if await is_blacklisted(url):
        indicators.append("Domain found in phishing blacklist")
        score += 40
    
    # 4. Check for typosquatting
    similar = check_typosquatting(url)
    if similar:
        indicators.append(f"Similar to legitimate domain: {similar}")
        score += 20
    
    return {
        'score': min(score, 100),
        'risk_level': get_risk_level(score),
        'indicators': indicators
    }
```

---

## Risk Levels

| Score | Level | Action |
|-------|-------|--------|
| 0-30 | ✅ Low | Safe to proceed |
| 31-60 | ⚠️ Medium | Exercise caution |
| 61-85 | 🔶 High | Likely phishing |
| 86-100 | 🔴 Critical | Confirmed phishing |

---

## Related Documentation

- [Security Audit](../SecurityAudit/overview.md)
- [Digital Footprint](../Footprint/overview.md)
