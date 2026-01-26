"""
File analysis and hash checking models
"""
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from config.constants import HashType, RiskLevel

# ========== FILE HASH MODELS ==========

class HashCheckRequest(BaseModel):
    """Request model for hash check"""
    hash: str
    hash_type: HashType = Field(default=HashType.SHA256)
    
    @validator('hash')
    def validate_hash(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError("Hash cannot be empty")
        
        # Basic hash format validation
        if not all(c in '0123456789abcdefABCDEF' for c in v):
            raise ValueError("Hash must contain only hexadecimal characters")
        
        return v.strip()

class BatchHashCheckRequest(BaseModel):
    """Request model for batch hash check"""
    hashes: List[str]
    hash_type: HashType = Field(default=HashType.SHA256)
    
    @validator('hashes')
    def validate_hashes(cls, v):
        if not v:
            raise ValueError("Hashes list cannot be empty")
        if len(v) > 100:
            raise ValueError("Maximum 100 hashes per batch")
        
        for hash_str in v:
            if not hash_str or len(hash_str.strip()) == 0:
                raise ValueError("Hash cannot be empty")
            if not all(c in '0123456789abcdefABCDEF' for c in hash_str.strip()):
                raise ValueError("All hashes must contain only hexadecimal characters")
        
        return [h.strip() for h in v]

class HashReputation(BaseModel):
    """Hash reputation information"""
    known_malicious: bool
    known_clean: bool
    detection_count: Optional[int] = 0
    detection_names: List[str] = []
    first_seen: Optional[str]
    last_seen: Optional[str]
    file_type: Optional[str]
    file_size: Optional[int]
    tags: List[str] = []

class HashCheckResult(BaseModel):
    """Hash check result"""
    hash: str
    hash_type: HashType
    timestamp: str
    reputation: HashReputation
    risk_level: RiskLevel
    confidence: float = Field(ge=0.0, le=1.0)
    sources_checked: List[str]
    recommendations: List[str]

class BatchHashCheckResult(BaseModel):
    """Batch hash check result"""
    timestamp: str
    total_hashes: int
    malicious_count: int
    clean_count: int
    unknown_count: int
    results: List[HashCheckResult]
    scan_duration_ms: int

# ========== FILE UPLOAD MODELS ==========

class FileUploadRequest(BaseModel):
    """File upload request metadata"""
    description: Optional[str] = None
    password_protected: bool = Field(default=False)

class FileAnalysisResult(BaseModel):
    """File analysis result"""
    filename: str
    file_size: int
    mime_type: str
    hash_md5: str
    hash_sha1: str
    hash_sha256: str
    timestamp: str
    is_executable: bool
    is_archive: bool
    is_encrypted: bool
    contains_macros: bool
    entropy: float = Field(ge=0.0, le=8.0)
    strings_found: List[str] = []
    magic_bytes: Optional[str]
    reputation: Optional[HashReputation] = None
    risk_level: RiskLevel
    warnings: List[str]
    scan_duration_ms: int

# ========== VIRUSTOTAL MODELS ==========

class VirusTotalCheckRequest(BaseModel):
    """Request model for VirusTotal check"""
    hash: str
    
    @validator('hash')
    def validate_hash(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError("Hash cannot be empty")
        if not all(c in '0123456789abcdefABCDEF' for c in v):
            raise ValueError("Hash must contain only hexadecimal characters")
        return v.strip()

class VirusTotalReport(BaseModel):
    """VirusTotal report"""
    hash: str
    timestamp: str
    permalink: str
    positives: int
    total: int
    scan_date: str
    scans: Dict[str, Dict[str, Any]]
    md5: Optional[str]
    sha1: Optional[str]
    sha256: Optional[str]
    meaningful_name: Optional[str]
    tags: List[str] = []
    times_submitted: Optional[int]
    last_analysis_date: Optional[str]

class MalwareDatabaseInfo(BaseModel):
    """Malware database information"""
    name: str
    version: str
    hash_count: int
    updated_at: str
    source: str