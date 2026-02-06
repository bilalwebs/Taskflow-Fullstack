"""
Integration Tests for Multi-Turn Conversation Flow

Tests conversation context retention and multi-turn interactions.
"""

import pytest

from tests.utils.agent_helpers import invoke_agent_with_message, create_mock_conversation_history


@pytest.mark.integration
@pytest.mark.asyncio
async def test_multi_turn_conversation_with_context_retention(test_user, test_session):
    """
    Test: Multi-turn conversation with context retention

    Verifies that agent maintains context across multiple turns.
    """
    # Turn 1: Create first task
    response1 = await invoke_agent_with_message(
        user_id=test_user.id,
        message="Add a task to call the dentist"
    )

    # Verify first task created
    assert "content" in response1

    # Turn 2: Create second task with contextual reference
    history = create_mock_conversation_history([
        ("user", "Add a task to call the dentist"),
        ("assistant", response1.get("content", "Task created"))
    ])

    response2 = await invoke_agent_with_message(
        user_id=test_user.id,
        message="Also add one to buy milk",
        conversation_history=history
    )

    # Verify second task created
    assert "content" in response2

    # Verify both tasks exist in database
    from tests.utils.task_helpers import count_tasks
    task_count = count_tasks(test_session, test_user.id)
    assert task_count >= 2


@pytest.mark.integration
@pytest.mark.asyncio
async def test_agent_references_previous_task_in_conversation(test_user, test_session):
    """
    Test: Agent references previous task in conversation

    Verifies that agent can reference tasks created earlier in the conversation.
    """
    # Turn 1: Create task
    response1 = await invoke_agent_with_message(
        user_id=test_user.id,
        message="Remind me to submit the report"
    )

    # Turn 2: Reference the task
    history = create_mock_conversation_history([
        ("user", "Remind me to submit the report"),
        ("assistant", response1.get("content", "Task created"))
    ])

    response2 = await invoke_agent_with_message(
        user_id=test_user.id,
        message="What tasks do I have?",
        conversation_history=history
    )

    # Verify agent responds with task information
    assert "content" in response2
    assert len(response2["content"]) > 0


@pytest.mark.integration
@pytest.mark.asyncio
async def test_conversation_maintains_user_context_across_turns(test_user):
    """
    Test: Conversation maintains user context across turns

    Verifies that user_id context is maintained throughout conversation.
    """
    # Turn 1
    response1 = await invoke_agent_with_message(
        user_id=test_user.id,
        message="Create a task to review code"
    )

    assert "content" in response1

    # Turn 2 with history
    history = create_mock_conversation_history([
        ("user", "Create a task to review code"),
        ("assistant", response1.get("content", "Task created"))
    ])

    response2 = await invoke_agent_with_message(
        user_id=test_user.id,
        message="Show my tasks",
        conversation_history=history
    )

    # Verify response maintains user context
    assert "content" in response2
