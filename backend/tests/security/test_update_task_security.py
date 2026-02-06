"""
Security Tests for update_task Tool

Validates security aspects of update_task tool:
- Task ownership enforcement
- Cross-user access prevention
"""

import pytest

from src.tools.update_task import update_task_internal
from tests.utils.task_helpers import create_test_task, get_task_by_id


@pytest.mark.security
@pytest.mark.asyncio
async def test_update_task_enforces_task_ownership(mock_mcp_context, mock_mcp_context_user2, test_session):
    """
    Test: update_task enforces task ownership

    Verifies that users can only update their own tasks.
    """
    # Setup: Create tasks for both users
    user1_task = create_test_task(test_session, mock_mcp_context.user_id, title="User 1 Task")
    user2_task = create_test_task(test_session, mock_mcp_context_user2.user_id, title="User 2 Task")

    # User 1 updates their own task (should succeed)
    result1 = await update_task_internal(
        ctx=mock_mcp_context,
        task_id=user1_task.id,
        title="Updated by User 1"
    )
    assert result1["status"] == "success"

    # User 1 tries to update user 2's task (should fail)
    result2 = await update_task_internal(
        ctx=mock_mcp_context,
        task_id=user2_task.id,
        title="Hacked by User 1"
    )
    assert result2["status"] == "error"
    assert "not found" in result2["error"].lower()

    # Verify user 2's task remains unchanged
    unchanged_task = get_task_by_id(test_session, user2_task.id)
    assert unchanged_task.title == "User 2 Task"


@pytest.mark.security
@pytest.mark.asyncio
async def test_update_task_with_user1_context_cannot_modify_user2_task(mock_mcp_context, mock_mcp_context_user2, test_session):
    """
    Test: update_task with user1 context cannot modify user2 task

    Verifies complete isolation - user 1 cannot modify user 2's tasks.
    """
    # Setup: Create task for user 2
    user2_task = create_test_task(
        test_session,
        mock_mcp_context_user2.user_id,
        title="User 2 Private Task",
        description="Confidential"
    )

    # User 1 attempts to update user 2's task
    result = await update_task_internal(
        ctx=mock_mcp_context,
        task_id=user2_task.id,
        title="Malicious Update",
        description="Hacked"
    )

    # Assert - should fail
    assert result["status"] == "error"
    assert "not found" in result["error"].lower()

    # Verify user 2's task remains unchanged
    unchanged_task = get_task_by_id(test_session, user2_task.id)
    assert unchanged_task.title == "User 2 Private Task"
    assert unchanged_task.description == "Confidential"
