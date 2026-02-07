# Fsociety SQL Database Schema

This document outlines the current SQL schema for the Fsociety platform. The database uses SQLite locally and is designed to be compatible with PostgreSQL for production.

## Overview

The database design follows a normalized structure with UUIDs (String(36)) as primary keys for all major entities.

## Table Definitions

### 1. Users Table (`users`)
Stores user profiles, authentication state, and session tokens.

| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | VARCHAR(36) | PRIMARY KEY | Unique identifier (UUID) |
| `email` | VARCHAR(255) | UNIQUE, NOT NULL | User's email |
| `username` | VARCHAR(50) | UNIQUE, NOT NULL | User's handle |
| `password_hash` | TEXT | NOT NULL | Hashed password |
| `refresh_token` | TEXT | | Current active refresh token |
| `refresh_token_expires_at` | DATETIME | | Expiration timestamp for session |
| `full_name` | VARCHAR(100) | | Optional full name |
| `phone` | VARCHAR(20) | | Optional contact |
| `company` | VARCHAR(100) | | Optional organization |
| `bio` | TEXT | | Optional biography |
| `role` | VARCHAR(20) | DEFAULT 'user' | 'admin' or 'user' |
| `is_active` | BOOLEAN | DEFAULT TRUE | Account status |
| `created_at` | DATETIME | DEFAULT NOW() | Record creation time |
| `updated_at` | DATETIME | DEFAULT NOW() | Last profile update |
| `last_login_at` | DATETIME | | Last time user logged in |
| `last_login_ip` | VARCHAR(45) | | IP of last login (IPv6 compatible) |
| `password_changed_at` | DATETIME | | Last password rotate time |

---

### 2. User Statistics (`user_stats`)
Aggregated metrics for dashboard and health monitoring.

| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `user_id` | VARCHAR(36) | PRIMARY KEY, FK -> users(id) | Owner |
| `total_scans` | INTEGER | DEFAULT 0 | Network scans count |
| `phishing_checks` | INTEGER | DEFAULT 0 | |
| `security_scans` | INTEGER | DEFAULT 0 | SSL/Header scans |
| `file_analysis`| INTEGER | DEFAULT 0 | Malware checks |
| `vpn_configs` | INTEGER | DEFAULT 0 | |
| `reports_generated` | INTEGER | DEFAULT 0 | |
| `malware_detected` | INTEGER | DEFAULT 0 | Count of malicious findings |
| `last_active` | DATETIME | | Last activity timestamp |

---

### 3. Activity Logs (`activity_logs`)
Records all audit-able events in the system.

| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | VARCHAR(36) | PRIMARY KEY | Unique ID |
| `user_id` | VARCHAR(36) | FK -> users(id), ON DELETE SET NULL | User who performed action |
| `action` | VARCHAR(50) | NOT NULL | 'login', 'scan', 'vpn', etc. |
| `details` | JSON | | Context-specific JSON data |
| `ip_address` | VARCHAR(45) | | IP of the requester |
| `user_agent` | TEXT | | Client user agent |
| `timestamp` | DATETIME | DEFAULT NOW() | Event time |

---

### 4. Network Scans (`network_scans`)
Stores results of port scans, DNS, Subdomains, etc.

| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | VARCHAR(36) | PRIMARY KEY | Unique ID |
| `scan_number` | INTEGER | | Auto-incrementing human readable ID |
| `user_id` | VARCHAR(36) | FK -> users(id), ON DELETE CASCADE | Scanned by |
| `scan_type` | VARCHAR(30) | NOT NULL | 'domain', 'ip', 'ports', etc. |
| `target` | VARCHAR(255) | NOT NULL | The domain/IP scanned |
| `status` | VARCHAR(20) | DEFAULT 'pending' | 'completed', 'failed', 'running' |
| `results` | JSON | | Raw output from scanner tools |
| `error` | TEXT | | Error message if failed |
| `started_at` | DATETIME | DEFAULT NOW() | Start time |
| `completed_at` | DATETIME | | End time |
| `duration_ms` | INTEGER | | Execution time in ms |

---

### 5. Security Scans (`security_scans`)
Specialized scans like SSL, HTTP Headers, and Phishing.

| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | VARCHAR(36) | PRIMARY KEY | Unique ID |
| `user_id` | VARCHAR(36) | FK -> users(id) | Scanned by |
| `category` | VARCHAR(30) | NOT NULL | 'ssl', 'headers', 'phishing' |
| `target` | TEXT | NOT NULL | URL or Domain |
| `risk_level` | VARCHAR(20) | | 'low', 'medium', 'high', 'critical' |
| `results` | JSON | | Detailed scan results |
| `created_at` | DATETIME | DEFAULT NOW() | Scan time |

---

### 6. Chat Sessions (`chat_sessions`)
AI conversation metadata.

| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | VARCHAR(36) | PRIMARY KEY | Unique ID |
| `user_id` | VARCHAR(36) | FK -> users(id), ON DELETE CASCADE | Owner |
| `title` | VARCHAR(100) | DEFAULT 'New Chat' | Auto-generated title |
| `created_at` | DATETIME | DEFAULT NOW() | |
| `updated_at` | DATETIME | DEFAULT NOW() | |

---

### 7. Chat Messages (`chat_messages`)
Individual messages in AI sessions.

| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | VARCHAR(36) | PRIMARY KEY | |
| `session_id` | VARCHAR(36) | FK -> chat_sessions(id), ON DELETE CASCADE | Parent session |
| `role` | VARCHAR(20) | NOT NULL | 'user' or 'assistant' |
| `content` | TEXT | NOT NULL | Message content |
| `timestamp` | DATETIME | DEFAULT NOW() | |

---

### 8. Footprint Scans (`footprint_scans`)
OSINT investigation snapshots.

| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | VARCHAR(36) | PRIMARY KEY | |
| `user_id` | VARCHAR(36) | FK -> users(id) | |
| `email_scanned` | VARCHAR(255) | | |
| `username_scanned` | VARCHAR(50) | | |
| `phone_scanned` | VARCHAR(20) | | |
| `platforms_checked` | JSON | | |
| `score` | INTEGER | DEFAULT 100 | Risk score |
| `status` | VARCHAR(20) | DEFAULT 'pending' | |
| `progress` | INTEGER | DEFAULT 0 | |
| `recommendations` | JSON | | |
| `error_message` | TEXT | | |
| `started_at` | DATETIME | | |
| `completed_at` | DATETIME | | |

---

### 9. Footprint Findings (`footprint_findings`)
Individual OSINT data points.

| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | VARCHAR(36) | PRIMARY KEY | |
| `scan_id` | VARCHAR(36) | FK -> footprint_scans(id), ON DELETE CASCADE | |
| `category` | VARCHAR(50) | | e.g., 'social_media' |
| `source` | VARCHAR(50) | | e.g., 'Twitter' |
| `severity` | VARCHAR(20) | | |
| `title` | VARCHAR(255) | | |
| `description` | TEXT | | |
| `url` | TEXT | | |
| `found_at` | DATETIME | | |

---

### 10. VPN Servers (`vpn_servers`)
Nodes available for tunnel connection.

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
User-specific profile files.

| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | VARCHAR(36) | PRIMARY KEY | |
| `user_id` | VARCHAR(36) | FK -> users(id) | |
| `server_id` | VARCHAR(50) | FK -> vpn_servers(id) | |
| `config_type` | VARCHAR(20) | | 'openvpn' or 'wireguard' |
| `filename` | VARCHAR(255) | | |
| `config_content` | TEXT | | The actual config data |
| `created_at` | DATETIME | DEFAULT NOW() | |

---

### 12. Malware Scans (`malware_scans`)
File analysis results.

| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | VARCHAR(36) | PRIMARY KEY | |
| `user_id` | VARCHAR(36) | FK -> users(id) | |
| `filename` | VARCHAR(255) | | |
| `file_hash` | VARCHAR(64) | NOT NULL | |
| `risk_level` | VARCHAR(20) | | |
| `is_malicious` | BOOLEAN | | |
| `results` | JSON | | Full detailed report |
| `created_at` | DATETIME | | |

---

### 13. Reports (`reports`)
Generated audit documents.

| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | VARCHAR(36) | PRIMARY KEY | |
| `user_id` | VARCHAR(36) | FK -> users(id) | |
| `title` | VARCHAR(255) | | |
| `report_type` | VARCHAR(50) | | e.g., 'comprehensive' |
| `file_path` | TEXT | | Storage location |
| `created_at` | DATETIME | DEFAULT NOW() | |

---

### 14. Password Reset Tokens (`password_reset_tokens`)
One-time tokens for account recovery.

| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | VARCHAR(36) | PRIMARY KEY | |
| `user_id` | VARCHAR(36) | FK -> users(id), ON DELETE CASCADE | |
| `token_hash` | VARCHAR(255) | NOT NULL, INDEX | |
| `expires_at` | DATETIME | NOT NULL | |
| `created_at` | DATETIME | | |

---

## JSON Structure Reference

Columns with JSON type store structured metadata:

1. **`activity_logs.details`**: Context like browser IP or scan target.
2. **`network_scans.results`**: Port lists, DNS data, and raw tool output.
3. **`security_scans.results`**: Certificate details, header analysis, and threat indicators.
4. **`malware_scans.results`**: Vendor detection counts and sandbox behavior.
5. **`footprint_scans.platforms_checked`**: List of social/leak sources analyzed.
