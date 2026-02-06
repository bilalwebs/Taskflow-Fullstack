"""
Contract Tests for create_task Tool

Validates that create_task tool adheres to its defined contract:
- Input schema validation
- Output schema validation
- Error schema validation
"""

import pytest
import json

from src.tools.create_task import create_task_internal, get_tool_definition


@pytest.mark.contract
@pytest.mark.asyncio
async def test_create_task_input_schema_validation(mock_mcp_context):
    """
    Test: create_task input schema validation

    Verifies that create_task accepts inputs matching the defined schema.
    """
    # Get tool definition
    tool_def = get_tool_definition()

    # Verify tool definition structure
    assert tool_def["type"] == "function"
    assert "function" in tool_def
    assert tool_def["function"]["name"] == "create_task"

    # Verify parameters schema
    params = tool_def["function"]["parameters"]
    assert params["type"] == "object"
    assert "properties" in params
    assert "title" in params["properties"]
    assert "description" in params["properties"]
    assert params["required"] == ["title"]

    # Test valid input (title only)
    result = await create_task_internal(
        ctx=mock_mcp_context,
        title="Test task"
    )
    assert result["status"] == "success"

    # Test valid input (title + description)
    result = await create_task_internal(
        ctx=mock_mcp_context,
        title="Test task",
        description="Test description"
    )
    assert result["status"] == "success"


@pytest.mark.contract
@pytest.mark.asyncio
async def test_create_task_output_schema_validation(mock_mcp_context):
    """
    Test: create_task output schema validation

    Verifies that create_task returns outputs matching the defined schema.
    """
    # Execute
    result = await create_task_internal(
        ctx=mock_mcp_context,
        title="Test task",
        description="Test description"
    )

    # Verify output schema
    assert "status" in result
    assert result["status"] == "success"

    assert "task" in result
    task = result["task"]

    # Verify task object schema
    assert "id" in task
    assert isinstance(task["id"], int)

    assert "title" in task
    assert isinstance(task["title"], str)
    assert task["title"] == "Test task"

    assert "description" in task
    assert task["description"] == "Test description"

    assert "completed" in task
    assert isinstance(task["completed"], bool)
    assert task["completed"] is False

    assert "created_at" in task
    assert isinstance(task["created_at"], str)

    assert "updated_at" in task
    assert isinstance(task["updated_at"], str)


@pytest.mark.contract
@pytest.mark.asyncio
async def test_create_task_error_schema_validation(mock_mcp_context):
    """
    Test: create_task error schema validation

    Verifies that create_task returns errors matching the defined schema.
    """
    # Test with empty title (should return error)
    result = await create_task_internal(
        ctx=mock_mcp_context,
        title=""
    )

    # Verify error schema
    assert "status" in result
    assert result["status"] == "error"

    assert "error" in result
    assert isinstance(result["error"], str)
    assert len(result["error"]) > 0

    # Test with title exceeding max length
    result = await create_task_internal(
        ctx=mock_mcp_context,
        title="A" * 201
    )

    # Verify error schema
    assert result["status"] == "error"
    assert "error" in result
    assert isinstance(result["error"], str)


@pytest.mark.contract
def test_create_task_tool_definition_matches_contract():
    """
    Test: create_task tool definition matches contract

    Verifies that the tool definition matches the contract specification.
    """
    # Load contract from file
    import os
    contract_path = os.path.join(
        os.path.dirname(__file__),
        "../../../specs/001-mcp-server-tools/contracts/create_task.json"
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
    assert "title" in tool_params["properties"]
    assert "description" in tool_params["properties"]
    assert tool_params["required"] == contract_input["required"]
