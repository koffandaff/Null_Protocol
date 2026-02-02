"""
Base Repository - Abstract class for database operations

Provides a consistent interface for CRUD operations.
All repository implementations should inherit from this class.
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, TypeVar, Generic
from sqlalchemy.orm import Session

T = TypeVar("T")


class BaseRepository(ABC, Generic[T]):
    """
    Abstract base repository defining the interface for all repositories.
    
    This pattern allows easy database swapping:
    1. Create a new repository implementation
    2. Switch the dependency injection
    3. No changes needed in services
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    @abstractmethod
    def create(self, data: Dict[str, Any]) -> T:
        """Create a new record"""
        pass
    
    @abstractmethod
    def get_by_id(self, id: str) -> Optional[T]:
        """Get a record by its ID"""
        pass
    
    @abstractmethod
    def get_all(self, limit: int = 100, skip: int = 0) -> List[T]:
        """Get all records with pagination"""
        pass
    
    @abstractmethod
    def update(self, id: str, data: Dict[str, Any]) -> Optional[T]:
        """Update a record by ID"""
        pass
    
    @abstractmethod
    def delete(self, id: str) -> bool:
        """Delete a record by ID"""
        pass
    
    def commit(self):
        """Commit the current transaction"""
        self.db.commit()
    
    def rollback(self):
        """Rollback the current transaction"""
        self.db.rollback()
