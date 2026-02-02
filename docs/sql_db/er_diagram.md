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

    VPN_SERVERS ||--o{ VPN_CONFIGS : "configs"
    CHAT_SESSIONS ||--o{ CHAT_MESSAGES : "msgs"
    FOOTPRINT_SCANS ||--o{ FOOTPRINT_FINDINGS : "findings"

    USERS {
        uuid id PK
        string email
        string username
        string password_hash
        string role
        string refresh_token
        timestamp refresh_token_expires_at
        boolean is_active
        timestamp created_at
    }

    USER_STATS {
        uuid user_id PK, FK
        int total_scans
        int security_scans
        int phishing_checks
        int malware_detected
        timestamp last_active
    }

    ACTIVITY_LOGS {
        uuid id PK
        uuid user_id FK
        string action
        jsonb details
        inet ip_address
        timestamp timestamp
    }

    NETWORK_SCANS {
        uuid id PK
        int scan_number
        uuid user_id FK
        string scan_type
        string target
        string status
        jsonb results
        timestamp started_at
    }

    SECURITY_SCANS {
        uuid id PK
        uuid user_id FK
        string category
        text target
        string risk_level
        jsonb results
        timestamp created_at
    }

    CHAT_SESSIONS {
        uuid id PK
        uuid user_id FK
        string title
        timestamp updated_at
    }

    CHAT_MESSAGES {
        uuid id PK
        uuid session_id FK
        string role
        text content
        timestamp timestamp
    }

    FOOTPRINT_SCANS {
        uuid id PK
        uuid user_id FK
        string email_scanned
        int score
        string status
    }

    FOOTPRINT_FINDINGS {
        uuid id PK
        uuid scan_id FK
        string category
        string source
        string severity
        text title
    }

    VPN_CONFIGS {
        uuid id PK
        uuid user_id FK
        string server_id FK
        text config_content
        timestamp created_at
    }

    VPN_SERVERS {
        string id PK
        string name
        string address
        string region
        boolean is_online
    }

    MALWARE_SCANS {
        uuid id PK
        uuid user_id FK
        string filename
        string file_hash
        boolean is_malicious
        jsonb results
    }

    REPORTS {
        uuid id PK
        uuid user_id FK
        string title
        string report_type
        text file_path
        timestamp created_at
    }
```

## Key Relationships

1.  **Users (Central Hub)**:
    -   Stores authentication, profile, and session state (`refresh_token`).
    -   One-to-One with `USER_STATS` for performance.
    -   One-to-Many with all activity and scan history.

2.  **Sessions & Messages**:
    -   Hierarchical relationship between `CHAT_SESSIONS` and `CHAT_MESSAGES`.

3.  **Scans & Findings**:
    -   `FOOTPRINT_SCANS` extracts multiple `FOOTPRINT_FINDINGS`.
    -   `SECURITY_SCANS` covers SSL, Headers, and Phishing.

4.  **VPN Infrastructure**:
    -   `VPN_SERVERS` is a static list managed by admins.
    -   `VPN_CONFIGS` links a user to a specific server.

## Data Lifecycle

-   **Cascading Deletes**: Deleting a User triggers cascading deletes for all associated scans, chats, and configurations to ensure GDPR compliance.
-   **Soft vs Hard Deletes**: Activity logs should be retained with a null `user_id` if a user is deleted (Audit trail), whereas private data (Chats/Scans) is hard-deleted.
