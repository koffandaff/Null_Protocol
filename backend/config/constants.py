"""
Application Constants and Enums
"""
from enum import Enum

class ScanModule(str, Enum):
    """Available scanning modules"""
    SSL = "ssl"
    HEADERS = "headers"
    PHISHING = "phishing"
    TECH_STACK = "tech_stack"
    HTTP_SECURITY = "http_security"
    FILE_HASH = "file_hash"
    VIRUSTOTAL = "virustotal"

class SecurityHeader(str, Enum):
    """Security headers to check"""
    CSP = "Content-Security-Policy"
    HSTS = "Strict-Transport-Security"
    X_FRAME_OPTIONS = "X-Frame-Options"
    X_CONTENT_TYPE_OPTIONS = "X-Content-Type-Options"
    X_XSS_PROTECTION = "X-XSS-Protection"
    REFERRER_POLICY = "Referrer-Policy"
    PERMISSIONS_POLICY = "Permissions-Policy"
    
class TLSVersion(str, Enum):
    """TLS versions"""
    SSLv2 = "SSLv2"
    SSLv3 = "SSLv3"
    TLSv1_0 = "TLSv1.0"
    TLSv1_1 = "TLSv1.1"
    TLSv1_2 = "TLSv1.2"
    TLSv1_3 = "TLSv1.3"

class HashType(str, Enum):
    """Supported hash types"""
    MD5 = "md5"
    SHA1 = "sha1"
    SHA256 = "sha256"
    SHA512 = "sha512"

class RiskLevel(str, Enum):
    """Risk levels for findings"""
    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class PhishingIndicator(str, Enum):
    """Phishing detection indicators"""
    SUSPICIOUS_TLD = "suspicious_tld"
    SHORT_DOMAIN_AGE = "short_domain_age"
    HTTPS_MISSING = "https_missing"
    IP_IN_URL = "ip_in_url"
    SUSPICIOUS_KEYWORD = "suspicious_keyword"
    LONG_URL = "long_url"
    SHORTENED_URL = "shortened_url"
    NON_STANDARD_PORT = "non_standard_port"
    VIRUSTOTAL_DETECTION = "virustotal_detection"

# Common technology fingerprints (Frameworks, Languages, Servers, Analytics)
TECHNOLOGY_PATTERNS = {
    # Frontend Frameworks
    "react": [
        "__NEXT_DATA__", "react-root", "react-app", "data-reactroot", "_next/static", "react.development.js"
    ],
    "vue": [
        "v-bind", "data-v-", "vue.js", "nuxt-link", "__nuxt", "vue.min.js"
    ],
    "angular": [
        "ng-app", "ng-controller", "angular.js", "ng-version", "angular.min.js"
    ],
    "jquery": [
        "jquery.min.js", "jquery-", "$(document).ready"
    ],
    "bootstrap": ["bootstrap.min.css", "bootstrap/", "bs-", "bootstrap.min.js"],
    "tailwindcss": ["tailwindcss", "tailwind.config"],
    
    # Backend Frameworks / Languages
    "python": [
        "X-Powered-By: Flask", "X-Powered-By: Django", "wsgi", "gunicorn", ".pyc", "python", "django", "flask"
    ],
    "php": [
        "X-Powered-By: PHP", ".php", "phpsessid", "laravel", "symfony", "wp-"
    ],
    "nodejs": [
        "X-Powered-By: Express", "node.js", "express", "koa", "server.js"
    ],
    "ruby": [
        "X-Powered-By: Phusion", "rails", ".rb", "ruby", "sinatra"
    ],
    "java": [
        "X-Powered-By: Servlet", "jsessionid", ".jsp", "spring", "tomcat"
    ],
    "aspnet": [
        "X-Powered-By: ASP.NET", ".aspx", "asp.net", "__viewstate", "X-AspNet-Version"
    ],
    "go": [
        "golang", "go lang", "gin", "echo"
    ],
    
    # CMS
    "wordpress": [
        "wp-content", "wp-includes", "wordpress", "/wp-admin/", "wp-json"
    ],
    "drupal": [
        "drupal", "/sites/default/", "drupal.js"
    ],
    "joomla": [
        "joomla", "/components/", "option=com_"
    ],
    
    # Web Servers
    "nginx": ["nginx/", "Server: nginx"],
    "apache": ["Apache/", "mod_", "httpd", "Server: Apache"],
    "iis": ["Server: Microsoft-IIS", ".ashx", "asp.net"],
    "litespeed": ["LiteSpeed", "X-Litespeed"],
    
    # CDN & Security
    "cloudflare": ["__cf_bm", "cf-ray", "cloudflare", "cf-cache-status"],
    "akamai": ["akamai", "akamaized.net"],
    "aws": ["amazonaws.com", "X-Amz", "aws-"],
    
    # Analytics & Tracking
    "google_analytics": ["UA-", "G-", "GTM-", "google-analytics.com", "googletagmanager"],
    "facebook_pixel": ["fbq(", "facebook.com/tr"],
    "hotjar": ["hotjar.com", "_hjid"]
}

# Common SSL/TLS vulnerabilities
SSL_VULNERABILITIES = {
    "heartbleed": {
        "cve": "CVE-2014-0160",
        "description": "Allows stealing information protected by SSL/TLS encryption",
        "risk": RiskLevel.CRITICAL
    },
    "poodle": {
        "cve": "CVE-2014-3566",
        "description": "Padding Oracle On Downgraded Legacy Encryption attack",
        "risk": RiskLevel.HIGH
    },
    "freak": {
        "cve": "CVE-2015-0204",
        "description": "Factoring RSA Export Keys attack",
        "risk": RiskLevel.MEDIUM
    },
    "logjam": {
        "cve": "CVE-2015-4000",
        "description": "Allows man-in-the-middle to downgrade TLS connections",
        "risk": RiskLevel.MEDIUM
    },
    "sweet32": {
        "cve": "CVE-2016-2183",
        "description": "Birthday attacks on 64-bit block ciphers",
        "risk": RiskLevel.LOW
    }
}

# Rate limits for new endpoints (requests per minute)
RATE_LIMITS = {
    "scan_ssl": 5,
    "scan_headers": 10,
    "scan_phishing": 3,
    "scan_tech_stack": 8,
    "scan_http_security": 10,
    "scan_file_hash": 20,
    "scan_hash_batch": 5,
    "scan_virustotal": 1
}