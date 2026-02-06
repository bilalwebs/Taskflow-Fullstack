"""
Integration Tests for Agent Create Task (User Story 1)

Tests the end-to-end workflow of AI agent creating tasks via chat endpoint.
"""

import pytest
import asyncio
from concurrent.futures import ThreadPoolExecutor

from tests.utils.agent_helpers import (
    invoke_agent_with_message,
    assert_tool_called,
    extract_tool_calls
)
from tests.utils.task_helpers import count_tasks, get_task_by_id


@pytest.mark.integration
@pytest.mark.asyncio
async def test_agent_creates_task_via_chat_endpoint(test_user, test_session, mock_mcp_context):
    """
    Test: Agent creates task via chat endpoint

    Verifies that AI agent can create a task through natural language interaction.
    """
    # Execute
    response = await invoke_agent_with_message(
        user_id=test_user.id,
        message="Add a task to buy groceries"
    )

    # Assert agent called create_task tool
    assert_tool_called(response, "create_task")

    # Verify task was created in database
    task_count = count_tasks(test_session, test_user.id)
    assert task_count == 1

    # Verify response contains confirmation
    assert response["content"] is not None
    assert len(response["content"]) > 0


@pytest.mark.integration
@pytest.mark.asyncio
async def test_agent_creates_task_with_natural_language_remind_me(test_user, test_session):
    """
    Test: Agent creates task with natural language "remind me to X"

    Verifies that agent recognizes "remind me to" intent and creates task.
    """
    # Execute
    response = await invoke_agent_with_message(
        user_id=test_user.id,
        message="Remind me to call the dentist tomorrow"
    )

    # Assert agent called create_task tool
    assert_tool_called(response, "create_task")

    # Verify task was created
    task_count = count_tasks(test_session, test_user.id)
    assert task_count == 1

    # Extract tool calls to verify parameters
    tool_calls = extract_tool_calls(response)
    create_task_call = next((tc for tc in tool_calls if tc["tool"] == "create_task"), None)
    assert create_task_call is not None

    # Verify tool was called with appropriate title
    result = create_task_call.get("result", {})
    assert result.get("status") == "success"


@pytest.mark.integration
@pytest.mark.asyncio
async def test_multiple_agents_create_tasks_concurrently_without_conflicts(test_user, test_user2, test_session):
    """
    Test: Multiple agents create tasks concurrently without conflicts

    Verifies that concurrent task creation by different agents doesn't cause conflicts.
    """
    # Define concurrent task creation operations
    async def create_task_for_user1():
        return await invoke_agent_with_message(
            user_id=test_user.id,
            message="Add task: User 1 Task A"
        )

    async def create_task_for_user2():
        return await invoke_agent_with_message(
            user_id=test_user2.id,
            message="Add task: User 2 Task B"
        )

    # Execute concurrently
    results = await asyncio.gather(
        create_task_for_user1(),
        create_task_for_user2(),
        return_exceptions=True
    )

    # Assert both succeeded
    assert len(results) == 2
    for result in results:
        assert not isinstance(result, Exception)
        assert_tool_called(result, "create_task")

    # Verify each user has exactly 1 task
    user1_count = count_tasks(test_session, test_user.id)
    user2_count = count_tasks(test_session, test_user2.id)

    assert user1_count == 1
    assert user2_count == 1


@pytest.mark.integration
@pytest.mark.asyncio
async def test_agent_creates_multiple_tasks_in_sequence(test_user, test_session):
    """
    Test: Agent creates multiple tasks in sequence

    Verifies that agent can create multiple tasks in a single conversation.
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
        message="Also add a task to buy eggs"
    )
    assert_tool_called(response2, "create_task")

    # Verify both tasks were created
    task_count = count_tasks(test_session, test_user.id)
    assert task_count == 2


@pytest.mark.integration
@pytest.mark.asyncio
async def test_agent_creates_task_with_description(test_user, test_session):
    """
    Test: Agent creates task with description from natural language

    Verifies that agent can extract both title and description from user message.
    """
    # Execute
    response = await invoke_agent_with_message(
        user_id=test_user.id,
        message="Add a task to review the PR. Make sure to check code quality and test coverage."
    )

    # Assert agent called create_task tool
    assert_tool_called(response, "create_task")

    # Verify task was created
    task_count = count_tasks(test_session, test_user.id)
    assert task_count == 1
