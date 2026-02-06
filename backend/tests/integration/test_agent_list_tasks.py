"""
Integration Tests for Agent List Tasks (User Story 2)

Tests the end-to-end workflow of AI agent listing tasks via chat endpoint.
"""

import pytest

from tests.utils.agent_helpers import (
    invoke_agent_with_message,
    assert_tool_called,
    extract_tool_calls
)
from tests.utils.task_helpers import create_multiple_tasks


@pytest.mark.integration
@pytest.mark.asyncio
async def test_agent_lists_tasks_via_chat_endpoint(test_user, test_session):
    """
    Test: Agent lists tasks via chat endpoint

    Verifies that AI agent can list tasks through natural language interaction.
    """
    # Setup: Create some tasks
    create_multiple_tasks(test_session, test_user.id, count=3, title_prefix="Task")

    # Execute
    response = await invoke_agent_with_message(
        user_id=test_user.id,
        message="Show me my tasks"
    )

    # Assert agent called list_tasks tool
    assert_tool_called(response, "list_tasks")

    # Verify response contains task information
    assert response["content"] is not None
    assert len(response["content"]) > 0


@pytest.mark.integration
@pytest.mark.asyncio
async def test_agent_lists_tasks_with_natural_language_show_my_tasks(test_user, test_session):
    """
    Test: Agent lists tasks with natural language "show my tasks"

    Verifies that agent recognizes "show my tasks" intent and lists tasks.
    """
    # Setup: Create tasks
    create_multiple_tasks(test_session, test_user.id, count=2, title_prefix="My Task")

    # Execute
    response = await invoke_agent_with_message(
        user_id=test_user.id,
        message="Show my tasks"
    )

    # Assert agent called list_tasks tool
    assert_tool_called(response, "list_tasks")

    # Extract tool calls to verify result
    tool_calls = extract_tool_calls(response)
    list_tasks_call = next((tc for tc in tool_calls if tc["tool"] == "list_tasks"), None)
    assert list_tasks_call is not None

    # Verify tool returned tasks
    result = list_tasks_call.get("result", {})
    assert "tasks" in result
    assert len(result["tasks"]) == 2


@pytest.mark.integration
@pytest.mark.asyncio
async def test_agent_lists_tasks_after_creating_multiple_tasks(test_user, test_session):
    """
    Test: Agent lists tasks after creating multiple tasks

    Verifies that agent can create tasks and then list them in sequence.
    """
    # Create first task
    response1 = await invoke_agent_with_message(
        user_id=test_user.id,
        message="Add a task to buy milk"
    )
    assert_tool_called(response1, "create_task")

    # Create second task
    response2 = await invoke_agent_with_message(
        user_id=test_user.id,
        message="Add a task to buy eggs"
    )
    assert_tool_called(response2, "create_task")

    # List tasks
    response3 = await invoke_agent_with_message(
        user_id=test_user.id,
        message="What are my tasks?"
    )
    assert_tool_called(response3, "list_tasks")

    # Verify list_tasks returned both tasks
    tool_calls = extract_tool_calls(response3)
    list_tasks_call = next((tc for tc in tool_calls if tc["tool"] == "list_tasks"), None)
    result = list_tasks_call.get("result", {})

    assert result["total"] == 2


@pytest.mark.integration
@pytest.mark.asyncio
async def test_agent_lists_tasks_with_empty_list(test_user, test_session):
    """
    Test: Agent lists tasks with empty list

    Verifies that agent handles empty task list gracefully.
    """
    # Execute without creating any tasks
    response = await invoke_agent_with_message(
        user_id=test_user.id,
        message="Show me my tasks"
    )

    # Assert agent called list_tasks tool
    assert_tool_called(response, "list_tasks")

    # Verify agent provides appropriate response for empty list
    assert response["content"] is not None
    # Agent should indicate no tasks exist


@pytest.mark.integration
@pytest.mark.asyncio
async def test_agent_lists_tasks_with_various_natural_language_phrases(test_user, test_session):
    """
    Test: Agent lists tasks with various natural language phrases

    Verifies that agent recognizes different ways of asking for task list.
    """
    # Setup: Create tasks
    create_multiple_tasks(test_session, test_user.id, count=2)

    # Test various phrases
    phrases = [
        "What do I need to do?",
        "List my todos",
        "What are my tasks?",
        "Show me my task list"
    ]

    for phrase in phrases:
        response = await invoke_agent_with_message(
            user_id=test_user.id,
            message=phrase
        )

        # Assert agent called list_tasks tool for each phrase
        assert_tool_called(response, "list_tasks")
