from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from typing import List, Dict
from datetime import datetime

from ..database import get_session
from ..middleware.auth import get_current_user
from ..models.task import Task
from ..schemas.task import TaskCreate, TaskUpdate, TaskResponse


router = APIRouter(prefix="/api/tasks", tags=["Tasks"])


@router.get("", response_model=List[TaskResponse], status_code=status.HTTP_200_OK)
async def list_tasks(
    session: Session = Depends(get_session),
    current_user: Dict = Depends(get_current_user)
):
    """
    List all tasks for authenticated user.

    Returns all tasks owned by the authenticated user, ordered by creation date (newest first).
    User identity is extracted from JWT token.
    """
    user_id = current_user["user_id"]

    # Query tasks filtered by authenticated user_id
    statement = select(Task).where(Task.user_id == user_id).order_by(Task.created_at.desc())
    tasks = session.exec(statement).all()

    return tasks


@router.post("", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    task_data: TaskCreate,
    session: Session = Depends(get_session),
    current_user: Dict = Depends(get_current_user)
):
    """
    Create a new task for authenticated user.

    User ID is extracted from JWT token, never from client input.
    Task starts with completed=False by default.
    """
    user_id = current_user["user_id"]

    # Validate title is not empty (Pydantic handles this, but double-check)
    if not task_data.title or task_data.title.strip() == "":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Title is required and cannot be empty"
        )

    # Create task with user_id from JWT (never from client)
    task = Task(
        title=task_data.title,
        description=task_data.description,
        completed=False,  # Always start as incomplete
        user_id=user_id,  # Set from JWT token
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )

    session.add(task)
    session.commit()
    session.refresh(task)

    return task


@router.get("/{task_id}", response_model=TaskResponse, status_code=status.HTTP_200_OK)
async def get_task(
    task_id: int,
    session: Session = Depends(get_session),
    current_user: Dict = Depends(get_current_user)
):
    """
    Get a specific task by ID.

    User must own the task. Returns 403 if task belongs to another user.
    Returns 404 if task doesn't exist.
    """
    user_id = current_user["user_id"]

    # Fetch task by ID
    task = session.get(Task, task_id)

    # Return 404 if task not found
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    # Verify ownership - return 403 if user doesn't own this task
    if task.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to access this task"
        )

    return task


@router.put("/{task_id}", response_model=TaskResponse, status_code=status.HTTP_200_OK)
async def update_task(
    task_id: int,
    task_data: TaskUpdate,
    session: Session = Depends(get_session),
    current_user: Dict = Depends(get_current_user)
):
    """
    Update an existing task.

    User must own the task. Only provided fields are updated.
    Updates the updated_at timestamp automatically.
    """
    user_id = current_user["user_id"]

    # Fetch task by ID
    task = session.get(Task, task_id)

    # Return 404 if task not found
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    # Verify ownership - return 403 if user doesn't own this task
    if task.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to update this task"
        )

    # Update only provided fields
    update_data = task_data.model_dump(exclude_unset=True)

    # Validate title if provided
    if "title" in update_data and (not update_data["title"] or update_data["title"].strip() == ""):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Title cannot be empty"
        )

    for field, value in update_data.items():
        setattr(task, field, value)

    # Update timestamp
    task.updated_at = datetime.utcnow()

    session.add(task)
    session.commit()
    session.refresh(task)

    return task


@router.delete("/{task_id}", status_code=status.HTTP_200_OK)
async def delete_task(
    task_id: int,
    session: Session = Depends(get_session),
    current_user: Dict = Depends(get_current_user)
):
    """
    Delete a task permanently.

    User must own the task. Returns success message on deletion.
    """
    user_id = current_user["user_id"]

    # Fetch task by ID
    task = session.get(Task, task_id)

    # Return 404 if task not found
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    # Verify ownership - return 403 if user doesn't own this task
    if task.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to delete this task"
        )

    # Delete task
    session.delete(task)
    session.commit()

    return {"message": "Task deleted successfully"}


@router.patch("/{task_id}/complete", response_model=TaskResponse, status_code=status.HTTP_200_OK)
async def toggle_task_completion(
    task_id: int,
    session: Session = Depends(get_session),
    current_user: Dict = Depends(get_current_user)
):
    """
    Toggle task completion status.

    Flips the completed boolean (True -> False or False -> True).
    User must own the task.
    """
    user_id = current_user["user_id"]

    # Fetch task by ID
    task = session.get(Task, task_id)

    # Return 404 if task not found
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    # Verify ownership - return 403 if user doesn't own this task
    if task.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to modify this task"
        )

    # Toggle completion status
    task.completed = not task.completed

    # Update timestamp
    task.updated_at = datetime.utcnow()

    session.add(task)
    session.commit()
    session.refresh(task)

    return task
