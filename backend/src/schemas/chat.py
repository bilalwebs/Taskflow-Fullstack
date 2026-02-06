"""
Chat API Schemas

Request and response models for the chat endpoint.
"""

from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Dict, Any
from datetime import datetime


class ChatRequest(BaseModel):
    """Request model for chat endpoint."""

    message: str = Field(
        ...,
        min_length=1,
        max_length=2000,
        description="User's natural language message"
    )
    conversation_id: Optional[int] = Field(
        default=None,
        description="Existing conversation ID to continue (omit for new conversation)"
    )

    @field_validator('message')
    @classmethod
    def validate_message(cls, v: str) -> str:
        """Validate message is not empty or whitespace-only."""
        if not v or v.strip() == "":
            raise ValueError("Message cannot be empty or whitespace-only")
        return v.strip()


class ToolCallResult(BaseModel):
    """Tool call result metadata."""

    tool: str = Field(..., description="Tool name")
    parameters: Dict[str, Any] = Field(..., description="Tool parameters")
    result: Dict[str, Any] = Field(..., description="Tool execution result")
    duration_ms: Optional[int] = Field(None, description="Execution time in milliseconds")


class ChatResponse(BaseModel):
    """Response model for chat endpoint."""

    conversation_id: int = Field(..., description="Conversation identifier")
    message_id: int = Field(..., description="Assistant message ID")
    assistant_message: str = Field(..., description="Natural language response from agent")
    tool_calls: Optional[List[ToolCallResult]] = Field(
        default=None,
        description="List of MCP tool invocations (empty if no tools used)"
    )
    timestamp: datetime = Field(..., description="Response generation timestamp")

    class Config:
        json_schema_extra = {
            "example": {
                "conversation_id": 456,
                "message_id": 789,
                "assistant_message": "I've added 'Buy groceries tomorrow' to your tasks. Task created successfully!",
                "tool_calls": [
                    {
                        "tool": "create_task",
                        "parameters": {
                            "title": "Buy groceries tomorrow",
                            "description": ""
                        },
                        "result": {
                            "task_id": 101,
                            "status": "success"
                        },
                        "duration_ms": 45
                    }
                ],
                "timestamp": "2026-02-03T10:30:00Z"
            }
        }
