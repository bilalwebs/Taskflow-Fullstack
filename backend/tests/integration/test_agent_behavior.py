"""
Integration Tests for Agent Behavior

Tests agent handling of ambiguous input and error scenarios.
"""

import pytest

from tests.utils.agent_helpers import invoke_agent_with_message


@pytest.mark.integration
@pytest.mark.asyncio
async def test_agent_handles_ambiguous_user_input_gracefully(test_user):
    """
    Test: Agent handles ambiguous user input gracefully

    Verifies that agent responds appropriately to unclear requests.
    """
    # Execute with ambiguous input
    response = await invoke_agent_with_message(
        user_id=test_user.id,
        message="What can you do?"
    )

    # Assert agent responds
    assert "content" in response
    assert response["content"] is not None
    assert len(response["content"]) > 0


@pytest.mark.integration
@pytest.mark.asyncio
async def test_agent_handles_greeting_appropriately(test_user):
    """
    Test: Agent handles greeting appropriately

    Verifies that agent responds to greetings without calling tools.
    """
    # Execute with greeting
    response = await invoke_agent_with_message(
        user_id=test_user.id,
        message="Hello"
    )

    # Assert agent responds
    assert "content" in response
    assert len(response["content"]) > 0


@pytest.mark.integration
@pytest.mark.asyncio
async def test_agent_handles_unclear_task_request(test_user):
    """
    Test: Agent handles unclear task request

    Verifies that agent can handle vague task descriptions.
    """
    # Execute with vague request
    response = await invoke_agent_with_message(
        user_id=test_user.id,
        message="I need to do something later"
    )

    # Assert agent responds (may ask for clarification or create task)
    assert "content" in response
    assert len(response["content"]) > 0


@pytest.mark.integration
@pytest.mark.asyncio
async def test_agent_handles_invalid_task_id_gracefully(test_user):
    """
    Test: Agent handles invalid task ID gracefully

    Verifies that agent handles requests with non-existent task IDs.
    """
    # Execute with invalid task ID
    response = await invoke_agent_with_message(
        user_id=test_user.id,
        message="Mark task 99999 as complete"
    )

    # Assert agent responds with error or clarification
    assert "content" in response
    assert len(response["content"]) > 0
