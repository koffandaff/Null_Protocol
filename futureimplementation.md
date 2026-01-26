
# 📋 **FUTURE FEATURES ROADMAP**

## 🎯 **PHASE 5: ADVANCED TOOLS & AUTOMATION**

### **1. VPN CONFIG GENERATOR**

**Description:** Create OpenVPN/WireGuard configurations for secure connections

**Components:**

```
📁 routers/VPN_Router.py
📁 models/VPN_Model.py
📁 services/VPN_Service.py
📁 utils/vpn_tools.py
📁 templates/vpn_configs/
```

**Endpoints:**

- `POST /api/vpn/openvpn` - Generate OpenVPN config
- `POST /api/vpn/wireguard` - Generate WireGuard config
- `GET /api/vpn/configs` - List user configs
- `GET /api/vpn/config/{id}/download` - Download config
- `DELETE /api/vpn/config/{id}` - Delete config
- `POST /api/vpn/revoke` - Revoke certificate (admin)

**Schemas:**

```python
class VPNConfigRequest(BaseModel):
    server_address: str
    port: int
    protocol: str  # udp/tcp
    cipher: Optional[str]
    auth: Optional[str]
    use_compression: bool = True
    dns_servers: List[str] = ["8.8.8.8", "1.1.1.1"]
    routes: List[str] = ["0.0.0.0/0"]

class WireGuardRequest(BaseModel):
    server_public_key: str
    server_endpoint: str
    client_private_key: Optional[str]  # Generate if not provided
    allowed_ips: str = "0.0.0.0/0"
    persistent_keepalive: int = 25
```

**Dependencies:**

- User: Can create/download own configs
- Admin: Can view all configs, revoke certificates, view usage stats

---

### **2. REPORT GENERATION SYSTEM**

**Description:** Generate professional PDF/HTML reports from scan results

**Components:**

```
📁 routers/Report_Router.py
📁 models/Report_Model.py
📁 services/Report_Service.py
📁 utils/report_generator.py
📁 templates/reports/
📁 static/reports/
```

**Endpoints:**

- `POST /api/reports/generate` - Generate report from scan
- `POST /api/reports/custom` - Create custom report
- `GET /api/reports` - List user reports
- `GET /api/reports/{id}` - Get report details
- `GET /api/reports/{id}/download` - Download report (PDF/HTML)
- `POST /api/reports/{id}/share` - Share report via email/link
- `DELETE /api/reports/{id}` - Delete report
- `GET /api/reports/templates` - List available templates (admin)

**Schemas:**

```python
class ReportRequest(BaseModel):
    scan_id: str
    report_type: Literal["pdf", "html", "json"]
    template: Optional[str] = "default"
    include_executive_summary: bool = True
    include_recommendations: bool = True
    include_technical_details: bool = False
    branding: Optional[Dict] = None

class ReportShareRequest(BaseModel):
    email: Optional[EmailStr]
    expiry_hours: int = 24
    password_protected: bool = False
    password: Optional[str]
```

**Dependencies:**

- User: Generate/download own reports, share with others
- Admin: View all reports, manage templates, view generation stats

---

### **3. SCAN SCHEDULING & AUTOMATION**

**Description:** Schedule recurring scans and receive notifications

**Components:**

```
📁 routers/Schedule_Router.py
📁 models/Schedule_Model.py
📁 services/Schedule_Service.py
📁 utils/scheduler.py
📁 workers/schedule_worker.py
```

**Endpoints:**

- `POST /api/schedules` - Create scheduled scan
- `GET /api/schedules` - List user schedules
- `GET /api/schedules/{id}` - Get schedule details
- `PUT /api/schedules/{id}` - Update schedule
- `DELETE /api/schedules/{id}` - Delete schedule
- `POST /api/schedules/{id}/pause` - Pause schedule
- `POST /api/schedules/{id}/resume` - Resume schedule
- `GET /api/schedules/{id}/history` - Get execution history
- `GET /api/schedules/upcoming` - Get upcoming scans
- `POST /api/notifications/preferences` - Set notification preferences

**Schemas:**

```python
class ScheduleRequest(BaseModel):
    name: str
    target: str
    scan_type: ScanType
    schedule: str  # cron expression
    enabled: bool = True
    notify_on_complete: bool = True
    notify_on_failure: bool = True
    notification_emails: List[EmailStr] = []
    max_executions: Optional[int]
    start_date: Optional[datetime]
    end_date: Optional[datetime]

class NotificationPreferences(BaseModel):
    email_notifications: bool = True
    webhook_url: Optional[str]
    telegram_bot_token: Optional[str]
    telegram_chat_id: Optional[str]
    slack_webhook: Optional[str]
```

