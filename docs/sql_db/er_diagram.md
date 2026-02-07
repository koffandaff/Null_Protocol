# Entity Relationship Diagram (ERD)

The following diagram visualizes the relationships between the Fsociety database entities.

```mermaid
erDiagram
    USERS ||--|| USER_STATS : "stats"
    USERS ||--o{ ACTIVITY_LOGS : "acts"
    USERS ||--o{ NETWORK_SCANS : "scans"
    USERS ||--o{ SECURITY_SCANS : "sec_scans"
    USERS ||--o{ CHAT_SESSIONS : "chats"
    USERS ||--o{ FOOTPRINT_SCANS : "osint"
    USERS ||--o{ VPN_CONFIGS : "vpns"
    USERS ||--o{ MALWARE_SCANS : "files"
    USERS ||--o{ REPORTS : "reps"
    USERS ||--o{ PASSWORD_RESET_TOKENS : "resets"

    VPN_SERVERS ||--o{ VPN_CONFIGS : "configs"
    CHAT_SESSIONS ||--o{ CHAT_MESSAGES : "msgs"
    FOOTPRINT_SCANS ||--o{ FOOTPRINT_FINDINGS : "findings"

    USERS {
        string id PK
        string email UK
        string username UK
        text password_hash
        text refresh_token
        datetime refresh_token_expires_at
        string full_name
        string phone
        string company
        text bio
        string role
        boolean is_active
        datetime created_at
        datetime updated_at
        datetime last_login_at
        string last_login_ip
        datetime password_changed_at
    }

    USER_STATS {
        string user_id PK, FK
        int total_scans
        int phishing_checks
        int security_scans
        int file_analysis
        int vpn_configs
        int reports_generated
        int malware_detected
        datetime last_active
    }

    ACTIVITY_LOGS {
        string id PK
        string user_id FK
        string action
        json details
        string ip_address
        text user_agent
        datetime timestamp
    }

    NETWORK_SCANS {
        string id PK
        int scan_number
        string user_id FK
        string scan_type
        string target
        string status
        json results
        text error
        datetime started_at
        datetime completed_at
        int duration_ms
    }

    SECURITY_SCANS {
        string id PK
        string user_id FK
        string category
        text target
        string risk_level
        json results
        datetime created_at
    }

    CHAT_SESSIONS {
        string id PK
        string user_id FK
        string title
        datetime created_at
        datetime updated_at
    }

    CHAT_MESSAGES {
        string id PK
        string session_id FK
        string role
        text content
        datetime timestamp
    }

    FOOTPRINT_SCANS {
        string id PK
        string user_id FK
        string email_scanned
        string username_scanned
        string phone_scanned
        json platforms_checked
        int score
        string status
        int progress
        json recommendations
        text error_message
        datetime started_at
        datetime completed_at
    }

    FOOTPRINT_FINDINGS {
        string id PK
        string scan_id FK
        string category
        string source
        string severity
        string title
        text description
        text url
        datetime found_at
    }

    VPN_CONFIGS {
        string id PK
        string user_id FK
        string server_id FK
        string config_type
        string filename
        text config_content
        datetime created_at
    }

    VPN_SERVERS {
        string id PK
        string name
        string address
        string region
        boolean is_online
        string current_load
    }

    MALWARE_SCANS {
        string id PK
        string user_id FK
        string filename
        string file_hash
        string risk_level
        boolean is_malicious
        json results
        datetime created_at
    }

    REPORTS {
        string id PK
        string user_id FK
        string title
        string report_type
        text file_path
        datetime created_at
    }

    PASSWORD_RESET_TOKENS {
        string id PK
        string user_id FK
        string token_hash
        datetime expires_at
        datetime created_at
    }
```

## Key Relationships

1.  **Users (Central Hub)**:
    -   Stores authentication, profile, and session state (`refresh_token`).
    -   One-to-One with `USER_STATS` for performance.
    -   One-to-Many with all activity and scan history.

2.  **Sessions & Messages**:
    -   Hierarchical relationship between `CHAT_SESSIONS` and `CHAT_MESSAGES`.

3.  **OSINT Architecture**:
    -   `FOOTPRINT_SCANS` extracts multiple `FOOTPRINT_FINDINGS`.

4.  **VPN Infrastructure**:
    -   `VPN_SERVERS` is a static list managed by admins.
    -   `VPN_CONFIGS` links a user to a specific server.

5.  **Audit & Safety**:
    -   `ACTIVITY_LOGS` tracks every major action.
    -   `PASSWORD_RESET_TOKENS` manages account recovery state.
