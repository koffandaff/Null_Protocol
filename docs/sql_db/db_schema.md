# Fsociety SQL Database Schema

This document outlines the proposed SQL schema for the Fsociety platform, transitioning from the current in-memory/JSON implementation to a robust relational database (PostgreSQL recommended).

## Overview

The database design follows a normalized structure to ensure data integrity, scalability, and performance. We use UUIDs as primary keys for all entities to avoid enumeration attacks and simplify distributed system integration.

## Table Definitions

### 1. Users Table (`users`)
Stores user profiles, authentication state, and session tokens.

| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | UUID | PRIMARY KEY | Unique identifier |
| `email` | VARCHAR(255) | UNIQUE, NOT NULL | User's email |
| `username` | VARCHAR(50) | UNIQUE, NOT NULL | User's handle |
| `password_hash` | TEXT | NOT NULL | Argon2/BCrypt hashed password |
| `refresh_token` | TEXT | | Current active refresh token |
| `refresh_token_expires_at` | TIMESTAMP | | Expiration timestamp for session |
| `full_name` | VARCHAR(100) | | Optional full name |
| `phone` | VARCHAR(20) | | Optional contact |
| `company` | VARCHAR(100) | | Optional organization |
| `bio` | TEXT | | Optional biography (max 500 chars) |
| `role` | VARCHAR(20) | DEFAULT 'user' | 'admin' or 'user' |
| `is_active` | BOOLEAN | DEFAULT TRUE | Account status (Admin can disable) |
| `created_at` | TIMESTAMP | DEFAULT NOW() | Record creation time |
| `updated_at` | TIMESTAMP | DEFAULT NOW() | Last profile update |
| `last_login_at` | TIMESTAMP | | Last time user logged in |
| `last_login_ip` | INET | | IP of last login |
| `password_changed_at` | TIMESTAMP | | Last password rotate time |

---

### 2. Activity Logs (`activity_logs`)
Records all audit-able events in the system for the Live Activity Feed.

| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | UUID | PRIMARY KEY | Unique ID |
| `user_id` | UUID | FK -> users(id), ON DELETE SET NULL | User who performed action |
| `action` | VARCHAR(50) | NOT NULL | 'login', 'scan', 'vpn', etc. |
| `details` | JSONB | | Context-specific JSON data |
| `ip_address` | INET | | IP of the requester |
| `user_agent` | TEXT | | Client user agent |
| `timestamp` | TIMESTAMP | DEFAULT NOW() | Event time |

---

### 3. User Statistics (`user_stats`)
Aggregated metrics for dashboard and health monitoring.

| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `user_id` | UUID | PRIMARY KEY, FK -> users(id) | Owner |
| `total_scans` | INTEGER | DEFAULT 0 | Network scans count |
| `phishing_checks` | INTEGER | DEFAULT 0 | |
| `security_scans` | INTEGER | DEFAULT 0 | SSL/Header scans |
| `file_analysis`| INTEGER | DEFAULT 0 | Malware checks |
| `vpn_configs` | INTEGER | DEFAULT 0 | |
| `reports_generated` | INTEGER | DEFAULT 0 | |
| `malware_detected` | INTEGER | DEFAULT 0 | Count of malicious findings |
| `last_active` | TIMESTAMP | | Last activity timestamp |

---

### 5. Network Scans (`network_scans`)
Stores results of port scans, DNS, Subdomains, etc.

| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | UUID | PRIMARY KEY | Unique ID |
| `scan_number` | SERIAL | | Human readable scan ID |
| `user_id` | UUID | FK -> users(id), ON DELETE CASCADE | Scanned by |
| `scan_type` | VARCHAR(30) | NOT NULL | 'domain', 'ip', 'ports', etc. |
| `target` | VARCHAR(255) | NOT NULL | The domain/IP scanned |
| `status` | VARCHAR(20) | DEFAULT 'pending' | 'completed', 'failed', 'running' |
| `results` | JSONB | | Raw output from scanner tools |
| `error` | TEXT | | Error message if failed |
| `started_at` | TIMESTAMP | DEFAULT NOW() | Start time |
| `completed_at` | TIMESTAMP | | End time |
| `duration_ms` | INTEGER | | Execution time in ms |

---

### 6. Security Scans (`security_scans`)
Specialized scans like SSL, HTTP Headers, and Phishing.

| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | UUID | PRIMARY KEY | Unique ID |
| `user_id` | UUID | FK -> users(id) | Scanned by |
| `category` | VARCHAR(30) | NOT NULL | 'ssl', 'headers', 'phishing' |
| `target` | TEXT | NOT NULL | URL or Domain |
| `risk_level` | VARCHAR(20) | | 'low', 'medium', 'high', 'critical' |
| `results` | JSONB | | Detailed scan results |
| `created_at` | TIMESTAMP | DEFAULT NOW() | Scan time |

---

### 7. Chat Sessions & Messages
Relational storage for AI interactions.

#### Table: `chat_sessions`
| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | UUID | PRIMARY KEY | Unique ID |
| `user_id` | UUID | FK -> users(id), ON DELETE CASCADE | Owner |
| `title` | VARCHAR(100) | DEFAULT 'New Chat' | User-provided or auto-generated |
| `created_at` | TIMESTAMP | DEFAULT NOW() | |
| `updated_at` | TIMESTAMP | DEFAULT NOW() | |