**Dependencies:**

- User: Manage own schedules, set notification preferences
- Admin: View all schedules, system-wide schedule limits, notification logs

---

### **4. THREAT INTELLIGENCE FEED**

**Description:** Integrate with threat intelligence APIs and maintain local IOC database

**Components:**

```
📁 routers/ThreatIntel_Router.py
📁 models/ThreatIntel_Model.py
📁 services/ThreatIntel_Service.py
📁 utils/threat_intel.py
📁 data/threat_intel/
```

**Endpoints:**

- `POST /api/threat-intel/lookup` - Lookup IOC (IP, Domain, Hash, URL)
- `POST /api/threat-intel/batch` - Batch IOC lookup
- `GET /api/threat-intel/feeds` - List available threat feeds
- `POST /api/threat-intel/feeds/{id}/sync` - Sync threat feed (admin)
- `GET /api/threat-intel/stats` - Get database stats
- `POST /api/threat-intel/search` - Search IOCs
- `GET /api/threat-intel/recent` - Get recent threats
- `POST /api/threat-intel/export` - Export IOCs (admin)

**Schemas:**

```python
class IOCLookupRequest(BaseModel):
    value: str
    type: Literal["ip", "domain", "hash", "url", "email"]
    sources: List[str] = ["local", "virustotal"]

class ThreatFeed(BaseModel):
    name: str
    url: str
    type: Literal["csv", "json", "stix", "misp"]
    update_frequency: str  # cron
    enabled: bool = True
    last_sync: Optional[datetime]
```

**Dependencies:**

- User: Lookup IOCs, view recent threats
- Admin: Manage threat feeds, sync databases, export data, configure sources

---

## 🎯 **PHASE 6: COLLABORATION & ENTERPRISE FEATURES**

### **5. TEAM WORKSPACES**

**Description:** Multi-user collaboration with role-based permissions

**Components:**

```
📁 routers/Team_Router.py
📁 models/Team_Model.py
📁 services/Team_Service.py
📁 utils/permissions.py
```

**Endpoints:**

- `POST /api/teams` - Create team
- `GET /api/teams` - List user's teams
- `GET /api/teams/{id}` - Get team details
- `PUT /api/teams/{id}` - Update team
- `DELETE /api/teams/{id}` - Delete team
- `POST /api/teams/{id}/members` - Add team member
- `PUT /api/teams/{id}/members/{user_id}` - Update member role
- `DELETE /api/teams/{id}/members/{user_id}` - Remove member
- `POST /api/teams/{id}/invite` - Send invitation
- `GET /api/teams/{id}/scans` - Get team scans
- `POST /api/teams/{id}/share-scan` - Share scan with team

**Schemas:**

```python
class TeamCreateRequest(BaseModel):
    name: str
    description: Optional[str]
    visibility: Literal["private", "public"] = "private"

class TeamInviteRequest(BaseModel):
    email: EmailStr
    role: Literal["viewer", "member", "admin"] = "member"
    message: Optional[str]

class TeamMemberUpdate(BaseModel):
    role: Literal["viewer", "member", "admin"]
    permissions: Optional[Dict]
```

**Dependencies:**

- User: Create/manage own teams, invite members
- Admin: View all teams, system-wide team limits, audit team activities

---

### **6. ASSET MANAGEMENT**

**Description:** Track and manage assets (domains, IPs, certificates)

**Components:**

```
📁 routers/Asset_Router.py
📁 models/Asset_Model.py
📁 services/Asset_Service.py
📁 utils/asset_discovery.py
```

**Endpoints:**

- `POST /api/assets` - Add asset
- `GET /api/assets` - List assets
- `GET /api/assets/{id}` - Get asset details
- `PUT /api/assets/{id}` - Update asset
- `DELETE /api/assets/{id}` - Delete asset
- `POST /api/assets/import` - Import assets from CSV
- `GET /api/assets/export` - Export assets
- `POST /api/assets/discover` - Discover assets from domain
- `GET /api/assets/{id}/history` - Get scan history for asset
- `POST /api/assets/{id}/monitor` - Enable monitoring
- `GET /api/assets/stats` - Get asset statistics
- `GET /api/assets/certificates/expiring` - Get expiring certificates

