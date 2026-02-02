# 🌐 API Layer

This document explains how API calls are handled in the Fsociety frontend.

---

## Table of Contents

- [Overview](#overview)
- [Api Class](#api-class)
- [Request Methods](#request-methods)
- [Error Handling](#error-handling)
- [Token Injection](#token-injection)

---

## Overview

The API layer (`api.js`) provides a centralized way to:

- Make HTTP requests to the backend
- Automatically inject Authorization headers
- Handle token refresh on 401 errors
- Provide consistent error handling

---

## Api Class

```javascript
// frontend/js/api.js

export class Api {
    static baseUrl = 'http://localhost:8000/api';
    
    // ==================== CORE REQUEST ====================
    static async request(endpoint, options = {}) {
        const url = `${this.baseUrl}${endpoint}`;
        
        // Default headers
        const headers = {
            'Content-Type': 'application/json',
            ...options.headers
        };
        
        // Add auth token if available
        const token = localStorage.getItem('access_token');
        if (token) {
            headers['Authorization'] = `Bearer ${token}`;
        }
        
        try {
            const response = await fetch(url, {
                ...options,
                headers,
                credentials: 'include'  // Include cookies
            });
            
            // Handle 401 - try refresh
            if (response.status === 401) {
                const refreshed = await this.refreshToken();
                if (refreshed) {
                    // Retry with new token
                    headers['Authorization'] = `Bearer ${localStorage.getItem('access_token')}`;
                    return this.request(endpoint, { ...options, headers });
                } else {
                    // Logout on refresh failure
                    this.handleAuthError();
                    throw new Error('Session expired');
                }
            }
            
            // Parse response
            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.detail || 'Request failed');
            }
            
            return data;
            
        } catch (error) {
            console.error(`API Error [${endpoint}]:`, error);
            throw error;
        }
    }
    
    // ==================== REFRESH TOKEN ====================
    static async refreshToken() {
        try {
            const response = await fetch(`${this.baseUrl}/auth/refresh`, {
                method: 'POST',
                credentials: 'include'
            });
            
            if (response.ok) {
                const data = await response.json();
                localStorage.setItem('access_token', data.access_token);
                return true;
            }
            return false;
        } catch {
            return false;
        }
    }
    
    // ==================== AUTH ERROR HANDLER ====================
    static handleAuthError() {
        localStorage.removeItem('access_token');
        localStorage.removeItem('user');
        window.location.hash = '#/login';
    }
}
```

---

## Request Methods

```javascript
// Convenience methods

static async get(endpoint) {
    return this.request(endpoint, { method: 'GET' });
}

static async post(endpoint, data) {
    return this.request(endpoint, {
        method: 'POST',
        body: JSON.stringify(data)
    });
}

static async put(endpoint, data) {
    return this.request(endpoint, {
        method: 'PUT',
        body: JSON.stringify(data)
    });
}

static async delete(endpoint) {
    return this.request(endpoint, { method: 'DELETE' });
}
```

---

## Usage Examples

```javascript
// GET request
const users = await Api.get('/admin/users');

// POST request
const result = await Api.post('/scans/network', {
    target: '192.168.1.1',
    scan_type: 'quick'
});

// PUT request
await Api.put(`/user/profile`, {
    full_name: 'John Doe',
    company: 'Fsociety'
});

// DELETE request
await Api.delete(`/chat/sessions/${sessionId}`);
```

---

## Error Handling

### In Views

```javascript
// frontend/js/views/dashboard.js

async loadData() {
    try {
        const stats = await Api.get('/user/stats');
        this.renderStats(stats);
    } catch (error) {
        Utils.showToast(error.message, 'error');
    }
}
```

### Common Error Responses

| Status | Meaning | Frontend Action |
|--------|---------|-----------------|
| 400 | Bad Request | Show error message |
| 401 | Unauthorized | Refresh or redirect to login |
| 403 | Forbidden | Show permission denied |
| 404 | Not Found | Show not found message |
| 429 | Rate Limited | Show rate limit message |
| 500 | Server Error | Show generic error |

---

## Request/Response Flow

```
View                      Api                        Backend
  │                         │                           │
  │── Api.post(endpoint) ──▶│                           │
  │                         │                           │
  │                         │── fetch with headers ────▶│
  │                         │   Authorization: Bearer   │
  │                         │   Content-Type: JSON      │
  │                         │   credentials: include    │
  │                         │                           │
  │                         │◀── Response ──────────────│
  │                         │                           │
  │                         │ if 401: refreshToken()    │
  │                         │ if error: throw Error     │
  │                         │                           │
  │◀── Parsed JSON ─────────│                           │
```

---

## Related Documentation

- [Auth](../Auth/overview.md)
- [Routing](../Routing/overview.md)
