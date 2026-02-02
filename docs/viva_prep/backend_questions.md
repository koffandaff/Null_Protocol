# 📝 Backend Viva Questions

100+ interview questions covering backend development for the Fsociety project.

---

## Table of Contents

1. [FastAPI & Web Framework](#fastapi--web-framework)
2. [Authentication & Security](#authentication--security)
3. [Database & SQLAlchemy](#database--sqlalchemy)
4. [API Design](#api-design)
5. [Caching & Performance](#caching--performance)
6. [Security Tools & Scanning](#security-tools--scanning)
7. [General Python](#general-python)

---

## FastAPI & Web Framework

### Q1: What is FastAPI and why did you choose it?
**Answer**: FastAPI is a modern, high-performance Python web framework. We chose it for:
- Automatic API documentation (Swagger/ReDoc)
- Built-in data validation with Pydantic
- Async support for I/O-bound operations
- Type hints for better code quality

### Q2: What is ASGI?
**Answer**: ASGI (Asynchronous Server Gateway Interface) is the async successor to WSGI. It allows handling multiple requests concurrently without blocking.

### Q3: What is the difference between sync and async endpoints?
**Answer**: 
- `def endpoint()` - Runs in thread pool, blocks that thread
- `async def endpoint()` - Non-blocking, can handle concurrent I/O

### Q4: What is dependency injection in FastAPI?
**Answer**: A way to provide shared resources (like database sessions) to endpoints:
```python
async def endpoint(db: Session = Depends(get_db)):
```

### Q5: What is middleware?
**Answer**: Code that runs before/after every request. Used for logging, CORS, authentication.

### Q6: How does CORS work?
**Answer**: Cross-Origin Resource Sharing allows browsers to make requests to different domains. We configure allowed origins, methods, and headers.

### Q7: What is Pydantic?
**Answer**: A data validation library that uses Python type hints. Validates request/response data automatically.

### Q8: How do you handle file uploads in FastAPI?
**Answer**: Using `UploadFile` type:
```python
async def upload(file: UploadFile):
    content = await file.read()
```

### Q9: What is a router in FastAPI?
**Answer**: A way to organize endpoints by feature (auth, scans, etc.) and include them with prefixes.

### Q10: How do you document API endpoints?
**Answer**: Using docstrings, response_model, and tags. FastAPI generates OpenAPI documentation automatically.

---

## Authentication & Security

### Q11: What is JWT?
**Answer**: JSON Web Token - a compact, signed token containing user claims (id, email, role). Used for stateless authentication.

### Q12: What are the parts of a JWT?
**Answer**: Header (algorithm), Payload (claims), Signature (verification).

### Q13: Why use both access and refresh tokens?
**Answer**: 
- Access token: Short-lived (15 min), used for API calls
- Refresh token: Long-lived (7 days), used to get new access tokens
- Limits damage if access token is stolen

### Q14: What is bcrypt?
**Answer**: A password hashing algorithm that's intentionally slow to prevent brute-force attacks. Includes automatic salting.

### Q15: What is a salt in password hashing?
**Answer**: Random data added to the password before hashing, ensuring identical passwords have different hashes.

### Q16: How do you prevent SQL injection?
**Answer**: Using SQLAlchemy ORM with parameterized queries. Never concatenate user input into SQL strings.

### Q17: What is rate limiting?
**Answer**: Restricting the number of requests per time window to prevent abuse. Example: 3 login attempts per minute.

### Q18: How do you store refresh tokens?
**Answer**: In HttpOnly cookies (client-side) and database (server-side) for validation.

### Q19: What is XSS?
**Answer**: Cross-Site Scripting - injecting malicious scripts into web pages. Prevented by escaping user content.

### Q20: What is CSRF?
**Answer**: Cross-Site Request Forgery - tricking users into making unwanted requests. Prevented with SameSite cookies.

### Q21: How does password reset work?
**Answer**: 
1. User requests reset with email
2. Server generates 6-digit OTP, stores hash
3. OTP sent to email (printed to console in dev)
4. User submits OTP + new password
5. Server verifies OTP hash and updates password

### Q22: What is user enumeration and how do you prevent it?
**Answer**: Revealing if an email exists. Prevented by returning same response regardless of email existence.

### Q23: What are HttpOnly cookies?
**Answer**: Cookies that JavaScript cannot access, protecting them from XSS attacks.

### Q24: What is the purpose of the 'exp' claim in JWT?
**Answer**: Expiration time - tokens automatically become invalid after this timestamp.

### Q25: How do you handle disabled accounts?
**Answer**: Check `is_active` flag during login and return 403 Forbidden with specific error code.

---

## Database & SQLAlchemy

### Q26: What is ORM?
**Answer**: Object-Relational Mapping - maps database tables to Python classes and rows to objects.

### Q27: What is SQLAlchemy?
**Answer**: Python's most popular ORM and SQL toolkit. Provides database-agnostic interface.

### Q28: What is the difference between engine and session?
**Answer**:
- Engine: Connection pool, low-level database access
- Session: High-level interface for queries and transactions

### Q29: What is a migration?
**Answer**: Version-controlled schema changes. Alembic is used with SQLAlchemy for migrations.

### Q30: What is lazy loading?
**Answer**: Related data is loaded from database only when accessed, not when parent is queried.

### Q31: What is eager loading?
**Answer**: Related data is loaded in the same query as parent using `joinedload()`.

### Q32: What is the N+1 query problem?
**Answer**: Loading N records and making N additional queries for related data. Fixed with eager loading.

### Q33: What is a foreign key?
**Answer**: A column that references the primary key of another table, establishing a relationship.

### Q34: What is CASCADE delete?
**Answer**: Automatically delete child records when parent is deleted.

### Q35: Why use UUIDs for primary keys?
**Answer**: Security (not guessable), distributed generation, unique across systems.

### Q36: What is database normalization?
**Answer**: Organizing data to reduce redundancy. Normal forms: 1NF, 2NF, 3NF.

### Q37: What is an index?
**Answer**: Data structure that speeds up queries on indexed columns. Trade-off: slower writes.

### Q38: How do you handle transactions?
**Answer**: SQLAlchemy sessions are transaction-aware. `commit()` saves, `rollback()` undoes.

### Q39: What is connection pooling?
**Answer**: Reusing database connections instead of creating new ones. Improves performance.

### Q40: What is SQLite and when is it appropriate?
**Answer**: File-based relational database. Good for development, single-user apps, prototyping.

---

## API Design

### Q41: What is REST?
**Answer**: Representational State Transfer - architectural style using HTTP methods (GET, POST, PUT, DELETE) for CRUD operations.

### Q42: What are HTTP status codes?
**Answer**: 
- 2xx: Success (200 OK, 201 Created)
- 4xx: Client error (400 Bad Request, 401 Unauthorized, 404 Not Found)
- 5xx: Server error (500 Internal Error)

### Q43: What is the difference between PUT and PATCH?
**Answer**: PUT replaces entire resource, PATCH updates partial fields.

### Q44: What is request validation?
**Answer**: Ensuring incoming data matches expected schema. FastAPI uses Pydantic for this.

### Q45: What is OpenAPI/Swagger?
**Answer**: Specification for describing REST APIs. FastAPI generates this automatically.

### Q46: How do you version an API?
**Answer**: URL path (`/v1/users`), header, or query parameter.

### Q47: What is idempotency?
**Answer**: Making the same request multiple times has the same effect as making it once. GET, PUT, DELETE should be idempotent.

### Q48: How do you handle pagination?
**Answer**: Using `limit` and `offset` query parameters:
```python
@router.get('/users')
def get_users(limit: int = 10, offset: int = 0):
```

### Q49: What is HATEOAS?
**Answer**: Hypermedia As The Engine Of Application State - including links in API responses.

### Q50: How do you handle errors in API?
**Answer**: Raise HTTPException with status code and detail message:
```python
raise HTTPException(status_code=404, detail="User not found")
```

---

## Caching & Performance

### Q51: What is caching?
**Answer**: Storing frequently accessed data in fast storage to reduce response time and load.

### Q52: What is TTL?
**Answer**: Time To Live - how long cached data remains valid before expiration.

### Q53: What is LRU cache?
**Answer**: Least Recently Used - eviction policy that removes oldest unused items when cache is full.

### Q54: What do you cache and why?
**Answer**: Scan results (expensive computations), DNS lookups, SSL checks. Not user data (privacy) or auth tokens (security).

### Q55: What is async/await in Python?
**Answer**: Syntax for non-blocking I/O. `async def` defines coroutine, `await` suspends until complete.

### Q56: When should you use async?
**Answer**: I/O-bound operations: database queries, HTTP requests, file operations.

### Q57: What is connection pooling?
**Answer**: Maintaining pool of reusable connections instead of creating new ones per request.

### Q58: How do you measure API performance?
**Answer**: Response time, throughput (requests/second), error rate, latency percentiles (p50, p99).

### Q59: What is a bottleneck?
**Answer**: The slowest part of the system that limits overall performance.

### Q60: How would you scale this application?
**Answer**: 
- Vertical: Bigger server
- Horizontal: Multiple instances behind load balancer
- Database: Read replicas, sharding
- Caching: Redis for distributed cache

---

## Security Tools & Scanning

### Q61: What is port scanning?
**Answer**: Probing a host to find open network ports and services.

### Q62: What is SSL/TLS?
**Answer**: Security protocols for encrypting network traffic. SSL is deprecated, TLS is current.

### Q63: What are security headers?
**Answer**: HTTP headers that improve security: CSP, HSTS, X-Frame-Options, etc.

### Q64: What is WHOIS?
**Answer**: Protocol for querying domain registration information.

### Q65: What is DNS?
**Answer**: Domain Name System - translates domain names to IP addresses.

### Q66: What is OSINT?
**Answer**: Open Source Intelligence - gathering information from public sources.

### Q67: What is a VPN?
**Answer**: Virtual Private Network - encrypted tunnel for secure communication.

### Q68: What is PKI?
**Answer**: Public Key Infrastructure - system for creating, managing digital certificates.

### Q69: What is a digital certificate?
**Answer**: Electronic document that proves ownership of a public key.

### Q70: What is malware analysis?
**Answer**: Examining suspicious files to identify malicious behavior.

---

## General Python

### Q71: What is a virtual environment?
**Answer**: Isolated Python environment with its own packages. Prevents dependency conflicts.

### Q72: What is `requirements.txt`?
**Answer**: File listing project dependencies for installation with `pip install -r requirements.txt`.

### Q73: What is type hinting?
**Answer**: Adding type annotations to Python code for better documentation and IDE support.

### Q74: What is a decorator?
**Answer**: Function that modifies another function's behavior. Example: `@router.get()`.

### Q75: What is a context manager?
**Answer**: Object that manages resources with `with` statement. Ensures cleanup.

### Q76: What is exception handling?
**Answer**: Using try/except to gracefully handle errors instead of crashing.

### Q77: What is a generator?
**Answer**: Function that yields values lazily instead of returning a list. Memory efficient.

### Q78: What is `*args` and `**kwargs`?
**Answer**: 
- `*args`: Variable positional arguments (tuple)
- `**kwargs`: Variable keyword arguments (dict)

### Q79: What is the GIL?
**Answer**: Global Interpreter Lock - allows only one thread to execute Python at a time.

### Q80: How do you run background tasks?
**Answer**: Using `asyncio`, threading, or task queues like Celery.

---

## Additional Questions

### Q81-Q85: Error Handling
81. How do you log errors? → Python logging module
82. What is a traceback? → Stack trace showing error origin
83. How do you handle unexpected errors? → Global exception handler
84. What is defensive programming? → Anticipating and handling edge cases
85. How do you test error handling? → Unit tests with expected exceptions

### Q86-Q90: Testing
86. What is unit testing? → Testing individual functions
87. What is integration testing? → Testing components together
88. What is pytest? → Python testing framework
89. What is test coverage? → Percentage of code tested
90. What is mocking? → Replacing dependencies with fake objects

### Q91-Q95: DevOps
91. What is CI/CD? → Continuous Integration/Deployment
92. What is Docker? → Container platform
93. What is environment variable? → External configuration
94. What is a reverse proxy? → Server that forwards requests (Nginx)
95. What is HTTPS? → HTTP over TLS encryption

### Q96-Q100: Architecture
96. What is microservices? → Distributed independent services
97. What is monolith? → Single unified application
98. What is the repository pattern? → Data access abstraction
99. What is the service layer? → Business logic layer
100. What is separation of concerns? → Each component has one responsibility

---

## Related Documentation

- [Auth Overview](../backend/Auth/overview.md)
- [Database Schema](../backend/Database/schema.md)
- [Caching](../backend/Caching_RateLimiting/caching.md)
