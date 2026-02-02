"""
File analysis router for hash checking, malware detection, etc.
"""
from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Query
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from typing import Optional, List

from model.File_Model import (
    HashCheckRequest, BatchHashCheckRequest, FileUploadRequest,
    HashCheckResult, BatchHashCheckResult, FileAnalysisResult,
    VirusTotalCheckRequest, VirusTotalReport,
    MalwareDatabaseInfo
)
# from service.File_Service import file_service  # Removed global instance
from routers.dependencies import get_current_user, require_admin
from utils.rate_limiter import rate_limiter
from database.engine import get_db

router = APIRouter()
security = HTTPBearer()

def get_file_service(db: Session = Depends(get_db)):
    """Get FileService with database session"""
    from service.File_Service import FileService
    return FileService(db)

# ========== HASH CHECKING ==========

@router.post("/hash/check", response_model=HashCheckResult)
async def check_hash(
    request: HashCheckRequest,
    current_user: dict = Depends(get_current_user),
    file_service = Depends(get_file_service)
):
    """Check hash against malware databases"""
    try:
        # Rate limit
        allowed, remaining, reset_in = rate_limiter.is_allowed(current_user['id'], "scan_file_hash")
        
        results = file_service.check_hash(current_user['id'], request)
        
        results['rate_limit'] = {
            'remaining': remaining,
            'reset_in': reset_in
        }
        
        return results
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/hash/batch", response_model=BatchHashCheckResult)
async def check_hash_batch(
    request: BatchHashCheckRequest,
    current_user: dict = Depends(get_current_user),
    file_service = Depends(get_file_service)
):
    """Check multiple hashes in batch"""
    try:
        # Rate limit
        allowed, remaining, reset_in = rate_limiter.is_allowed(current_user['id'], "scan_hash_batch")
        
        results = file_service.check_hash_batch(current_user['id'], request)
        
        results['rate_limit'] = {
            'remaining': remaining,
            'reset_in': reset_in
        }
        
        return results
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ========== FILE UPLOAD ANALYSIS ==========

@router.post("/upload/analyze", response_model=FileAnalysisResult)
async def analyze_file_upload(
    file: UploadFile = File(..., description="File to analyze"),
    description: Optional[str] = Query(None, description="Optional description"),
    password_protected: bool = Query(False, description="Is the file password protected?"),
    use_virustotal: bool = Query(True, description="Cross-reference hash with VirusTotal"),
    current_user: dict = Depends(get_current_user),
    file_service = Depends(get_file_service)
):
    """Analyze uploaded file"""
    try:
        # Read file content
        content = await file.read()
        
        # Create request
        request = FileUploadRequest(
            description=description,
            password_protected=password_protected
        )
        
        # Analyze file
        results = file_service.analyze_file(
            current_user['id'], content, file.filename, request, use_virustotal=use_virustotal
        )
        
        return results
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ========== VIRUSTOTAL INTEGRATION ==========

@router.post("/virustotal/check", response_model=VirusTotalReport)
async def check_virustotal(
    request: VirusTotalCheckRequest,
    current_user: dict = Depends(get_current_user),
    file_service = Depends(get_file_service)
):
    """Check hash on VirusTotal (requires API key)"""
    try:
        # Rate limit (strict)
        allowed, remaining, reset_in = rate_limiter.is_allowed(current_user['id'], "scan_virustotal")
        if not allowed:
            raise HTTPException(
                status_code=429,
                detail={
                    "error": "Rate limit exceeded",
                    "limit": "1 request per minute for VirusTotal",
                    "reset_in": reset_in
                }
            )
        
        results = file_service.check_virustotal(current_user['id'], request)
        
        results['rate_limit'] = {
            'remaining': remaining,
            'reset_in': reset_in
        }
        
        return results
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ========== MALWARE DATABASE MANAGEMENT (Admin Only) ==========

@router.get("/malware/database", response_model=MalwareDatabaseInfo)
async def get_malware_database_info(
    current_user: dict = Depends(require_admin),
    file_service = Depends(get_file_service)
):
    """Get information about local malware database (admin only)"""
    try:
        return file_service.get_malware_database_info(current_user['id'])
    except ValueError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/malware/database/update")
async def update_malware_database(
    hashes: List[dict],
    current_user: dict = Depends(require_admin),
    file_service = Depends(get_file_service)
):
    """Update local malware database with new hashes (admin only)"""
    try:
        result = file_service.update_malware_database(current_user['id'], hashes)
        return {"message": "Malware database updated successfully", **result}
    except ValueError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ========== FILE TYPE INFORMATION ==========

@router.get("/supported/hash-types")
async def get_supported_hash_types():
    """Get list of supported hash types"""
    from config.constants import HashType
    
    hash_types = []
    for ht in HashType:
        hash_types.append({
            'type': ht.value,
            'description': f'{ht.value.upper()} hash'
        })
    
    return hash_types

@router.get("/supported/file-types")
async def get_supported_file_types():
    """Get information about supported file types"""
    return {
        'max_file_size_mb': 10,
        'supported_types': [
            'executables (exe, dll, so, dylib)',
            'archives (zip, rar, 7z, tar)',
            'documents (pdf, doc, docx, xls, xlsx)',
            'scripts (js, py, sh, bat, ps1)',
            'images (jpg, png, gif, bmp)'
        ],
        'analysis_includes': [
            'hash calculation (MD5, SHA1, SHA256)',
            'file type detection',
            'entropy analysis',
            'string extraction',
            'malware hash checking'
        ]
    }