#### Table: `chat_messages`
| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | UUID | PRIMARY KEY | |
| `session_id` | UUID | FK -> chat_sessions(id), ON DELETE CASCADE | Parent session |
| `role` | VARCHAR(20) | NOT NULL | 'user' or 'assistant' |
| `content` | TEXT | NOT NULL | The actual message |
| `timestamp` | TIMESTAMP | DEFAULT NOW() | |

---

### 8. Digital Footprint
Tracking OSINT findings.

#### Table: `footprint_scans`
| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | UUID | PRIMARY KEY | |
| `user_id` | UUID | FK -> users(id) | |
| `email_scanned` | VARCHAR(255) | | |
| `username_scanned` | VARCHAR(50) | | |
| `score` | INTEGER | 0-100 | Risk score |
| `status` | VARCHAR(20) | | |
| `started_at` | TIMESTAMP | | |
| `completed_at` | TIMESTAMP | | |

#### Table: `footprint_findings`
| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | UUID | PRIMARY KEY | |
| `scan_id` | UUID | FK -> footprint_scans(id), ON DELETE CASCADE | |
| `category` | VARCHAR(50) | | e.g., 'social_media' |
| `source` | VARCHAR(50) | | e.g., 'Twitter' |
| `severity` | VARCHAR(20) | | |
| `title` | VARCHAR(255) | | |
| `description` | TEXT | | |
| `url` | TEXT | | |
| `found_at` | TIMESTAMP | | |

---

### 9. Malware/File Analysis (`malware_scans`)
| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | UUID | PRIMARY KEY | |
| `user_id` | UUID | FK -> users(id) | |
| `filename` | VARCHAR(255) | | |
| `file_hash` | VARCHAR(64) | NOT NULL | SHA256 usually |
| `risk_level` | VARCHAR(20) | | |
| `is_malicious` | BOOLEAN | | |
| `results` | JSONB | | Full info (Virustotal, details) |
| `created_at` | TIMESTAMP | | |

---

### 10. VPN Servers (`vpn_servers`)
Manageable server list for the VPN gateway.

| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | VARCHAR(50) | PRIMARY KEY | e.g., 'us-east' |
| `name` | VARCHAR(100) | NOT NULL | Display name |
| `address` | VARCHAR(255) | NOT NULL | IP or Domain |
| `region` | VARCHAR(50) | | |
| `is_online` | BOOLEAN | DEFAULT TRUE | |
| `current_load` | VARCHAR(10) | | e.g., '42%' |

---

### 11. VPN Configurations (`vpn_configs`)
Generated configuration files for users.

| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | UUID | PRIMARY KEY | |
| `user_id` | UUID | FK -> users(id) | |
| `server_id` | VARCHAR(50) | FK -> vpn_servers(id) | |
| `config_type` | VARCHAR(20) | | 'openvpn' |
| `filename` | VARCHAR(255) | | |
| `config_content` | TEXT | | The generated config file |
| `created_at` | TIMESTAMP | DEFAULT NOW() | |

---

### 12. Reports (`reports`)
Generated PDF/HTML reports for security audits.

| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | UUID | PRIMARY KEY | |
| `user_id` | UUID | FK -> users(id) | |
| `title` | VARCHAR(255) | | |
| `report_type` | VARCHAR(50) | | 'comprehensive', 'scan_summary' |
| `file_path` | TEXT | | Path to stored report |
| `created_at` | TIMESTAMP | DEFAULT NOW() | |

---

## JSONB Structure Reference

To maintain flexibility across diverse scanner outputs, several columns use `JSONB`. Below are the expected structures for these fields.

### 1. `activity_logs.details`
| Action | Example Structure |
| :--- | :--- |
| `login` | `{"ip": "1.1.1.1", "success": true}` |
| `scan` | `{"scan_type": "ports", "target": "example.com"}` |
| `vpn` | `{"server": "us-east", "action": "generated"}` |

### 2. `network_scans.results`
Stores the output of `network_tools`.
- `port_results`: `[{"port": 80, "state": "open", "service": "http"}]`
- `dns_records`: `{"A": ["..."], "MX": ["..."]}`
- `whois`: `{"registrar": "...", "expiry": "..."}`

### 3. `security_scans.results`
- **SSL**: `{"certificate": {...}, "tls_v1_3": true, "vulnerabilities": []}`
- **Headers**: `{"server": "nginx", "missing_headers": ["Content-Security-Policy"]}`
- **Phishing**: `{"risk_score": 0.85, "indicators": ["typosquatting", "low_domain_age"]}`

### 4. `malware_scans.results`
- `virustotal`: `{"positives": 5, "total": 70, "permalink": "..."}`
- `static_analysis`: `{"strings": ["..."], "is_packed": false}`

### 5. `footprint_scans.findings`
Reference to structure in `footprint_findings` table, but also cached in `FootprintScanResult`.
- `category`: `email_exposure`, `social_media`, `data_breach`
- `source`: `Twitter`, `LinkedIn`, `HaveIBeenPwned`
