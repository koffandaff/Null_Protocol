"""
Chat Repository - Database operations for chat sessions and messages
"""
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc

from database.repositories.base import BaseRepository
from database.models import ChatSession, ChatMessage


class ChatRepository(BaseRepository[ChatSession]):
    """
    Repository for ChatSession and ChatMessage operations.
    """
    
    def __init__(self, db: Session):
        super().__init__(db)

    # ==================== BaseRepository Implementation ====================

    def create(self, data: Dict[str, Any]) -> ChatSession:
        """Create a new chat session from dictionary data"""
        return self.create_session(
            user_id=data.get("user_id"),
            title=data.get("title", "New Chat")
        )

    def get_by_id(self, id: str) -> Optional[ChatSession]:
        """Get session by ID (admin use mostly)"""
        return self.db.query(ChatSession).filter(ChatSession.id == id).first()

    def get_all(self, limit: int = 100, skip: int = 0) -> List[ChatSession]:
        """Get all sessions (admin use)"""
        return (
            self.db.query(ChatSession)
            .order_by(desc(ChatSession.updated_at))
            .offset(skip)
            .limit(limit)
            .all()
        )

    def update(self, id: str, data: Dict[str, Any]) -> Optional[ChatSession]:
        """Update session details"""
        session = self.get_by_id(id)
        if not session:
            return None
            
        for key, value in data.items():
            if hasattr(session, key):
                setattr(session, key, value)
        
        session.updated_at = datetime.now(timezone.utc)
        self.db.commit()
        self.db.refresh(session)
        return session

    def delete(self, id: str) -> bool:
        """Delete session by ID"""
        session = self.get_by_id(id)
        if not session:
            return False
        
        self.db.delete(session)
        self.db.commit()
        return True
    
    # ==================== Session Operations ====================
    
    def create_session(self, user_id: str, title: str = "New Chat") -> ChatSession:
        """Create a new chat session"""
        session = ChatSession(
            user_id=user_id,
            title=title,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)
        return session
    
    def get_user_sessions(self, user_id: str) -> List[Dict]:
        """Get all sessions for a user with message counts"""
        from sqlalchemy import func
        
        # Get sessions with message counts in one query
        # Get sessions with message counts in one query
        # Use a subquery to count messages per session
        # This avoids GROUP BY issues with full entity selection in Postgres
        stmt = (
            self.db.query(
                ChatMessage.session_id, 
                func.count(ChatMessage.id).label("count")
            )
            .group_by(ChatMessage.session_id)
            .subquery()
        )
        
        try:
            results = (
                self.db.query(ChatSession, func.coalesce(stmt.c.count, 0).label("message_count"))
                .outerjoin(stmt, ChatSession.id == stmt.c.session_id)
                .filter(ChatSession.user_id == user_id)
                .order_by(desc(ChatSession.updated_at))
                .all()
            )
        except Exception as e:
            print(f"DB ERROR in get_user_sessions: {e}")
            # Fallback to simple query if complex one fails
            try:
                print("Falling back to simple query...")
                sessions = (
                    self.db.query(ChatSession)
                    .filter(ChatSession.user_id == user_id)
                    .order_by(desc(ChatSession.updated_at))
                    .all()
                )
                return [
                    {
                        "id": s.id,
                        "title": s.title,
                        "created_at": s.created_at,
                        "updated_at": s.updated_at,
                        "message_count": len(s.messages) # N+1 query but safe fallback
                    }
                    for s in sessions
                ]
            except Exception as e2:
                print(f"Fallback failed: {e2}")
                raise e
        
        sessions = []
        for session, count in results:
            sessions.append({
                "id": session.id,
                "title": session.title,
                "created_at": session.created_at,
                "updated_at": session.updated_at,
                "message_count": count
            })
        return sessions
    
    def get_session(self, session_id: str, user_id: str) -> Optional[ChatSession]:
        """Get specific session with full message history"""
        return (
            self.db.query(ChatSession)
            .filter(ChatSession.id == session_id, ChatSession.user_id == user_id)
            .first()
        )
    
    def delete_session(self, session_id: str, user_id: str) -> bool:
        """Delete a session"""
        session = self.get_session(session_id, user_id)
        if not session:
            return False
        
        self.db.delete(session)
        self.db.commit()
        return True
    
    def update_session_title(self, session_id: str, user_id: str, new_title: str) -> bool:
        """Update the title of a session"""
        session = self.get_session(session_id, user_id)
        if not session:
            return False
            
        session.title = new_title
        session.updated_at = datetime.now(timezone.utc)
        self.db.commit()
        return True

    # ==================== Message Operations ====================
    
    def add_message(self, session_id: str, user_id: str, role: str, content: str) -> Optional[ChatMessage]:
        """Add a message to a session"""
        session = self.get_session(session_id, user_id)
        if not session:
            return None
            
        message = ChatMessage(
            session_id=session_id,
            role=role,
            content=content,
            timestamp=datetime.now(timezone.utc)
        )
        
        # Update session title if this is the first user message
        user_messages_count = self.db.query(ChatMessage).filter(
            ChatMessage.session_id == session_id,
            ChatMessage.role == "user"
        ).count()
        
        if role == "user" and user_messages_count == 0:
            session.title = content[:30] + "..." if len(content) > 30 else content
            
        session.updated_at = datetime.now(timezone.utc)
        
        self.db.add(message)
        self.db.commit()
        self.db.refresh(message)
        return message

    def edit_message(self, session_id: str, user_id: str, message_id: str, new_content: str) -> bool:
        """
        Edit a message content and remove subsequent messages.
        """
        session = self.get_session(session_id, user_id)
        if not session:
            return False
            
        # Find the message
        message = self.db.query(ChatMessage).filter(
            ChatMessage.id == message_id,
            ChatMessage.session_id == session_id
        ).first()
        
        if not message or message.role != "user":
            return False
            
        # Update content
        message.content = new_content
        
        # Remove subsequent messages
        self.db.query(ChatMessage).filter(
            ChatMessage.session_id == session_id,
            ChatMessage.timestamp > message.timestamp
        ).delete()
        
        session.updated_at = datetime.now(timezone.utc)
        self.db.commit()
        return True
    
    def get_context_messages(self, session_id: str, user_id: str, limit: int = 10) -> List[Dict]:
        """Get recent messages for context (Ollama format)"""
        session = self.get_session(session_id, user_id)
        if not session:
            return []
            
        # SQLAlchemy relationship handles fetching messages
        # Sort by timestamp to be sure
        messages = sorted(session.messages, key=lambda x: x.timestamp)
        recent = messages[-limit:]
        
        return [{"role": m.role, "content": m.content} for m in recent]
