"""
End-to-End Integration Tests

Tests complete workflows across the entire system including:
- Complete task lifecycle (create, list, complete, delete)
- Multi-turn conversation with context retention
- Agent handling ambiguous input
- Agent tool selection based on intent
"""

import pytest

from tests.utils.agent_helpers import invoke_agent_with_message, assert_tool_called
from tests.utils.task_helpers import count_tasks, get_task_by_id


@pytest.mark.integration
@pytest.mark.asyncio
async def test_complete_task_lifecycle(test_user, test_session):
    """
    Test: Complete task lifecycle (create, list, complete, delete)

    Verifies end-to-end workflow of all task operations.
    """
    # Step 1: Create task
    response1 = await invoke_agent_with_message(
        user_id=test_user.id,
        message="Add a task to buy groceries"
    )
    assert_tool_called(response1, "create_task")

    # Step 2: List tasks
    response2 = await invoke_agent_with_message(
        user_id=test_user.id,
        message="Show my tasks"
    )
    assert_tool_called(response2, "list_tasks")

    # Verify task exists
    task_count = count_tasks(test_session, test_user.id)
    assert task_count == 1

    # Step 3: Mark complete (need task ID from list)
    # For simplicity, get task from database
    from sqlmodel import select
    from src.models.task import Task
    statement = select(Task).where(Task.user_id == test_user.id)
    task = test_session.exec(statement).first()

    response3 = await invoke_agent_with_message(
        user_id=test_user.id,
        message=f"Mark task {task.id} as complete"
    )
    assert_tool_called(response3, "mark_complete")

    # Step 4: Delete task
    response4 = await invoke_agent_with_message(
        user_id=test_user.id,
        message=f"Delete task {task.id}"
    )
    assert_tool_called(response4, "delete_task")

    # Verify task deleted
    final_count = count_tasks(test_session, test_user.id)
    assert final_count == 0


@pytest.mark.integration
@pytest.mark.asyncio
async def test_multi_turn_conversation_with_context_retention(test_user, test_session):
    """
    Test: Multi-turn conversation with context retention

    Verifies that agent maintains context across multiple turns.
    """
    # Turn 1: Create task
    response1 = await invoke_agent_with_message(
        user_id=test_user.id,
        message="Add a task to call the dentist"
    )
    assert_tool_called(response1, "create_task")

    # Turn 2: Reference previous context
    response2 = await invoke_agent_with_message(
        user_id=test_user.id,
        message="Also add one to buy milk"
    )
    assert_tool_called(response2, "create_task")

    # Verify both tasks created
    task_count = count_tasks(test_session, test_user.id)
    assert task_count == 2


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

    # Assert agent responds (may not call tools)
    assert response["content"] is not None
    assert len(response["content"]) > 0


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
