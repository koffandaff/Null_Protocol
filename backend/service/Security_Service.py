"""
Security scanning service for SSL, headers, phishing, etc.
"""
from typing import Dict, Optional, List
from datetime import datetime
import time

from model.Security_Model import (
    SSLScanRequest, HeaderScanRequest, PhishingCheckRequest,
    TechStackRequest, HTTPSecurityRequest,
    SSLScanResult, HeaderScanResult, PhishingCheckResult,
    TechStackResult, HTTPSecurityResult
)
from utils.ssrf_guard import ssrf_guard
from utils.security_tools import security_tools
from utils.phishing_tools import phishing_tools
from utils.cache_tools import cache_tools
from utils.rate_limiter import rate_limiter
from model.Auth_Model import db

class SecurityService:
    def __init__(self):
        self.db = db
    
    # ========== SSL/TLS SCANNING ==========
    
    def scan_ssl(self, user_id: str, request: SSLScanRequest) -> Dict:
        """Perform SSL/TLS scan"""
        # Rate limiting
        allowed, remaining, reset_in = rate_limiter.is_allowed(user_id, "scan_ssl")
        if not allowed:
            raise ValueError(f"Rate limit exceeded. Try again in {reset_in} seconds")
        
        # Check cache
        cache_key = cache_tools.get_key("ssl", request.domain, {"port": request.port})
        cached = cache_tools.get(cache_key)
        
        if cached:
            # Update with user-specific metadata
            cached['user_id'] = user_id
            cached['cached'] = True
            cached['cache_hit'] = True
            return cached
        
        # Perform scan
        start_time = time.time()
        
        try:
            # Validate target
            if not ssrf_guard.validate_target(request.domain, "domain"):
                raise ValueError("Domain not allowed for security reasons")
            
            # Perform scan
            scan_results = security_tools.scan_ssl(request.domain, request.port)
            
            # Add metadata
            scan_results['user_id'] = user_id
            scan_results['scan_type'] = 'ssl'
            scan_results['request'] = request.dict()
            scan_results['cached'] = False
            scan_results['cache_hit'] = False
            scan_results['total_duration_ms'] = int((time.time() - start_time) * 1000)
            
            # Cache results
            cache_tools.set(cache_key, scan_results)
            
            # Log activity
            self.db.log_activity(
                user_id=user_id,
                action="ssl_scan",
                details={
                    'domain': request.domain,
                    'port': request.port,
                    'results': {'vulnerabilities_found': len(scan_results.get('vulnerabilities', []))}
                }
            )
            
            # Update stats
            self.db.update_user_stats(user_id, {'security_scans': 1})
            
            return scan_results
            
        except Exception as e:
            raise ValueError(f"SSL scan failed: {str(e)}")
    
    # ========== HTTP HEADER ANALYSIS ==========
    
    def scan_headers(self, user_id: str, request: HeaderScanRequest) -> Dict:
        """Analyze HTTP headers"""
        # Rate limiting
        allowed, remaining, reset_in = rate_limiter.is_allowed(user_id, "scan_headers")
        if not allowed:
            raise ValueError(f"Rate limit exceeded. Try again in {reset_in} seconds")
        
        # Check cache
        cache_key = cache_tools.get_key("headers", request.url, {"follow_redirects": request.follow_redirects})
        cached = cache_tools.get(cache_key)
        
        if cached:
            cached['user_id'] = user_id
            cached['cached'] = True
            cached['cache_hit'] = True
            return cached
        
        # Perform scan
        start_time = time.time()
        
        try:
            # Validate URL
            if not ssrf_guard.validate_target(request.url, "url"):
                raise ValueError("URL not allowed for security reasons")
            
            # Analyze headers
            scan_results = security_tools.analyze_headers(request.url, request.follow_redirects)
            
            # Add metadata
            scan_results['user_id'] = user_id
            scan_results['scan_type'] = 'headers'
            scan_results['request'] = request.dict()
            scan_results['cached'] = False
            scan_results['cache_hit'] = False
            scan_results['total_duration_ms'] = int((time.time() - start_time) * 1000)
            
            # Cache results
            cache_tools.set(cache_key, scan_results)
            
            # Log activity
            self.db.log_activity(
                user_id=user_id,
                action="header_scan",
                details={
                    'url': request.url,
                    'status_code': scan_results.get('status_code'),
                    'technologies_found': len(scan_results.get('technologies', []))
                }
            )
            
            # Update stats
            self.db.update_user_stats(user_id, {'security_scans': 1})
            
            return scan_results
            
        except Exception as e:
            raise ValueError(f"Header analysis failed: {str(e)}")
    
    # ========== PHISHING DETECTION ==========
    
    def check_phishing(self, user_id: str, request: PhishingCheckRequest) -> Dict:
        """Check URL for phishing indicators"""
        # Rate limiting
        allowed, remaining, reset_in = rate_limiter.is_allowed(user_id, "scan_phishing")
        if not allowed:
            raise ValueError(f"Rate limit exceeded. Try again in {reset_in} seconds")
        
        # Check cache
        cache_key = cache_tools.get_key("phishing", request.url, {"deep_analysis": request.deep_analysis})
        cached = cache_tools.get(cache_key)
        
        if cached:
            cached['user_id'] = user_id
            cached['cached'] = True
            cached['cache_hit'] = True
            return cached
        
        # Perform check
        start_time = time.time()
        
        try:
            # Validate URL
            if not ssrf_guard.validate_target(request.url, "url"):
                raise ValueError("URL not allowed for security reasons")
            
            # Check for phishing
            scan_results = phishing_tools.check_phishing(request.url, request.deep_analysis)
            
            # Add metadata
            scan_results['user_id'] = user_id
            scan_results['scan_type'] = 'phishing'
            scan_results['request'] = request.dict()
            scan_results['cached'] = False
            scan_results['cache_hit'] = False
            scan_results['total_duration_ms'] = int((time.time() - start_time) * 1000)
            
            # Cache results (cache negative results too)
            cache_tools.set(cache_key, scan_results)
            
            # Log activity
            self.db.log_activity(
                user_id=user_id,
                action="phishing_check",
                details={
                    'url': request.url,
                    'is_phishing': scan_results.get('is_phishing', False),
                    'risk_score': scan_results.get('risk_score', 0)
                }
            )
            
            # Update stats
            if scan_results.get('is_phishing', False):
                self.db.update_user_stats(user_id, {'phishing_detected': 1})
            self.db.update_user_stats(user_id, {'phishing_checks': 1})
            
            return scan_results
            
        except Exception as e:
            raise ValueError(f"Phishing check failed: {str(e)}")
    
    # ========== TECHNOLOGY STACK DETECTION ==========
    
    def detect_tech_stack(self, user_id: str, request: TechStackRequest) -> Dict:
        """Detect technology stack"""
        # Rate limiting
        allowed, remaining, reset_in = rate_limiter.is_allowed(user_id, "scan_tech_stack")
        if not allowed:
            raise ValueError(f"Rate limit exceeded. Try again in {reset_in} seconds")
        
        # Check cache
        cache_key = cache_tools.get_key("tech_stack", request.domain, {})
        cached = cache_tools.get(cache_key)
        
        if cached:
            cached['user_id'] = user_id
            cached['cached'] = True
            cached['cache_hit'] = True
            return cached
        
        # Perform detection
        start_time = time.time()
        
        try:
            # Validate domain
            if not ssrf_guard.validate_target(request.domain, "domain"):
                raise ValueError("Domain not allowed for security reasons")
            
            # Detect technologies
            scan_results = security_tools.detect_tech_stack(request.domain)
            
            # Add metadata
            scan_results['user_id'] = user_id
            scan_results['scan_type'] = 'tech_stack'
            scan_results['request'] = request.dict()
            scan_results['cached'] = False
            scan_results['cache_hit'] = False
            scan_results['total_duration_ms'] = int((time.time() - start_time) * 1000)
            
            # Cache results
            cache_tools.set(cache_key, scan_results)
            
            # Log activity
            self.db.log_activity(
                user_id=user_id,
                action="tech_stack_detection",
                details={
                    'domain': request.domain,
                    'technologies_found': len(scan_results.get('technologies', []))
                }
            )
            
            # Update stats
            self.db.update_user_stats(user_id, {'tech_scans': 1})
            
            return scan_results
            
        except Exception as e:
            raise ValueError(f"Technology detection failed: {str(e)}")
    
    # ========== HTTP SECURITY ANALYSIS ==========
    
    def analyze_http_security(self, user_id: str, request: HTTPSecurityRequest) -> Dict:
        """Perform HTTP security analysis"""
        # Rate limiting
        allowed, remaining, reset_in = rate_limiter.is_allowed(user_id, "scan_http_security")
        if not allowed:
            raise ValueError(f"Rate limit exceeded. Try again in {reset_in} seconds")
        
        # Check cache
        cache_key = cache_tools.get_key("http_security", request.url, {})
        cached = cache_tools.get(cache_key)
        
        if cached:
            cached['user_id'] = user_id
            cached['cached'] = True
            cached['cache_hit'] = True
            return cached
        
        # Perform analysis
        start_time = time.time()
        
        try:
            # Validate URL
            if not ssrf_guard.validate_target(request.url, "url"):
                raise ValueError("URL not allowed for security reasons")
            
            # Analyze security
            scan_results = security_tools.analyze_http_security(request.url)
            
            # Add metadata
            scan_results['user_id'] = user_id
            scan_results['scan_type'] = 'http_security'
            scan_results['request'] = request.dict()
            scan_results['cached'] = False
            scan_results['cache_hit'] = False
            scan_results['total_duration_ms'] = int((time.time() - start_time) * 1000)
            
            # Cache results
            cache_tools.set(cache_key, scan_results)
            
            # Log activity
            self.db.log_activity(
                user_id=user_id,
                action="http_security_analysis",
                details={
                    'url': request.url,
                    'security_score': scan_results.get('overall_score', 0)
                }
            )
            
            # Update stats
            self.db.update_user_stats(user_id, {'security_scans': 1})
            
            return scan_results
            
        except Exception as e:
            raise ValueError(f"HTTP security analysis failed: {str(e)}")
    
    # ========== CACHE MANAGEMENT ==========
    
    def get_cache_stats(self, user_id: str) -> Dict:
        """Get cache statistics"""
        # Only admin can view cache stats
        user = self.db.get_userby_id(user_id)
        if not user or user.get('role') != 'admin':
            raise ValueError("Admin access required")
        
        return cache_tools.get_stats()
    
    def clear_cache(self, user_id: str, cache_type: str = None) -> Dict:
        """Clear cache"""
        # Only admin can clear cache
        user = self.db.get_userby_id(user_id)
        if not user or user.get('role') != 'admin':
            raise ValueError("Admin access required")
        
        result = cache_tools.clear(cache_type)
        
        # Log activity
        self.db.log_activity(
            user_id=user_id,
            action="cache_clear",
            details={
                'cache_type': cache_type or 'all',
                'entries_cleared': result['cleared']
            }
        )
        
        return result
    
    def get_cache_entries(self, user_id: str, limit: int = 50) -> List[Dict]:
        """Get cache entries for inspection"""
        # Only admin can view cache entries
        user = self.db.get_userby_id(user_id)
        if not user or user.get('role') != 'admin':
            raise ValueError("Admin access required")
        
        return cache_tools.get_entries(limit)

# Global instance
security_service = SecurityService()