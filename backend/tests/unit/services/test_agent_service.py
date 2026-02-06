"""
Unit Tests for AgentService

Tests the AgentService orchestration including:
- Creates user-scoped context
- Executes tools with MCPContext
- Handles tool errors gracefully
- Formats conversation history correctly
"""

import pytest
from unittest.mock import Mock, patch

from src.services.agent_service import AgentService
from tests.utils.task_helpers import create_test_task


@pytest.mark.unit
@pytest.mark.asyncio
async def test_agent_service_creates_user_scoped_context(test_user):
    """
    Test: AgentService creates user-scoped context

    Verifies that AgentService initializes with user_id pre-bound.
    """
    # Execute
    agent_service = AgentService(user_id=test_user.id)

    # Assert
    assert agent_service.user_id == test_user.id
    assert agent_service.mcp_context is not None
    assert agent_service.mcp_context.user_id == test_user.id


@pytest.mark.unit
@pytest.mark.asyncio
async def test_agent_service_executes_tools_with_mcp_context(test_user, mock_mcp_context, test_session):
    """
    Test: AgentService executes tools with MCPContext

    Verifies that AgentService can execute MCP tools with context.
    """
    # Setup
    agent_service = AgentService(user_id=test_user.id)
    create_test_task(test_session, test_user.id, title="Test Task")

    # Execute
    result = await agent_service.execute_tool(
        tool_name="list_tasks",
        arguments={}
    )

    # Assert
    assert "tasks" in result
    assert isinstance(result["tasks"], list)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_agent_service_handles_tool_errors_gracefully(test_user):
    """
    Test: AgentService handles tool errors gracefully

    Verifies that AgentService catches and returns errors from tools.
    """
    # Setup
    agent_service = AgentService(user_id=test_user.id)

    # Execute with invalid tool name
    result = await agent_service.execute_tool(
        tool_name="nonexistent_tool",
        arguments={}
    )

    # Assert - should return error structure
    assert "status" in result or "error" in result


@pytest.mark.unit
def test_agent_service_formats_conversation_history_correctly(test_user):
    """
    Test: AgentService formats conversation history correctly

    Verifies that AgentService converts database messages to OpenAI format.
    """
    # Setup
    agent_service = AgentService(user_id=test_user.id)

    # Mock messages
    from src.models.message import MessageRole
    mock_messages = [
        Mock(role=MessageRole.USER, content="Hello"),
        Mock(role=MessageRole.ASSISTANT, content="Hi there")
    ]

    # Execute
    history = agent_service.format_conversation_history(mock_messages)

    # Assert
    assert len(history) == 2
    assert history[0]["role"] == "user"
    assert history[0]["content"] == "Hello"
    assert history[1]["role"] == "assistant"
    assert history[1]["content"] == "Hi there"
