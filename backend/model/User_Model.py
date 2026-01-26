from pydantic import BaseModel, validator
from typing import Optional, List, Dict
from datetime import datetime

# ========== REQUEST MODELS ==========

class UserProfileUpdate(BaseModel):
    """Request model for updating user profile"""
    username: Optional[str] = None
    full_name: Optional[str] = None
    phone: Optional[str] = None
    company: Optional[str] = None
    bio: Optional[str] = None
    
    @validator('username')
    def validate_username(cls, v):
        if v is not None and len(v) < 3:
            raise ValueError('Username must be at least 3 characters')
        if v is not None and len(v) > 50:
            raise ValueError('Username must be less than 50 characters')
        return v
    
    @validator('bio')
    def validate_bio(cls, v):
        if v is not None and len(v) > 500:
            raise ValueError('Bio must be less than 500 characters')
        return v
    
    @validator('phone')
    def validate_phone(cls, v):
        if v is not None:
            # Basic phone validation
            import re
            phone_pattern = r'^[\d\s\-\+\(\)]{10,20}$'
            if not re.match(phone_pattern, v):
                raise ValueError('Invalid phone number format')
        return v

class PasswordChange(BaseModel):
    """Request model for changing password"""
    current_password: str
    new_password: str
    
    @validator('new_password')
    def validate_password(cls, v):
        if len(v) < 6:
            raise ValueError('Password must be at least 6 characters')
        if len(v) > 100:
            raise ValueError('Password must be less than 100 characters')
        
        # Check password strength
        import re
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least one number')
        
        return v

class DeleteAccountRequest(BaseModel):
    """Request model for deleting account"""
    password: str  # Require password for account deletion

# ========== RESPONSE MODELS ==========

class ActivityLog(BaseModel):
    """Activity log entry"""
    id: str
    user_id: str
    action: str
    details: Optional[Dict] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    timestamp: str

class UserStats(BaseModel):
    """User statistics"""
    total_scans: int = 0
    phishing_checks: int = 0
    vpn_configs: int = 0
    reports_generated: int = 0
    last_active: Optional[str] = None
    security_scans: int = 0  # NEW: For SSL/headers scans
    file_analysis: int = 0   # NEW: For file analysis
    malware_detected: int = 0  # NEW: Malware detection count

class UserResponse(BaseModel):
    """User profile response"""
    id: str
    email: str
    username: str
    full_name: Optional[str] = None
    phone: Optional[str] = None
    company: Optional[str] = None
    bio: Optional[str] = None
    role: str = "user"
    created_at: str
    updated_at: Optional[str] = None
    password_changed_at: Optional[str] = None
    is_active: bool = True

# ========== COMPREHENSIVE RESPONSE MODELS ==========

class ActivityResponse(BaseModel):
    """Activity logs response"""
    activities: List[ActivityLog]
    total: int
    page: int
    limit: int

class StatsResponse(BaseModel):
    """User statistics response"""
    stats: UserStats

class ProfileUpdateResponse(BaseModel):
    """Profile update response"""
    message: str = "Profile updated successfully"
    user: UserResponse

class PasswordChangeResponse(BaseModel):
    """Password change response"""
    message: str = "Password changed successfully"

class AccountDeletionResponse(BaseModel):
    """Account deletion response"""
    message: str = "Account deleted successfully"

# ========== ADMIN MODELS (For future use) ==========

class AdminUserUpdate(BaseModel):
    """Admin user update model"""
    username: Optional[str] = None
    role: Optional[str] = None
    is_active: Optional[bool] = None
    
    @validator('role')
    def validate_role(cls, v):
        if v is not None and v not in ['user', 'admin']:
            raise ValueError('Role must be either "user" or "admin"')
        return v

class UserSearchParams(BaseModel):
    """User search parameters"""
    email: Optional[str] = None
    username: Optional[str] = None
    role: Optional[str] = None
    is_active: Optional[bool] = None
    date_from: Optional[str] = None
    date_to: Optional[str] = None