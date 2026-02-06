"""
Get Task MCP Tool

This tool enables the AI agent to retrieve details of a specific task by ID.
Useful for multi-step operations and context-aware task references.
"""

from typing import Dict, Any
from sqlmodel import Session, select
from ..models.task import Task
from .mcp_server import MCPContext


async def get_task_internal(
    ctx: MCPContext,
    task_id: int
) -> Dict[str, Any]:
    """
    Internal MCP tool for retrieving a specific task by ID.

    This function is called by the AgentService with user_id pre-bound.
    It retrieves detailed information about a single task.

    Args:
        ctx: MCP context containing db_engine and user_id
        task_id: ID of the task to retrieve

    Returns:
        Dict containing:
            - task: Task details (id, title, description, completed, timestamps)
            - status: "success" or "error"
            - error: Error message (only if status is "error")

    Error Cases:
        - Task not found: Returns error "Task not found"
        - Task belongs to different user: Returns error "Task not found" (security)
        - Invalid task_id: Returns error "Invalid task ID"
        - Database error: Returns error with message
    """
    try:
        # Validate task_id
        if not isinstance(task_id, int) or task_id <= 0:
            return {
                "status": "error",
                "error": "Invalid task ID"
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
        print(f"Error getting task: {str(e)}")
        return {
            "status": "error",
            "error": f"Database error: {str(e)}"
        }


def get_tool_definition() -> Dict[str, Any]:
    """
    Get OpenAI function calling definition for get_task tool.

    Returns:
        Tool definition in OpenAI function calling format
    """
    return {
        "type": "function",
        "function": {
            "name": "get_task",
            "description": (
                "Retrieve detailed information about a specific task by its ID. "
                "Use this when the user asks for details about a particular task. "
                "Examples: 'show me task 5', 'what's in task 3', 'details of the first task', "
                "'tell me about task 10'."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "task_id": {
                        "type": "integer",
                        "description": "The ID of the task to retrieve"
                    }
                },
                "required": ["task_id"]
            }
        }
    }
