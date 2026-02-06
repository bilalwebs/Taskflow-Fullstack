"""
Delete Task MCP Tool

This tool enables the AI agent to permanently delete tasks.
Enforces user_id scoping for security.
"""

from typing import Dict, Any
from sqlmodel import Session, select
from ..models.task import Task
from .mcp_server import MCPContext


async def delete_task_internal(
    ctx: MCPContext,
    task_id: int
) -> Dict[str, Any]:
    """
    Internal MCP tool for deleting a task.

    This function is called by the AgentService with user_id pre-bound.
    It permanently removes the task from the database.

    Args:
        ctx: MCP context containing db_engine and user_id
        task_id: ID of the task to delete

    Returns:
        Dict containing:
            - status: "success" or "error"
            - message: Confirmation message
            - deleted_task_id: ID of the deleted task
            - error: Error message (only if status is "error")

    Error Cases:
        - Task not found: Returns error "Task not found"
        - Task belongs to different user: Returns error "Task not found" (security)
        - Database error: Returns error with message
    """
    try:
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

            # Store task title for confirmation message
            task_title = task.title

            # Delete task
            session.delete(task)
            session.commit()

            # Return structured result
            return {
                "status": "success",
                "message": f"Task '{task_title}' deleted successfully",
                "deleted_task_id": task_id
            }

    except Exception as e:
        # Log error and return structured error response
        print(f"Error deleting task: {str(e)}")
        return {
            "status": "error",
            "error": f"Database error: {str(e)}"
        }


def get_tool_definition() -> Dict[str, Any]:
    """
    Get OpenAI function calling definition for delete_task tool.

    Returns:
        Tool definition in OpenAI function calling format
    """
    return {
        "type": "function",
        "function": {
            "name": "delete_task",
            "description": (
                "Permanently delete a task. "
                "Use this when the user wants to remove, delete, or cancel a task. "
                "Examples: 'delete X', 'remove the task', 'cancel task 3', "
                "'get rid of X', 'delete my first task'."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "task_id": {
                        "type": "integer",
                        "description": "The ID of the task to delete"
                    }
                },
                "required": ["task_id"]
            }
        }
    }
