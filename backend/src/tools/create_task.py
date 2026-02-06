"""
Create Task MCP Tool

This tool enables the AI agent to create new tasks for the authenticated user.
Enforces user_id scoping and validates input parameters.
"""

from typing import Dict, Any
from sqlmodel import Session
from datetime import datetime
from ..models.task import Task
from .mcp_server import MCPContext


async def create_task_internal(
    ctx: MCPContext,
    title: str,
    description: str = ""
) -> Dict[str, Any]:
    """
    Internal MCP tool for creating a new task.

    This function is called by the AgentService with user_id pre-bound.
    It creates a task in the database and returns structured result.

    Args:
        ctx: MCP context containing db_engine and user_id
        title: Task title (required, 1-200 chars)
        description: Task description (optional, max 2000 chars)

    Returns:
        Dict containing:
            - task: Created task details (id, title, description, completed, timestamps)
            - status: "success" or "error"
            - error: Error message (only if status is "error")

    Error Cases:
        - Empty title: Returns error "Title is required"
        - Title too long: Returns error "Title exceeds 200 characters"
        - Database error: Returns error with message
    """
    try:
        # Validate title
        if not title or title.strip() == "":
            return {
                "status": "error",
                "error": "Title is required"
            }

        title = title.strip()

        if len(title) > 200:
            return {
                "status": "error",
                "error": "Title exceeds 200 characters"
            }

        # Validate description length
        if description and len(description) > 2000:
            return {
                "status": "error",
                "error": "Description exceeds 2000 characters"
            }

        # Create task in database
        with ctx.get_session() as session:
            task = Task(
                title=title,
                description=description if description else None,
                completed=False,
                user_id=ctx.user_id,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )

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
        print(f"Error creating task: {str(e)}")
        return {
            "status": "error",
            "error": f"Database error: {str(e)}"
        }


def get_tool_definition() -> Dict[str, Any]:
    """
    Get OpenAI function calling definition for create_task tool.

    Returns:
        Tool definition in OpenAI function calling format
    """
    return {
        "type": "function",
        "function": {
            "name": "create_task",
            "description": (
                "Create a new task for the user. "
                "Use this when the user wants to add a task, reminder, or todo item. "
                "Examples: 'remind me to X', 'add task X', 'I need to X', 'create a task for X'."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {
                        "type": "string",
                        "description": "The task title or main description (required, 1-200 characters)"
                    },
                    "description": {
                        "type": "string",
                        "description": "Additional details or notes about the task (optional, max 2000 characters)"
                    }
                },
                "required": ["title"]
            }
        }
    }
