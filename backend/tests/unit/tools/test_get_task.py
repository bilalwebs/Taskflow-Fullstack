"""
Unit Tests for get_task MCP Tool

Tests the get_task tool functionality including:
- Retrieves task by ID
- Error for non-existent task_id
- Task ownership validation
"""

import pytest

from src.tools.get_task import get_task_internal
from tests.utils.task_helpers import create_test_task


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_task_retrieves_task_by_id(mock_mcp_context, test_session):
    """
    Test: get_task retrieves task by ID

    Verifies that get_task successfully retrieves a task by its ID.
    """
    # Setup
    task = create_test_task(
        test_session,
        mock_mcp_context.user_id,
        title="Test Task",
        description="Test description",
        completed=False
    )

    # Execute
    result = await get_task_internal(
        ctx=mock_mcp_context,
        task_id=task.id
    )

    # Assert
    assert result["status"] == "success"
    assert "task" in result

    task_data = result["task"]
    assert task_data["id"] == task.id
    assert task_data["title"] == "Test Task"
    assert task_data["description"] == "Test description"
    assert task_data["completed"] is False


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_task_with_non_existent_task_id_returns_error(mock_mcp_context):
    """
    Test: get_task with non-existent task_id returns error

    Verifies that get_task returns error for non-existent task.
    """
    # Execute
    result = await get_task_internal(
        ctx=mock_mcp_context,
        task_id=99999
    )

    # Assert
    assert result["status"] == "error"
    assert "error" in result
    assert "not found" in result["error"].lower()


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_task_validates_task_ownership(mock_mcp_context, mock_mcp_context_user2, test_session):
    """
    Test: get_task validates task ownership

    Verifies that get_task returns error when trying to access another user's task.
    """
    # Setup: Create task for user 2
    task = create_test_task(test_session, mock_mcp_context_user2.user_id, title="User 2 Task")

    # Execute with user 1 context
    result = await get_task_internal(
        ctx=mock_mcp_context,
        task_id=task.id
    )

    # Assert - should fail (unauthorized)
    assert result["status"] == "error"
    assert "not found" in result["error"].lower()


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_task_returns_all_task_fields(mock_mcp_context, test_session):
    """
    Test: get_task returns all task fields

    Verifies that get_task returns complete task information.
    """
    # Setup
    task = create_test_task(
        test_session,
        mock_mcp_context.user_id,
        title="Complete Task",
        description="Full description",
        completed=True
    )

    # Execute
    result = await get_task_internal(
        ctx=mock_mcp_context,
        task_id=task.id
    )

    # Assert all fields present
    assert result["status"] == "success"
    task_data = result["task"]

    assert "id" in task_data
    assert "title" in task_data
    assert "description" in task_data
    assert "completed" in task_data
    assert "created_at" in task_data
    assert "updated_at" in task_data
