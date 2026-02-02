"""
Footprint Router - SQLite Version

API endpoints for Digital Footprint Scanner.
Protected routes for OSINT-based digital footprint analysis.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from model.Footprint_Model import (
    FootprintScanRequest, FootprintScanResult, FootprintScanSummary
)
from service.Footprint_Service import FootprintService
from database.engine import get_db
from routers.dependencies import get_current_user

router = APIRouter()


def get_footprint_service(db: Session = Depends(get_db)) -> FootprintService:
    """Get FootprintService with database session"""
    return FootprintService(db)


# ========================
# Scan Endpoints
# ========================

@router.post("/scan", response_model=FootprintScanResult)
async def start_scan(
    request: FootprintScanRequest,
    current_user: dict = Depends(get_current_user),
    footprint_service: FootprintService = Depends(get_footprint_service)
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
    current_user: dict = Depends(get_current_user),
    footprint_service: FootprintService = Depends(get_footprint_service)
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
async def get_scan_history(
    current_user: dict = Depends(get_current_user),
    footprint_service: FootprintService = Depends(get_footprint_service)
):
    """Get all past scans for the current user"""
    return footprint_service.get_user_scans(current_user["id"])


@router.delete("/scan/{scan_id}")
async def delete_scan(
    scan_id: str,
    current_user: dict = Depends(get_current_user),
    footprint_service: FootprintService = Depends(get_footprint_service)
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
