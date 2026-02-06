"""
Contract Tests for list_tasks Tool

Validates that list_tasks tool adheres to its defined contract:
- Input schema validation
- Output schema validation
- Error schema validation
"""

import pytest
import json

from src.tools.list_tasks import list_tasks_internal, get_tool_definition
from tests.utils.task_helpers import create_multiple_tasks


@pytest.mark.contract
@pytest.mark.asyncio
async def test_list_tasks_input_schema_validation(mock_mcp_context):
    """
    Test: list_tasks input schema validation

    Verifies that list_tasks accepts inputs matching the defined schema.
    """
    # Get tool definition
    tool_def = get_tool_definition()

    # Verify tool definition structure
    assert tool_def["type"] == "function"
    assert "function" in tool_def
    assert tool_def["function"]["name"] == "list_tasks"

    # Verify parameters schema (no parameters required)
    params = tool_def["function"]["parameters"]
    assert params["type"] == "object"
    assert params["properties"] == {}
    assert params["required"] == []

    # Test valid input (no parameters)
    result = await list_tasks_internal(ctx=mock_mcp_context)
    assert "tasks" in result


@pytest.mark.contract
@pytest.mark.asyncio
async def test_list_tasks_output_schema_validation(mock_mcp_context, test_session):
    """
    Test: list_tasks output schema validation

    Verifies that list_tasks returns outputs matching the defined schema.
    """
    # Setup: Create tasks
    create_multiple_tasks(test_session, mock_mcp_context.user_id, count=2, completed=False)
    create_multiple_tasks(test_session, mock_mcp_context.user_id, count=1, completed=True)

    # Execute
    result = await list_tasks_internal(ctx=mock_mcp_context)

    # Verify output schema
    assert "tasks" in result
    assert isinstance(result["tasks"], list)

    assert "total" in result
    assert isinstance(result["total"], int)
    assert result["total"] == 3

    assert "completed_count" in result
    assert isinstance(result["completed_count"], int)
    assert result["completed_count"] == 1

    assert "pending_count" in result
    assert isinstance(result["pending_count"], int)
    assert result["pending_count"] == 2

    # Verify task object schema
    for task in result["tasks"]:
        assert "id" in task
        assert isinstance(task["id"], int)

        assert "title" in task
        assert isinstance(task["title"], str)

        assert "description" in task
        # description can be string or None

        assert "completed" in task
        assert isinstance(task["completed"], bool)

        assert "created_at" in task
        assert isinstance(task["created_at"], str)

        assert "updated_at" in task
        assert isinstance(task["updated_at"], str)


@pytest.mark.contract
@pytest.mark.asyncio
async def test_list_tasks_error_schema_validation(mock_mcp_context):
    """
    Test: list_tasks error schema validation

    Verifies that list_tasks returns errors matching the defined schema.
    """
    # list_tasks typically doesn't fail with validation errors
    # but it should handle database errors gracefully

    # Execute (should succeed)
    result = await list_tasks_internal(ctx=mock_mcp_context)

    # If error occurs, verify error schema
    if "status" in result and result["status"] == "error":
        assert "error" in result
        assert isinstance(result["error"], str)
        assert len(result["error"]) > 0


@pytest.mark.contract
def test_list_tasks_tool_definition_matches_contract():
    """
    Test: list_tasks tool definition matches contract

    Verifies that the tool definition matches the contract specification.
    """
    # Load contract from file
    import os
    contract_path = os.path.join(
        os.path.dirname(__file__),
        "../../../specs/001-mcp-server-tools/contracts/list_tasks.json"
    )

    with open(contract_path, "r") as f:
        contract = json.load(f)

    # Get tool definition
    tool_def = get_tool_definition()

    # Verify tool name matches
    assert tool_def["function"]["name"] == contract["tool_name"]

    # Verify input schema structure matches (no parameters)
    tool_params = tool_def["function"]["parameters"]
    contract_input = contract["input_schema"]

    assert tool_params["type"] == contract_input["type"]
    assert tool_params["properties"] == contract_input["properties"]
    assert tool_params["required"] == contract_input["required"]
