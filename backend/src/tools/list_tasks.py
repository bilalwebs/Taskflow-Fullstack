"""
List Tasks MCP Tool

This tool enables the AI agent to retrieve all tasks for the authenticated user.
Returns task list with completion status and counts.
"""

from typing import Dict, Any, List
from sqlmodel import Session, select
from ..models.task import Task
from .mcp_server import MCPContext


async def list_tasks_internal(ctx: MCPContext) -> Dict[str, Any]:
    """
    Internal MCP tool for listing all tasks for the authenticated user.

    This function is called by the AgentService with user_id pre-bound.
    It retrieves all tasks from the database and returns structured result.

    Args:
        ctx: MCP context containing db_engine and user_id

    Returns:
        Dict containing:
            - tasks: List of task objects with all fields
            - total: Total number of tasks
            - completed_count: Number of completed tasks
            - pending_count: Number of incomplete tasks

    Error Cases:
        - Database connection failure: Returns error with message
        - No tasks found: Returns empty array (not an error)
    """
    try:
        # Query tasks for user
        with ctx.get_session() as session:
            statement = select(Task).where(Task.user_id == ctx.user_id)
            tasks = session.exec(statement).all()

            # Convert tasks to dict format
            task_list = []
            for task in tasks:
                task_list.append({
                    "id": task.id,
                    "title": task.title,
                    "description": task.description,
                    "completed": task.completed,
                    "created_at": task.created_at.isoformat(),
                    "updated_at": task.updated_at.isoformat()
                })

            # Calculate counts
            completed_count = sum(1 for t in tasks if t.completed)
            pending_count = sum(1 for t in tasks if not t.completed)

            return {
                "tasks": task_list,
                "total": len(tasks),
                "completed_count": completed_count,
                "pending_count": pending_count
            }

    except Exception as e:
        # Log error and return structured error response
        print(f"Error listing tasks: {str(e)}")
        return {
            "status": "error",
            "error": f"Database error: {str(e)}",
            "tasks": [],
            "total": 0,
            "completed_count": 0,
            "pending_count": 0
        }


def get_tool_definition() -> Dict[str, Any]:
    """
    Get OpenAI function calling definition for list_tasks tool.

    Returns:
        Tool definition in OpenAI function calling format
    """
    return {
        "type": "function",
        "function": {
            "name": "list_tasks",
            "description": (
                "Retrieve all tasks for the user with their completion status. "
                "Use this when the user wants to see their tasks, check what they need to do, "
                "or inquire about their task list. "
                "Examples: 'show my tasks', 'what do I need to do', 'list my todos', "
                "'what are my tasks', 'show me my task list'."
            ),
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    }
