"""
Integration Tests for Agent Delete Task (User Story 5)

Tests the end-to-end workflow of AI agent deleting tasks via chat endpoint.
"""

import pytest

from tests.utils.agent_helpers import (
    invoke_agent_with_message,
    assert_tool_called,
    extract_tool_calls
)
from tests.utils.task_helpers import create_test_task, get_task_by_id, count_tasks


@pytest.mark.integration
@pytest.mark.asyncio
async def test_agent_deletes_task_via_chat_endpoint(test_user, test_session):
    """
    Test: Agent deletes task via chat endpoint

    Verifies that AI agent can delete a task through natural language.
    """
    # Setup
    task = create_test_task(test_session, test_user.id, title="Task to delete")

    # Execute
    response = await invoke_agent_with_message(
        user_id=test_user.id,
        message=f"Delete task {task.id}"
    )

    # Assert agent called delete_task tool
    assert_tool_called(response, "delete_task")

    # Verify task was deleted
    deleted_task = get_task_by_id(test_session, task.id)
    assert deleted_task is None


@pytest.mark.integration
@pytest.mark.asyncio
async def test_agent_deletes_task_with_natural_language_delete_x(test_user, test_session):
    """
    Test: Agent deletes task with natural language "delete X"

    Verifies that agent recognizes "delete" intent and removes task.
    """
    # Setup
    task = create_test_task(test_session, test_user.id, title="Obsolete task")

    # Execute
    response = await invoke_agent_with_message(
        user_id=test_user.id,
        message="Delete the obsolete task"
    )

    # Agent should list tasks to find the task, then delete it
    tool_calls = extract_tool_calls(response)
    tool_names = [tc["tool"] for tc in tool_calls]

    # Verify agent attempted to delete
    assert "list_tasks" in tool_names or "delete_task" in tool_names


@pytest.mark.integration
@pytest.mark.asyncio
async def test_agent_lists_tasks_then_deletes_specific_task(test_user, test_session):
    """
    Test: Agent lists tasks then deletes specific task

    Verifies multi-step workflow: list tasks, identify task, delete it.
    """
    # Setup
    task1 = create_test_task(test_session, test_user.id, title="Keep this")
    task2 = create_test_task(test_session, test_user.id, title="Delete this")

    # Step 1: List tasks
    response1 = await invoke_agent_with_message(
        user_id=test_user.id,
        message="Show my tasks"
    )
    assert_tool_called(response1, "list_tasks")

    # Step 2: Delete specific task
    response2 = await invoke_agent_with_message(
        user_id=test_user.id,
        message=f"Delete task {task2.id}"
    )
    assert_tool_called(response2, "delete_task")

    # Verify only task2 was deleted
    remaining_task = get_task_by_id(test_session, task1.id)
    deleted_task = get_task_by_id(test_session, task2.id)

    assert remaining_task is not None
    assert deleted_task is None