**Schemas:**

```python
class AssetCreateRequest(BaseModel):
    name: str
    type: Literal["domain", "ip", "subdomain", "certificate", "service"]
    value: str
    description: Optional[str]
    tags: List[str] = []
    owner: Optional[str]
    criticality: Literal["low", "medium", "high", "critical"] = "medium"
    monitoring_enabled: bool = False

class AssetDiscoveryRequest(BaseModel):
    domain: str
    discover_subdomains: bool = True
    discover_ips: bool = True
    discover_services: bool = True
```

**Dependencies:**

- User: Manage own assets, discovery, monitoring
- Admin: View all assets, system-wide asset limits, configure discovery engines

---

### **7. COMPLIANCE FRAMEWORK**

**Description:** Compliance checks against standards (NIST, ISO27001, GDPR)

**Components:**

```
📁 routers/Compliance_Router.py
📁 models/Compliance_Model.py
📁 services/Compliance_Service.py
📁 utils/compliance_checker.py
📁 data/compliance_frameworks/
```

**Endpoints:**

- `POST /api/compliance/scan` - Run compliance scan
- `GET /api/compliance/frameworks` - List available frameworks
- `GET /api/compliance/checks` - List compliance checks
- `POST /api/compliance/assessments` - Create compliance assessment
- `GET /api/compliance/assessments` - List assessments
- `GET /api/compliance/assessments/{id}` - Get assessment details
- `GET /api/compliance/assessments/{id}/report` - Get compliance report
- `POST /api/compliance/evidence` - Upload compliance evidence
- `GET /api/compliance/stats` - Get compliance statistics

**Schemas:**

```python
class ComplianceScanRequest(BaseModel):
    framework: Literal["nist", "iso27001", "gdpr", "pci_dss", "hipaa"]
    scope: List[str]  # Asset IDs or domains
    include_tests: bool = True
    generate_report: bool = True

class ComplianceEvidence(BaseModel):
    assessment_id: str
    control_id: str
    evidence_type: Literal["document", "screenshot", "config", "log"]
    description: str
    file: Optional[UploadFile]
    url: Optional[str]
```

**Dependencies:**

- User: Run compliance scans, manage assessments, upload evidence
- Admin: Configure frameworks, manage checks, view all assessments, export compliance data

---

### **8. API GATEWAY & WEBHOOKS**

**Description:** API management and webhook integrations

**Components:**

```
📁 routers/API_Router.py
📁 models/API_Model.py
📁 services/API_Service.py
📁 utils/webhook_handler.py
```

**Endpoints:**

- `POST /api/api-keys` - Create API key
- `GET /api/api-keys` - List API keys
- `DELETE /api/api-keys/{id}` - Revoke API key
- `POST /api/webhooks` - Create webhook
- `GET /api/webhooks` - List webhooks
- `PUT /api/webhooks/{id}` - Update webhook
- `DELETE /api/webhooks/{id}` - Delete webhook
- `GET /api/webhooks/{id}/logs` - Get webhook logs
- `POST /api/webhooks/test` - Test webhook
- `GET /api/usage` - Get API usage statistics
- `GET /api/rate-limits` - Get current rate limits

**Schemas:**

```python
class APIKeyCreateRequest(BaseModel):
    name: str
    permissions: Dict[str, List[str]]  # endpoint -> methods
    expiry_days: Optional[int]
    ip_restrictions: Optional[List[str]]

class WebhookCreateRequest(BaseModel):
    name: str
    url: str
    events: List[str]  # scan.completed, user.created, etc.
    secret: Optional[str]
    enabled: bool = True
    retry_count: int = 3
    timeout: int = 10
```

**Dependencies:**

- User: Manage own API keys and webhooks
- Admin: View all API keys, system-wide rate limits, webhook statistics, audit API usage

---

## 🎯 **PHASE 7: AI & ADVANCED ANALYTICS**

### **9. AI SECURITY ASSISTANT**

**Description:** AI-powered security recommendations and analysis

**Components:**

```
📁 routers/AI_Router.py
📁 models/AI_Model.py
📁 services/AI_Service.py
📁 utils/ai_assistant.py
📁 data/knowledge_base/
```

**Endpoints:**

