"""
Performance Tests for MCP Tools

Tests performance characteristics of all MCP tools:
- list_tasks completes in <500ms for 1000 tasks
- create_task completes in <100ms
- mark_complete completes in <100ms
- update_task completes in <100ms
- delete_task completes in <100ms
"""

import pytest
import time

from src.tools.list_tasks import list_tasks_internal
from src.tools.create_task import create_task_internal
from src.tools.mark_complete import mark_complete_internal
from src.tools.update_task import update_task_internal
from src.tools.delete_task import delete_task_internal
from tests.utils.task_helpers import create_multiple_tasks, create_test_task


@pytest.mark.performance
@pytest.mark.asyncio
async def test_list_tasks_completes_in_under_500ms_for_1000_tasks(mock_mcp_context, test_session):
    """
    Test: list_tasks completes in <500ms for 1000 tasks

    Verifies that list_tasks meets performance target with large dataset.
    """
    # Setup: Create 1000 tasks
    create_multiple_tasks(test_session, mock_mcp_context.user_id, count=1000, title_prefix="Task")

    # Execute and measure time
    start_time = time.time()
    result = await list_tasks_internal(ctx=mock_mcp_context)
    duration_ms = (time.time() - start_time) * 1000

    # Assert
    assert result["total"] == 1000
    assert duration_ms < 500, f"list_tasks took {duration_ms}ms, expected <500ms"


@pytest.mark.performance
@pytest.mark.asyncio
async def test_create_task_completes_in_under_100ms(mock_mcp_context):
    """
    Test: create_task completes in <100ms

    Verifies that create_task meets performance target.
    """
    # Execute and measure time
    start_time = time.time()
    result = await create_task_internal(
        ctx=mock_mcp_context,
        title="Performance test task"
    )
    duration_ms = (time.time() - start_time) * 1000

    # Assert
    assert result["status"] == "success"
    assert duration_ms < 100, f"create_task took {duration_ms}ms, expected <100ms"


@pytest.mark.performance
@pytest.mark.asyncio
async def test_mark_complete_completes_in_under_100ms(mock_mcp_context, test_session):
    """
    Test: mark_complete completes in <100ms

    Verifies that mark_complete meets performance target.
    """
    # Setup
    task = create_test_task(test_session, mock_mcp_context.user_id, title="Test")

    # Execute and measure time
    start_time = time.time()
    result = await mark_complete_internal(
        ctx=mock_mcp_context,
        task_id=task.id
    )
    duration_ms = (time.time() - start_time) * 1000

    # Assert
    assert result["status"] == "success"
    assert duration_ms < 100, f"mark_complete took {duration_ms}ms, expected <100ms"


@pytest.mark.performance
@pytest.mark.asyncio
async def test_update_task_completes_in_under_100ms(mock_mcp_context, test_session):
    """
    Test: update_task completes in <100ms

    Verifies that update_task meets performance target.
    """
    # Setup
    task = create_test_task(test_session, mock_mcp_context.user_id, title="Test")

    # Execute and measure time
    start_time = time.time()
    result = await update_task_internal(
        ctx=mock_mcp_context,
        task_id=task.id,
        title="Updated"
    )
    duration_ms = (time.time() - start_time) * 1000

    # Assert
    assert result["status"] == "success"
    assert duration_ms < 100, f"update_task took {duration_ms}ms, expected <100ms"


@pytest.mark.performance
@pytest.mark.asyncio
async def test_delete_task_completes_in_under_100ms(mock_mcp_context, test_session):
    """
    Test: delete_task completes in <100ms

    Verifies that delete_task meets performance target.
    """
    # Setup
    task = create_test_task(test_session, mock_mcp_context.user_id, title="Test")

    # Execute and measure time
    start_time = time.time()
    result = await delete_task_internal(
        ctx=mock_mcp_context,
        task_id=task.id
    )
    duration_ms = (time.time() - start_time) * 1000

    # Assert
    assert result["status"] == "success"
    assert duration_ms < 100, f"delete_task took {duration_ms}ms, expected <100ms"
