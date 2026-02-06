"""
Unit Tests for create_task MCP Tool

Tests the create_task tool functionality including:
- Valid task creation with title only
- Task creation with title and description
- Validation errors for empty title
- Validation errors for title exceeding 200 chars
- Validation errors for description exceeding 2000 chars
- User_id scoping from MCPContext
"""

import pytest
from datetime import datetime

from src.tools.create_task import create_task_internal
from tests.utils.task_helpers import get_task_by_id, count_tasks


@pytest.mark.unit
@pytest.mark.asyncio
async def test_create_task_with_valid_title(mock_mcp_context, test_session):
    """
    Test: create_task with valid title

    Verifies that create_task successfully creates a task with just a title.
    """
    # Execute
    result = await create_task_internal(
        ctx=mock_mcp_context,
        title="Buy groceries"
    )

    # Assert
    assert result["status"] == "success"
    assert "task" in result
    assert result["task"]["title"] == "Buy groceries"
    assert result["task"]["description"] is None
    assert result["task"]["completed"] is False
    assert "id" in result["task"]
    assert "created_at" in result["task"]
    assert "updated_at" in result["task"]

    # Verify task persisted in database
    task_id = result["task"]["id"]
    task = get_task_by_id(test_session, task_id)
    assert task is not None
    assert task.title == "Buy groceries"
    assert task.user_id == mock_mcp_context.user_id


@pytest.mark.unit
@pytest.mark.asyncio
async def test_create_task_with_title_and_description(mock_mcp_context, test_session):
    """
    Test: create_task with title and description

    Verifies that create_task successfully creates a task with both title and description.
    """
    # Execute
    result = await create_task_internal(
        ctx=mock_mcp_context,
        title="Review PR",
        description="Check code quality and test coverage"
    )

    # Assert
    assert result["status"] == "success"
    assert result["task"]["title"] == "Review PR"
    assert result["task"]["description"] == "Check code quality and test coverage"
    assert result["task"]["completed"] is False

    # Verify task persisted in database
    task_id = result["task"]["id"]
    task = get_task_by_id(test_session, task_id)
    assert task is not None
    assert task.title == "Review PR"
    assert task.description == "Check code quality and test coverage"
    assert task.user_id == mock_mcp_context.user_id


@pytest.mark.unit
@pytest.mark.asyncio
async def test_create_task_with_empty_title_returns_error(mock_mcp_context):
    """
    Test: create_task with empty title returns error

    Verifies that create_task returns validation error for empty title.
    """
    # Execute
    result = await create_task_internal(
        ctx=mock_mcp_context,
        title=""
    )

    # Assert
    assert result["status"] == "error"
    assert "error" in result
    assert "Title is required" in result["error"]


@pytest.mark.unit
@pytest.mark.asyncio
async def test_create_task_with_whitespace_only_title_returns_error(mock_mcp_context):
    """
    Test: create_task with whitespace-only title returns error

    Verifies that create_task returns validation error for whitespace-only title.
    """
    # Execute
    result = await create_task_internal(
        ctx=mock_mcp_context,
        title="   "
    )

    # Assert
    assert result["status"] == "error"
    assert "error" in result
    assert "Title is required" in result["error"]


@pytest.mark.unit
@pytest.mark.asyncio
async def test_create_task_with_title_exceeding_200_chars_returns_error(mock_mcp_context):
    """
    Test: create_task with title exceeding 200 chars returns error

    Verifies that create_task returns validation error for title exceeding 200 characters.
    """
    # Create a title with 201 characters
    long_title = "A" * 201

    # Execute
    result = await create_task_internal(
        ctx=mock_mcp_context,
        title=long_title
    )

    # Assert
    assert result["status"] == "error"
    assert "error" in result
    assert "Title exceeds 200 characters" in result["error"]


@pytest.mark.unit
@pytest.mark.asyncio
async def test_create_task_with_description_exceeding_2000_chars_returns_error(mock_mcp_context):
    """
    Test: create_task with description exceeding 2000 chars returns error

    Verifies that create_task returns validation error for description exceeding 2000 characters.
    """
    # Create a description with 2001 characters
    long_description = "B" * 2001

    # Execute
    result = await create_task_internal(
        ctx=mock_mcp_context,
        title="Valid title",
        description=long_description
    )

    # Assert
    assert result["status"] == "error"
    assert "error" in result
    assert "Description exceeds 2000 characters" in result["error"]


@pytest.mark.unit
@pytest.mark.asyncio
async def test_create_task_persists_user_id_from_mcp_context(mock_mcp_context, test_session):
    """
    Test: create_task persists user_id from MCPContext

    Verifies that create_task correctly uses user_id from MCPContext for data scoping.
    """
    # Execute
    result = await create_task_internal(
        ctx=mock_mcp_context,
        title="Test task for user scoping"
    )

    # Assert
    assert result["status"] == "success"

    # Verify task has correct user_id from context
    task_id = result["task"]["id"]
    task = get_task_by_id(test_session, task_id)
    assert task is not None
    assert task.user_id == mock_mcp_context.user_id

    # Verify task count for user
    task_count = count_tasks(test_session, mock_mcp_context.user_id)
    assert task_count == 1


@pytest.mark.unit
@pytest.mark.asyncio
async def test_create_task_with_max_valid_title_length(mock_mcp_context, test_session):
    """
    Test: create_task with maximum valid title length (200 chars)

    Verifies that create_task accepts title with exactly 200 characters.
    """
    # Create a title with exactly 200 characters
    max_title = "A" * 200

    # Execute
    result = await create_task_internal(
        ctx=mock_mcp_context,
        title=max_title
    )

    # Assert
    assert result["status"] == "success"
    assert result["task"]["title"] == max_title

    # Verify task persisted
    task_id = result["task"]["id"]
    task = get_task_by_id(test_session, task_id)
    assert task is not None
    assert len(task.title) == 200


@pytest.mark.unit
@pytest.mark.asyncio
async def test_create_task_with_max_valid_description_length(mock_mcp_context, test_session):
    """
    Test: create_task with maximum valid description length (2000 chars)

    Verifies that create_task accepts description with exactly 2000 characters.
    """
    # Create a description with exactly 2000 characters
    max_description = "B" * 2000

    # Execute
    result = await create_task_internal(
        ctx=mock_mcp_context,
        title="Valid title",
        description=max_description
    )

    # Assert
    assert result["status"] == "success"
    assert result["task"]["description"] == max_description

    # Verify task persisted
    task_id = result["task"]["id"]
    task = get_task_by_id(test_session, task_id)
    assert task is not None
    assert len(task.description) == 2000
