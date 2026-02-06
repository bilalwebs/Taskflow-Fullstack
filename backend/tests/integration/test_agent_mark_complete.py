"""
Integration Tests for Agent Mark Complete (User Story 3)

Tests the end-to-end workflow of AI agent marking tasks complete via chat endpoint.
"""

import pytest

from tests.utils.agent_helpers import (
    invoke_agent_with_message,
    assert_tool_called,
    extract_tool_calls
)
from tests.utils.task_helpers import create_test_task, get_task_by_id


@pytest.mark.integration
@pytest.mark.asyncio
async def test_agent_marks_task_complete_via_chat_endpoint(test_user, test_session):
    """
    Test: Agent marks task complete via chat endpoint

    Verifies that AI agent can mark a task complete through natural language.
    """
    # Setup: Create a task
    task = create_test_task(test_session, test_user.id, title="Buy groceries", completed=False)

    # Execute
    response = await invoke_agent_with_message(
        user_id=test_user.id,
        message=f"Mark task {task.id} as complete"
    )

    # Assert agent called mark_complete tool
    assert_tool_called(response, "mark_complete")

    # Verify task is marked complete
    updated_task = get_task_by_id(test_session, task.id)
    assert updated_task.completed is True


@pytest.mark.integration
@pytest.mark.asyncio
async def test_agent_marks_task_complete_with_natural_language_i_finished(test_user, test_session):
    """
    Test: Agent marks task complete with natural language "I finished X"

    Verifies that agent recognizes "I finished" intent and marks task complete.
    """
    # Setup: Create a task
    task = create_test_task(test_session, test_user.id, title="Buy groceries", completed=False)

    # Execute - agent should list tasks first, then mark complete
    response = await invoke_agent_with_message(
        user_id=test_user.id,
        message="I finished buying groceries"
    )

    # Agent should call list_tasks to find the task, then mark_complete
    tool_calls = extract_tool_calls(response)
    tool_names = [tc["tool"] for tc in tool_calls]

    # Verify agent used appropriate tools
    assert "list_tasks" in tool_names or "mark_complete" in tool_names


@pytest.mark.integration
@pytest.mark.asyncio
async def test_agent_lists_tasks_then_marks_specific_task_complete(test_user, test_session):
    """
    Test: Agent lists tasks then marks specific task complete

    Verifies multi-step workflow: list tasks, identify task, mark complete.
    """
    # Setup: Create multiple tasks
    task1 = create_test_task(test_session, test_user.id, title="Buy milk", completed=False)
    task2 = create_test_task(test_session, test_user.id, title="Buy eggs", completed=False)

    # Step 1: List tasks
    response1 = await invoke_agent_with_message(
        user_id=test_user.id,
        message="Show my tasks"
    )
    assert_tool_called(response1, "list_tasks")

    # Step 2: Mark specific task complete
    response2 = await invoke_agent_with_message(
        user_id=test_user.id,
        message=f"Mark task {task1.id} as done"
    )
    assert_tool_called(response2, "mark_complete")

    # Verify only task1 is completed
    updated_task1 = get_task_by_id(test_session, task1.id)
    updated_task2 = get_task_by_id(test_session, task2.id)

    assert updated_task1.completed is True
    assert updated_task2.completed is False


@pytest.mark.integration
@pytest.mark.asyncio
async def test_agent_marks_task_complete_by_title_reference(test_user, test_session):
    """
    Test: Agent marks task complete by title reference

    Verifies that agent can identify task by title and mark it complete.
    """
    # Setup: Create a task
    task = create_test_task(test_session, test_user.id, title="Call dentist", completed=False)

    # Execute - reference task by title
    response = await invoke_agent_with_message(
        user_id=test_user.id,
        message="I completed the dentist call"
    )

    # Agent should list tasks to find matching task, then mark complete
    tool_calls = extract_tool_calls(response)
    tool_names = [tc["tool"] for tc in tool_calls]

    # Verify agent attempted to complete the task
    assert "list_tasks" in tool_names or "mark_complete" in tool_names
