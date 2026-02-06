"""
Error Message Security Tests

Tests that error messages don't expose sensitive internal information.
"""

import pytest

from src.tools.create_task import create_task_internal
from src.tools.get_task import get_task_internal
from src.tools.update_task import update_task_internal
from tests.utils.task_helpers import create_test_task


@pytest.mark.security
@pytest.mark.asyncio
async def test_error_messages_do_not_expose_database_schema(mock_mcp_context):
    """
    Test: Error messages do not expose database schema

    Verifies that error messages don't reveal table names, column names, or schema details.
    """
    # Trigger various errors
    result1 = await create_task_internal(ctx=mock_mcp_context, title="A" * 201)
    result2 = await get_task_internal(ctx=mock_mcp_context, task_id=99999)
    result3 = await update_task_internal(ctx=mock_mcp_context, task_id=99999, title="Test")

    # Check all error messages
    for result in [result1, result2, result3]:
        if result["status"] == "error":
            error_msg = result["error"].lower()

            # Should not contain database-specific terms
            assert "table" not in error_msg
            assert "column" not in error_msg
            assert "schema" not in error_msg
            assert "constraint" not in error_msg
            assert "foreign key" not in error_msg
            assert "primary key" not in error_msg
            assert "index" not in error_msg


@pytest.mark.security
@pytest.mark.asyncio
async def test_error_messages_do_not_expose_internal_paths(mock_mcp_context):
    """
    Test: Error messages do not expose internal paths

    Verifies that error messages don't reveal file system paths or internal structure.
    """
    # Trigger errors
    result1 = await create_task_internal(ctx=mock_mcp_context, title="")
    result2 = await get_task_internal(ctx=mock_mcp_context, task_id=-1)

    # Check error messages
    for result in [result1, result2]:
        if result["status"] == "error":
            error_msg = result["error"]

            # Should not contain file paths
            assert "/" not in error_msg or "not found" in error_msg.lower()
            assert "\\" not in error_msg
            assert "src/" not in error_msg
            assert "backend/" not in error_msg
            assert ".py" not in error_msg


@pytest.mark.security
@pytest.mark.asyncio
async def test_error_messages_do_not_expose_stack_traces(mock_mcp_context):
    """
    Test: Error messages do not expose stack traces

    Verifies that error messages don't include stack traces or exception details.
    """
    # Trigger various errors
    result1 = await create_task_internal(ctx=mock_mcp_context, title=None)
    result2 = await update_task_internal(ctx=mock_mcp_context, task_id=99999, title="Test")

    # Check error messages
    for result in [result1, result2]:
        if result["status"] == "error":
            error_msg = result["error"].lower()

            # Should not contain stack trace elements
            assert "traceback" not in error_msg
            assert "file \"" not in error_msg
            assert "line " not in error_msg
            assert "exception" not in error_msg
            assert "error:" not in error_msg or error_msg.count("error:") == 1


@pytest.mark.security
@pytest.mark.asyncio
async def test_error_messages_are_user_friendly(mock_mcp_context):
    """
    Test: Error messages are user-friendly

    Verifies that error messages provide helpful information without technical details.
    """
    # Test validation errors
    result1 = await create_task_internal(ctx=mock_mcp_context, title="")
    assert result1["status"] == "error"
    assert len(result1["error"]) > 0
    assert "title" in result1["error"].lower() or "required" in result1["error"].lower()

    # Test not found errors
    result2 = await get_task_internal(ctx=mock_mcp_context, task_id=99999)
    assert result2["status"] == "error"
    assert "not found" in result2["error"].lower()


@pytest.mark.security
@pytest.mark.asyncio
async def test_error_messages_consistent_across_tools(mock_mcp_context, mock_mcp_context_user2, test_session):
    """
    Test: Error messages consistent across tools

    Verifies that similar errors produce consistent messages across different tools.
    """
    # Create task for user 2
    user2_task = create_test_task(test_session, mock_mcp_context_user2.user_id, title="User 2 Task")

    # User 1 tries to access user 2's task via different tools
    result1 = await get_task_internal(ctx=mock_mcp_context, task_id=user2_task.id)
    result2 = await update_task_internal(ctx=mock_mcp_context, task_id=user2_task.id, title="Test")

    # Both should return "not found" error (consistent messaging)
    assert result1["status"] == "error"
    assert result2["status"] == "error"
    assert "not found" in result1["error"].lower()
    assert "not found" in result2["error"].lower()
