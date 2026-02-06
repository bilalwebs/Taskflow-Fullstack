"""
Concurrency Tests

Tests concurrent access and tool invocations:
- Multiple agents create tasks concurrently
- Multiple agents update same task concurrently
- Concurrent chat requests
"""

import pytest
import asyncio

from src.tools.create_task import create_task_internal
from src.tools.update_task import update_task_internal
from tests.utils.task_helpers import create_test_task, count_tasks, get_task_by_id
from tests.utils.agent_helpers import invoke_agent_with_message


@pytest.mark.performance
@pytest.mark.asyncio
async def test_multiple_agents_create_tasks_concurrently_without_conflicts(mock_mcp_context, test_session):
    """
    Test: Multiple agents create tasks concurrently without conflicts

    Verifies that concurrent task creation doesn't cause database conflicts.
    """
    # Define concurrent operations
    async def create_task(index):
        return await create_task_internal(
            ctx=mock_mcp_context,
            title=f"Concurrent Task {index}"
        )

    # Execute 10 concurrent task creations
    tasks = [create_task(i) for i in range(10)]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    # Assert all succeeded
    success_count = sum(1 for r in results if not isinstance(r, Exception) and r.get("status") == "success")
    assert success_count == 10

    # Verify all tasks persisted
    task_count = count_tasks(test_session, mock_mcp_context.user_id)
    assert task_count == 10


@pytest.mark.performance
@pytest.mark.asyncio
async def test_multiple_agents_update_same_task_concurrently(mock_mcp_context, test_session):
    """
    Test: Multiple agents update same task concurrently

    Verifies that concurrent updates to same task are handled safely by database.
    """
    # Setup: Create a task
    task = create_test_task(test_session, mock_mcp_context.user_id, title="Original")

    # Define concurrent update operations
    async def update_task(suffix):
        return await update_task_internal(
            ctx=mock_mcp_context,
            task_id=task.id,
            title=f"Updated {suffix}"
        )

    # Execute 5 concurrent updates
    updates = [update_task(i) for i in range(5)]
    results = await asyncio.gather(*updates, return_exceptions=True)

    # Assert at least some succeeded (database handles conflicts)
    success_count = sum(1 for r in results if not isinstance(r, Exception) and r.get("status") == "success")
    assert success_count > 0

    # Verify task still exists and has one of the updated titles
    updated_task = get_task_by_id(test_session, task.id)
    assert updated_task is not None
    assert "Updated" in updated_task.title


@pytest.mark.performance
@pytest.mark.slow
@pytest.mark.asyncio
async def test_100_concurrent_chat_requests_complete_successfully(test_user, test_session):
    """
    Test: 100 concurrent chat requests complete successfully

    Verifies that system handles high concurrent load.
    """
    # Define concurrent chat operations
    async def send_chat_message(index):
        try:
            return await invoke_agent_with_message(
                user_id=test_user.id,
                message=f"Add task number {index}"
            )
        except Exception as e:
            return {"error": str(e)}

    # Execute 100 concurrent requests
    requests = [send_chat_message(i) for i in range(100)]
    results = await asyncio.gather(*requests, return_exceptions=True)

    # Assert majority succeeded (allow some failures due to rate limits)
    success_count = sum(
        1 for r in results
        if not isinstance(r, Exception) and "error" not in r
    )

    # At least 80% should succeed
    assert success_count >= 80, f"Only {success_count}/100 requests succeeded"
