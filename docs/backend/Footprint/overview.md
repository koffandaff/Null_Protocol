# 👣 Digital Footprint Module

This document explains how digital footprint scanning works in Fsociety.

---

## Overview

The Digital Footprint module performs OSINT (Open Source Intelligence) reconnaissance:

- **Email Search**: Find accounts linked to an email
- **Username Search**: Check username availability across platforms
- **Data Breach Check**: Search for exposed credentials
- **Social Media Presence**: Discover public profiles

---

## OSINT Techniques

### Data Sources

| Source | Type | Data Retrieved |
|--------|------|----------------|
| Public APIs | Social | Profile information |
| WHOIS | Domain | Registration data |
| DNS Records | Technical | Email servers, etc. |
| Web Scraping | Social | Public posts |
| Breach Databases | Security | Exposed credentials |

---

## API Endpoints

### Start Footprint Scan
```http
POST /api/footprint/scan
Authorization: Bearer <token>
Content-Type: application/json

{
  "email": "user@example.com",
  "username": "johndoe"
}
```

### Response
```json
{
  "scan_id": "uuid",
  "status": "completed",
  "score": 65,
  "findings": [
    {
      "source": "LinkedIn",
      "category": "social",
      "severity": "low",
      "title": "Public profile found",
      "url": "https://linkedin.com/in/johndoe"
    },
    {
      "source": "HaveIBeenPwned",
      "category": "breach",
      "severity": "high",
      "title": "Email found in data breach",
      "description": "Adobe 2013 breach"
    }
  ],
  "recommendations": [
    "Enable 2FA on all accounts",
    "Change passwords for breached accounts",
    "Review privacy settings on social media"
  ]
}
```

---

## Privacy Score

| Score | Level | Meaning |
|-------|-------|---------|
| 80-100 | 🟢 Good | Minimal exposure |
| 60-79 | 🟡 Fair | Some public data |
| 40-59 | 🟠 Concerning | Significant exposure |
| 0-39 | 🔴 Poor | High-risk exposure |

---

## Code Flow

```python
# service/Footprint_Service.py

async def run_footprint_scan(self, user_id: str, data: dict) -> dict:
    """Run comprehensive footprint scan"""
    findings = []
    
    # 1. Check social media platforms
    if data.get('username'):
        social = await check_social_platforms(data['username'])
        findings.extend(social)
    
    # 2. Check data breaches
    if data.get('email'):
        breaches = await check_breaches(data['email'])
        findings.extend(breaches)
    
    # 3. Calculate privacy score
    score = calculate_privacy_score(findings)
    
    # 4. Generate recommendations
    recommendations = generate_recommendations(findings)
    
    # 5. Save to database
    scan = self.footprint_repo.create({
        'user_id': user_id,
        'email_scanned': data.get('email'),
        'username_scanned': data.get('username'),
        'score': score,
        'findings': findings,
        'recommendations': recommendations
    })
    
    return scan.to_dict()
```

---

## Ethical Considerations

1. **User Consent**: Only scan user's own data
2. **Rate Limiting**: Prevent abuse of external services
3. **Data Retention**: Scan results deleted after 30 days
4. **No Storage of Breached Passwords**: Only check, never store

---

## Related Documentation

- [Phishing Detection](../Phishing/overview.md)
- [Security Audit](../SecurityAudit/overview.md)
