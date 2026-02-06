"""
Update Task MCP Tool

This tool enables the AI agent to update existing task details.
Supports updating title and/or description.
"""

from typing import Dict, Any, Optional
from sqlmodel import Session, select
from datetime import datetime
from ..models.task import Task
from .mcp_server import MCPContext


async def update_task_internal(
    ctx: MCPContext,
    task_id: int,
    title: Optional[str] = None,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """
    Internal MCP tool for updating a task's details.

    This function is called by the AgentService with user_id pre-bound.
    It updates the task's title and/or description.

    Args:
        ctx: MCP context containing db_engine and user_id
        task_id: ID of the task to update
        title: New task title (optional, 1-200 chars)
        description: New task description (optional, max 2000 chars)

    Returns:
        Dict containing:
            - task: Updated task details
            - status: "success" or "error"
            - error: Error message (only if status is "error")

    Error Cases:
        - Task not found: Returns error "Task not found"
        - Task belongs to different user: Returns error "Task not found" (security)
        - Empty title: Returns error "Title cannot be empty"
        - Title too long: Returns error "Title exceeds 200 characters"
        - No fields to update: Returns error "No fields provided to update"
        - Database error: Returns error with message
    """
    try:
        # Validate that at least one field is provided
        if title is None and description is None:
            return {
                "status": "error",
                "error": "No fields provided to update"
            }

        # Validate title if provided
        if title is not None:
            title = title.strip()
            if not title:
                return {
                    "status": "error",
                    "error": "Title cannot be empty"
                }
            if len(title) > 200:
                return {
                    "status": "error",
                    "error": "Title exceeds 200 characters"
                }

        # Validate description length if provided
        if description is not None and len(description) > 2000:
            return {
                "status": "error",
                "error": "Description exceeds 2000 characters"
            }

        # Query task with user_id scoping for security
        with ctx.get_session() as session:
            statement = select(Task).where(
                Task.id == task_id,
                Task.user_id == ctx.user_id
            )
            task = session.exec(statement).first()

            if not task:
                return {
                    "status": "error",
                    "error": "Task not found"
                }

            # Update fields
            if title is not None:
                task.title = title
            if description is not None:
                task.description = description

            task.updated_at = datetime.utcnow()

            session.add(task)
            session.commit()
            session.refresh(task)

            # Return structured result
            return {
                "status": "success",
                "task": {
                    "id": task.id,
                    "title": task.title,
                    "description": task.description,
                    "completed": task.completed,
                    "created_at": task.created_at.isoformat(),
                    "updated_at": task.updated_at.isoformat()
                }
            }

    except Exception as e:
        # Log error and return structured error response
        print(f"Error updating task: {str(e)}")
        return {
            "status": "error",
            "error": f"Database error: {str(e)}"
        }


def get_tool_definition() -> Dict[str, Any]:
    """
    Get OpenAI function calling definition for update_task tool.

    Returns:
        Tool definition in OpenAI function calling format
    """
    return {
        "type": "function",
        "function": {
            "name": "update_task",
            "description": (
                "Update an existing task's title or description. "
                "Use this when the user wants to modify, change, or edit a task. "
                "Examples: 'change X to Y', 'update the task', 'edit task 3', "
                "'rename X to Y', 'add details to the task'."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "task_id": {
                        "type": "integer",
                        "description": "The ID of the task to update"
                    },
                    "title": {
                        "type": "string",
                        "description": "New task title (optional, 1-200 characters)"
                    },
                    "description": {
                        "type": "string",
                        "description": "New task description (optional, max 2000 characters)"
                    }
                },
                "required": ["task_id"]
            }
        }
    }
