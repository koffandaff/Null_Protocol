# Normalization and Optimization Plan

This document explains the normalization strategy used for the SQL database and plans for performance optimization.

## Data Normalization

The schema is designed to adhere to **Third Normal Form (3NF)** wherever practical, while using `JSONB` for specific complex data structures to maintain flexibility.

### 1. First Normal Form (1NF)
- All tables have a Primary Key (`id`).
- All columns contain atomic values (Except for JSONB fields which are used for "blobs" that don't need relational querying).
- No repeating groups.

### 2. Second Normal Form (2NF)
- All non-key attributes are fully dependent on the Primary Key.
- Composite keys are avoided; UUIDs serve as simple Primary Keys.
- Example: **Chat Messages** are linked to a **Chat Session** via `session_id`. All message data (content, role) depends only on the message's unique `id`.

### 3. Third Normal Form (3NF)
- No transitive dependencies.
- Example: In the `users` table, all fields (bio, company, role, refresh_token) describe the user identified by the `id`. We don't store "Company Address" in the `users` table, as that would depend on the company, not the user.

---

## Strategic Use of JSONB

While we follow relational principles, we use `JSONB` (in PostgreSQL) or `TEXT/BLOB` (in simple SQL) for the following:

- **Scan Results**: The output of a network scan or security audit can be highly varied and deeply nested. Storing this as JSONB allows the UI to render whatever the tool produces without requiring dozens of specialized tables.
- **Activity Details**: Different actions (login vs. scan) have different metadata. JSONB handles this polymorphism efficiently.

---

## Indexing Strategy

To maintain performance as the database grows, we will implement the following indexes:

| Table | Column(s) | Index Type | Reason |
| :--- | :--- | :--- | :--- |
| `users` | `email` | B-TREE (Unique) | Frequent login lookups |
| `users` | `username` | B-TREE (Unique) | Profile lookups |
| `activity_logs` | `user_id`, `timestamp` | B-TREE | Rendering user history sorted by time |
| `network_scans` | `user_id`, `started_at` | B-TREE | Dashboard scan history |
| `chat_messages` | `session_id`, `timestamp` | B-TREE | Loading chat history |
| `activity_logs` | `details` | GIN | Querying inside JSON blobs for admin searches |

---

## Data Integrity Constraints

- **Foreign Keys**: All child tables (scans, messages, sessions) use `user_id` as a foreign key with `ON DELETE CASCADE`.
- **Enums**: Roles (`admin`, `user`) and Scan Statuses (`pending`, `completed`, `running`, `failed`) are constrained at the database level using `CHECK` constraints or Native Enums.
- **Timestamps**: `created_at` and `updated_at` are automatically managed via DB triggers or application-level hooks to ensure audit-ability.
