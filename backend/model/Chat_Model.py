"""
Chat Models and Database for AI Chatbot Feature
Uses Ollama with Koffan/Cybiz:latest model
"""
import json
import os
import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


# ========================
# Pydantic Schemas
# ========================

class ChatMessage(BaseModel):
    """Individual chat message"""
    role: str = Field(..., description="'user' or 'assistant'")
    content: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ChatSession(BaseModel):
    """Chat session with message history"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    title: str = "New Chat"
    messages: List[ChatMessage] = []
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class ChatRequest(BaseModel):
    """Request to send a message"""
    session_id: Optional[str] = None  # If None, create new session
    message: str


class ChatSessionResponse(BaseModel):
    """Response for session info (without full messages)"""
    id: str
    title: str
    created_at: datetime
    updated_at: datetime
    message_count: int


class ChatSessionDetail(BaseModel):
    """Full session with messages"""
    id: str
    title: str
    messages: List[ChatMessage]
    created_at: datetime
    updated_at: datetime


# ========================
# JSON File Database
# ========================

class ChatDatabase:
    def __init__(self, db_path: str = "data/chat_sessions.json"):
        self.db_path = db_path
        self._ensure_db_exists()
    
    def _ensure_db_exists(self):
        """Ensure database file and directory exist"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        if not os.path.exists(self.db_path):
            self._save_data({"sessions": []})
    
    def _load_data(self) -> Dict:
        try:
            with open(self.db_path, 'r') as f:
                return json.load(f)
        except:
            return {"sessions": []}
    
    def _save_data(self, data: Dict):
        with open(self.db_path, 'w') as f:
            json.dump(data, f, indent=2, default=str)
    
    # Session Operations
    
    def create_session(self, user_id: str, initial_message: str = None) -> ChatSession:
        """Create a new chat session"""
        session = ChatSession(user_id=user_id)
        
        if initial_message:
            session.messages.append(ChatMessage(role="user", content=initial_message))
            # Generate title from first message (first 30 chars)
            session.title = initial_message[:30] + "..." if len(initial_message) > 30 else initial_message
        
        data = self._load_data()
        data["sessions"].append(session.dict())
        self._save_data(data)
        
        return session
    
    def get_user_sessions(self, user_id: str) -> List[ChatSessionResponse]:
        """Get all sessions for a user (summary only)"""
        data = self._load_data()
        user_sessions = [s for s in data["sessions"] if s.get("user_id") == user_id]
        
        # Sort by updated_at descending (most recent first)
        user_sessions.sort(key=lambda x: x.get("updated_at", ""), reverse=True)
        
        return [
            ChatSessionResponse(
                id=s["id"],
                title=s.get("title", "Untitled"),
                created_at=s.get("created_at", datetime.utcnow()),
                updated_at=s.get("updated_at", datetime.utcnow()),
                message_count=len(s.get("messages", []))
            )
            for s in user_sessions
        ]
    
    def get_session(self, session_id: str, user_id: str) -> Optional[ChatSession]:
        """Get specific session with full message history"""
        data = self._load_data()
        
        for s in data["sessions"]:
            if s["id"] == session_id and s.get("user_id") == user_id:
                return ChatSession(**s)
        
        return None
    
    def add_message(self, session_id: str, user_id: str, role: str, content: str) -> bool:
        """Add a message to a session"""
        data = self._load_data()
        
        for s in data["sessions"]:
            if s["id"] == session_id and s.get("user_id") == user_id:
                message = ChatMessage(role=role, content=content)
                s["messages"].append(message.dict())
                s["updated_at"] = datetime.utcnow().isoformat()
                
                # Update title if this is the first user message
                if role == "user" and len([m for m in s["messages"] if m["role"] == "user"]) == 1:
                    s["title"] = content[:30] + "..." if len(content) > 30 else content
                
                self._save_data(data)
                return True
        
        return False
    
    def delete_session(self, session_id: str, user_id: str) -> bool:
        """Delete a session"""
        data = self._load_data()
        original_length = len(data["sessions"])
        
        data["sessions"] = [
            s for s in data["sessions"] 
            if not (s["id"] == session_id and s.get("user_id") == user_id)
        ]
        
        if len(data["sessions"]) < original_length:
            self._save_data(data)
            return True
        
        return False
    
    def update_session_title(self, session_id: str, user_id: str, new_title: str) -> bool:
        """Update the title of a session"""
        data = self._load_data()
        for s in data["sessions"]:
            if s["id"] == session_id and s.get("user_id") == user_id:
                s["title"] = new_title
                s["updated_at"] = datetime.utcnow().isoformat()
                self._save_data(data)
                return True
        return False
    
    def get_context_messages(self, session_id: str, user_id: str, limit: int = 10) -> List[Dict]:
        """Get recent messages for context (Ollama format)"""
        session = self.get_session(session_id, user_id)
        
        if not session:
            return []
        
        # Get last N messages
        recent = session.messages[-limit:]
        
        return [{"role": m.role, "content": m.content} for m in recent]


# Global database instance
chat_db = ChatDatabase()