- `POST /api/ai/chat` - Chat with security assistant
- `POST /api/ai/analyze-scan` - AI analysis of scan results
- `POST /api/ai/generate-recommendations` - Generate security recommendations
- `POST /api/ai/explain-vulnerability` - Explain vulnerability in simple terms
- `POST /api/ai/prioritize-findings` - Prioritize findings by risk
- `GET /api/ai/context` - Get AI context/memory
- `POST /api/ai/feedback` - Provide feedback on AI response
- `GET /api/ai/stats` - Get AI usage statistics

**Schemas:**

```python
class AIChatRequest(BaseModel):
    message: str
    context: Optional[Dict]  # scan_id, asset_id, etc.
    temperature: float = Field(0.7, ge=0, le=1)
    max_tokens: int = Field(500, ge=1, le=2000)

class AIAnalysisRequest(BaseModel):
    scan_id: str
    analysis_type: Literal["executive", "technical", "remediation"]
    language: str = "en"
    detail_level: Literal["brief", "detailed", "comprehensive"] = "detailed"
```

**Dependencies:**

- User: Chat with AI, get analysis and recommendations
- Admin: Configure AI models, view usage stats, manage knowledge base, set AI limits

---

### **10. SECURITY DASHBOARD & ANALYTICS**

**Description:** Interactive dashboards with advanced analytics

**Components:**

```
📁 routers/Dashboard_Router.py
📁 models/Dashboard_Model.py
📁 services/Dashboard_Service.py
📁 utils/analytics.py
📁 static/dashboards/
```

**Endpoints:**

- `GET /api/dashboard/overview` - Get overview dashboard
- `GET /api/dashboard/security` - Get security dashboard
- `GET /api/dashboard/compliance` - Get compliance dashboard
- `GET /api/dashboard/performance` - Get performance dashboard
- `POST /api/dashboard/widgets` - Create custom widget
- `GET /api/dashboard/widgets` - List widgets
- `PUT /api/dashboard/widgets/{id}` - Update widget
- `DELETE /api/dashboard/widgets/{id}` - Delete widget
- `POST /api/dashboard/layouts` - Save dashboard layout
- `GET /api/dashboard/export` - Export dashboard data
- `GET /api/dashboard/alerts` - Get security alerts
- `POST /api/dashboard/notifications` - Set dashboard notifications

**Schemas:**

```python
class DashboardWidget(BaseModel):
    name: str
    type: Literal["chart", "metric", "table", "list"]
    data_source: str
    config: Dict
    refresh_interval: int = 300
    size: Dict[str, int]  # width, height

class DashboardAlert(BaseModel):
    title: str
    description: str
    severity: Literal["info", "warning", "error", "critical"]
    source: str
    timestamp: datetime
    acknowledged: bool = False
```

**Dependencies:**

- User: View dashboards, create custom widgets, set notifications
- Admin: View all dashboards, system-wide analytics, configure alert rules, export analytics

---

### **11. PENETRATION TESTING TOOLS**

**Description:** Integrated penetration testing toolkit

**Components:**

```
📁 routers/Pentest_Router.py
📁 models/Pentest_Model.py
📁 services/Pentest_Service.py
📁 utils/pentest_tools.py
📁 data/payloads/
```

**Endpoints:**

- `POST /api/pentest/vulnerability-scan` - Run vulnerability scan
- `POST /api/pentest/brute-force` - Brute force testing (with consent)
- `POST /api/pentest/sql-injection` - SQL injection testing
- `POST /api/pentest/xss` - XSS testing
- `POST /api/pentest/csrf` - CSRF testing
- `GET /api/pentest/payloads` - List payloads
- `POST /api/pentest/payloads` - Add custom payload
- `POST /api/pentest/recon` - Reconnaissance gathering
- `GET /api/pentest/reports` - Get pentest reports
- `POST /api/pentest/authorization` - Request authorization (admin)

**Schemas:**

```python
class PentestRequest(BaseModel):
    target: str
    test_type: Literal["vulnerability", "brute_force", "sql", "xss", "csrf", "recon"]
    intensity: Literal["low", "medium", "high"] = "medium"
    authorized: bool = False  # Must be true for destructive tests
    authorization_token: Optional[str]  # From admin

class AuthorizationRequest(BaseModel):
    target: str
    test_type: str
    reason: str
    duration_hours: int = 24
    scope: Optional[str]
```

**Dependencies:**

- User: Run non-destructive tests, view payloads, generate reports
- Admin: Authorize destructive tests, manage payloads, view all pentest activities, audit logs

---

