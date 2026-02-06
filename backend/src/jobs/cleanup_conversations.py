"""
Conversation Cleanup Job

Implements 90-day retention policy for conversations and messages.
Permanently deletes soft-deleted conversations older than 90 days.
"""

from sqlmodel import Session, select
from datetime import datetime, timedelta
from ..database import engine
from ..models.conversation import Conversation
from ..models.message import Message
from ..utils.logging import StructuredLogger

logger = StructuredLogger("cleanup")


def cleanup_old_conversations(dry_run: bool = False) -> dict:
    """
    Delete conversations and messages older than 90 days.

    This function implements the 90-day retention policy by:
    1. Finding conversations soft-deleted more than 90 days ago
    2. Deleting associated messages
    3. Permanently deleting the conversations

    Args:
        dry_run: If True, only count records without deleting

    Returns:
        Dict with cleanup statistics
    """
    cutoff_date = datetime.utcnow() - timedelta(days=90)

    with Session(engine) as session:
        # Find conversations to delete
        statement = select(Conversation).where(
            Conversation.deleted_at.is_not(None),
            Conversation.deleted_at < cutoff_date
        )
        conversations_to_delete = session.exec(statement).all()

        conversation_count = len(conversations_to_delete)
        message_count = 0

        if not dry_run:
            for conversation in conversations_to_delete:
                # Delete associated messages
                message_statement = select(Message).where(
                    Message.conversation_id == conversation.id
                )
                messages = session.exec(message_statement).all()
                message_count += len(messages)

                for message in messages:
                    session.delete(message)

                # Delete conversation
                session.delete(conversation)

            session.commit()

            logger.info(
                "cleanup_completed",
                conversations_deleted=conversation_count,
                messages_deleted=message_count,
                cutoff_date=cutoff_date.isoformat()
            )
        else:
            # Count messages without deleting
            for conversation in conversations_to_delete:
                message_statement = select(Message).where(
                    Message.conversation_id == conversation.id
                )
                messages = session.exec(message_statement).all()
                message_count += len(messages)

            logger.info(
                "cleanup_dry_run",
                conversations_to_delete=conversation_count,
                messages_to_delete=message_count,
                cutoff_date=cutoff_date.isoformat()
            )

    return {
        "conversations_deleted": conversation_count,
        "messages_deleted": message_count,
        "cutoff_date": cutoff_date.isoformat(),
        "dry_run": dry_run
    }


def cleanup_orphaned_messages() -> dict:
    """
    Delete messages that belong to deleted conversations.

    This is a safety cleanup for any orphaned messages.

    Returns:
        Dict with cleanup statistics
    """
    with Session(engine) as session:
        # Find messages with no parent conversation
        statement = select(Message).where(
            ~Message.conversation_id.in_(
                select(Conversation.id)
            )
        )
        orphaned_messages = session.exec(statement).all()

        count = len(orphaned_messages)

        for message in orphaned_messages:
            session.delete(message)

        session.commit()

        logger.info(
            "orphaned_messages_cleanup",
            messages_deleted=count
        )

    return {
        "orphaned_messages_deleted": count
    }


if __name__ == "__main__":
    """
    Run cleanup job from command line.

    Usage:
        python -m backend.src.jobs.cleanup_conversations
        python -m backend.src.jobs.cleanup_conversations --dry-run
    """
    import sys

    dry_run = "--dry-run" in sys.argv

    print("Starting conversation cleanup job...")
    print(f"Dry run: {dry_run}")
    print(f"Cutoff date: {(datetime.utcnow() - timedelta(days=90)).isoformat()}")
    print()

    # Run main cleanup
    result = cleanup_old_conversations(dry_run=dry_run)
    print(f"Conversations deleted: {result['conversations_deleted']}")
    print(f"Messages deleted: {result['messages_deleted']}")
    print()

    # Run orphaned messages cleanup
    if not dry_run:
        orphaned_result = cleanup_orphaned_messages()
        print(f"Orphaned messages deleted: {orphaned_result['orphaned_messages_deleted']}")
        print()

    print("Cleanup job completed!")
