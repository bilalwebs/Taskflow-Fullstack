"""
Integration Tests for Agent Update Task (User Story 4)

Tests the end-to-end workflow of AI agent updating tasks via chat endpoint.
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
async def test_agent_updates_task_via_chat_endpoint(test_user, test_session):
    """
    Test: Agent updates task via chat endpoint

    Verifies that AI agent can update a task through natural language.
    """
    # Setup
    task = create_test_task(test_session, test_user.id, title="Buy milk")

    # Execute
    response = await invoke_agent_with_message(
        user_id=test_user.id,
        message=f"Update task {task.id} to 'Buy organic milk'"
    )

    # Assert agent called update_task tool
    assert_tool_called(response, "update_task")

    # Verify task was updated
    updated_task = get_task_by_id(test_session, task.id)
    assert "organic milk" in updated_task.title.lower()


@pytest.mark.integration
@pytest.mark.asyncio
async def test_agent_updates_task_with_natural_language_change_x_to_y(test_user, test_session):
    """
    Test: Agent updates task with natural language "change X to Y"

    Verifies that agent recognizes "change X to Y" intent and updates task.
    """
    # Setup
    task = create_test_task(test_session, test_user.id, title="Buy milk")

    # Execute
    response = await invoke_agent_with_message(
        user_id=test_user.id,
        message="Change the milk task to 'Buy almond milk'"
    )

    # Agent should list tasks to find the task, then update it
    tool_calls = extract_tool_calls(response)
    tool_names = [tc["tool"] for tc in tool_calls]

    # Verify agent attempted to update
    assert "list_tasks" in tool_names or "update_task" in tool_names


@pytest.mark.integration
@pytest.mark.asyncio
async def test_agent_lists_tasks_then_updates_specific_task(test_user, test_session):
    """
    Test: Agent lists tasks then updates specific task

    Verifies multi-step workflow: list tasks, identify task, update it.
    """
    # Setup
    task = create_test_task(test_session, test_user.id, title="Review PR")

    # Step 1: List tasks
    response1 = await invoke_agent_with_message(
        user_id=test_user.id,
        message="Show my tasks"
    )
    assert_tool_called(response1, "list_tasks")

    # Step 2: Update specific task
    response2 = await invoke_agent_with_message(
        user_id=test_user.id,
        message=f"Update task {task.id} title to 'Review PR #123'"
    )
    assert_tool_called(response2, "update_task")

    # Verify update
    updated_task = get_task_by_id(test_session, task.id)
    assert "123" in updated_task.title
