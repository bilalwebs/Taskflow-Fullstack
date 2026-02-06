from sqlmodel import Field, SQLModel, Relationship
from typing import Optional, List, TYPE_CHECKING
from datetime import datetime

if TYPE_CHECKING:
    from .task import Task
    from .conversation import Conversation


class User(SQLModel, table=True):
    """User model representing a person with an account in the system."""

    __tablename__ = "users"

    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True, max_length=255)
    password_hash: str = Field(max_length=255)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    tasks: List["Task"] = Relationship(back_populates="owner", cascade_delete=True)
    conversations: List["Conversation"] = Relationship(back_populates="owner", cascade_delete=True)
