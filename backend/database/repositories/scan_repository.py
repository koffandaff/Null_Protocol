"""
Scan Repository - Database operations for network and security scans

Handles all scan-related database operations.
"""
from datetime import datetime
from typing import Any, Dict, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc

from database.repositories.base import BaseRepository
from database.models import NetworkScan, SecurityScan


class ScanRepository(BaseRepository[NetworkScan]):
    """
    Repository for NetworkScan and SecurityScan operations.
    """
    
    def __init__(self, db: Session):
        super().__init__(db)
        self._scan_counter = 0
    
    # ==================== NETWORK SCANS ====================
    
    def create(self, data: Dict[str, Any]) -> NetworkScan:
        """Create a new network scan"""
        # Get next scan number
        max_num = self.db.query(NetworkScan.scan_number).order_by(desc(NetworkScan.scan_number)).first()
        next_num = (max_num[0] + 1) if max_num and max_num[0] else 1
        
        scan = NetworkScan(
            user_id=data.get("user_id"),
            scan_type=data.get("scan_type"),
            target=data.get("target"),
            status=data.get("status", "pending"),
            scan_number=next_num,
        )
        self.db.add(scan)
        self.db.commit()
        self.db.refresh(scan)
        return scan
    
    def get_by_id(self, id: str) -> Optional[NetworkScan]:
        """Get scan by ID"""
        return self.db.query(NetworkScan).filter(NetworkScan.id == id).first()
    
    def get_all(self, limit: int = 50, skip: int = 0) -> List[NetworkScan]:
        """Get all scans (admin)"""
        return (
            self.db.query(NetworkScan)
            .order_by(desc(NetworkScan.started_at))
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def get_by_user(self, user_id: str, limit: int = 20, skip: int = 0) -> List[NetworkScan]:
        """Get scans for a specific user"""
        return (
            self.db.query(NetworkScan)
            .filter(NetworkScan.user_id == user_id)
            .order_by(desc(NetworkScan.started_at))
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def count_by_user(self, user_id: str) -> int:
        """Count scans for a user"""
        return self.db.query(NetworkScan).filter(NetworkScan.user_id == user_id).count()
    
    def update(self, id: str, data: Dict[str, Any]) -> Optional[NetworkScan]:
        """Update scan by ID"""
        scan = self.get_by_id(id)
        if not scan:
            return None
        
        for key, value in data.items():
            if hasattr(scan, key):
                setattr(scan, key, value)
        
        self.db.commit()
        self.db.refresh(scan)
        return scan
    
    def delete(self, id: str) -> bool:
        """Delete scan by ID"""
        scan = self.get_by_id(id)
        if not scan:
            return False
        
        self.db.delete(scan)
        self.db.commit()
        return True
    
    # ==================== SECURITY SCANS ====================
    
    def create_security_scan(self, data: Dict[str, Any]) -> SecurityScan:
        """Create a new security scan (SSL, Headers, Phishing)"""
        scan = SecurityScan(
            user_id=data.get("user_id"),
            category=data.get("category"),
            target=data.get("target"),
            risk_level=data.get("risk_level"),
            results=data.get("results"),
        )
        self.db.add(scan)
        self.db.commit()
        self.db.refresh(scan)
        return scan
    
    def get_security_scans_by_user(self, user_id: str, category: str = None, 
                                    limit: int = 20, skip: int = 0) -> List[SecurityScan]:
        """Get security scans for a user"""
        q = self.db.query(SecurityScan).filter(SecurityScan.user_id == user_id)
        
        if category:
            q = q.filter(SecurityScan.category == category)
        
        return q.order_by(desc(SecurityScan.created_at)).offset(skip).limit(limit).all()
