"""
MCP Server Setup Module

This module provides the MCP server configuration and context setup for the AI agent.
MCP tools are embedded in the FastAPI process for security and performance.
"""

from typing import Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncEngine
from sqlmodel import Session
from ..database import engine


class MCPContext:
    """
    MCP Context configuration containing shared resources for MCP tools.

    This context is passed to all MCP tools to provide access to:
    - Database engine for query execution
    - User ID for data isolation
    - Configuration settings
    """

    def __init__(
        self,
        db_engine: AsyncEngine,
        user_id: int,
        config: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize MCP context.

        Args:
            db_engine: SQLAlchemy async engine for database operations
            user_id: Authenticated user ID for data scoping
            config: Optional configuration dictionary
        """
        self.db_engine = db_engine
        self.user_id = user_id
        self.config = config or {}

    def get_session(self) -> Session:
        """
        Create a new database session.

        Returns:
            SQLModel Session instance
        """
        return Session(self.db_engine)


class MCPServer:
    """
    MCP Server setup and configuration.

    This class manages the MCP server lifecycle and tool registration.
    In embedded mode, tools are registered directly in the FastAPI process.
    """

    def __init__(self):
        """Initialize MCP server."""
        self.tools = {}
        self.db_engine = engine

    def register_tool(self, name: str, tool_func: callable):
        """
        Register an MCP tool.

        Args:
            name: Tool name (e.g., "list_tasks")
            tool_func: Tool function to execute
        """
        self.tools[name] = tool_func

    def create_context(self, user_id: int) -> MCPContext:
        """
        Create a user-scoped MCP context.

        Args:
            user_id: Authenticated user ID

        Returns:
            MCPContext instance with user_id pre-bound
        """
        return MCPContext(
            db_engine=self.db_engine,
            user_id=user_id
        )

    def get_tool(self, name: str) -> Optional[callable]:
        """
        Get a registered tool by name.

        Args:
            name: Tool name

        Returns:
            Tool function or None if not found
        """
        return self.tools.get(name)

    def list_tools(self) -> list[str]:
        """
        List all registered tool names.

        Returns:
            List of tool names
        """
        return list(self.tools.keys())


# Global MCP server instance
mcp_server = MCPServer()
