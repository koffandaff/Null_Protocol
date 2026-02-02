# 🔧 Frontend Utilities

This document details the utility functions available in Fsociety frontend.

---

## Table of Contents

- [Utils Class](#utils-class)
- [Helper Methods](#helper-methods)
- [DOM Utilities](#dom-utilities)
- [Formatters](#formatters)

---

## Utils Class

The `Utils` class in `utils.js` provides commonly used helper functions.

```javascript
// frontend/js/utils.js

export class Utils {
    // Collection of static utility methods
}
```

---

## Helper Methods

### Toast Notifications

```javascript
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

static getToastIcon(type) {
    switch(type) {
        case 'success': return 'check_circle';
        case 'error': return 'error';
        case 'warning': return 'warning';
        default: return 'info';
    }
}
```

### Generate Unique ID

```javascript
static generateId() {
    return Date.now().toString(36) + Math.random().toString(36).substr(2);
}

// Usage
const id = Utils.generateId(); // "ln5k7j2a3x4m2"
```

### Debounce Function

```javascript
static debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Usage: Debounce search input
const debouncedSearch = Utils.debounce((query) => {
    Api.get(`/search?q=${query}`);
}, 300);

input.addEventListener('input', (e) => debouncedSearch(e.target.value));
```

### Copy to Clipboard

```javascript
static async copyToClipboard(text) {
    try {
        await navigator.clipboard.writeText(text);
        this.showToast('Copied to clipboard', 'success');
    } catch {
        this.showToast('Failed to copy', 'error');
    }
}
```

---

## DOM Utilities

### Safe Query Selector

```javascript
static $(selector) {
    return document.querySelector(selector);
}

static $$(selector) {
    return document.querySelectorAll(selector);
}

// Usage
const btn = Utils.$('#submit-btn');
const cards = Utils.$$('.card');
```

### Escape HTML

```javascript
static escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Prevents XSS when inserting user content
element.innerHTML = `<p>${Utils.escapeHtml(userInput)}</p>`;
```

---

## Formatters

### Format Date

```javascript
static formatDate(dateString) {
    if (!dateString) return 'N/A';
    
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

// Usage
Utils.formatDate('2024-01-15T10:30:00Z'); // "Jan 15, 2024, 10:30 AM"
```

### Format Relative Time

```javascript
static formatRelativeTime(dateString) {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now - date;
    const diffSec = Math.floor(diffMs / 1000);
    const diffMin = Math.floor(diffSec / 60);
    const diffHour = Math.floor(diffMin / 60);
    const diffDay = Math.floor(diffHour / 24);
    
    if (diffSec < 60) return 'Just now';
    if (diffMin < 60) return `${diffMin}m ago`;
    if (diffHour < 24) return `${diffHour}h ago`;
    if (diffDay < 7) return `${diffDay}d ago`;
    
    return this.formatDate(dateString);
}

// Usage
Utils.formatRelativeTime(activity.timestamp); // "5m ago"
```

### Format File Size

```javascript
static formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

// Usage
Utils.formatFileSize(1048576); // "1 MB"
```

### Format Number

```javascript
static formatNumber(num) {
    if (num >= 1000000) return (num / 1000000).toFixed(1) + 'M';
    if (num >= 1000) return (num / 1000).toFixed(1) + 'K';
    return num.toString();
}

// Usage
Utils.formatNumber(1500); // "1.5K"
```

---

## Validation Helpers

### Email Validation

```javascript
static isValidEmail(email) {
    const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return regex.test(email);
}
```

### Password Strength

```javascript
static getPasswordStrength(password) {
    let score = 0;
    
    if (password.length >= 8) score++;
    if (password.length >= 12) score++;
    if (/[a-z]/.test(password)) score++;
    if (/[A-Z]/.test(password)) score++;
    if (/[0-9]/.test(password)) score++;
    if (/[^a-zA-Z0-9]/.test(password)) score++;
    
    if (score <= 2) return { level: 'weak', color: 'red' };
    if (score <= 4) return { level: 'medium', color: 'orange' };
    return { level: 'strong', color: 'green' };
}
```

---

## Related Documentation

- [Components](../Components/overview.md)
- [API](../API/overview.md)