## 🎯 **PHASE 8: DEPLOYMENT & SCALING**

### **12. CONTAINERIZATION & ORCHESTRATION**

**Description:** Docker containers and Kubernetes orchestration

**Components:**

```
📁 docker/
📁 kubernetes/
📁 scripts/deploy/
📁 monitoring/
```

**Files:**

- `Dockerfile` - Application Dockerfile
- `docker-compose.yml` - Development environment
- `docker-compose.prod.yml` - Production environment
- `kubernetes/deployment.yaml` - K8s deployment
- `kubernetes/service.yaml` - K8s service
- `kubernetes/ingress.yaml` - K8s ingress
- `scripts/deploy.sh` - Deployment script
- `monitoring/prometheus.yml` - Prometheus config
- `monitoring/grafana/` - Grafana dashboards

---

### **13. MONITORING & OBSERVABILITY**

**Description:** Comprehensive monitoring and logging

**Components:**

```
📁 routers/Monitor_Router.py
📁 models/Monitor_Model.py
📁 services/Monitor_Service.py
📁 utils/monitoring.py
```

**Endpoints:**

- `GET /api/monitor/health` - Detailed health check
- `GET /api/monitor/metrics` - Prometheus metrics
- `GET /api/monitor/logs` - Application logs
- `GET /api/monitor/performance` - Performance metrics
- `GET /api/monitor/alerts` - System alerts
- `POST /api/monitor/webhook` - External monitoring webhook
- `GET /api/monitor/status` - System status
- `GET /api/monitor/usage` - Resource usage

**Schemas:**

```python
class MonitorAlert(BaseModel):
    type: Literal["cpu", "memory", "disk", "api", "database"]
    threshold: float
    duration: int
    action: Literal["alert", "scale", "restart"]

class LogQuery(BaseModel):
    level: Optional[Literal["debug", "info", "warning", "error"]]
    service: Optional[str]
    time_range: str = "1h"
    search: Optional[str]
    limit: int = 100
```

**Dependencies:**

- User: View own logs and metrics
- Admin: Full system monitoring, configure alerts, view all logs, system diagnostics

---

## 📋 **IMPLEMENTATION PRIORITY**

### **HIGH PRIORITY (Next 2 Weeks):**

1. VPN Config Generator - Basic utility
2. Report Generation - PDF/HTML reports
3. Scan Scheduling - Cron-based scheduling

### **MEDIUM PRIORITY (Next Month):**

4. Team Workspaces - Collaboration
5. Asset Management - Asset tracking
6. Threat Intelligence - IOC database

### **LOW PRIORITY (Next Quarter):**

7. Compliance Framework - Standards compliance
8. AI Assistant - Basic recommendations
9. Pentesting Tools - Security testing

### **INFRASTRUCTURE (Ongoing):**

10. Containerization - Docker/K8s
11. Monitoring - Observability
12. API Gateway - Advanced API management

---

## 📊 **DEPENDENCY MATRIX**

| Feature       | User Dependencies           | Admin Dependencies           | Shared Dependencies       |
| ------------- | --------------------------- | ---------------------------- | ------------------------- |
| VPN Generator | Create/config/download own  | View all, revoke certs       | OpenSSL, config templates |
| Report System | Generate/download/share own | Templates, all reports       | Report templates, PDF lib |
| Scheduling    | Manage own schedules        | System limits, all schedules | Cron parser, scheduler    |
| Threat Intel  | Lookup IOCs                 | Manage feeds, sync           | IOC databases, APIs       |
| Teams         | Create/manage own teams     | All teams, limits            | Permission system         |
| Assets        | Manage own assets           | All assets, discovery        | Asset discovery tools     |
| Compliance    | Run scans, upload evidence  | Frameworks, all assessments  | Compliance checkers       |
| AI Assistant  | Chat, get recommendations   | Configure models, stats      | LLM integration           |
| Dashboard     | Custom widgets, alerts      | All dashboards, analytics    | Charting libraries        |
| Pentesting    | Non-destructive tests       | Authorize, audit logs        | Security testing tools    |
| Monitoring    | Own metrics/logs            | Full system monitoring       | Metrics collection        |
| API Gateway   | Own API keys/webhooks       | All keys, rate limits        | API management            |

---

## 🚀 **NEXT STEPS CHECKLIST**

### **Immediate (Today-Tomorrow):**

