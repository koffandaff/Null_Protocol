"""
User Router - SQLite Version

Endpoints for user profile, password, and activity management.
"""
from fastapi import APIRouter, HTTPException, Depends, status, Request
from sqlalchemy.orm import Session

from model.User_Model import (
    UserProfileUpdate, PasswordChange, 
    ActivityResponse, StatsResponse, DeleteAccountRequest,
    UserResponse
)
from service.Auth_Service import AuthService
from service.User_Service import UserService
from database.engine import get_db
from routers.dependencies import get_current_user

router = APIRouter()


def get_user_service(db: Session = Depends(get_db)) -> UserService:
    """Get UserService with database session"""
    return UserService(db)


# ========== PROFILE MANAGEMENT ==========

@router.get("/profile", response_model=UserResponse)
async def get_profile(
    current_user: dict = Depends(get_current_user),
    request: Request = None,
    db: Session = Depends(get_db)
):
    """Get current user profile"""
    try:
        user_service = UserService(db)
        
        # Log activity
        user_service.log_activity(
            user_id=current_user['id'],
            action="view_profile",
            details={"action": "get_profile"},
            request=request
        )
        
        # Return user data from dependency
        return UserResponse(**current_user)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/profile", response_model=UserResponse)
async def update_profile(
    profile_data: UserProfileUpdate,
    current_user: dict = Depends(get_current_user),
    request: Request = None,
    user_service: UserService = Depends(get_user_service)
):
    """Update user profile"""
    try:
        # Log activity
        user_service.log_activity(
            user_id=current_user['id'],
            action="profile_update",
            details={"fields_updated": list(profile_data.dict(exclude_unset=True).keys())},
            request=request
        )
        
        # Update profile
        result = user_service.update_profile(current_user['id'], profile_data.dict(exclude_unset=True))
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ========== PASSWORD MANAGEMENT ==========

@router.put("/password")
async def change_password(
    password_data: PasswordChange,
    current_user: dict = Depends(get_current_user),
    request: Request = None,
    user_service: UserService = Depends(get_user_service)
):
    """Change user password"""
    try:
        # Change password (also logs activity internally)
        user_service.change_password(
            current_user['id'],
            password_data.current_password,
            password_data.new_password
        )
        return {"message": "Password changed successfully"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ========== ACCOUNT MANAGEMENT ==========

@router.delete("/account")
async def delete_account(
    delete_request: DeleteAccountRequest,
    current_user: dict = Depends(get_current_user),
    request: Request = None,
    user_service: UserService = Depends(get_user_service)
):
    """Delete user account"""
    try:
        # Log activity (before deletion)
        user_service.log_activity(
            user_id=current_user['id'],
            action="account_deletion",
            request=request
        )
        
        # Delete account
        user_service.delete_account(current_user['id'], delete_request.password)
        return {"message": "Account deleted successfully"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ========== ACTIVITY & STATISTICS ==========

@router.get("/activities", response_model=ActivityResponse)
async def get_activities(
    limit: int = 20,
    page: int = 1,
    current_user: dict = Depends(get_current_user),
    request: Request = None,
    user_service: UserService = Depends(get_user_service)
):
    """Get user activity logs"""
    try:
        # Log activity
        user_service.log_activity(
            user_id=current_user['id'],
            action="view_activities",
            details={"limit": limit, "page": page},
            request=request
        )
        
        # Get activities
        result = user_service.get_user_activities(current_user['id'], limit, page)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats", response_model=StatsResponse)
async def get_stats(
    current_user: dict = Depends(get_current_user),
    request: Request = None,
    user_service: UserService = Depends(get_user_service)
):
    """Get user statistics"""
    try:
        # Log activity
        user_service.log_activity(
            user_id=current_user['id'],
            action="view_stats",
            request=request
        )
        
        # Get stats
        stats = user_service.get_user_stats(current_user['id'])
        return {"stats": stats}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))