"""
ConversationService for managing chat conversations and messages.

This service handles CRUD operations for conversations, message creation
with sequence numbering, and conversation history retrieval.
"""
from sqlmodel import Session, select, func
from typing import List, Optional, Dict, Any
from datetime import datetime
from ..models.conversation import Conversation
from ..models.message import Message, MessageRole


class ConversationService:
    """
    Service for managing conversations and messages.

    This service provides:
    - Conversation CRUD operations
    - Message creation with automatic sequence numbering
    - Conversation history retrieval
    - User-scoped data access
    """

    def __init__(self, session: Session):
        """
        Initialize the ConversationService.

        Args:
            session: SQLModel database session
        """
        self.session = session

    def create_conversation(self, user_id: int) -> Conversation:
        """
        Create a new conversation for a user.

        Args:
            user_id: ID of the user creating the conversation

        Returns:
            Conversation: The newly created conversation

        Raises:
            Exception: If database operation fails
        """
        conversation = Conversation(
            user_id=user_id,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

        self.session.add(conversation)
        self.session.commit()
        self.session.refresh(conversation)

        return conversation

    def get_conversation(
        self,
        conversation_id: int,
        user_id: int
    ) -> Optional[Conversation]:
        """
        Retrieve a specific conversation by ID.

        This method enforces user_id scoping - users can only access
        their own conversations.

        Args:
            conversation_id: ID of the conversation to retrieve
            user_id: ID of the authenticated user

        Returns:
            Conversation if found and belongs to user, None otherwise
        """
        statement = select(Conversation).where(
            Conversation.id == conversation_id,
            Conversation.user_id == user_id
        )
        return self.session.exec(statement).first()

    def list_conversations(
        self,
        user_id: int,
        limit: int = 50,
        offset: int = 0
    ) -> List[Conversation]:
        """
        List all conversations for a user.

        Conversations are returned in reverse chronological order
        (most recent first).

        Args:
            user_id: ID of the authenticated user
            limit: Maximum number of conversations to return (default: 50)
            offset: Number of conversations to skip (default: 0)

        Returns:
            List of conversations belonging to the user
        """
        statement = (
            select(Conversation)
            .where(Conversation.user_id == user_id)
            .order_by(Conversation.updated_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(self.session.exec(statement).all())

    def delete_conversation(
        self,
        conversation_id: int,
        user_id: int
    ) -> bool:
        """
        Delete a conversation and all its messages.

        This method enforces user_id scoping - users can only delete
        their own conversations.

        Args:
            conversation_id: ID of the conversation to delete
            user_id: ID of the authenticated user

        Returns:
            True if conversation was deleted, False if not found
        """
        conversation = self.get_conversation(conversation_id, user_id)
        if not conversation:
            return False

        self.session.delete(conversation)
        self.session.commit()
        return True

    def create_message(
        self,
        conversation_id: int,
        user_id: int,
        role: MessageRole,
        content: str,
        tool_calls: Optional[Dict[str, Any]] = None
    ) -> Optional[Message]:
        """
        Create a new message in a conversation with automatic sequence numbering.

        This method:
        1. Verifies the conversation exists and belongs to the user
        2. Calculates the next sequence number
        3. Creates the message with proper sequencing
        4. Updates the conversation's updated_at timestamp

        Args:
            conversation_id: ID of the conversation
            user_id: ID of the authenticated user
            role: Message role (USER or ASSISTANT)
            content: Message content
            tool_calls: Optional tool call metadata

        Returns:
            Message if created successfully, None if conversation not found

        Raises:
            Exception: If database operation fails
        """
        # Verify conversation exists and belongs to user
        conversation = self.get_conversation(conversation_id, user_id)
        if not conversation:
            return None

        # Get next sequence number
        sequence_number = self._get_next_sequence_number(conversation_id)

        # Create message
        message = Message(
            conversation_id=conversation_id,
            role=role,
            content=content,
            tool_calls=tool_calls,
            sequence_number=sequence_number,
            created_at=datetime.utcnow()
        )

        self.session.add(message)

        # Update conversation timestamp
        conversation.updated_at = datetime.utcnow()
        self.session.add(conversation)

        self.session.commit()
        self.session.refresh(message)

        return message

    def get_conversation_history(
        self,
        conversation_id: int,
        user_id: int,
        include_deleted: bool = False
    ) -> List[Message]:
        """
        Retrieve all messages in a conversation in chronological order.

        This method enforces user_id scoping - users can only access
        messages from their own conversations.

        Args:
            conversation_id: ID of the conversation
            user_id: ID of the authenticated user
            include_deleted: Whether to include soft-deleted messages (default: False)

        Returns:
            List of messages ordered by sequence_number (oldest first)
            Empty list if conversation not found or doesn't belong to user
        """
        # Verify conversation exists and belongs to user
        conversation = self.get_conversation(conversation_id, user_id)
        if not conversation:
            return []

        # Build query
        statement = (
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.sequence_number.asc())
        )

        # Filter out deleted messages unless requested
        if not include_deleted:
            statement = statement.where(Message.deleted_at.is_(None))

        return list(self.session.exec(statement).all())

    def get_message_count(
        self,
        conversation_id: int,
        user_id: int
    ) -> int:
        """
        Get the total number of messages in a conversation.

        Args:
            conversation_id: ID of the conversation
            user_id: ID of the authenticated user

        Returns:
            Number of messages (excluding deleted), 0 if conversation not found
        """
        # Verify conversation exists and belongs to user
        conversation = self.get_conversation(conversation_id, user_id)
        if not conversation:
            return 0

        statement = (
            select(func.count(Message.id))
            .where(
                Message.conversation_id == conversation_id,
                Message.deleted_at.is_(None)
            )
        )
        return self.session.exec(statement).one()

    def _get_next_sequence_number(self, conversation_id: int) -> int:
        """
        Calculate the next sequence number for a message in a conversation.

        This method finds the highest existing sequence number and adds 1.
        If no messages exist, returns 1.

        Args:
            conversation_id: ID of the conversation

        Returns:
            Next sequence number to use
        """
        statement = (
            select(func.max(Message.sequence_number))
            .where(Message.conversation_id == conversation_id)
        )
        max_sequence = self.session.exec(statement).one()

        # If no messages exist, start at 1
        if max_sequence is None:
            return 1

        return max_sequence + 1

    def soft_delete_message(
        self,
        message_id: int,
        conversation_id: int,
        user_id: int
    ) -> bool:
        """
        Soft delete a message (set deleted_at timestamp).

        This method enforces user_id scoping - users can only delete
        messages from their own conversations.

        Args:
            message_id: ID of the message to delete
            conversation_id: ID of the conversation
            user_id: ID of the authenticated user

        Returns:
            True if message was deleted, False if not found
        """
        # Verify conversation belongs to user
        conversation = self.get_conversation(conversation_id, user_id)
        if not conversation:
            return False

        # Find message
        statement = select(Message).where(
            Message.id == message_id,
            Message.conversation_id == conversation_id
        )
        message = self.session.exec(statement).first()

        if not message:
            return False

        # Soft delete
        message.deleted_at = datetime.utcnow()
        self.session.add(message)
        self.session.commit()

        return True
