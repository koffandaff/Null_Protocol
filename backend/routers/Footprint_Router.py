"""
Footprint Router - API endpoints for Digital Footprint Scanner
Protected routes for OSINT-based digital footprint analysis
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import List

from model.Footprint_Model import (
    FootprintScanRequest, FootprintScanResult, FootprintScanSummary
)
from service.Footprint_Service import footprint_service
from service.Auth_Service import AuthService
from model.Auth_Model import db as auth_db


router = APIRouter()
security = HTTPBearer()
auth_service = AuthService(auth_db)


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Dependency to get current authenticated user"""
    token = credentials.credentials
    user = auth_service.get_current_user(token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


# ========================
# Scan Endpoints
# ========================

@router.post("/scan", response_model=FootprintScanResult)
async def start_scan(
    request: FootprintScanRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Start a new digital footprint scan.
    Requires user consent to proceed.
    """
    if not request.consent_given:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User consent is required to perform the scan"
        )
    
    try:
        scan = await footprint_service.start_scan(current_user["id"], request)
        return scan
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start scan: {str(e)}")


@router.get("/scan/{scan_id}")
async def get_scan(
    scan_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get scan status and results"""
    scan = footprint_service.get_scan(scan_id, current_user["id"])
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")
    
    return {
        "id": scan.id,
        "email_scanned": scan.email_scanned,
        "username_scanned": scan.username_scanned,
        "platforms_checked": scan.platforms_checked,
        "status": scan.status,
        "progress": scan.progress,
        "score": scan.score,
        "findings": [f.dict() for f in scan.findings],
        "recommendations": scan.recommendations,
        "started_at": scan.started_at,
        "completed_at": scan.completed_at,
        "error_message": scan.error_message
    }


@router.get("/history", response_model=List[FootprintScanSummary])
async def get_scan_history(current_user: dict = Depends(get_current_user)):
    """Get all past scans for the current user"""
    return footprint_service.get_user_scans(current_user["id"])


@router.delete("/scan/{scan_id}")
async def delete_scan(
    scan_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Delete a scan from history"""
    deleted = footprint_service.delete_scan(scan_id, current_user["id"])
    if not deleted:
        raise HTTPException(status_code=404, detail="Scan not found")
    return {"message": "Scan deleted successfully"}


# ========================
# Info Endpoint
# ========================

@router.get("/platforms")
async def get_available_platforms():
    """Get list of supported social platforms for scanning"""
    return {
        "platforms": [
            {"id": "twitter", "name": "Twitter/X", "icon": "alternate_email"},
            {"id": "instagram", "name": "Instagram", "icon": "photo_camera"},
            {"id": "facebook", "name": "Facebook", "icon": "groups"},
            {"id": "linkedin", "name": "LinkedIn", "icon": "work"},
            {"id": "tiktok", "name": "TikTok", "icon": "music_note"},
            {"id": "reddit", "name": "Reddit", "icon": "forum"},
            {"id": "github", "name": "GitHub", "icon": "code"},
            {"id": "discord", "name": "Discord", "icon": "headset_mic"}
        ]
    }
