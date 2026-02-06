"""
Security Tests for list_tasks Tool

Validates security aspects of list_tasks tool:
- User_id scoping enforcement (cross-user isolation)
- Prevents access to other users' tasks
"""

import pytest

from src.tools.list_tasks import list_tasks_internal
from tests.utils.task_helpers import create_multiple_tasks


@pytest.mark.security
@pytest.mark.asyncio
async def test_list_tasks_enforces_user_id_scoping(mock_mcp_context, mock_mcp_context_user2, test_session):
    """
    Test: list_tasks enforces user_id scoping (cross-user isolation)

    Verifies that list_tasks only returns tasks for the authenticated user.
    """
    # Setup: Create tasks for both users
    create_multiple_tasks(test_session, mock_mcp_context.user_id, count=3, title_prefix="User1 Task")
    create_multiple_tasks(test_session, mock_mcp_context_user2.user_id, count=2, title_prefix="User2 Task")

    # Execute for user 1
    result1 = await list_tasks_internal(ctx=mock_mcp_context)

    # Assert user 1 sees only their tasks
    assert result1["total"] == 3
    assert len(result1["tasks"]) == 3

    for task in result1["tasks"]:
        assert "User1 Task" in task["title"]
        assert "User2 Task" not in task["title"]

    # Execute for user 2
    result2 = await list_tasks_internal(ctx=mock_mcp_context_user2)

    # Assert user 2 sees only their tasks
    assert result2["total"] == 2
    assert len(result2["tasks"]) == 2

    for task in result2["tasks"]:
        assert "User2 Task" in task["title"]
        assert "User1 Task" not in task["title"]


@pytest.mark.security
@pytest.mark.asyncio
async def test_list_tasks_with_user1_context_cannot_see_user2_tasks(mock_mcp_context, mock_mcp_context_user2, test_session):
    """
    Test: list_tasks with user1 context cannot see user2 tasks

    Verifies complete data isolation between users.
    """
    # Setup: Create tasks for user 2 only
    create_multiple_tasks(test_session, mock_mcp_context_user2.user_id, count=5, title_prefix="User2 Secret Task")

    # Execute with user 1 context
    result = await list_tasks_internal(ctx=mock_mcp_context)

    # Assert user 1 sees no tasks (zero data leakage)
    assert result["total"] == 0
    assert len(result["tasks"]) == 0
    assert result["completed_count"] == 0
    assert result["pending_count"] == 0

    # Verify no user 2 tasks are visible
    for task in result["tasks"]:
        assert "User2 Secret Task" not in task["title"]


@pytest.mark.security
@pytest.mark.asyncio
async def test_list_tasks_returns_only_authenticated_user_tasks(mock_mcp_context, mock_mcp_context_user2, test_session):
    """
    Test: list_tasks returns only authenticated user tasks

    Comprehensive test for data isolation across multiple users.
    """
    # Setup: Create tasks for both users with different counts
    user1_tasks = create_multiple_tasks(test_session, mock_mcp_context.user_id, count=4)
    user2_tasks = create_multiple_tasks(test_session, mock_mcp_context_user2.user_id, count=3)

    # Get task IDs for verification
    user1_task_ids = [t.id for t in user1_tasks]
    user2_task_ids = [t.id for t in user2_tasks]

    # Execute for user 1
    result1 = await list_tasks_internal(ctx=mock_mcp_context)

    # Verify user 1 sees only their task IDs
    result1_task_ids = [t["id"] for t in result1["tasks"]]
    assert set(result1_task_ids) == set(user1_task_ids)
    assert not any(tid in user2_task_ids for tid in result1_task_ids)

    # Execute for user 2
    result2 = await list_tasks_internal(ctx=mock_mcp_context_user2)

    # Verify user 2 sees only their task IDs
    result2_task_ids = [t["id"] for t in result2["tasks"]]
    assert set(result2_task_ids) == set(user2_task_ids)
    assert not any(tid in user1_task_ids for tid in result2_task_ids)


@pytest.mark.security
@pytest.mark.asyncio
async def test_list_tasks_with_large_dataset_maintains_isolation(mock_mcp_context, mock_mcp_context_user2, test_session):
    """
    Test: list_tasks with large dataset maintains isolation

    Verifies that data isolation is maintained even with many tasks.
    """
    # Setup: Create many tasks for both users
    create_multiple_tasks(test_session, mock_mcp_context.user_id, count=50, title_prefix="User1")
    create_multiple_tasks(test_session, mock_mcp_context_user2.user_id, count=50, title_prefix="User2")

    # Execute for user 1
    result1 = await list_tasks_internal(ctx=mock_mcp_context)

    # Assert user 1 sees exactly 50 tasks, all their own
    assert result1["total"] == 50
    assert len(result1["tasks"]) == 50

    for task in result1["tasks"]:
        assert "User1" in task["title"]

    # Execute for user 2
    result2 = await list_tasks_internal(ctx=mock_mcp_context_user2)

    # Assert user 2 sees exactly 50 tasks, all their own
    assert result2["total"] == 50
    assert len(result2["tasks"]) == 50

    for task in result2["tasks"]:
        assert "User2" in task["title"]
