# 🕵️‍♂️ Fsociety Cybersecurity Platform

**Fsociety** is a high-performance, modular cybersecurity scanning and analysis platform built with **FastAPI**. It provides a comprehensive suite of tools for security professionals and enthusiasts to analyze domains, networks, and files for vulnerabilities and threats.

## ✨ Key Features

### 🛡️ Security Analysis
- **SSL/TLS Scanner**: Deep analysis of SSL certificates and configurations.
- **HTTP Header Analyzer**: Checks for security headers (HSTS, CSP, etc.) and best practices.
- **Phishing Detection**: Real-time URL reputation and phishing indicator analysis.
- **File Intelligence**: Malware hash checking and file type validation.

### 🌐 Network & Domain Tools
- **Advanced DNS**: Full DNS record lookups (A, AAAA, MX, TXT, etc.).
- **WHOIS Intelligence**: Comprehensive domain registration data.
- **Infrastructure Scanning**: IP geolocation and port availability scanning.
- **Subdomain Discovery**: Automated discovery of subdomains.

### 🔒 Enterprise-Grade Security
- **SSRF Guard**: Built-in protection against Server-Side Request Forgery.
- **JWT Authentication**: Secure user management with access and refresh tokens.
- **Role-Based Access**: Granular permissions for Users and Admins.
- **Rate Limiting**: Intelligent API protection.

## 🛠️ Technology Stack
- **Backend**: FastAPI (Python 3.9+)
- **Storage**: In-memory TempDb (NoSQL Style)
- **Frontend**: Vanilla HTML/CSS/JS (In development)
- **Security**: JWT, Argon2 Password Hashing, SSRF Protection

## 🚀 Quick Start

### Prerequisites
- Python 3.9 or higher
- `pip` package manager

### Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/koffandaff/Fsociety_WebService.git
   cd Fsociety_WebService
   ```
2. Install dependencies:
   ```bash
   pip install -r backend/requirements.txt
   ```
3. Run the development server:
   ```bash
   cd backend
   fastapi dev
   ```
4. Access the API documentation:
   - Swagger UI: `http://localhost:8000/docs`
   - ReDoc: `http://localhost:8000/redoc`

## 📂 Project Structure
```text
backend/
├── routers/     # API endpoints
├── services/    # Business logic
├── models/      # Data schemas & TempDb
├── utils/       # Shared utilities
└── config/      # App configuration
```

## 📜 License
This project is for educational and security testing purposes only. Refer to the `LICENSE` file for more details.

---
*"Our democracy has been hacked. Our privacy has been violated. But now, we have the tools."* 🎭
