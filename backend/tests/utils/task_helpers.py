"""
Task Helper Utilities for Testing

This module provides utility functions for creating and managing tasks in tests.
"""

from typing import Optional, List
from datetime import datetime
from sqlmodel import Session

from src.models.task import Task


def create_test_task(
    session: Session,
    user_id: int,
    title: str = "Test Task",
    description: Optional[str] = None,
    completed: bool = False
) -> Task:
    """
    Create a test task in the database.

    Args:
        session: Database session
        user_id: User ID who owns the task
        title: Task title
        description: Optional task description
        completed: Completion status

    Returns:
        Created Task instance
    """
    task = Task(
        user_id=user_id,
        title=title,
        description=description,
        completed=completed,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )

    session.add(task)
    session.commit()
    session.refresh(task)

    return task


def create_multiple_tasks(
    session: Session,
    user_id: int,
    count: int,
    title_prefix: str = "Task",
    completed: bool = False
) -> List[Task]:
    """
    Create multiple test tasks for a user.

    Args:
        session: Database session
        user_id: User ID who owns the tasks
        count: Number of tasks to create
        title_prefix: Prefix for task titles
        completed: Completion status for all tasks

    Returns:
        List of created Task instances
    """
    tasks = []

    for i in range(count):
        task = create_test_task(
            session=session,
            user_id=user_id,
            title=f"{title_prefix} {i+1}",
            description=f"Description for {title_prefix} {i+1}",
            completed=completed
        )
        tasks.append(task)

    return tasks


def get_task_by_id(session: Session, task_id: int) -> Optional[Task]:
    """
    Retrieve a task by ID.

    Args:
        session: Database session
        task_id: Task ID to retrieve

    Returns:
        Task instance or None if not found
    """
    return session.get(Task, task_id)


def delete_all_tasks(session: Session, user_id: Optional[int] = None):
    """
    Delete all tasks, optionally filtered by user.

    Args:
        session: Database session
        user_id: Optional user ID to filter by
    """
    if user_id:
        session.query(Task).filter(Task.user_id == user_id).delete()
    else:
        session.query(Task).delete()

    session.commit()


def count_tasks(session: Session, user_id: int, completed: Optional[bool] = None) -> int:
    """
    Count tasks for a user, optionally filtered by completion status.

    Args:
        session: Database session
        user_id: User ID to count tasks for
        completed: Optional completion status filter

    Returns:
        Number of tasks matching criteria
    """
    query = session.query(Task).filter(Task.user_id == user_id)

    if completed is not None:
        query = query.filter(Task.completed == completed)

    return query.count()


def assert_task_equals(task: Task, expected_title: str, expected_user_id: int, expected_completed: bool = False):
    """
    Assert that a task matches expected values.

    Args:
        task: Task instance to check
        expected_title: Expected task title
        expected_user_id: Expected user ID
        expected_completed: Expected completion status

    Raises:
        AssertionError: If task doesn't match expected values
    """
    assert task.title == expected_title, f"Expected title '{expected_title}', got '{task.title}'"
    assert task.user_id == expected_user_id, f"Expected user_id {expected_user_id}, got {task.user_id}"
    assert task.completed == expected_completed, f"Expected completed {expected_completed}, got {task.completed}"
