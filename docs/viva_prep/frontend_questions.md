# 📝 Frontend Viva Questions

100+ interview questions covering frontend development for the Fsociety project.

---

## Table of Contents

1. [JavaScript Fundamentals](#javascript-fundamentals)
2. [DOM & Events](#dom--events)
3. [Authentication & Security](#authentication--security)
4. [Routing & Navigation](#routing--navigation)
5. [API & Network](#api--network)
6. [CSS & Styling](#css--styling)
7. [Performance & Best Practices](#performance--best-practices)

---

## JavaScript Fundamentals

### Q1: What is ES6?
**Answer**: ECMAScript 2015 - major JavaScript update with classes, arrow functions, modules, template literals, destructuring.

### Q2: What are arrow functions?
**Answer**: Shorter function syntax with lexical `this` binding:
```javascript
const add = (a, b) => a + b;
```

### Q3: What is destructuring?
**Answer**: Extracting values from objects/arrays into variables:
```javascript
const { email, password } = formData;
```

### Q4: What are template literals?
**Answer**: String interpolation with backticks:
```javascript
`Hello, ${name}!`
```

### Q5: What is the difference between let, const, and var?
**Answer**: 
- `var`: Function-scoped, hoisted
- `let`: Block-scoped, can be reassigned
- `const`: Block-scoped, cannot be reassigned

### Q6: What is the spread operator?
**Answer**: Expands arrays/objects:
```javascript
const newArray = [...oldArray, newItem];
const newObj = {...oldObj, newProp: value};
```

### Q7: What is async/await?
**Answer**: Syntax for handling promises that looks synchronous:
```javascript
const data = await fetch(url);
```

### Q8: What is a Promise?
**Answer**: Object representing eventual completion/failure of async operation.

### Q9: What is the event loop?
**Answer**: JavaScript's mechanism for handling async operations. Stack, queue, microtasks.

### Q10: What is hoisting?
**Answer**: Moving declarations to top of scope during compilation. var/function are hoisted.

### Q11: What is closure?
**Answer**: Function that remembers its outer scope even when executed elsewhere.

### Q12: What is 'this' in JavaScript?
**Answer**: Context object - depends on how function is called. Arrow functions inherit from enclosing scope.

### Q13: What is prototypal inheritance?
**Answer**: Objects inherit from other objects via prototype chain.

### Q14: What is a class in JavaScript?
**Answer**: Syntactic sugar over prototypal inheritance. Uses `constructor`, `extends`, `static`.

### Q15: What is a module?
**Answer**: Self-contained code unit with exports and imports:
```javascript
export class Api { }
import { Api } from './api.js';
```

---

## DOM & Events

### Q16: What is the DOM?
**Answer**: Document Object Model - tree representation of HTML that JavaScript can manipulate.

### Q17: How do you select elements?
**Answer**: 
```javascript
document.getElementById('id')
document.querySelector('.class')
document.querySelectorAll('selector')
```

### Q18: What is event delegation?
**Answer**: Attaching event listener to parent instead of each child. Uses event bubbling.

### Q19: What is event bubbling?
**Answer**: Events propagate from target up to ancestors. Can be stopped with `stopPropagation()`.

### Q20: What is event.preventDefault()?
**Answer**: Prevents default browser behavior (form submit, link navigation).

### Q21: How do you create elements dynamically?
**Answer**: 
```javascript
const div = document.createElement('div');
div.innerHTML = 'Hello';
parent.appendChild(div);
```

### Q22: What is innerHTML vs textContent?
**Answer**: 
- `innerHTML`: HTML content (can inject HTML)
- `textContent`: Text only (safer)

### Q23: What is a custom event?
**Answer**: User-defined event:
```javascript
element.dispatchEvent(new CustomEvent('myEvent', { detail: data }));
```

### Q24: What is the DOMContentLoaded event?
**Answer**: Fires when HTML is parsed, before stylesheets and images.

### Q25: How do you remove an element?
**Answer**: 
```javascript
element.remove();
// or
parent.removeChild(element);
```

---

## Authentication & Security

### Q26: How do you store tokens?
**Answer**: Access token in localStorage, refresh token in HttpOnly cookie.

### Q27: What is localStorage?
**Answer**: Browser storage that persists across sessions. Accessible via JavaScript.

### Q28: What is sessionStorage?
**Answer**: Browser storage that clears when tab closes.

### Q29: What is XSS?
**Answer**: Cross-Site Scripting - injecting malicious scripts. Prevent by escaping user content.

### Q30: How do you prevent XSS?
**Answer**: 
- Escape HTML output
- Use textContent instead of innerHTML
- Content Security Policy headers

### Q31: What is CSRF?
**Answer**: Cross-Site Request Forgery - unauthorized actions using user's session.

### Q32: How do you handle expired tokens?
**Answer**: Check for 401 response, call refresh endpoint, retry original request.

### Q33: What is the Authorization header?
**Answer**: HTTP header for sending credentials:
```javascript
headers: { 'Authorization': `Bearer ${token}` }
```

### Q34: How do you implement logout?
**Answer**: 
1. Call backend logout endpoint
2. Clear localStorage (token, user)
3. Redirect to login page

### Q35: What is a protected route?
**Answer**: Route that requires authentication. Check token before rendering.

---

## Routing & Navigation

### Q36: What is SPA?
**Answer**: Single Page Application - one HTML page, content updated via JavaScript.

### Q37: What is hash-based routing?
**Answer**: Using URL hash (`#/path`) for navigation without server requests.

### Q38: How does hash routing work?
**Answer**: 
1. Listen for `hashchange` event
2. Parse hash to get route
3. Match to view
4. Render view

### Q39: Why not use path-based routing?
**Answer**: Requires server configuration for fallback. Hash works with any static server.

### Q40: What is client-side routing?
**Answer**: JavaScript handles navigation, no full page reloads.

### Q41: How do you implement route guards?
**Answer**: Check authentication before rendering:
```javascript
if (route.requiresAuth && !Auth.isAuthenticated()) {
    redirect('/login');
}
```

### Q42: What is programmatic navigation?
**Answer**: Navigating via JavaScript instead of link click:
```javascript
window.location.hash = '#/dashboard';
```

### Q43: How do you handle 404 pages?
**Answer**: Check if route exists in routes map, render 404 view if not.

### Q44: What is the History API?
**Answer**: Browser API for managing history. `pushState`, `popstate` event.

### Q45: Why use `python -m http.server`?
**Answer**: Simple, zero-config static file server. Perfect for development.

---

## API & Network

### Q46: What is fetch()?
**Answer**: Modern API for making HTTP requests. Returns Promise.

### Q47: How do you handle fetch errors?
**Answer**: 
```javascript
try {
    const response = await fetch(url);
    if (!response.ok) throw new Error('Request failed');
    return await response.json();
} catch (error) {
    showError(error.message);
}
```

### Q48: What is CORS?
**Answer**: Cross-Origin Resource Sharing - browser security for cross-domain requests.

### Q49: What is the credentials option?
**Answer**: Include cookies in cross-origin requests:
```javascript
fetch(url, { credentials: 'include' })
```

### Q50: How do you send JSON data?
**Answer**: 
```javascript
fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data)
})
```

### Q51: What is the difference between GET and POST?
**Answer**: 
- GET: Retrieve data (no body, cacheable)
- POST: Send data (has body, not cacheable)

### Q52: How do you handle loading states?
**Answer**: Show spinner before request, hide after completion:
```javascript
showLoading();
const data = await Api.get('/data');
hideLoading();
renderData(data);
```

### Q53: What is debouncing?
**Answer**: Delaying function execution until input stops:
```javascript
const debounced = debounce(search, 300);
input.oninput = (e) => debounced(e.target.value);
```

### Q54: What is throttling?
**Answer**: Limiting function calls to once per time period.

### Q55: How do you handle network errors?
**Answer**: Check if error is NetworkError, show offline message.

---

## CSS & Styling

### Q56: What is CSS specificity?
**Answer**: Rules determining which styles apply. ID > class > element.

### Q57: What is flexbox?
**Answer**: CSS layout mode for one-dimensional layouts:
```css
display: flex;
justify-content: center;
align-items: center;
```

### Q58: What is CSS Grid?
**Answer**: Two-dimensional layout system:
```css
display: grid;
grid-template-columns: repeat(3, 1fr);
```

### Q59: What are CSS custom properties?
**Answer**: Variables in CSS:
```css
:root { --primary: #00ff9d; }
.btn { color: var(--primary); }
```

### Q60: What is responsive design?
**Answer**: Adapting layout to different screen sizes using media queries.

### Q61: What are media queries?
**Answer**: CSS rules that apply at specific screen sizes:
```css
@media (max-width: 768px) { }
```

### Q62: What is BEM?
**Answer**: Block-Element-Modifier - CSS naming convention:
```css
.card__header--active
```

### Q63: What is a CSS reset?
**Answer**: Styles that normalize browser defaults for consistency.

### Q64: What is z-index?
**Answer**: Controls stacking order of positioned elements.

### Q65: What is position: sticky?
**Answer**: Element is relative until scroll threshold, then fixed.

---

## Performance & Best Practices

### Q66: What is lazy loading?
**Answer**: Delaying resource loading until needed. Images, code splitting.

### Q67: What is code splitting?
**Answer**: Breaking application into smaller chunks loaded on demand.

### Q68: What is minification?
**Answer**: Removing whitespace and comments from code to reduce size.

### Q69: What is bundling?
**Answer**: Combining multiple files into one to reduce HTTP requests.

### Q70: What is caching?
**Answer**: Browser storing files locally to avoid re-downloading.

### Q71: How do you optimize images?
**Answer**: Compression, proper format (WebP), lazy loading, srcset.

### Q72: What is the critical rendering path?
**Answer**: Steps browser takes to render page. Optimize CSS, defer JS.

### Q73: What is a memory leak?
**Answer**: Memory not released when no longer needed. Event listeners, intervals.

### Q74: How do you prevent memory leaks?
**Answer**: Remove event listeners, clear intervals, null references.

### Q75: What is virtual DOM?
**Answer**: In-memory representation of DOM for efficient updates. Used by React.

---

## Additional Questions

### Q76-Q80: Modern JavaScript
76. What is optional chaining? → `obj?.prop`
77. What is nullish coalescing? → `value ?? default`
78. What is a Map vs Object? → Map: any key type, ordered
79. What is a Set? → Collection of unique values
80. What is Symbol? → Unique primitive for object keys

### Q81-Q85: Browser APIs
81. What is localStorage? → Persistent key-value storage
82. What is IndexedDB? → Client-side database
83. What is the Clipboard API? → Copy/paste programmatically
84. What is the Notification API? → Browser notifications
85. What is the Geolocation API? → User location access

### Q86-Q90: Error Handling
86. What is try/catch? → Exception handling block
87. What is finally? → Always executes after try/catch
88. How do you throw errors? → `throw new Error('message')`
89. What is error.stack? → Stack trace string
90. How do you handle rejected promises? → `.catch()` or try/catch with await

### Q91-Q95: Testing
91. What is unit testing? → Testing individual functions
92. What is E2E testing? → Testing complete user flows
93. What is Jest? → JavaScript testing framework
94. What is a test assertion? → Verifying expected outcome
95. What is code coverage? → Percentage of code tested

### Q96-Q100: Accessibility
96. What is ARIA? → Accessible Rich Internet Applications
97. What is semantic HTML? → Using correct elements (nav, main, article)
98. What is keyboard navigation? → Using site without mouse
99. What is alt text? → Image description for screen readers
100. What is color contrast? → Sufficient difference between text and background

---

## Related Documentation

- [Frontend Auth](../frontend/Auth/overview.md)
- [Routing](../frontend/Routing/overview.md)
- [Components](../frontend/Components/overview.md)
