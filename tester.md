# Fsociety Platform - Testing Protocol

This document provides a step-by-step guide to verify all functionalities of the Fsociety Cybersecurity Platform.

## 1. Authentication Flow
**Goal**: Verify user creation, login, and access control.

1.  **Signup (New User)**
    *   Navigate to `#/signup`.
    *   Enter valid details (Email, Username).
    *   **Test Password Strength**: Enter `weak` (should be red). Enter `StrongP@ss1` (should be green).
    *   Click "Initialize User".
    *   *Expected*: Redirect to Dashboard or Success Toast.

2.  **Login**
    *   Navigate to `#/login`.
    *   Enter invalid credentials. *Expected*: Error Toast.
    *   Enter valid credentials. *Expected*: Redirect to `#/dashboard`.

3.  **Logout**
    *   Click "LOGOUT" in the top right.
    *   *Expected*: User session cleared, redirect to login.

## 2. Network Scanning Module
**Goal**: Verify scanning capabilities.

1.  **Domain Scan**
    *   Navigate to **Network Scan**.
    *   Select "Full Domain Scan".
    *   Target: `example.com`.
    *   Click "Initiate Scan".
    *   *Expected*: JSON results displayed with pretty coloring showing IP and subdomains.

2.  **Port Scan**
    *   Select "Port Scan".
    *   Target: `scanme.nmap.org` (or localhost).
    *   *Expected*: List of open ports.

## 3. Security Audit Module
**Goal**: Verify security tools.

1.  **SSL Scan**
    *   Navigate to **Security Audit**.
    *   Select "SSL/TLS Scan".
    *   Target: `google.com`.
    *   *Expected*: Certificate chain details and validity.

2.  **Headers Analysis**
    *   Select "HTTP Headers Analysis".
    *   Target: `github.com`.
    *   *Expected*: Security headers breakdown (HSTS, CSP, etc.).

## 4. File Analysis Module
**Goal**: Verify malware detection simulation.

1.  **Hash Check**
    *   Navigate to **File Analysis**.
    *   Select "Check Hash".
    *   Enter a known hash (e.g., empty MD5 `d41d8cd98f00b204e9800998ecf8427e`).
    *   *Expected*: Result showing safe/malicious status.

## 5. VPN Configuration
**Goal**: Verify config generation.

1.  **OpenVPN**
    *   Navigate to **VPN Configs**.
    *   Select "OpenVPN" tab.
    *   Enter Server Address: `vpn.test.com`.
    *   Click "Generate".
    *   *Expected*: New config card appears in list.

## 6. Admin Panel (Admin Only)
**Goal**: Verify admin privileges.

1.  **Access Control**
    *   Log in as a standard user.
    *   Check sidebar. *Expected*: "Admin Panel" should be **hidden**.
2.  **Admin Login**
    *   **Default Admin**: Email: `admin@fsociety.com`, Password: `Admin123!` (Created on server start).
    *   Log in with these credentials.
    *   Navigate to **Admin Panel**.
    *   *Expected*: List of all users.
    *   **Action**: Delete a test user. *Expected*: User removed from list.

## 7. History & Persistence
**Goal**: Verify data saving.

1.  **Scan History**
    *   Navigate to **Operation History**.
    *   *Expected*: List of all scans performed in previous steps.
    *   Click "VIEW". *Expected*: Modal opens with full JSON results.

---
**Note**: Ensure backend is running (`fastapi dev`) before starting tests.
