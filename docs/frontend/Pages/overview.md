# 📄 Frontend Pages

This document provides an overview of all page views in Fsociety.

---

## Table of Contents

- [View Architecture](#view-architecture)
- [Page List](#page-list)
- [View Lifecycle](#view-lifecycle)
- [Creating a New View](#creating-a-new-view)

---

## View Architecture

Each page is a **View class** that follows a consistent pattern:

```javascript
export class ExampleView {
    
    // Return HTML string
    async render() {
        return `<div>...</div>`;
    }
    
    // Called after HTML is in DOM
    async afterRender() {
        this.attachEventListeners();
        await this.loadData();
    }
}
```

---

## Page List

| Route | View | File | Description |
|-------|------|------|-------------|
| `#/` | LandingView | `landing.js` | Public landing page |
| `#/login` | LoginView | `login.js` | Login form |
| `#/signup` | SignupView | `signup.js` | Registration form |
| `#/forgot-password` | ForgotView | `forgot.js` | Password recovery |
| `#/dashboard` | DashboardView | `dashboard.js` | User dashboard |
| `#/scan` | ScanView | `scan.js` | Network scanning |
| `#/security` | SecurityView | `security.js` | Security audits |
| `#/phishing` | PhishingView | `phishing.js` | Phishing detection |
| `#/footprint` | FootprintView | `footprint.js` | Digital footprint |
| `#/vpn` | VPNView | `vpn.js` | VPN configuration |
| `#/files` | FilesView | `files.js` | File analysis |
| `#/chat` | ChatView | `chat.js` | AI assistant |
| `#/admin` | AdminView | `admin.js` | Admin panel |
| `#/settings` | SettingsView | `settings.js` | User settings |
| `#/privacy` | PrivacyView | `legal.js` | Privacy policy |
| `#/terms` | TermsView | `legal.js` | Terms of service |

---

## View Lifecycle

```
1. Router matches hash to route
            │
            ▼
2. Router creates View instance
            │
            ▼
3. Router calls view.render()
            │
            ▼
4. Router sets app.innerHTML
            │
            ▼
5. Router calls view.afterRender()
            │
            ▼
6. View attaches event listeners
            │
            ▼
7. View loads data from API
```

---

## Creating a New View

### Step 1: Create View File

```javascript
// frontend/js/views/example.js

import { Api } from '../api.js';
import { Auth } from '../auth.js';
import { Utils } from '../utils.js';

export class ExampleView {
    
    async render() {
        const user = Auth.getCurrentUser();
        
        return `
            <div class="page-container">
                <div class="page-header">
                    <h1>Example Page</h1>
                    <p>Welcome, ${user.username}!</p>
                </div>
                
                <div class="content">
                    <button id="action-btn" class="btn">
                        Do Something
                    </button>
                    
                    <div id="results"></div>
                </div>
            </div>
        `;
    }
    
    async afterRender() {
        // Attach event listeners
        document.getElementById('action-btn')
            .addEventListener('click', () => this.handleAction());
        
        // Load initial data
        await this.loadData();
    }
    
    async loadData() {
        try {
            const data = await Api.get('/example/data');
            this.renderResults(data);
        } catch (error) {
            Utils.showToast(error.message, 'error');
        }
    }
    
    handleAction() {
        Utils.showToast('Action performed!', 'success');
    }
    
    renderResults(data) {
        document.getElementById('results').innerHTML = `
            <pre>${JSON.stringify(data, null, 2)}</pre>
        `;
    }
}
```

### Step 2: Register Route

```javascript
// frontend/js/router.js

import { ExampleView } from './views/example.js';

const routes = {
    // ... existing routes
    '/example': { view: ExampleView, requiresAuth: true }
};
```

### Step 3: Add Navigation Link

```javascript
// In sidebar or navbar component
<a href="#/example">Example</a>
```

---

## Dynamic Content Pattern

```javascript
// Loading state
document.getElementById('results').innerHTML = `
    <div class="loading-spinner"></div>
`;

// Load data
const data = await Api.get('/endpoint');

// Update with data
document.getElementById('results').innerHTML = `
    ${data.items.map(item => `
        <div class="item">${item.name}</div>
    `).join('')}
`;
```

---

## Related Documentation

- [Routing](../Routing/overview.md)
- [Components](../Components/overview.md)
