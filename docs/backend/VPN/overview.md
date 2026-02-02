# 🔒 VPN Configuration Module

This document explains how VPN configuration generation works in Fsociety.

---

## Overview

The VPN module generates OpenVPN configuration files with real PKI certificates:

- **Certificate Generation**: Creates CA, server, and client certificates
- **Configuration Files**: Produces ready-to-use .ovpn files
- **Server Selection**: Allows choosing from available VPN servers

---

## How It Works

```
┌───────────────────────────────────────────────────────────────────┐
│                    VPN Configuration Flow                         │
└───────────────────────────────────────────────────────────────────┘

  1. User selects server        2. Backend generates certs
     ┌──────────┐                   ┌─────────────────┐
     │ Frontend │ ───────────────▶  │ VPN_Service.py  │
     │ (select) │                   │                 │
     └──────────┘                   │ • Generate CA   │
                                    │ • Create keys   │
                                    │ • Sign certs    │
                                    └─────────────────┘
                                            │
                                            ▼
  4. .ovpn file downloaded      3. Config assembled
     ┌──────────┐                   ┌─────────────────┐
     │ Client   │ ◀──────────────── │ .ovpn file      │
     │ OpenVPN  │                   │ with embedded   │
     └──────────┘                   │ certificates    │
                                    └─────────────────┘
```

---

## Files

| File | Purpose |
|------|---------|
| `routers/VPN_Router.py` | API endpoints |
| `service/VPN_Service.py` | Certificate generation |
| `utils/vpn_tools.py` | PKI utilities |

---

## API Endpoints

### Get Available Servers
```http
GET /api/vpn/servers
Authorization: Bearer <token>
```

### Generate Configuration
```http
POST /api/vpn/generate
Authorization: Bearer <token>
Content-Type: application/json

{
  "server_id": "us-east-1"
}
```

### Response
```json
{
  "config_id": "uuid",
  "filename": "fsociety_us-east-1.ovpn",
  "config_content": "client\ndev tun\n...",
  "created_at": "2024-01-01T12:00:00"
}
```

---

## Certificate Generation

### Using Python Cryptography Library

```python
# utils/vpn_tools.py

from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa

def generate_ca():
    """Generate Certificate Authority"""
    # Generate CA private key
    ca_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048
    )
    
    # Create CA certificate
    ca_name = x509.Name([
        x509.NameAttribute(NameOID.COUNTRY_NAME, "US"),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, "Fsociety VPN"),
        x509.NameAttribute(NameOID.COMMON_NAME, "Fsociety CA")
    ])
    
    ca_cert = (
        x509.CertificateBuilder()
        .subject_name(ca_name)
        .issuer_name(ca_name)
        .public_key(ca_key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(datetime.utcnow())
        .not_valid_after(datetime.utcnow() + timedelta(days=3650))
        .add_extension(
            x509.BasicConstraints(ca=True, path_length=None),
            critical=True
        )
        .sign(ca_key, hashes.SHA256())
    )
    
    return ca_key, ca_cert
```

---

## OpenVPN Config Structure

```
client
dev tun
proto udp
remote vpn.fsociety.com 1194
resolv-retry infinite
nobind
persist-key
persist-tun
cipher AES-256-CBC
auth SHA256
verb 3

<ca>
-----BEGIN CERTIFICATE-----
[CA Certificate]
-----END CERTIFICATE-----
</ca>

<cert>
-----BEGIN CERTIFICATE-----
[Client Certificate]
-----END CERTIFICATE-----
</cert>

<key>
-----BEGIN RSA PRIVATE KEY-----
[Client Private Key]
-----END RSA PRIVATE KEY-----
</key>
```

---

## Security Notes

1. **Private keys never leave the client**
2. **Each user gets unique certificates**
3. **Certificates are revocable**
4. **TLS 1.2+ encrypted tunnel**

---

## Related Documentation

- [Cryptography Docs](https://cryptography.io/)
- [OpenVPN Manual](https://openvpn.net/community-resources/)
