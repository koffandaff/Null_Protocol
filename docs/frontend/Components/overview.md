# 🧩 Frontend Components

This document details reusable UI components in Fsociety.

---

## Table of Contents

- [Component Overview](#component-overview)
- [Component List](#component-list)
- [Usage Examples](#usage-examples)
- [CSS Classes](#css-classes)

---

## Component Overview

Fsociety uses **template literal components** - reusable HTML generators implemented as JavaScript functions.

### Pattern

```javascript
// Component definition
function Card({ title, content }) {
    return `
        <div class="card">
            <h3>${title}</h3>
            <p>${content}</p>
        </div>
    `;
}

// Usage
document.innerHTML = Card({ title: 'Hello', content: 'World' });
```

---

## Component List

### 1. Toast Notifications

```javascript
// frontend/js/utils.js

static showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.innerHTML = `
        <span class="material-symbols-outlined">${this.getToastIcon(type)}</span>
        <span>${message}</span>
    `;
    
    document.body.appendChild(toast);
    
    setTimeout(() => {
        toast.classList.add('toast-hide');
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

// Usage
Utils.showToast('Success!', 'success');
Utils.showToast('Error occurred', 'error');
Utils.showToast('Warning', 'warning');
```

### 2. Modal Dialog

```javascript
static showModal(title, content, actions = []) {
    const modal = document.createElement('div');
    modal.className = 'modal-overlay';
    modal.innerHTML = `
        <div class="modal">
            <div class="modal-header">
                <h3>${title}</h3>
                <button class="modal-close">&times;</button>
            </div>
            <div class="modal-body">
                ${content}
            </div>
            <div class="modal-footer">
                ${actions.map(a => `
                    <button class="btn ${a.class}" data-action="${a.action}">
                        ${a.label}
                    </button>
                `).join('')}
            </div>
        </div>
    `;
    
    document.body.appendChild(modal);
    
    // Close handlers
    modal.querySelector('.modal-close').onclick = () => modal.remove();
    modal.onclick = (e) => {
        if (e.target === modal) modal.remove();
    };
    
    return modal;
}

// Usage
Utils.showModal('Confirm', 'Are you sure?', [
    { label: 'Cancel', class: 'btn-secondary', action: 'cancel' },
    { label: 'Confirm', class: 'btn-primary', action: 'confirm' }
]);
```

### 3. Loading Spinner

```javascript
static showLoading(container) {
    container.innerHTML = `
        <div class="loading-container">
            <div class="spinner"></div>
            <p>Loading...</p>
        </div>
    `;
}

// Usage
Utils.showLoading(document.getElementById('results'));
```

### 4. Sidebar Navigation

```javascript
// In views that use sidebar
renderSidebar() {
    return `
        <aside class="sidebar">
            <div class="sidebar-header">
                <img src="/assets/logo.png" alt="Logo">
                <h2>Fsociety</h2>
            </div>
            
            <nav class="sidebar-nav">
                <a href="#/dashboard" class="${this.isActive('/dashboard')}">
                    <span class="material-symbols-outlined">dashboard</span>
                    Dashboard
                </a>
                <a href="#/scan" class="${this.isActive('/scan')}">
                    <span class="material-symbols-outlined">radar</span>
                    Network Scan
                </a>
                <a href="#/security" class="${this.isActive('/security')}">
                    <span class="material-symbols-outlined">security</span>
                    Security Audit
                </a>
                <!-- More links... -->
            </nav>
        </aside>
    `;
}
```

### 5. Stats Card

```javascript
renderStatCard({ icon, label, value, trend }) {
    return `
        <div class="stat-card">
            <div class="stat-icon">
                <span class="material-symbols-outlined">${icon}</span>
            </div>
            <div class="stat-info">
                <span class="stat-value">${value}</span>
                <span class="stat-label">${label}</span>
            </div>
            ${trend ? `
                <span class="stat-trend ${trend > 0 ? 'up' : 'down'}">
                    ${trend > 0 ? '+' : ''}${trend}%
                </span>
            ` : ''}
        </div>
    `;
}

// Usage
renderStatCard({ icon: 'radar', label: 'Total Scans', value: 152, trend: 12 })
```

---

## Usage in Views

```javascript
// frontend/js/views/dashboard.js

import { Utils } from '../utils.js';

export class DashboardView {
    
    async render() {
        return `
            <div class="dashboard">
                ${this.renderSidebar()}
                
                <main class="main-content">
                    <div class="stats-grid" id="stats-container">
                        ${Utils.showLoading()}
                    </div>
                </main>
            </div>
        `;
    }
    
    async afterRender() {
        const stats = await Api.get('/user/stats');
        
        document.getElementById('stats-container').innerHTML = `
            ${this.renderStatCard({ icon: 'radar', label: 'Scans', value: stats.total_scans })}
            ${this.renderStatCard({ icon: 'security', label: 'Audits', value: stats.security_scans })}
            ${this.renderStatCard({ icon: 'description', label: 'Reports', value: stats.reports_generated })}
        `;
    }
}
```

---

## CSS Classes

### Buttons

| Class | Effect |
|-------|--------|
| `.btn` | Primary button (green) |
| `.btn-secondary` | Secondary button (gray) |
| `.btn-danger` | Danger button (red) |
| `.btn-outline` | Outline button |
| `.btn-sm` | Small button |
| `.btn-lg` | Large button |

### Cards

| Class | Effect |
|-------|--------|
| `.card` | Basic card container |
| `.card-header` | Card header section |
| `.card-body` | Card content section |
| `.card.glass` | Glassmorphism effect |

### Layout

| Class | Effect |
|-------|--------|
| `.page-container` | Full-page wrapper |
| `.sidebar` | Left sidebar |
| `.main-content` | Main content area |
| `.grid-2` | 2-column grid |
| `.grid-3` | 3-column grid |

---

## Related Documentation

- [Pages](../Pages/overview.md)
- [Utility](../Utility/overview.md)
