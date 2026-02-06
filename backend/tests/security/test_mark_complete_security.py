"""
Security Tests for mark_complete Tool

Validates security aspects of mark_complete tool:
- Task ownership enforcement
- Cross-user access prevention
"""

import pytest

from src.tools.mark_complete import mark_complete_internal
from tests.utils.task_helpers import create_test_task, get_task_by_id


@pytest.mark.security
@pytest.mark.asyncio
async def test_mark_complete_enforces_task_ownership(mock_mcp_context, mock_mcp_context_user2, test_session):
    """
    Test: mark_complete enforces task ownership

    Verifies that users can only mark their own tasks as complete.
    """
    # Setup: Create tasks for both users
    user1_task = create_test_task(test_session, mock_mcp_context.user_id, title="User 1 Task")
    user2_task = create_test_task(test_session, mock_mcp_context_user2.user_id, title="User 2 Task")

    # User 1 marks their own task complete (should succeed)
    result1 = await mark_complete_internal(
        ctx=mock_mcp_context,
        task_id=user1_task.id
    )
    assert result1["status"] == "success"

    # User 1 tries to mark user 2's task complete (should fail)
    result2 = await mark_complete_internal(
        ctx=mock_mcp_context,
        task_id=user2_task.id
    )
    assert result2["status"] == "error"
    assert "not found" in result2["error"].lower()

    # Verify user 2's task remains unchanged
    unchanged_task = get_task_by_id(test_session, user2_task.id)
    assert unchanged_task.completed is False


@pytest.mark.security
@pytest.mark.asyncio
async def test_mark_complete_with_user1_context_cannot_modify_user2_task(mock_mcp_context, mock_mcp_context_user2, test_session):
    """
    Test: mark_complete with user1 context cannot modify user2 task

    Verifies complete isolation - user 1 cannot modify user 2's tasks.
    """
    # Setup: Create task for user 2
    user2_task = create_test_task(
        test_session,
        mock_mcp_context_user2.user_id,
        title="User 2 Private Task",
        completed=False
    )

    # User 1 attempts to mark user 2's task complete
    result = await mark_complete_internal(
        ctx=mock_mcp_context,
        task_id=user2_task.id
    )

    # Assert - should fail with "not found" error (prevents information disclosure)
    assert result["status"] == "error"
    assert "not found" in result["error"].lower()

    # Verify user 2's task remains unchanged
    unchanged_task = get_task_by_id(test_session, user2_task.id)
    assert unchanged_task.completed is False
    assert unchanged_task.title == "User 2 Private Task"


@pytest.mark.security
@pytest.mark.asyncio
async def test_mark_complete_error_message_prevents_information_disclosure(mock_mcp_context, mock_mcp_context_user2, test_session):
    """
    Test: mark_complete error message prevents information disclosure

    Verifies that error messages don't reveal whether a task exists for another user.
    """
    # Setup: Create task for user 2
    user2_task = create_test_task(test_session, mock_mcp_context_user2.user_id, title="Secret Task")

    # User 1 tries to access user 2's task
    result_unauthorized = await mark_complete_internal(
        ctx=mock_mcp_context,
        task_id=user2_task.id
    )

    # User 1 tries to access non-existent task
    result_not_found = await mark_complete_internal(
        ctx=mock_mcp_context,
        task_id=99999
    )

    # Both should return same error message (prevents information disclosure)
    assert result_unauthorized["status"] == "error"
    assert result_not_found["status"] == "error"

    # Error messages should be similar (both say "not found")
    assert "not found" in result_unauthorized["error"].lower()
    assert "not found" in result_not_found["error"].lower()
