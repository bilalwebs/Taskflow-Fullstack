"""
Unit Tests for update_task MCP Tool

Tests the update_task tool functionality including:
- Updates title only
- Updates description only
- Updates both title and description
- Error when no fields provided
- Error for non-existent task_id
- Task ownership validation
- Preserves unchanged fields
"""

import pytest

from src.tools.update_task import update_task_internal
from tests.utils.task_helpers import create_test_task, get_task_by_id


@pytest.mark.unit
@pytest.mark.asyncio
async def test_update_task_updates_title_only(mock_mcp_context, test_session):
    """
    Test: update_task updates title only

    Verifies that update_task can update just the title while preserving other fields.
    """
    # Setup
    task = create_test_task(
        test_session,
        mock_mcp_context.user_id,
        title="Old Title",
        description="Original description"
    )

    # Execute
    result = await update_task_internal(
        ctx=mock_mcp_context,
        task_id=task.id,
        title="New Title"
    )

    # Assert
    assert result["status"] == "success"
    assert result["task"]["title"] == "New Title"

    # Verify in database
    updated_task = get_task_by_id(test_session, task.id)
    assert updated_task.title == "New Title"
    assert updated_task.description == "Original description"  # Preserved


@pytest.mark.unit
@pytest.mark.asyncio
async def test_update_task_updates_description_only(mock_mcp_context, test_session):
    """
    Test: update_task updates description only

    Verifies that update_task can update just the description while preserving title.
    """
    # Setup
    task = create_test_task(
        test_session,
        mock_mcp_context.user_id,
        title="Original Title",
        description="Old description"
    )

    # Execute
    result = await update_task_internal(
        ctx=mock_mcp_context,
        task_id=task.id,
        description="New description"
    )

    # Assert
    assert result["status"] == "success"
    assert result["task"]["description"] == "New description"

    # Verify in database
    updated_task = get_task_by_id(test_session, task.id)
    assert updated_task.title == "Original Title"  # Preserved
    assert updated_task.description == "New description"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_update_task_updates_both_title_and_description(mock_mcp_context, test_session):
    """
    Test: update_task updates both title and description

    Verifies that update_task can update both fields simultaneously.
    """
    # Setup
    task = create_test_task(
        test_session,
        mock_mcp_context.user_id,
        title="Old Title",
        description="Old description"
    )

    # Execute
    result = await update_task_internal(
        ctx=mock_mcp_context,
        task_id=task.id,
        title="New Title",
        description="New description"
    )

    # Assert
    assert result["status"] == "success"
    assert result["task"]["title"] == "New Title"
    assert result["task"]["description"] == "New description"

    # Verify in database
    updated_task = get_task_by_id(test_session, task.id)
    assert updated_task.title == "New Title"
    assert updated_task.description == "New description"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_update_task_with_no_fields_returns_error(mock_mcp_context, test_session):
    """
    Test: update_task with no fields returns error

    Verifies that update_task returns error when neither title nor description provided.
    """
    # Setup
    task = create_test_task(test_session, mock_mcp_context.user_id, title="Test")

    # Execute - call with no title or description
    result = await update_task_internal(
        ctx=mock_mcp_context,
        task_id=task.id
    )

    # Assert
    assert result["status"] == "error"
    assert "error" in result
    assert "field" in result["error"].lower() or "provided" in result["error"].lower()


@pytest.mark.unit
@pytest.mark.asyncio
async def test_update_task_with_non_existent_task_id_returns_error(mock_mcp_context):
    """
    Test: update_task with non-existent task_id returns error

    Verifies that update_task returns error for non-existent task.
    """
    # Execute
    result = await update_task_internal(
        ctx=mock_mcp_context,
        task_id=99999,
        title="New Title"
    )

    # Assert
    assert result["status"] == "error"
    assert "error" in result
    assert "not found" in result["error"].lower()


@pytest.mark.unit
@pytest.mark.asyncio
async def test_update_task_validates_task_ownership(mock_mcp_context, mock_mcp_context_user2, test_session):
    """
    Test: update_task validates task ownership

    Verifies that update_task returns error when trying to update another user's task.
    """
    # Setup: Create task for user 2
    task = create_test_task(test_session, mock_mcp_context_user2.user_id, title="User 2 Task")

    # Execute with user 1 context
    result = await update_task_internal(
        ctx=mock_mcp_context,
        task_id=task.id,
        title="Hacked Title"
    )

    # Assert - should fail
    assert result["status"] == "error"
    assert "not found" in result["error"].lower()

    # Verify task unchanged
    unchanged_task = get_task_by_id(test_session, task.id)
    assert unchanged_task.title == "User 2 Task"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_update_task_preserves_unchanged_fields(mock_mcp_context, test_session):
    """
    Test: update_task preserves unchanged fields

    Verifies that update_task doesn't modify fields that weren't specified.
    """
    # Setup
    task = create_test_task(
        test_session,
        mock_mcp_context.user_id,
        title="Original Title",
        description="Original description",
        completed=True
    )
    original_created_at = task.created_at

    # Execute - update only title
    result = await update_task_internal(
        ctx=mock_mcp_context,
        task_id=task.id,
        title="New Title"
    )

    # Assert
    assert result["status"] == "success"

    # Verify unchanged fields preserved
    updated_task = get_task_by_id(test_session, task.id)
    assert updated_task.title == "New Title"  # Changed
    assert updated_task.description == "Original description"  # Preserved
    assert updated_task.completed is True  # Preserved
    assert updated_task.created_at == original_created_at  # Preserved


@pytest.mark.unit
@pytest.mark.asyncio
async def test_update_task_with_empty_string_description(mock_mcp_context, test_session):
    """
    Test: update_task with empty string description

    Verifies that update_task can clear description by setting it to empty string.
    """
    # Setup
    task = create_test_task(
        test_session,
        mock_mcp_context.user_id,
        title="Test",
        description="Original description"
    )

    # Execute - set description to empty string
    result = await update_task_internal(
        ctx=mock_mcp_context,
        task_id=task.id,
        description=""
    )

    # Assert
    assert result["status"] == "success"

    # Verify description cleared
    updated_task = get_task_by_id(test_session, task.id)
    assert updated_task.description == "" or updated_task.description is None


@pytest.mark.unit
@pytest.mark.asyncio
async def test_update_task_validates_title_length(mock_mcp_context, test_session):
    """
    Test: update_task validates title length

    Verifies that update_task enforces title length constraints.
    """
    # Setup
    task = create_test_task(test_session, mock_mcp_context.user_id, title="Test")

    # Execute with title exceeding 200 chars
    long_title = "A" * 201
    result = await update_task_internal(
        ctx=mock_mcp_context,
        task_id=task.id,
        title=long_title
    )

    # Assert
    assert result["status"] == "error"
    assert "200" in result["error"] or "exceeds" in result["error"].lower()


@pytest.mark.unit
@pytest.mark.asyncio
async def test_update_task_validates_description_length(mock_mcp_context, test_session):
    """
    Test: update_task validates description length

    Verifies that update_task enforces description length constraints.
    """
    # Setup
    task = create_test_task(test_session, mock_mcp_context.user_id, title="Test")

    # Execute with description exceeding 2000 chars
    long_description = "B" * 2001
    result = await update_task_internal(
        ctx=mock_mcp_context,
        task_id=task.id,
        description=long_description
    )

    # Assert
    assert result["status"] == "error"
    assert "2000" in result["error"] or "exceeds" in result["error"].lower()
