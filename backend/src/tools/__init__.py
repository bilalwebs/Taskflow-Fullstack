"""
MCP Tools Package

This package contains all MCP tools for the AI agent.
Tools are user-scoped and enforce data isolation.
"""

from .mcp_server import MCPServer, MCPContext, mcp_server
from .list_tasks import list_tasks_internal, get_tool_definition as get_list_tasks_definition
from .create_task import create_task_internal, get_tool_definition as get_create_task_definition
from .mark_complete import mark_complete_internal, get_tool_definition as get_mark_complete_definition
from .update_task import update_task_internal, get_tool_definition as get_update_task_definition
from .delete_task import delete_task_internal, get_tool_definition as get_delete_task_definition
from .get_task import get_task_internal, get_tool_definition as get_get_task_definition

# Register tools with MCP server
mcp_server.register_tool("list_tasks", list_tasks_internal)
mcp_server.register_tool("create_task", create_task_internal)
mcp_server.register_tool("mark_complete", mark_complete_internal)
mcp_server.register_tool("update_task", update_task_internal)
mcp_server.register_tool("delete_task", delete_task_internal)
mcp_server.register_tool("get_task", get_task_internal)

__all__ = [
    "MCPServer",
    "MCPContext",
    "mcp_server",
    "list_tasks_internal",
    "create_task_internal",
    "mark_complete_internal",
    "update_task_internal",
    "delete_task_internal",
    "get_task_internal",
    "get_list_tasks_definition",
    "get_create_task_definition",
    "get_mark_complete_definition",
    "get_update_task_definition",
    "get_delete_task_definition",
    "get_get_task_definition",
]
