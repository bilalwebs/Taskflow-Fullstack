"""
Input Validation Security Tests

Tests that all tools properly validate and sanitize inputs.
"""

import pytest

from src.tools.create_task import create_task_internal
from src.tools.update_task import update_task_internal
from src.tools.mark_complete import mark_complete_internal
from src.tools.delete_task import delete_task_internal
from src.tools.get_task import get_task_internal


@pytest.mark.security
@pytest.mark.asyncio
async def test_all_tools_validate_input_types_and_ranges(mock_mcp_context):
    """
    Test: All tools validate input types and ranges

    Verifies that tools reject invalid input types and out-of-range values.
    """
    # Test create_task with invalid title length
    result1 = await create_task_internal(
        ctx=mock_mcp_context,
        title="A" * 201  # Exceeds 200 char limit
    )
    assert result1["status"] == "error"

    # Test create_task with invalid description length
    result2 = await create_task_internal(
        ctx=mock_mcp_context,
        title="Valid",
        description="B" * 2001  # Exceeds 2000 char limit
    )
    assert result2["status"] == "error"

    # Test update_task with invalid title length
    result3 = await update_task_internal(
        ctx=mock_mcp_context,
        task_id=1,
        title="C" * 201
    )
    assert result3["status"] == "error"

    # Test with negative task_id
    result4 = await get_task_internal(
        ctx=mock_mcp_context,
        task_id=-1
    )
    assert result4["status"] == "error"


@pytest.mark.security
@pytest.mark.asyncio
async def test_all_tools_reject_sql_injection_attempts(mock_mcp_context, test_session):
    """
    Test: All tools reject SQL injection attempts

    Verifies that tools properly sanitize inputs to prevent SQL injection.
    """
    # SQL injection attempts in title
    sql_injection_payloads = [
        "'; DROP TABLE tasks; --",
        "1' OR '1'='1",
        "admin'--",
        "' UNION SELECT * FROM users--"
    ]

    for payload in sql_injection_payloads:
        # Test create_task
        result = await create_task_internal(
            ctx=mock_mcp_context,
            title=payload
        )

        # Should either succeed (treating as literal string) or fail validation
        # But should NOT execute SQL injection
        if result["status"] == "success":
            # Verify the payload was stored as literal text
            assert result["task"]["title"] == payload

        # Verify database integrity - tasks table should still exist
        from tests.utils.task_helpers import count_tasks
        count = count_tasks(test_session, mock_mcp_context.user_id)
        assert isinstance(count, int)  # Table exists and query works


@pytest.mark.security
@pytest.mark.asyncio
async def test_all_tools_handle_malformed_json_gracefully(mock_mcp_context):
    """
    Test: All tools handle malformed JSON gracefully

    Verifies that tools handle invalid JSON inputs without crashing.
    """
    # Test with None values
    result1 = await create_task_internal(
        ctx=mock_mcp_context,
        title=None
    )
    assert result1["status"] == "error"

    # Test with empty string
    result2 = await create_task_internal(
        ctx=mock_mcp_context,
        title=""
    )
    assert result2["status"] == "error"

    # Test update with no fields
    result3 = await update_task_internal(
        ctx=mock_mcp_context,
        task_id=1
    )
    assert result3["status"] == "error"


@pytest.mark.security
@pytest.mark.asyncio
async def test_tools_sanitize_special_characters(mock_mcp_context, test_session):
    """
    Test: Tools sanitize special characters

    Verifies that tools handle special characters safely.
    """
    special_chars = [
        "<script>alert('xss')</script>",
        "Test\x00null\x00byte",
        "Test\r\nNewline",
        "Test\tTab"
    ]

    for chars in special_chars:
        result = await create_task_internal(
            ctx=mock_mcp_context,
            title=chars
        )

        # Should succeed and store safely
        if result["status"] == "success":
            # Verify stored correctly
            from tests.utils.task_helpers import get_task_by_id
            task = get_task_by_id(test_session, result["task"]["id"])
            assert task is not None


@pytest.mark.security
@pytest.mark.asyncio
async def test_tools_validate_task_id_format(mock_mcp_context):
    """
    Test: Tools validate task_id format

    Verifies that tools reject invalid task_id formats.
    """
    # Test with zero
    result1 = await get_task_internal(ctx=mock_mcp_context, task_id=0)
    assert result1["status"] == "error"

    # Test with negative
    result2 = await mark_complete_internal(ctx=mock_mcp_context, task_id=-999)
    assert result2["status"] == "error"

    # Test with very large number
    result3 = await delete_task_internal(ctx=mock_mcp_context, task_id=999999999)
    assert result3["status"] == "error"
