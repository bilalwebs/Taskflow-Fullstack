"""
Cross-User Isolation Security Tests

Comprehensive tests to ensure complete data isolation between users.
"""

import pytest

from src.tools.create_task import create_task_internal
from src.tools.list_tasks import list_tasks_internal
from src.tools.get_task import get_task_internal
from src.tools.mark_complete import mark_complete_internal
from src.tools.update_task import update_task_internal
from src.tools.delete_task import delete_task_internal
from tests.utils.task_helpers import create_test_task


@pytest.mark.security
@pytest.mark.asyncio
async def test_user1_cannot_access_user2_tasks_via_any_tool(mock_mcp_context, mock_mcp_context_user2, test_session):
    """
    Test: User1 cannot access User2 tasks via any tool

    Comprehensive test ensuring complete data isolation across all tools.
    """
    # Setup: Create tasks for user 2
    user2_task = create_test_task(test_session, mock_mcp_context_user2.user_id, title="User 2 Task")

    # Test 1: User 1 cannot list user 2's tasks
    list_result = await list_tasks_internal(ctx=mock_mcp_context)
    assert list_result["total"] == 0
    assert len(list_result["tasks"]) == 0

    # Test 2: User 1 cannot get user 2's task by ID
    get_result = await get_task_internal(ctx=mock_mcp_context, task_id=user2_task.id)
    assert get_result["status"] == "error"
    assert "not found" in get_result["error"].lower()

    # Test 3: User 1 cannot mark user 2's task complete
    mark_result = await mark_complete_internal(ctx=mock_mcp_context, task_id=user2_task.id)
    assert mark_result["status"] == "error"
    assert "not found" in mark_result["error"].lower()

    # Test 4: User 1 cannot update user 2's task
    update_result = await update_task_internal(
        ctx=mock_mcp_context,
        task_id=user2_task.id,
        title="Hacked"
    )
    assert update_result["status"] == "error"
    assert "not found" in update_result["error"].lower()

    # Test 5: User 1 cannot delete user 2's task
    delete_result = await delete_task_internal(ctx=mock_mcp_context, task_id=user2_task.id)
    assert delete_result["status"] == "error"
    assert "not found" in delete_result["error"].lower()


@pytest.mark.security
@pytest.mark.asyncio
async def test_user1_cannot_modify_user2_tasks_via_any_tool(mock_mcp_context, mock_mcp_context_user2, test_session):
    """
    Test: User1 cannot modify User2 tasks via any tool

    Verifies that all modification operations respect user boundaries.
    """
    # Setup: Create task for user 2
    user2_task = create_test_task(
        test_session,
        mock_mcp_context_user2.user_id,
        title="Original Title",
        description="Original Description",
        completed=False
    )

    # Attempt 1: Mark complete
    await mark_complete_internal(ctx=mock_mcp_context, task_id=user2_task.id)

    # Attempt 2: Update
    await update_task_internal(
        ctx=mock_mcp_context,
        task_id=user2_task.id,
        title="Modified Title"
    )

    # Attempt 3: Delete
    await delete_task_internal(ctx=mock_mcp_context, task_id=user2_task.id)

    # Verify: User 2's task remains unchanged
    from tests.utils.task_helpers import get_task_by_id
    unchanged_task = get_task_by_id(test_session, user2_task.id)

    assert unchanged_task is not None
    assert unchanged_task.title == "Original Title"
    assert unchanged_task.description == "Original Description"
    assert unchanged_task.completed is False


@pytest.mark.security
@pytest.mark.asyncio
async def test_user1_cannot_delete_user2_tasks_via_any_tool(mock_mcp_context, mock_mcp_context_user2, test_session):
    """
    Test: User1 cannot delete User2 tasks via any tool

    Verifies that delete operations respect user boundaries.
    """
    # Setup: Create multiple tasks for user 2
    from tests.utils.task_helpers import create_multiple_tasks
    user2_tasks = create_multiple_tasks(test_session, mock_mcp_context_user2.user_id, count=5)

    # User 1 attempts to delete all user 2's tasks
    for task in user2_tasks:
        result = await delete_task_internal(ctx=mock_mcp_context, task_id=task.id)
        assert result["status"] == "error"

    # Verify: All user 2's tasks still exist
    from tests.utils.task_helpers import count_tasks
    user2_task_count = count_tasks(test_session, mock_mcp_context_user2.user_id)
    assert user2_task_count == 5


@pytest.mark.security
@pytest.mark.asyncio
async def test_complete_isolation_between_three_users(mock_mcp_context, mock_mcp_context_user2, test_session):
    """
    Test: Complete isolation between three users

    Verifies data isolation works correctly with multiple users.
    """
    # Create third user context
    from src.tools.mcp_server import MCPContext
    user3_context = MCPContext(user_id=3)

    # Create tasks for all three users
    from tests.utils.task_helpers import create_multiple_tasks
    create_multiple_tasks(test_session, mock_mcp_context.user_id, count=3, title_prefix="User1")
    create_multiple_tasks(test_session, mock_mcp_context_user2.user_id, count=4, title_prefix="User2")
    create_multiple_tasks(test_session, user3_context.user_id, count=5, title_prefix="User3")

    # Verify each user sees only their own tasks
    result1 = await list_tasks_internal(ctx=mock_mcp_context)
    assert result1["total"] == 3

    result2 = await list_tasks_internal(ctx=mock_mcp_context_user2)
    assert result2["total"] == 4

    result3 = await list_tasks_internal(ctx=user3_context)
    assert result3["total"] == 5

    # Verify no cross-contamination
    for task in result1["tasks"]:
        assert "User1" in task["title"]

    for task in result2["tasks"]:
        assert "User2" in task["title"]

    for task in result3["tasks"]:
        assert "User3" in task["title"]
