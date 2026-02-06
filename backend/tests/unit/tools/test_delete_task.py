"""
Unit Tests for delete_task MCP Tool

Tests the delete_task tool functionality including:
- Removes task from database
- Error for non-existent task_id
- Task ownership validation
- Returns deleted task details
"""

import pytest

from src.tools.delete_task import delete_task_internal
from tests.utils.task_helpers import create_test_task, get_task_by_id, count_tasks


@pytest.mark.unit
@pytest.mark.asyncio
async def test_delete_task_removes_task_from_database(mock_mcp_context, test_session):
    """
    Test: delete_task removes task from database

    Verifies that delete_task permanently removes the task.
    """
    # Setup
    task = create_test_task(test_session, mock_mcp_context.user_id, title="Task to delete")
    task_id = task.id

    # Execute
    result = await delete_task_internal(
        ctx=mock_mcp_context,
        task_id=task_id
    )

    # Assert
    assert result["status"] == "success"
    assert result["task"]["id"] == task_id
    assert result["task"]["title"] == "Task to delete"

    # Verify task no longer exists
    deleted_task = get_task_by_id(test_session, task_id)
    assert deleted_task is None


@pytest.mark.unit
@pytest.mark.asyncio
async def test_delete_task_with_non_existent_task_id_returns_error(mock_mcp_context):
    """
    Test: delete_task with non-existent task_id returns error

    Verifies that delete_task returns error for non-existent task.
    """
    # Execute
    result = await delete_task_internal(
        ctx=mock_mcp_context,
        task_id=99999
    )

    # Assert
    assert result["status"] == "error"
    assert "error" in result
    assert "not found" in result["error"].lower()


@pytest.mark.unit
@pytest.mark.asyncio
async def test_delete_task_validates_task_ownership(mock_mcp_context, mock_mcp_context_user2, test_session):
    """
    Test: delete_task validates task ownership

    Verifies that delete_task returns error when trying to delete another user's task.
    """
    # Setup: Create task for user 2
    task = create_test_task(test_session, mock_mcp_context_user2.user_id, title="User 2 Task")

    # Execute with user 1 context
    result = await delete_task_internal(
        ctx=mock_mcp_context,
        task_id=task.id
    )

    # Assert - should fail
    assert result["status"] == "error"
    assert "not found" in result["error"].lower()

    # Verify task still exists
    unchanged_task = get_task_by_id(test_session, task.id)
    assert unchanged_task is not None
    assert unchanged_task.title == "User 2 Task"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_delete_task_returns_deleted_task_details(mock_mcp_context, test_session):
    """
    Test: delete_task returns deleted task details

    Verifies that delete_task returns information about the deleted task.
    """
    # Setup
    task = create_test_task(test_session, mock_mcp_context.user_id, title="My Task")

    # Execute
    result = await delete_task_internal(
        ctx=mock_mcp_context,
        task_id=task.id
    )

    # Assert response contains task details
    assert result["status"] == "success"
    assert "task" in result
    assert result["task"]["id"] == task.id
    assert result["task"]["title"] == "My Task"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_delete_task_decrements_task_count(mock_mcp_context, test_session):
    """
    Test: delete_task decrements task count

    Verifies that deleting a task reduces the total task count.
    """
    # Setup: Create 3 tasks
    task1 = create_test_task(test_session, mock_mcp_context.user_id, title="Task 1")
    task2 = create_test_task(test_session, mock_mcp_context.user_id, title="Task 2")
    task3 = create_test_task(test_session, mock_mcp_context.user_id, title="Task 3")

    # Verify initial count
    initial_count = count_tasks(test_session, mock_mcp_context.user_id)
    assert initial_count == 3

    # Delete one task
    result = await delete_task_internal(
        ctx=mock_mcp_context,
        task_id=task2.id
    )
    assert result["status"] == "success"

    # Verify count decreased
    final_count = count_tasks(test_session, mock_mcp_context.user_id)
    assert final_count == 2


@pytest.mark.unit
@pytest.mark.asyncio
async def test_delete_task_is_permanent(mock_mcp_context, test_session):
    """
    Test: delete_task is permanent (no soft delete)

    Verifies that deleted tasks cannot be recovered.
    """
    # Setup
    task = create_test_task(test_session, mock_mcp_context.user_id, title="Permanent Delete")
    task_id = task.id

    # Delete task
    result = await delete_task_internal(
        ctx=mock_mcp_context,
        task_id=task_id
    )
    assert result["status"] == "success"

    # Verify task is completely gone (not soft deleted)
    deleted_task = get_task_by_id(test_session, task_id)
    assert deleted_task is None

    # Attempting to delete again should fail
    result2 = await delete_task_internal(
        ctx=mock_mcp_context,
        task_id=task_id
    )
    assert result2["status"] == "error"
