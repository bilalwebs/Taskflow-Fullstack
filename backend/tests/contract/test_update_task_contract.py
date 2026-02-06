"""
Contract Tests for update_task Tool

Validates that update_task tool adheres to its defined contract.
"""

import pytest
import json

from src.tools.update_task import update_task_internal, get_tool_definition
from tests.utils.task_helpers import create_test_task


@pytest.mark.contract
@pytest.mark.asyncio
async def test_update_task_input_schema_validation(mock_mcp_context, test_session):
    """
    Test: update_task input schema validation

    Verifies that update_task accepts inputs matching the defined schema.
    """
    # Get tool definition
    tool_def = get_tool_definition()

    # Verify tool definition structure
    assert tool_def["type"] == "function"
    assert "function" in tool_def
    assert tool_def["function"]["name"] == "update_task"

    # Verify parameters schema
    params = tool_def["function"]["parameters"]
    assert params["type"] == "object"
    assert "properties" in params
    assert "task_id" in params["properties"]
    assert "title" in params["properties"]
    assert "description" in params["properties"]
    assert params["required"] == ["task_id"]

    # Test valid input
    task = create_test_task(test_session, mock_mcp_context.user_id, title="Test")
    result = await update_task_internal(
        ctx=mock_mcp_context,
        task_id=task.id,
        title="Updated"
    )
    assert result["status"] == "success"


@pytest.mark.contract
@pytest.mark.asyncio
async def test_update_task_output_schema_validation(mock_mcp_context, test_session):
    """
    Test: update_task output schema validation

    Verifies that update_task returns outputs matching the defined schema.
    """
    # Setup
    task = create_test_task(test_session, mock_mcp_context.user_id, title="Test")

    # Execute
    result = await update_task_internal(
        ctx=mock_mcp_context,
        task_id=task.id,
        title="Updated Title"
    )

    # Verify output schema
    assert "status" in result
    assert result["status"] == "success"

    assert "task" in result
    task_data = result["task"]

    assert "id" in task_data
    assert isinstance(task_data["id"], int)

    assert "title" in task_data
    assert isinstance(task_data["title"], str)

    assert "completed" in task_data
    assert isinstance(task_data["completed"], bool)

    assert "updated_at" in task_data
    assert isinstance(task_data["updated_at"], str)


@pytest.mark.contract
@pytest.mark.asyncio
async def test_update_task_error_schema_validation(mock_mcp_context):
    """
    Test: update_task error schema validation

    Verifies that update_task returns errors matching the defined schema.
    """
    # Execute with non-existent task_id
    result = await update_task_internal(
        ctx=mock_mcp_context,
        task_id=99999,
        title="New Title"
    )

    # Verify error schema
    assert "status" in result
    assert result["status"] == "error"

    assert "error" in result
    assert isinstance(result["error"], str)
    assert len(result["error"]) > 0


@pytest.mark.contract
def test_update_task_tool_definition_matches_contract():
    """
    Test: update_task tool definition matches contract

    Verifies that the tool definition matches the contract specification.
    """
    # Load contract from file
    import os
    contract_path = os.path.join(
        os.path.dirname(__file__),
        "../../../specs/001-mcp-server-tools/contracts/update_task.json"
    )

    with open(contract_path, "r") as f:
        contract = json.load(f)

    # Get tool definition
    tool_def = get_tool_definition()

    # Verify tool name matches
    assert tool_def["function"]["name"] == contract["tool_name"]

    # Verify input schema structure matches
    tool_params = tool_def["function"]["parameters"]
    contract_input = contract["input_schema"]

    assert tool_params["type"] == contract_input["type"]
    assert "task_id" in tool_params["properties"]
    assert "title" in tool_params["properties"]
    assert "description" in tool_params["properties"]
    assert tool_params["required"] == contract_input["required"]
