from sqlmodel import Field, SQLModel, Relationship, Column, JSON
from sqlalchemy import ForeignKey, Integer
from typing import Optional, Dict, Any, TYPE_CHECKING
from datetime import datetime
from enum import Enum

if TYPE_CHECKING:
    from .message import Message
    from .conversation import Conversation
    from .user import User


class ToolCallStatus(str, Enum):
    """Enum representing the status of a tool call."""
    SUCCESS = "success"
    ERROR = "error"


class ToolCallLog(SQLModel, table=True):
    """ToolCallLog model for auditing MCP tool invocations."""

    __tablename__ = "tool_call_logs"

    id: Optional[int] = Field(default=None, primary_key=True)
    message_id: Optional[int] = Field(
        default=None,
        sa_column=Column(Integer, ForeignKey("messages.id", ondelete="SET NULL"))
    )
    conversation_id: int = Field(
        sa_column=Column(Integer, ForeignKey("conversations.id", ondelete="CASCADE"), index=True, nullable=False)
    )
    user_id: int = Field(
        sa_column=Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    )
    tool_name: str = Field(max_length=50, index=True)
    arguments: Dict[str, Any] = Field(sa_column=Column(JSON))
    result: Dict[str, Any] = Field(sa_column=Column(JSON))
    status: ToolCallStatus = Field(sa_column_kwargs={"nullable": False})
    execution_time_ms: int = Field(default=0)
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)

    # Relationships
    message: Optional["Message"] = Relationship()
    conversation: "Conversation" = Relationship()
    user: "User" = Relationship()
