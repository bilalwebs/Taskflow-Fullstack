"""
Agent Helper Utilities for Testing

This module provides utility functions for testing AI agent behavior and tool invocations.
"""

from typing import Dict, Any, Optional, List
import asyncio

from src.services.agent_service import AgentService
from src.tools.mcp_server import MCPContext


async def invoke_agent_with_message(
    user_id: int,
    message: str,
    conversation_history: Optional[List[Dict[str, str]]] = None
) -> Dict[str, Any]:
    """
    Invoke the AI agent with a message and return the response.

    Args:
        user_id: User ID for context
        message: User message to process
        conversation_history: Optional conversation history

    Returns:
        Agent response dict with content, tool_calls, etc.
    """
    agent_service = AgentService(user_id=user_id)

    if conversation_history is None:
        conversation_history = []

    response = await agent_service.process_message(
        message=message,
        conversation_history=conversation_history
    )

    return response


async def invoke_tool_directly(
    context: MCPContext,
    tool_name: str,
    **kwargs
) -> Dict[str, Any]:
    """
    Invoke an MCP tool directly with given parameters.

    Args:
        context: MCPContext with user_id pre-bound
        tool_name: Name of tool to invoke
        **kwargs: Tool parameters

    Returns:
        Tool execution result
    """
    from src.tools import mcp_server

    tool_func = mcp_server.get_tool(tool_name)

    if not tool_func:
        raise ValueError(f"Tool '{tool_name}' not found")

    result = await tool_func(context, **kwargs)
    return result


def extract_tool_calls(agent_response: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Extract tool calls from agent response.

    Args:
        agent_response: Agent response dict

    Returns:
        List of tool call dicts
    """
    return agent_response.get("tool_calls", [])


def assert_tool_called(agent_response: Dict[str, Any], tool_name: str):
    """
    Assert that a specific tool was called in the agent response.

    Args:
        agent_response: Agent response dict
        tool_name: Expected tool name

    Raises:
        AssertionError: If tool was not called
    """
    tool_calls = extract_tool_calls(agent_response)

    tool_names = [tc.get("tool") for tc in tool_calls]

    assert tool_name in tool_names, f"Expected tool '{tool_name}' to be called, but got: {tool_names}"


def assert_tool_succeeded(tool_result: Dict[str, Any]):
    """
    Assert that a tool execution succeeded.

    Args:
        tool_result: Tool execution result

    Raises:
        AssertionError: If tool execution failed
    """
    status = tool_result.get("status")

    if status == "error":
        error_msg = tool_result.get("error", "Unknown error")
        raise AssertionError(f"Tool execution failed: {error_msg}")

    assert status == "success", f"Expected status 'success', got '{status}'"


def assert_tool_failed(tool_result: Dict[str, Any], expected_error: Optional[str] = None):
    """
    Assert that a tool execution failed with expected error.

    Args:
        tool_result: Tool execution result
        expected_error: Optional expected error message substring

    Raises:
        AssertionError: If tool execution succeeded or error doesn't match
    """
    status = tool_result.get("status")

    assert status == "error", f"Expected status 'error', got '{status}'"

    if expected_error:
        error_msg = tool_result.get("error", "")
        assert expected_error in error_msg, f"Expected error containing '{expected_error}', got '{error_msg}'"


def create_mock_conversation_history(messages: List[tuple]) -> List[Dict[str, str]]:
    """
    Create mock conversation history for testing.

    Args:
        messages: List of (role, content) tuples

    Returns:
        Formatted conversation history

    Example:
        history = create_mock_conversation_history([
            ("user", "Add a task to buy groceries"),
            ("assistant", "I've added the task.")
        ])
    """
    history = []

    for role, content in messages:
        history.append({
            "role": role,
            "content": content
        })

    return history


async def test_agent_intent_recognition(
    user_id: int,
    message: str,
    expected_tool: str
) -> bool:
    """
    Test that agent correctly recognizes user intent and selects appropriate tool.

    Args:
        user_id: User ID for context
        message: User message
        expected_tool: Expected tool name to be called

    Returns:
        True if agent selected correct tool, False otherwise
    """
    response = await invoke_agent_with_message(user_id, message)

    tool_calls = extract_tool_calls(response)

    if not tool_calls:
        return False

    tool_names = [tc.get("tool") for tc in tool_calls]

    return expected_tool in tool_names
