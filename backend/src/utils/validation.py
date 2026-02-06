"""
Input Sanitization and Validation Utilities

Provides utilities for sanitizing and validating user input.
Prevents injection attacks and ensures data integrity.
"""

import re
from typing import Optional
import html


def sanitize_message_content(content: str, max_length: int = 2000) -> str:
    """
    Sanitize user message content.

    Args:
        content: Raw user input
        max_length: Maximum allowed length

    Returns:
        Sanitized content

    Raises:
        ValueError: If content is invalid
    """
    if not content or not isinstance(content, str):
        raise ValueError("Message content must be a non-empty string")

    # Strip whitespace
    content = content.strip()

    if not content:
        raise ValueError("Message content cannot be empty")

    # Check length
    if len(content) > max_length:
        raise ValueError(f"Message content exceeds {max_length} characters")

    # HTML escape to prevent XSS
    content = html.escape(content)

    # Remove null bytes
    content = content.replace('\x00', '')

    # Normalize whitespace (replace multiple spaces with single space)
    content = re.sub(r'\s+', ' ', content)

    return content


def validate_conversation_id(conversation_id: Optional[int]) -> Optional[int]:
    """
    Validate conversation ID.

    Args:
        conversation_id: Conversation ID to validate

    Returns:
        Validated conversation ID or None

    Raises:
        ValueError: If conversation_id is invalid
    """
    if conversation_id is None:
        return None

    if not isinstance(conversation_id, int):
        raise ValueError("Conversation ID must be an integer")

    if conversation_id <= 0:
        raise ValueError("Conversation ID must be positive")

    return conversation_id


def validate_task_title(title: str, max_length: int = 200) -> str:
    """
    Validate and sanitize task title.

    Args:
        title: Task title
        max_length: Maximum allowed length

    Returns:
        Sanitized title

    Raises:
        ValueError: If title is invalid
    """
    if not title or not isinstance(title, str):
        raise ValueError("Title must be a non-empty string")

    # Strip whitespace
    title = title.strip()

    if not title:
        raise ValueError("Title cannot be empty")

    # Check length
    if len(title) > max_length:
        raise ValueError(f"Title exceeds {max_length} characters")

    # HTML escape
    title = html.escape(title)

    # Remove null bytes
    title = title.replace('\x00', '')

    return title


def validate_task_description(description: Optional[str], max_length: int = 2000) -> Optional[str]:
    """
    Validate and sanitize task description.

    Args:
        description: Task description
        max_length: Maximum allowed length

    Returns:
        Sanitized description or None

    Raises:
        ValueError: If description is invalid
    """
    if description is None or description == "":
        return None

    if not isinstance(description, str):
        raise ValueError("Description must be a string")

    # Strip whitespace
    description = description.strip()

    if not description:
        return None

    # Check length
    if len(description) > max_length:
        raise ValueError(f"Description exceeds {max_length} characters")

    # HTML escape
    description = html.escape(description)

    # Remove null bytes
    description = description.replace('\x00', '')

    return description
