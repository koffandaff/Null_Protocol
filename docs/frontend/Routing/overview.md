# 🛤️ Frontend Routing

This document explains how client-side routing works in Fsociety.

---

## Table of Contents

- [Overview](#overview)
- [Hash-Based Routing](#hash-based-routing)
- [Why python http.server?](#why-python-httpserver)
- [Router Implementation](#router-implementation)
- [Route Guards](#route-guards)
- [Navigation](#navigation)

---

## Overview

Fsociety uses **hash-based routing** (`#/path`) for single-page application navigation:

- No server configuration required
- Works with any static file server
- Full control over navigation in JavaScript
- History-like behavior without server-side routing

---

## Hash-Based Routing

### How It Works

```
URL: http://localhost:5500/#/dashboard
                           │
                           └── Hash portion (handled by JS)
```

### URL Examples

| Hash | View |
|------|------|
| `#/` | Landing Page |
| `#/login` | Login Page |
| `#/signup` | Signup Page |
| `#/dashboard` | User Dashboard |
| `#/scan` | Network Scanner |
| `#/chat` | AI Chat |
| `#/admin` | Admin Panel |
| `#/settings` | User Settings |

---

## Why python http.server?

### Command
```bash
python -m http.server 5500
```

### What It Does

1. **Serves Static Files**: HTML, CSS, JS, images
2. **No Configuration**: Zero setup required
3. **Local Development**: Perfect for dev/testing

### Why Not Other Options?

| Server | Good For | Fsociety Use Case |
|--------|----------|-------------------|
| Apache/Nginx | Production, complex routing | Overkill for dev |
| Vite/Webpack | Build tools, HMR | No build step needed |
| Express | API + static | Backend is separate |
| **http.server** | Simple static serving | ✅ Perfect fit |

### Caching Behavior

- `http.server` respects browser caching
- Add `?v=123` to URLs to bust cache during development
- No automatic cache headers (use for development only)

### Auth Handling

Since we use hash-based routing:
- Server doesn't need to know about routes
- Auth is handled entirely client-side
- Protected routes checked in JavaScript before rendering

---

## Router Implementation

```javascript
// frontend/js/router.js

import { LandingView } from './views/landing.js';
import { LoginView } from './views/login.js';
import { DashboardView } from './views/dashboard.js';
import { Auth } from './auth.js';

export class Router {
    constructor() {
        this.routes = {
            '/': { view: LandingView, requiresAuth: false },
            '/login': { view: LoginView, requiresAuth: false },
            '/signup': { view: SignupView, requiresAuth: false },
            '/dashboard': { view: DashboardView, requiresAuth: true },
            '/scan': { view: ScanView, requiresAuth: true },
            '/chat': { view: ChatView, requiresAuth: true },
            '/admin': { view: AdminView, requiresAuth: true, requiresAdmin: true },
            '/settings': { view: SettingsView, requiresAuth: true }
        };
    }
    
    init() {
        // Listen for hash changes
        window.addEventListener('hashchange', () => this.handleRoute());
        
        // Handle initial load
        this.handleRoute();
    }
    
    handleRoute() {
        // Get current hash
        const hash = window.location.hash.slice(1) || '/';
        const route = this.routes[hash];
        
        if (!route) {
            this.render404();
            return;
        }
        
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
        
        // Render the view
        this.renderView(route.view);
    }
    
    async renderView(ViewClass) {
        const view = new ViewClass();
        const app = document.getElementById('app');
        
        // Render HTML
        app.innerHTML = await view.render();
        
        // Call lifecycle hook
        if (view.afterRender) {
            await view.afterRender();
        }
    }
    
    render404() {
        document.getElementById('app').innerHTML = `
            <div style="text-align: center; padding: 4rem;">
                <h1>404 - Page Not Found</h1>
                <a href="#/dashboard">Go to Dashboard</a>
            </div>
        `;
    }
}

// Initialize on page load
const router = new Router();
document.addEventListener('DOMContentLoaded', () => router.init());
```

---

## Route Guards

### Authentication Guard

```javascript
if (route.requiresAuth && !Auth.isAuthenticated()) {
    // Store intended destination
    sessionStorage.setItem('redirect_after_login', hash);
    window.location.hash = '#/login';
    return;
}
```

### Admin Guard

```javascript
if (route.requiresAdmin && !Auth.isAdmin()) {
    Utils.showToast('Admin access required', 'error');
    window.location.hash = '#/dashboard';
    return;
}
```

### Post-Login Redirect

```javascript
// In login view after successful login
const redirect = sessionStorage.getItem('redirect_after_login');
if (redirect) {
    sessionStorage.removeItem('redirect_after_login');
    window.location.hash = `#${redirect}`;
} else {
    window.location.hash = '#/dashboard';
}
```

---

## Navigation

### Programmatic Navigation

```javascript
// Navigate to a route
window.location.hash = '#/dashboard';

// Navigate with state (using sessionStorage)
sessionStorage.setItem('scanTarget', '192.168.1.1');
window.location.hash = '#/scan';
```

### Link Navigation

```html
<a href="#/dashboard">Dashboard</a>
<a href="#/scan">Scan</a>
<a href="#/chat">Chat</a>
```

### Navigation Helper

```javascript
// frontend/js/utils.js

static navigate(path) {
    window.location.hash = `#${path}`;
}

// Usage
Utils.navigate('/dashboard');
```

---

## Related Documentation

- [Auth](../Auth/overview.md)
- [Pages](../Pages/overview.md)
