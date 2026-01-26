from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from routers import (
    Auth_Router, User_Router, Admin_Router, 
    Scan_Router, Security_Router, File_Router,
    VPN_Router, Chat_Router, Footprint_Router
)
from datetime import datetime, timezone
import sys
import platform
import os

# Load Env Variables
load_dotenv()

app = FastAPI(
    title='Fsociety Cybersecurity Platform API',
    version='2.0.0',
    description='Advanced cybersecurity scanning and analysis platform',
    docs_url='/docs',
    redoc_url='/redoc'
)

# Request Logging Middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = datetime.now()
    url = str(request.url)
    method = request.method
    
    print(f"\n[>>>] {method} {url}")
    
    # Simple interaction tracking
    if "/api/auth" in url:
        print(f"[AUTH] Interaction detected on {url}")
    elif "/api/scans" in url:
        print(f"[SCAN] Scanner activity on {url}")

    try:
        response = await call_next(request)
        process_time = (datetime.now() - start_time).total_seconds()
        print(f"[<<<] {response.status_code} ({process_time:.3f}s)")
        return response
    except Exception as e:
        print(f"[ERR] {method} {url} - Error: {str(e)}")
        raise e

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

# Startup Event to Create Admin
@app.on_event("startup")
async def startup_event():
    from model.Auth_Model import db
    from service.Auth_Service import AuthService
    
    auth_service = AuthService(db)
    # Check if admin exists
    admin_email = "admin@fsociety.com"
    if not db.get_userby_email(admin_email):
        # Create default admin
        print(f"Creating default admin user: {admin_email}")
        try:
            admin_data = {
                "email": admin_email,
                "username": "admin",
                "password": "Admin123!", # Strong password to pass validation
                "role": "admin",
                "full_name": "System Administrator",
                "bio": "Root access authorized."
            }
            auth_service.register_user(admin_data)
        except Exception as e:
            print(f"Failed to create default admin: {e}")

# Include routers
app.include_router(Auth_Router.router, prefix='/api/auth', tags=['Authentication'])
app.include_router(User_Router.router, prefix='/api/user', tags=['User Management'])
app.include_router(Admin_Router.router, prefix='/api/admin', tags=['Admin'])
app.include_router(Scan_Router.router, prefix='/api/scans', tags=['Scanning'])
app.include_router(Security_Router.router, prefix='/api/security', tags=['Security Scanning'])
app.include_router(File_Router.router, prefix='/api/files', tags=['File Analysis'])
app.include_router(VPN_Router.router, prefix='/api/vpn', tags=['VPN Tools'])
app.include_router(Chat_Router.router, prefix='/api/chat', tags=['AI Chatbot'])
app.include_router(Footprint_Router.router, prefix='/api/footprint', tags=['Digital Footprint'])

# Health and root endpoints
@app.get('/')
async def root():
    """Root endpoint with API information"""
    return {
        'message': 'Fsociety Cybersecurity Platform API',
        'version': '2.0.0',
        'status': 'operational',
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'endpoints': {
            'auth': '/api/auth',
            'user': '/api/user',
            'admin': '/api/admin',
            'scans': '/api/scans',
            'security': '/api/security',
            'files': '/api/files',
            'vpn': '/api/vpn',
            'docs': '/docs',
            'redoc': '/redoc'
        }
    }

@app.get('/health')
async def health_check():
    """Basic health check endpoint"""
    return {
        'status': 'healthy',
        'service': 'fsociety-api',
        'timestamp': datetime.now(timezone.utc).isoformat()
    }

@app.get('/status')
async def status_check():
    """Detailed status check"""
    try:
        import psutil
        uptime = datetime.now() - datetime.fromtimestamp(psutil.boot_time())
        system_stats = {
            'python_version': sys.version.split()[0],
            'platform': platform.platform(),
            'processor': platform.processor(),
            'cpu_usage': f"{psutil.cpu_percent()}%",
            'memory_usage': f"{psutil.virtual_memory().percent}%",
            'disk_usage': f"{psutil.disk_usage('/').percent}%",
            'uptime': str(uptime).split('.')[0]
        }
    except ImportError:
        system_stats = {
            'python_version': sys.version.split()[0],
            'platform': platform.platform(),
            'error': 'psutil not installed'
        }

    return {
        'status': 'operational',
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'system': system_stats,
        'services': {
            'authentication': 'active',
            'scanning': 'active',
            'security_scanning': 'active',
            'file_analysis': 'active',
            'database': 'in-memory (active)'
        }
    }