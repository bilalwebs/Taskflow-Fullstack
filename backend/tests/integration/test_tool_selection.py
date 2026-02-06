"""
Integration Tests for Tool Selection

Tests agent's ability to select correct tools based on user intent.
"""

import pytest

from tests.utils.agent_helpers import invoke_agent_with_message, assert_tool_called, test_agent_intent_recognition


@pytest.mark.integration
@pytest.mark.asyncio
async def test_agent_selects_correct_tool_based_on_user_intent(test_user, test_session):
    """
    Test: Agent selects correct tool based on user intent

    Verifies that agent correctly interprets user intent and selects appropriate tools.
    """
    # Test create intent
    response1 = await invoke_agent_with_message(
        user_id=test_user.id,
        message="Remind me to call mom"
    )
    assert_tool_called(response1, "create_task")

    # Test list intent
    response2 = await invoke_agent_with_message(
        user_id=test_user.id,
        message="What do I need to do?"
    )
    assert_tool_called(response2, "list_tasks")


@pytest.mark.integration
@pytest.mark.asyncio
async def test_agent_recognizes_create_task_intent_variations(test_user):
    """
    Test: Agent recognizes create_task intent variations

    Verifies that agent recognizes different phrasings for creating tasks.
    """
    # Test various create task phrasings
    create_phrases = [
        "Add a task to buy groceries",
        "Remind me to call the dentist",
        "I need to submit the report",
        "Create a task for reviewing code"
    ]

    for phrase in create_phrases:
        result = await test_agent_intent_recognition(
            user_id=test_user.id,
            message=phrase,
            expected_tool="create_task"
        )
        assert result, f"Agent failed to recognize create intent for: {phrase}"


@pytest.mark.integration
@pytest.mark.asyncio
async def test_agent_recognizes_list_tasks_intent_variations(test_user):
    """
    Test: Agent recognizes list_tasks intent variations

    Verifies that agent recognizes different phrasings for listing tasks.
    """
    # Test various list task phrasings
    list_phrases = [
        "Show my tasks",
        "What do I need to do?",
        "List all my tasks",
        "What's on my todo list?"
    ]

    for phrase in list_phrases:
        result = await test_agent_intent_recognition(
            user_id=test_user.id,
            message=phrase,
            expected_tool="list_tasks"
        )
        assert result, f"Agent failed to recognize list intent for: {phrase}"


@pytest.mark.integration
@pytest.mark.asyncio
async def test_agent_recognizes_mark_complete_intent(test_user, test_session):
    """
    Test: Agent recognizes mark_complete intent

    Verifies that agent recognizes intent to mark tasks complete.
    """
    # Create a task first
    from tests.utils.task_helpers import create_test_task
    task = create_test_task(test_session, test_user.id, title="Test task")

    # Test mark complete intent
    response = await invoke_agent_with_message(
        user_id=test_user.id,
        message=f"Mark task {task.id} as complete"
    )

    assert_tool_called(response, "mark_complete")


@pytest.mark.integration
@pytest.mark.asyncio
async def test_agent_recognizes_update_task_intent(test_user, test_session):
    """
    Test: Agent recognizes update_task intent

    Verifies that agent recognizes intent to update tasks.
    """
    # Create a task first
    from tests.utils.task_helpers import create_test_task
    task = create_test_task(test_session, test_user.id, title="Old title")

    # Test update intent
    response = await invoke_agent_with_message(
        user_id=test_user.id,
        message=f"Change task {task.id} title to 'New title'"
    )

    assert_tool_called(response, "update_task")


@pytest.mark.integration
@pytest.mark.asyncio
async def test_agent_recognizes_delete_task_intent(test_user, test_session):
    """
    Test: Agent recognizes delete_task intent

    Verifies that agent recognizes intent to delete tasks.
    """
    # Create a task first
    from tests.utils.task_helpers import create_test_task
    task = create_test_task(test_session, test_user.id, title="Task to delete")

    # Test delete intent
    response = await invoke_agent_with_message(
        user_id=test_user.id,
        message=f"Delete task {task.id}"
    )

    assert_tool_called(response, "delete_task")
