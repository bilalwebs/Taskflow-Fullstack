"""
Unit Tests for mark_complete MCP Tool

Tests the mark_complete tool functionality including:
- Toggles task to completed
- Idempotent behavior on already completed tasks
- Error handling for non-existent task_id
- Task ownership validation
- Updates updated_at timestamp
"""

import pytest
from datetime import datetime, timedelta

from src.tools.mark_complete import mark_complete_internal
from tests.utils.task_helpers import create_test_task, get_task_by_id


@pytest.mark.unit
@pytest.mark.asyncio
async def test_mark_complete_toggles_task_to_completed(mock_mcp_context, test_session):
    """
    Test: mark_complete toggles task to completed

    Verifies that mark_complete successfully marks a pending task as completed.
    """
    # Setup: Create a pending task
    task = create_test_task(test_session, mock_mcp_context.user_id, title="Test Task", completed=False)

    # Execute
    result = await mark_complete_internal(
        ctx=mock_mcp_context,
        task_id=task.id
    )

    # Assert
    assert result["status"] == "success"
    assert result["task"]["id"] == task.id
    assert result["task"]["title"] == "Test Task"
    assert result["task"]["completed"] is True

    # Verify task is marked complete in database
    updated_task = get_task_by_id(test_session, task.id)
    assert updated_task.completed is True


@pytest.mark.unit
@pytest.mark.asyncio
async def test_mark_complete_on_already_completed_task_is_idempotent(mock_mcp_context, test_session):
    """
    Test: mark_complete on already completed task is idempotent

    Verifies that marking an already completed task as complete succeeds without error.
    """
    # Setup: Create a completed task
    task = create_test_task(test_session, mock_mcp_context.user_id, title="Completed Task", completed=True)

    # Execute
    result = await mark_complete_internal(
        ctx=mock_mcp_context,
        task_id=task.id
    )

    # Assert - should succeed (idempotent)
    assert result["status"] == "success"
    assert result["task"]["completed"] is True

    # Verify task remains completed
    updated_task = get_task_by_id(test_session, task.id)
    assert updated_task.completed is True


@pytest.mark.unit
@pytest.mark.asyncio
async def test_mark_complete_with_non_existent_task_id_returns_error(mock_mcp_context):
    """
    Test: mark_complete with non-existent task_id returns error

    Verifies that mark_complete returns error for non-existent task.
    """
    # Execute with non-existent task_id
    result = await mark_complete_internal(
        ctx=mock_mcp_context,
        task_id=99999
    )

    # Assert
    assert result["status"] == "error"
    assert "error" in result
    assert "not found" in result["error"].lower()


@pytest.mark.unit
@pytest.mark.asyncio
async def test_mark_complete_validates_task_ownership(mock_mcp_context, mock_mcp_context_user2, test_session):
    """
    Test: mark_complete validates task ownership

    Verifies that mark_complete returns error when trying to complete another user's task.
    """
    # Setup: Create task for user 2
    task = create_test_task(test_session, mock_mcp_context_user2.user_id, title="User 2 Task")

    # Execute with user 1 context (trying to complete user 2's task)
    result = await mark_complete_internal(
        ctx=mock_mcp_context,
        task_id=task.id
    )

    # Assert - should fail (unauthorized)
    assert result["status"] == "error"
    assert "error" in result
    assert "not found" in result["error"].lower()  # Returns "not found" to prevent information disclosure

    # Verify task remains unchanged
    unchanged_task = get_task_by_id(test_session, task.id)
    assert unchanged_task.completed is False


@pytest.mark.unit
@pytest.mark.asyncio
async def test_mark_complete_updates_updated_at_timestamp(mock_mcp_context, test_session):
    """
    Test: mark_complete updates updated_at timestamp

    Verifies that mark_complete updates the updated_at timestamp.
    """
    # Setup: Create task with old timestamp
    task = create_test_task(test_session, mock_mcp_context.user_id, title="Test Task")
    original_updated_at = task.updated_at

    # Wait a moment to ensure timestamp difference
    import time
    time.sleep(0.1)

    # Execute
    result = await mark_complete_internal(
        ctx=mock_mcp_context,
        task_id=task.id
    )

    # Assert
    assert result["status"] == "success"

    # Verify updated_at was updated
    updated_task = get_task_by_id(test_session, task.id)
    assert updated_task.updated_at > original_updated_at


@pytest.mark.unit
@pytest.mark.asyncio
async def test_mark_complete_toggles_completed_to_incomplete(mock_mcp_context, test_session):
    """
    Test: mark_complete toggles completed task back to incomplete

    Verifies that mark_complete can toggle a completed task back to incomplete.
    """
    # Setup: Create a completed task
    task = create_test_task(test_session, mock_mcp_context.user_id, title="Completed Task", completed=True)

    # Execute mark_complete (should toggle to incomplete)
    result = await mark_complete_internal(
        ctx=mock_mcp_context,
        task_id=task.id
    )

    # Assert - task should be toggled to incomplete
    assert result["status"] == "success"
    assert result["task"]["completed"] is False

    # Verify in database
    updated_task = get_task_by_id(test_session, task.id)
    assert updated_task.completed is False


@pytest.mark.unit
@pytest.mark.asyncio
async def test_mark_complete_returns_task_details(mock_mcp_context, test_session):
    """
    Test: mark_complete returns task details in response

    Verifies that mark_complete returns complete task information.
    """
    # Setup
    task = create_test_task(test_session, mock_mcp_context.user_id, title="My Task")

    # Execute
    result = await mark_complete_internal(
        ctx=mock_mcp_context,
        task_id=task.id
    )

    # Assert response contains required fields
    assert result["status"] == "success"
    assert "task" in result

    task_data = result["task"]
    assert "id" in task_data
    assert "title" in task_data
    assert "completed" in task_data
    assert "updated_at" in task_data

    assert task_data["id"] == task.id
    assert task_data["title"] == "My Task"
