"""
Mark Complete MCP Tool

This tool enables the AI agent to toggle task completion status.
Supports marking tasks as complete or incomplete.
"""

from typing import Dict, Any
from sqlmodel import Session, select
from datetime import datetime
from ..models.task import Task
from .mcp_server import MCPContext


async def mark_complete_internal(
    ctx: MCPContext,
    task_id: int
) -> Dict[str, Any]:
    """
    Internal MCP tool for toggling task completion status.

    This function is called by the AgentService with user_id pre-bound.
    It finds the task and toggles its completed status.

    Args:
        ctx: MCP context containing db_engine and user_id
        task_id: ID of the task to mark complete/incomplete

    Returns:
        Dict containing:
            - task: Updated task details
            - status: "success" or "error"
            - action: "marked_complete" or "marked_incomplete"
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

            # Toggle completion status
            task.completed = not task.completed
            task.updated_at = datetime.utcnow()

            session.add(task)
            session.commit()
            session.refresh(task)

            # Return structured result
            return {
                "status": "success",
                "action": "marked_complete" if task.completed else "marked_incomplete",
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
        print(f"Error marking task complete: {str(e)}")
        return {
            "status": "error",
            "error": f"Database error: {str(e)}"
        }


def get_tool_definition() -> Dict[str, Any]:
    """
    Get OpenAI function calling definition for mark_complete tool.

    Returns:
        Tool definition in OpenAI function calling format
    """
    return {
        "type": "function",
        "function": {
            "name": "mark_complete",
            "description": (
                "Toggle the completion status of a task (mark as complete or incomplete). "
                "Use this when the user indicates they finished a task or wants to mark it as done. "
                "Examples: 'I finished X', 'mark X as done', 'complete the task', "
                "'I completed X', 'mark task 5 as complete'."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "task_id": {
                        "type": "integer",
                        "description": "The ID of the task to mark as complete/incomplete"
                    }
                },
                "required": ["task_id"]
            }
        }
    }
