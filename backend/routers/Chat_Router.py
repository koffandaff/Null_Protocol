"""
Chat Router - Protected API endpoints for AI Chatbot
Uses Server-Sent Events (SSE) for streaming responses
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import List, Optional
from pydantic import BaseModel

from model.Chat_Model import ChatRequest, ChatSessionResponse, ChatSessionDetail
from service.Chat_Service import chat_service
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
# Session Endpoints
# ========================

@router.get("/sessions", response_model=List[ChatSessionResponse])
async def get_sessions(current_user: dict = Depends(get_current_user)):
    """Get all chat sessions for the current user"""
    sessions = chat_service.get_user_sessions(current_user["id"])
    return sessions


@router.post("/sessions", response_model=ChatSessionResponse)
async def create_session(current_user: dict = Depends(get_current_user)):
    """Create a new empty chat session"""
    session = chat_service.create_session(current_user["id"])
    return ChatSessionResponse(
        id=session.id,
        title=session.title,
        created_at=session.created_at,
        updated_at=session.updated_at,
        message_count=len(session.messages)
    )


@router.get("/sessions/{session_id}")
async def get_session(session_id: str, current_user: dict = Depends(get_current_user)):
    """Get a specific chat session with all messages"""
    session = chat_service.get_session(session_id, current_user["id"])
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return {
        "id": session.id,
        "title": session.title,
        "messages": [
            {
                "role": m.role,
                "content": m.content,
                "timestamp": m.timestamp.isoformat() if hasattr(m.timestamp, 'isoformat') else str(m.timestamp)
            }
            for m in session.messages
        ],
        "created_at": session.created_at,
        "updated_at": session.updated_at
    }


@router.delete("/sessions/{session_id}")
async def delete_session(session_id: str, current_user: dict = Depends(get_current_user)):
    """Delete a chat session"""
    deleted = chat_service.delete_session(session_id, current_user["id"])
    if not deleted:
        raise HTTPException(status_code=404, detail="Session not found")
    return {"message": "Session deleted successfully"}


class UpdateTitleRequest(BaseModel):
    title: str


@router.put("/sessions/{session_id}/title")
async def update_session_title(
    session_id: str, 
    request: UpdateTitleRequest,
    current_user: dict = Depends(get_current_user)
):
    """Update chat session title"""
    updated = chat_service.update_session_title(session_id, current_user["id"], request.title)
    if not updated:
        raise HTTPException(status_code=404, detail="Session not found")
    return {"message": "Title updated successfully"}


# ========================
# Chat Endpoint (SSE Streaming)
# ========================

class SendMessageRequest(BaseModel):
    session_id: Optional[str] = None
    message: str


@router.post("/send")
async def send_message(
    request: SendMessageRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Send a message and receive streaming response via SSE.
    If session_id is None, a new session will be created.
    """
    username = current_user.get("username", "User")
    
    async def event_generator():
        async for chunk in chat_service.send_message_stream(
            user_id=current_user["id"],
            session_id=request.session_id,
            message=request.message,
            username=username
        ):
            yield f"data: {chunk}\n\n"
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"  # Disable nginx buffering
        }
    )


# ========================
# Health Check
# ========================

@router.get("/health")
async def check_health():
    """Check if Ollama is running and model is available"""
    health = await chat_service.check_ollama_health()
    return {
        "ollama_connected": health["connected"],
        "model_available": health["model_available"],
        "model": chat_service.model,
        "status": "ready" if health["connected"] and health["model_available"] else "offline"
    }
