"""
Security scanning router for SSL, headers, phishing, etc.
"""
from fastapi import APIRouter, HTTPException, Depends, Query
from fastapi.security import HTTPBearer
from typing import Optional, List
from datetime import datetime, timezone

from model.Security_Model import (
    SSLScanRequest, HeaderScanRequest, PhishingCheckRequest,
    TechStackRequest, HTTPSecurityRequest,
    SSLScanResult, HeaderScanResult, PhishingCheckResult,
    TechStackResult, HTTPSecurityResult
)
from service.Security_Service import security_service
from routers.dependencies import get_current_user, require_admin
from utils.rate_limiter import rate_limiter

router = APIRouter()
security = HTTPBearer()

# ========== SSL/TLS SCANNING ==========

@router.post("/ssl", response_model=SSLScanResult)
async def scan_ssl(
    request: SSLScanRequest,
    current_user: dict = Depends(get_current_user)
):
    """Perform SSL/TLS certificate scan"""
    try:
        # Add rate limit headers
        allowed, remaining, reset_in = rate_limiter.is_allowed(current_user['id'], "scan_ssl")
        
        results = security_service.scan_ssl(current_user['id'], request)
        
        # Add rate limit info to response
        results['rate_limit'] = {
            'remaining': remaining,
            'reset_in': reset_in
        }
        
        return results
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/headers", response_model=HeaderScanResult)
async def scan_headers(
    request: HeaderScanRequest,
    current_user: dict = Depends(get_current_user)
):
    """Analyze HTTP headers and detect technologies"""
    try:
        # Rate limit headers
        allowed, remaining, reset_in = rate_limiter.is_allowed(current_user['id'], "scan_headers")
        
        results = security_service.scan_headers(current_user['id'], request)
        
        results['rate_limit'] = {
            'remaining': remaining,
            'reset_in': reset_in
        }
        
        return results
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/phishing/check", response_model=PhishingCheckResult)
async def check_phishing(
    request: PhishingCheckRequest,
    current_user: dict = Depends(get_current_user)
):
    """Check URL for phishing indicators"""
    try:
        # Rate limit
        allowed, remaining, reset_in = rate_limiter.is_allowed(current_user['id'], "scan_phishing")
        
        results = security_service.check_phishing(current_user['id'], request)
        
        results['rate_limit'] = {
            'remaining': remaining,
            'reset_in': reset_in
        }
        
        return results
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/tech-stack", response_model=TechStackResult)
async def scan_tech_stack(
    request: TechStackRequest,
    current_user: dict = Depends(get_current_user)
):
    """Detect technology stack for a domain"""
    try:
        # Rate limit
        allowed, remaining, reset_in = rate_limiter.is_allowed(current_user['id'], "scan_tech_stack")
        
        results = security_service.detect_tech_stack(current_user['id'], request)
        
        results['rate_limit'] = {
            'remaining': remaining,
            'reset_in': reset_in
        }
        
        return results
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/http-security", response_model=HTTPSecurityResult)
async def scan_http_security(
    request: HTTPSecurityRequest,
    current_user: dict = Depends(get_current_user)
):
    """Perform comprehensive HTTP security analysis"""
    try:
        # Rate limit
        allowed, remaining, reset_in = rate_limiter.is_allowed(current_user['id'], "scan_http_security")
        
        results = security_service.analyze_http_security(current_user['id'], request)
        
        results['rate_limit'] = {
            'remaining': remaining,
            'reset_in': reset_in
        }
        
        return results
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ========== CACHE MANAGEMENT (Admin Only) ==========

@router.get("/cache/stats")
async def get_cache_stats(
    current_user: dict = Depends(require_admin)
):
    """Get cache statistics (admin only)"""
    try:
        return security_service.get_cache_stats(current_user['id'])
    except ValueError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/cache/clear")
async def clear_cache(
    cache_type: Optional[str] = Query(None, description="Type of cache to clear (e.g., 'ssl', 'headers'). Leave empty to clear all."),
    current_user: dict = Depends(require_admin)
):
    """Clear cache (admin only)"""
    try:
        result = security_service.clear_cache(current_user['id'], cache_type)
        return {"message": "Cache cleared successfully", **result}
    except ValueError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/cache/entries")
async def get_cache_entries(
    limit: int = Query(50, ge=1, le=200),
    current_user: dict = Depends(require_admin)
):
    """Get cache entries for inspection (admin only)"""
    try:
        return security_service.get_cache_entries(current_user['id'], limit)
    except ValueError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ========== HEALTH & PERFORMANCE ==========

@router.get("/health/detailed")
async def detailed_health_check():
    """Get detailed system health information"""
    from config.settings import settings
    import sys
    import platform
    
    health_info = {
        'app': {
            'name': settings.APP_NAME,
            'version': settings.APP_VERSION,
            'debug': settings.DEBUG
        },
        'system': {
            'python_version': sys.version,
            'platform': platform.platform(),
            'processor': platform.processor()
        },
        'services': {
            'security_tools': True,
            'phishing_tools': True,
            'cache': settings.CACHE_ENABLED,
            'rate_limiting': True
        },
        'timestamp': datetime.now(timezone.utc).isoformat()
    }
    
    return health_info

@router.get("/rate-limits")
async def get_rate_limits(
    current_user: dict = Depends(get_current_user)
):
    """Get current rate limits for user"""
    try:
        limits = {}
        endpoints = [
            "scan_ssl", "scan_headers", "scan_phishing",
            "scan_tech_stack", "scan_http_security",
            "scan_file_hash", "scan_hash_batch", "scan_virustotal"
        ]
        
        for endpoint in endpoints:
            allowed, remaining, reset_in = rate_limiter.is_allowed(current_user['id'], endpoint)
            limits[endpoint] = {
                'allowed': allowed,
                'remaining': remaining,
                'reset_in': reset_in
            }
        
        return limits
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))