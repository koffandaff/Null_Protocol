"""
Security scanning models for SSL, headers, phishing, etc.
"""
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum
from config.constants import TLSVersion, RiskLevel, SecurityHeader, PhishingIndicator, HashType

# ========== SSL/TLS MODELS ==========

class SSLScanRequest(BaseModel):
    """Request model for SSL/TLS scan"""
    domain: str
    port: int = Field(default=443, ge=1, le=65535)
    full_scan: bool = Field(default=False)
    
    @validator('domain')
    def validate_domain(cls, v):
        from utils.ssrf_guard import ssrf_guard
        if not ssrf_guard.validate_target(v, "domain"):
            raise ValueError("Domain not allowed for security reasons")
        return v

class CertificateInfo(BaseModel):
    """SSL certificate information"""
    subject: Dict[str, str]
    issuer: Dict[str, str]
    version: int
    serial_number: str
    not_before: str
    not_after: str
    signature_algorithm: str
    public_key_algorithm: str
    public_key_bits: int
    san: List[str] = []  # Subject Alternative Names
    ocsp_must_staple: bool = False
    extended_validation: bool = False

class TLSInfo(BaseModel):
    """TLS protocol information"""
    version: TLSVersion
    supported: bool
    preferred: bool = False

class CipherSuite(BaseModel):
    """Cipher suite information"""
    name: str
    protocol: str
    bits: int
    kx: str  # Key exchange
    au: str  # Authentication
    enc: str  # Encryption
    mac: str  # Message Authentication Code

class Vulnerability(BaseModel):
    """SSL/TLS vulnerability"""
    name: str
    cve: Optional[str]
    description: str
    risk: RiskLevel
    affected: bool
    details: Optional[Dict] = None

class SSLScanResult(BaseModel):
    """Complete SSL/TLS scan result"""
    domain: str
    port: int
    timestamp: str
    certificate: CertificateInfo
    tls_versions: List[TLSInfo]
    cipher_suites: List[CipherSuite]
    vulnerabilities: List[Vulnerability]
    ocsp_stapling: bool
    hsts_preloaded: bool
    certificate_transparency: bool
    scan_duration_ms: int

# ========== HTTP HEADER MODELS ==========

class HeaderScanRequest(BaseModel):
    """Request model for HTTP header scan"""
    url: str
    follow_redirects: bool = Field(default=True, description="Follow HTTP redirects")
    
    @validator('url')
    def validate_url(cls, v):
        from utils.ssrf_guard import ssrf_guard
        if not ssrf_guard.validate_target(v, "url"):
            raise ValueError("URL not allowed for security reasons")
        
        # Ensure URL has scheme
        if not v.startswith(('http://', 'https://')):
            v = f'https://{v}'
        
        return v

class SecurityHeaderInfo(BaseModel):
    """Individual security header information"""
    header: SecurityHeader
    present: bool
    value: Optional[str] = None
    recommendation: Optional[str] = None
    risk: RiskLevel

class Technology(BaseModel):
    """Detected technology"""
    name: str
    version: Optional[str]
    confidence: float = Field(ge=0.0, le=1.0)
    categories: List[str] = []  # e.g., ["cms", "framework", "analytics"]

class HeaderScanResult(BaseModel):
    """Complete HTTP header scan result"""
    url: str
    timestamp: str
    status_code: int
    server: Optional[str]
    content_type: Optional[str]
    content_length: Optional[int]
    security_headers: List[SecurityHeaderInfo]
    technologies: List[Technology]
    cookies: List[Dict] = []
    redirects: List[Dict] = []
    scan_duration_ms: int

# ========== PHISHING DETECTION MODELS ==========

class PhishingCheckRequest(BaseModel):
    """Request model for phishing check"""
    url: str
    deep_analysis: bool = Field(default=False)
    
    @validator('url')
    def validate_url(cls, v):
        from utils.ssrf_guard import ssrf_guard
        if not ssrf_guard.validate_target(v, "url"):
            raise ValueError("URL not allowed for security reasons")
        
        # Ensure URL has scheme
        if not v.startswith(('http://', 'https://')):
            v = f'https://{v}'
        
        return v

class PhishingIndicatorInfo(BaseModel):
    """Phishing detection indicator"""
    indicator: PhishingIndicator
    present: bool
    score: float = Field(ge=0.0, le=1.0)
    details: Optional[str] = None

class PhishingCheckResult(BaseModel):
    """Phishing check result"""
    url: str
    timestamp: str
    domain: str
    final_url: Optional[str]  # After redirects
    risk_score: float = Field(ge=0.0, le=1.0)
    is_phishing: bool
    indicators: List[PhishingIndicatorInfo]
    ssl_valid: Optional[bool]
    domain_age_days: Optional[int]
    reputation: Optional[Dict] = None  # For future external API integration
    scan_duration_ms: int

# ========== TECHNOLOGY STACK MODELS ==========

class TechStackRequest(BaseModel):
    """Request model for technology stack detection"""
    domain: str
    
    @validator('domain')
    def validate_domain(cls, v):
        from utils.ssrf_guard import ssrf_guard
        if not ssrf_guard.validate_target(v, "domain"):
            raise ValueError("Domain not allowed for security reasons")
        return v

class TechStackResult(BaseModel):
    """Technology stack detection result"""
    domain: str
    timestamp: str
    technologies: List[Technology]
    categories: Dict[str, List[str]]  # Group by category
    confidence_score: float = Field(ge=0.0, le=1.0)
    scan_duration_ms: int

# ========== HTTP SECURITY MODELS ==========

class HTTPSecurityRequest(BaseModel):
    """Request model for HTTP security analysis"""
    url: str
    
    @validator('url')
    def validate_url(cls, v):
        from utils.ssrf_guard import ssrf_guard
        if not ssrf_guard.validate_target(v, "url"):
            raise ValueError("URL not allowed for security reasons")
        
        if not v.startswith(('http://', 'https://')):
            v = f'https://{v}'
        
        return v

class HTTPSecurityResult(BaseModel):
    """HTTP security analysis result"""
    url: str
    timestamp: str
    overall_score: float = Field(ge=0.0, le=1.0)
    security_headers_score: float
    cookie_security_score: float
    transport_security_score: float
    recommendations: List[str]
    warnings: List[str]
    scan_duration_ms: int