"""
FastAPI dependencies for authentication and authorization.

This module provides reusable dependency functions for route handlers.
"""
from fastapi import Depends, HTTPException, status
from sqlmodel import Session, select
from typing import Dict
from ..middleware.auth import get_current_user
from ..models.user import User
from ..database import get_session


async def verify_jwt(
    current_user: Dict[str, any] = Depends(get_current_user)
) -> Dict[str, any]:
    """
    Verify JWT token and return authenticated user information.

    This dependency can be injected into route handlers to ensure
    the request is authenticated. It extracts user_id and email
    from the verified JWT token.

    Usage:
        @app.get("/api/protected")
        async def protected_route(user: Dict = Depends(verify_jwt)):
            user_id = user["user_id"]
            email = user["email"]
            # ... route logic

    Args:
        current_user: User info from JWT token (injected by get_current_user)

    Returns:
        Dict containing user_id and email from token payload

    Raises:
        HTTPException: 401 if token is invalid or expired
    """
    return current_user


async def get_current_user_from_db(
    current_user: Dict[str, any] = Depends(get_current_user),
    session: Session = Depends(get_session)
) -> User:
    """
    Verify JWT token and fetch full User model from database.

    This dependency verifies the JWT token and then fetches the
    complete User object from the database. Use this when you need
    access to the full user model with relationships.

    Usage:
        @app.get("/api/profile")
        async def get_profile(user: User = Depends(get_current_user_from_db)):
            return {"email": user.email, "created_at": user.created_at}

    Args:
        current_user: User info from JWT token (injected by get_current_user)
        session: Database session

    Returns:
        User model instance from database

    Raises:
        HTTPException: 401 if token is invalid or 404 if user not found
    """
    user_id = current_user["user_id"]

    # Fetch user from database
    statement = select(User).where(User.id == user_id)
    user = session.exec(statement).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return user
