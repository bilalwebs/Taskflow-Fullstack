"""
Security Tests for get_task Tool

Validates security aspects of get_task tool:
- Task ownership enforcement
"""

import pytest

from src.tools.get_task import get_task_internal
from tests.utils.task_helpers import create_test_task


@pytest.mark.security
@pytest.mark.asyncio
async def test_get_task_enforces_task_ownership(mock_mcp_context, mock_mcp_context_user2, test_session):
    """
    Test: get_task enforces task ownership

    Verifies that users can only retrieve their own tasks.
    """
    # Setup: Create tasks for both users
    user1_task = create_test_task(test_session, mock_mcp_context.user_id, title="User 1 Task")
    user2_task = create_test_task(test_session, mock_mcp_context_user2.user_id, title="User 2 Task")

    # User 1 retrieves their own task (should succeed)
    result1 = await get_task_internal(
        ctx=mock_mcp_context,
        task_id=user1_task.id
    )
    assert result1["status"] == "success"
    assert result1["task"]["title"] == "User 1 Task"

    # User 1 tries to retrieve user 2's task (should fail)
    result2 = await get_task_internal(
        ctx=mock_mcp_context,
        task_id=user2_task.id
    )
    assert result2["status"] == "error"
    assert "not found" in result2["error"].lower()