1. [ ] Create `config/wordlists/` directory with files
2. [ ] Create `workers/scan_worker.py`
3. [ ] Run comprehensive test suite
4. [ ] Fix any test failures
5. [ ] Test all new Phase 4 endpoints

### **Short-term (This Week):**

1. [ ] Implement VPN Config Generator (Phase 5.1)
2. [ ] Implement Report Generation (Phase 5.2)
3. [ ] Implement basic scheduling (Phase 5.3)
4. [ ] Add database persistence (PostgreSQL)
5. [ ] Implement Redis for caching

### **Medium-term (Next 2 Weeks):**

1. [ ] Implement Team Workspaces
2. [ ] Implement Asset Management
3. [ ] Add Docker containerization
4. [ ] Implement basic monitoring
5. [ ] Add comprehensive documentation

### **Long-term (Next Month):**

1. [ ] Implement AI Security Assistant
2. [ ] Implement Compliance Framework
3. [ ] Add advanced analytics
4. [ ] Implement pentesting tools
5. [ ] Add Kubernetes orchestration

---

## 📖 **README.md TEMPLATE**

```markdown
# 🛡️ Fsociety Cybersecurity Platform

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)]()
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104.1-green)]()
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Security: Enabled](https://img.shields.io/badge/Security-Enabled-red)]()

> **Advanced cybersecurity scanning, analysis, and automation platform** - A comprehensive toolkit for security professionals, researchers, and organizations.

## ✨ Features

### 🔐 **Core Security Scanning**
- **Domain Analysis**: WHOIS, DNS records, subdomain discovery
- **IP Intelligence**: Geolocation, port scanning, service detection
- **SSL/TLS Scanner**: Certificate analysis, vulnerability detection
- **HTTP Security**: Header analysis, technology fingerprinting
- **Phishing Detection**: URL analysis with heuristic scoring

### 📁 **File & Malware Analysis**
- **Hash Reputation**: Check against malware databases
- **File Analysis**: Upload and analyze suspicious files
- **VirusTotal Integration**: External reputation checking
- **Local Malware DB**: Offline hash database

### 🛠️ **Advanced Tools**
- **VPN Config Generator**: OpenVPN/WireGuard configuration
- **Report Generation**: Professional PDF/HTML reports
- **Scan Scheduling**: Automated recurring scans
- **Threat Intelligence**: IOC database and feeds

### 👥 **Collaboration**
- **Team Workspaces**: Multi-user collaboration
- **Asset Management**: Track domains, IPs, certificates
- **Compliance Framework**: NIST, ISO27001, GDPR checks

### 🤖 **AI & Analytics**
- **Security Assistant**: AI-powered recommendations
- **Interactive Dashboards**: Real-time analytics
- **Penetration Testing**: Integrated security testing tools

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Redis (optional, for caching)
- PostgreSQL (optional, for production)

### Installation

```bash
# Clone repository
git clone https://github.com/yourusername/fsociety-platform.git
cd fsociety-platform/backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create environment file
cp .env.example .env
# Edit .env with your configuration

# Run the application
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

Visit `http://localhost:8000/docs` for interactive API documentation.

## 📚 API Documentation

### Authentication

All endpoints (except `/api/auth/*`) require JWT authentication.

1. **Sign Up**: `POST /api/auth/signup`
2. **Log In**: `POST /api/auth/login`
3. **Refresh Token**: `POST /api/auth/refresh`

### Quick Examples

```bash
# Sign up
curl -X POST "http://localhost:8000/api/auth/signup" \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "secure123", "username": "security_user"}'

# Log in
curl -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "secure123"}'

# Scan a domain (with token)
curl -X POST "http://localhost:8000/api/scans/domain" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"domain": "example.com"}'

# Check SSL certificate
curl -X POST "http://localhost:8000/api/security/ssl" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"domain": "example.com", "port": 443}'
```

## 🏗️ Architecture

```
Fsociety Platform Architecture:
┌─────────────────────────────────────────────────────────┐
│                    Frontend (React/Vue)                  │
├─────────────────────────────────────────────────────────┤
│                    API Gateway (FastAPI)                 │
├──────────────┬──────────────┬───────────────────────────┤
│   Auth       │   Scanning   │     File Analysis         │
│   Service    │   Service    │     Service               │
├──────────────┼──────────────┼───────────────────────────┤
│   Cache      │   Workers    │     Database              │
│   (Redis)    │   (Celery)   │     (PostgreSQL)          │
└──────────────┴──────────────┴───────────────────────────┘
```
