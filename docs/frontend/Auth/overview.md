# 🔐 Frontend Authentication

This document explains how authentication is managed on the frontend.

---

## Table of Contents

- [Overview](#overview)
- [Token Management](#token-management)
- [Auth Class](#auth-class)
- [Login Flow](#login-flow)
- [Token Refresh](#token-refresh)
- [Protected Routes](#protected-routes)

---

## Overview

The frontend authentication system manages:

- **Access Token**: Short-lived JWT stored in localStorage
- **Refresh Token**: Long-lived JWT stored in HttpOnly cookie
- **User Data**: Current user info in localStorage
- **Route Protection**: Redirect unauthenticated users

---

## Token Management

### Storage Locations

| Token | Storage | Accessible by JS |
|-------|---------|------------------|
| Access Token | localStorage | ✅ Yes |
| Refresh Token | HttpOnly Cookie | ❌ No |
| User Data | localStorage | ✅ Yes |

### Why This Design?

1. **Access Token in localStorage**: Needed in Authorization header
2. **Refresh Token in Cookie**: Protected from XSS attacks
3. **Short-lived Access**: Limits exposure if token is stolen

---

## Auth Class

```javascript
// frontend/js/auth.js

export class Auth {
    
    // ==================== LOGIN ====================
    static async login(email, password) {
        const response = await Api.post('/auth/login', { 
            email, 
            password 
        });
        
        // Store access token
        localStorage.setItem('access_token', response.access_token);
        
        // Store user data
        localStorage.setItem('user', JSON.stringify(response.user));
        
        // Refresh token is automatically stored as HttpOnly cookie
        return response.user;
    }
    
    // ==================== LOGOUT ====================
    static async logout() {
        try {
            await Api.post('/auth/logout');
        } finally {
            // Always clear local storage
            localStorage.removeItem('access_token');
            localStorage.removeItem('user');
        }
    }
    
    // ==================== CHECK AUTH ====================
    static isAuthenticated() {
        return !!localStorage.getItem('access_token');
    }
    
    static getCurrentUser() {
        const user = localStorage.getItem('user');
        return user ? JSON.parse(user) : null;
    }
    
    static isAdmin() {
        const user = this.getCurrentUser();
        return user && user.role === 'admin';
    }
    
    static getToken() {
        return localStorage.getItem('access_token');
    }
}
```

---

## Login Flow

```
User                      Frontend                    Backend
  │                          │                           │
  │── Enter credentials ────▶│                           │
  │                          │                           │
  │                          │── POST /auth/login ──────▶│
  │                          │   {email, password}       │
  │                          │                           │
  │                          │◀── access_token (JSON) ───│
  │                          │◀── refresh_token (Cookie) │
  │                          │                           │
  │                          │ Store in localStorage:    │
  │                          │ - access_token            │
  │                          │ - user                    │
  │                          │                           │
  │◀── Redirect to Dashboard ─│                          │
```

---

## Token Refresh

### Automatic Refresh on API Errors

```javascript
// frontend/js/api.js

class Api {
    static async request(endpoint, options = {}) {
        const token = Auth.getToken();
        
        // Add Authorization header
        options.headers = {
            ...options.headers,
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
        };
        
        const response = await fetch(`${BASE_URL}${endpoint}`, options);
        
        // If token expired
        if (response.status === 401) {
            // Try to refresh
            const refreshed = await this.refreshToken();
            
            if (refreshed) {
                // Retry original request with new token
                options.headers['Authorization'] = `Bearer ${Auth.getToken()}`;
                return fetch(`${BASE_URL}${endpoint}`, options);
            } else {
                // Refresh failed, logout
                Auth.logout();
                window.location.hash = '#/login';
                return;
            }
        }
        
        return response.json();
    }
    
    static async refreshToken() {
        try {
            const response = await fetch(`${BASE_URL}/auth/refresh`, {
                method: 'POST',
                credentials: 'include'  // Send cookies!
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
}
```

---

## Protected Routes

### Route Configuration

```javascript
// frontend/js/router.js

const routes = {
    '/': { view: LandingView, requiresAuth: false },
    '/login': { view: LoginView, requiresAuth: false },
    '/signup': { view: SignupView, requiresAuth: false },
    '/dashboard': { view: DashboardView, requiresAuth: true },
    '/admin': { view: AdminView, requiresAuth: true, requiresAdmin: true },
    '/scan': { view: ScanView, requiresAuth: true },
    '/chat': { view: ChatView, requiresAuth: true }
};
```

### Route Guard

```javascript
async navigate(path) {
    const route = routes[path];
    
    // Check authentication
    if (route.requiresAuth && !Auth.isAuthenticated()) {
        window.location.hash = '#/login';
        return;
    }
    
    // Check admin role
    if (route.requiresAdmin && !Auth.isAdmin()) {
        window.location.hash = '#/dashboard';
        return;
    }
    
    // Render view
    const view = new route.view();
    document.getElementById('app').innerHTML = await view.render();
    view.afterRender?.();
}
```

---

## Security Considerations

1. **XSS Protection**: Refresh token in HttpOnly cookie
2. **CSRF Protection**: SameSite=Lax on cookies
3. **Token Expiry**: Short-lived access tokens (15 min)
4. **Automatic Logout**: On failed refresh

---

## Related Documentation

- [API Layer](../API/overview.md)
- [Routing](../Routing/overview.md)
