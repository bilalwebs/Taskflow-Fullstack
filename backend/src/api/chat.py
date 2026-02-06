"""
Chat API Router

Provides conversational task management through natural language.
Users send messages, and the AI agent responds with task operations via MCP tools.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request, Response
from fastapi.responses import StreamingResponse
from sqlmodel import Session, select
from typing import Dict, AsyncGenerator
from datetime import datetime
import json
import logging

from ..database import get_session
from ..middleware.auth import get_current_user
from ..middleware.rate_limit import rate_limit_middleware
from ..models.conversation import Conversation
from ..models.message import Message, MessageRole
from ..schemas.chat import ChatRequest, ChatResponse
from ..services.agent_service import AgentService


# Configure logger
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["Chat"])


@router.post("/{user_id}/chat", response_model=ChatResponse, status_code=status.HTTP_200_OK)
async def chat(
    user_id: int,
    chat_request: ChatRequest,
    http_request: Request,
    response: Response,
    session: Session = Depends(get_session),
    current_user: Dict = Depends(get_current_user)
):
    """
    Process conversational task management request.

    This endpoint:
    1. Verifies JWT authentication and user_id match
    2. Loads or creates conversation
    3. Saves user message to database
    4. Processes message with AI agent
    5. Saves assistant response to database
    6. Returns response with tool call metadata

    Args:
        user_id: User identifier from URL (must match JWT)
        request: ChatRequest with message and optional conversation_id
        session: Database session dependency
        current_user: Authenticated user from JWT token

    Returns:
        ChatResponse with conversation_id, message_id, assistant_message, and tool_calls

    Raises:
        HTTPException 400: Invalid message format
        HTTPException 401: Missing or invalid JWT token
        HTTPException 403: User_id mismatch or unauthorized conversation access
        HTTPException 404: Conversation not found
        HTTPException 500: Agent processing failure
    """
    # Log incoming chat request
    logger.info(
        f"Chat request received - user_id={user_id}, "
        f"conversation_id={chat_request.conversation_id}, "
        f"message_length={len(chat_request.message)}"
    )

    # Apply rate limiting
    await rate_limit_middleware(http_request, user_id)

    # Verify user_id matches JWT token
    if current_user["user_id"] != user_id:
        logger.warning(
            f"Authorization failed - URL user_id={user_id} does not match "
            f"JWT user_id={current_user['user_id']}"
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission denied",
            headers={"X-Error-Details": "URL user_id does not match authenticated user"}
        )

    # Validate and sanitize message content
    try:
        from ..utils.validation import sanitize_message_content, validate_conversation_id
        sanitized_message = sanitize_message_content(chat_request.message)
        validated_conversation_id = validate_conversation_id(chat_request.conversation_id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

    # Load or create conversation
    conversation = None
    if chat_request.conversation_id:
        # Load existing conversation
        logger.debug(f"Loading existing conversation_id={chat_request.conversation_id}")
        conversation = session.get(Conversation, chat_request.conversation_id)

        # Verify conversation exists
        if not conversation:
            logger.warning(f"Conversation not found - conversation_id={chat_request.conversation_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found",
                headers={"X-Error-Details": f"conversation_id {chat_request.conversation_id} does not exist"}
            )

        # Verify conversation belongs to authenticated user
        if conversation.user_id != user_id:
            logger.warning(
                f"Unauthorized conversation access - conversation_id={chat_request.conversation_id}, "
                f"owner_id={conversation.user_id}, requester_id={user_id}"
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Permission denied",
                headers={"X-Error-Details": "Conversation belongs to different user"}
            )

        # Check if conversation is soft-deleted
        if conversation.deleted_at is not None:
            logger.warning(f"Attempted access to deleted conversation_id={chat_request.conversation_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found",
                headers={"X-Error-Details": "Conversation was deleted"}
            )

        logger.info(f"Loaded existing conversation_id={conversation.id}")
    else:
        # Create new conversation
        logger.info(f"Creating new conversation for user_id={user_id}")
        conversation = Conversation(
            user_id=user_id,
            title=None,  # Can be auto-generated from first message later
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        session.add(conversation)
        session.commit()
        session.refresh(conversation)
        logger.info(f"Created new conversation_id={conversation.id}")

    # Calculate sequence number for the new message
    message_count_stmt = select(Message).where(
        Message.conversation_id == conversation.id,
        Message.deleted_at.is_(None)
    )
    existing_message_count = len(session.exec(message_count_stmt).all())
    next_sequence_number = existing_message_count + 1

    # Save user message to database (before agent processing)
    logger.debug(f"Persisting user message to conversation_id={conversation.id}, sequence={next_sequence_number}")
    user_message = Message(
        conversation_id=conversation.id,
        role=MessageRole.USER,
        content=chat_request.message,
        tool_calls=None,
        sequence_number=next_sequence_number,
        created_at=datetime.utcnow()
    )
    session.add(user_message)
    session.commit()
    session.refresh(user_message)
    logger.debug(f"User message persisted - message_id={user_message.id}")

    # Load conversation history for agent context (last 20 messages for performance)
    statement = (
        select(Message)
        .where(Message.conversation_id == conversation.id)
        .where(Message.deleted_at.is_(None))
        .order_by(Message.created_at.desc())
        .limit(20)
    )
    history_messages = session.exec(statement).all()

    # Reverse to get chronological order (oldest to newest)
    history_messages = list(reversed(history_messages))

    # Initialize agent service with user_id
    agent_service = AgentService(user_id=user_id)

    # Format conversation history for agent
    conversation_history = agent_service.format_conversation_history(history_messages)

    # Process message with agent (with timeout)
    import asyncio
    logger.info(
        f"Processing message with agent - conversation_id={conversation.id}, "
        f"history_length={len(conversation_history)}"
    )

    try:
        agent_response = await asyncio.wait_for(
            agent_service.process_message(
                message=sanitized_message,
                conversation_history=conversation_history[:-1]  # Exclude the just-added user message
            ),
            timeout=30.0  # 30 second timeout
        )

        logger.info(
            f"Agent processing completed - conversation_id={conversation.id}, "
            f"tool_calls={len(agent_response.get('tool_calls', []) or [])}"
        )

    except asyncio.TimeoutError:
        logger.error(
            f"Agent processing timeout - conversation_id={conversation.id}, "
            f"exceeded 30 second limit"
        )
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail="Agent processing timeout - request took longer than 30 seconds"
        )
    except Exception as e:
        # Log error and return 500 with user-friendly message
        logger.error(
            f"Agent processing error - conversation_id={conversation.id}, "
            f"error={str(e)}",
            exc_info=True
        )

        # User-friendly error messages for common OpenAI API failures
        error_message = "Agent processing failed"
        if "rate_limit" in str(e).lower():
            error_message = "AI service is currently busy. Please try again in a moment."
        elif "api_key" in str(e).lower() or "authentication" in str(e).lower():
            error_message = "AI service configuration error. Please contact support."
        elif "timeout" in str(e).lower():
            error_message = "AI service is taking too long to respond. Please try again."
        elif "connection" in str(e).lower():
            error_message = "Unable to connect to AI service. Please try again."

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_message,
            headers={"X-Error-Details": str(e)}
        )

    # Calculate sequence number for assistant response
    assistant_sequence_number = next_sequence_number + 1

    # Save assistant response to database (after agent processing)
    logger.debug(f"Persisting assistant response to conversation_id={conversation.id}, sequence={assistant_sequence_number}")
    assistant_message = Message(
        conversation_id=conversation.id,
        role=MessageRole.ASSISTANT,
        content=agent_response.get("content", ""),
        tool_calls=agent_response.get("tool_calls"),
        sequence_number=assistant_sequence_number,
        created_at=datetime.utcnow()
    )
    session.add(assistant_message)

    # Update conversation timestamp
    conversation.updated_at = datetime.utcnow()
    session.add(conversation)

    session.commit()
    session.refresh(assistant_message)
    logger.debug(f"Assistant response persisted - message_id={assistant_message.id}")

    # Add rate limit headers to response
    if hasattr(http_request, 'state') and hasattr(http_request.state, 'rate_limit_headers'):
        for header_name, header_value in http_request.state.rate_limit_headers.items():
            response.headers[header_name] = header_value

    # Build response
    logger.info(
        f"Chat request completed successfully - conversation_id={conversation.id}, "
        f"message_id={assistant_message.id}, user_id={user_id}"
    )

    return ChatResponse(
        conversation_id=conversation.id,
        message_id=assistant_message.id,
        assistant_message=agent_response.get("content", ""),
        tool_calls=agent_response.get("tool_calls"),
        timestamp=assistant_message.created_at
    )


@router.post("/{user_id}/chat/stream")
async def chat_stream(
    user_id: int,
    request: ChatRequest,
    session: Session = Depends(get_session),
    current_user: Dict = Depends(get_current_user)
):
    """
    Stream chat response with Server-Sent Events (SSE).

    Provides progressive response rendering for better user experience.
    Streams agent response in chunks as it's generated.

    Args:
        user_id: User identifier from URL (must match JWT)
        request: Chat request with message and optional conversation_id
        session: Database session dependency
        current_user: Authenticated user from JWT token

    Returns:
        StreamingResponse with text/event-stream content type

    Raises:
        HTTPException 400: Invalid message format
        HTTPException 401: Missing or invalid JWT token
        HTTPException 403: User_id mismatch or unauthorized conversation access
        HTTPException 404: Conversation not found
        HTTPException 500: Agent processing failure
    """
    # Verify user_id matches JWT token
    if current_user["user_id"] != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission denied"
        )

    async def event_generator() -> AsyncGenerator[str, None]:
        """Generate SSE events for streaming response."""
        try:
            # Load or create conversation (same logic as non-streaming endpoint)
            conversation = None
            if request.conversation_id:
                conversation = session.get(Conversation, request.conversation_id)
                if not conversation or conversation.user_id != user_id:
                    yield f"data: {json.dumps({'error': 'Conversation not found', 'done': True})}\n\n"
                    return
                if conversation.deleted_at is not None:
                    yield f"data: {json.dumps({'error': 'Conversation was deleted', 'done': True})}\n\n"
                    return
            else:
                conversation = Conversation(
                    user_id=user_id,
                    title=None,
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )
                session.add(conversation)
                session.commit()
                session.refresh(conversation)

            # Calculate sequence number
            message_count_stmt = select(Message).where(
                Message.conversation_id == conversation.id,
                Message.deleted_at.is_(None)
            )
            existing_message_count = len(session.exec(message_count_stmt).all())
            user_seq = existing_message_count + 1

            # Save user message
            user_message = Message(
                conversation_id=conversation.id,
                role=MessageRole.USER,
                content=request.message,
                tool_calls=None,
                sequence_number=user_seq,
                created_at=datetime.utcnow()
            )
            session.add(user_message)
            session.commit()

            # Load conversation history
            statement = (
                select(Message)
                .where(Message.conversation_id == conversation.id)
                .where(Message.deleted_at.is_(None))
                .order_by(Message.created_at.desc())
                .limit(20)
            )
            history_messages = session.exec(statement).all()
            history_messages = list(reversed(history_messages))

            # Initialize agent service
            agent_service = CohereAgentService(user_id=user_id)
            conversation_history = agent_service.format_conversation_history(history_messages)

            # Process message with agent
            agent_response = await agent_service.process_message(
                message=request.message,
                conversation_history=conversation_history[:-1]
            )

            # Stream response content in chunks
            content = agent_response.get("content", "")
            chunk_size = 10  # Characters per chunk

            for i in range(0, len(content), chunk_size):
                chunk = content[i:i + chunk_size]
                yield f"data: {json.dumps({'content': chunk, 'done': False})}\n\n"

            # Save assistant response
            assistant_message = Message(
                conversation_id=conversation.id,
                role=MessageRole.ASSISTANT,
                content=content,
                tool_calls=agent_response.get("tool_calls"),
                sequence_number=user_seq + 1,
                created_at=datetime.utcnow()
            )
            session.add(assistant_message)

            # Update conversation timestamp
            conversation.updated_at = datetime.utcnow()
            session.add(conversation)
            session.commit()
            session.refresh(assistant_message)

            # Send final event with metadata
            final_data = {
                "done": True,
                "conversation_id": conversation.id,
                "message_id": assistant_message.id,
                "tool_calls": agent_response.get("tool_calls"),
                "timestamp": assistant_message.created_at.isoformat()
            }
            yield f"data: {json.dumps(final_data)}\n\n"

        except Exception as e:
            # Stream error event
            error_data = {
                "error": str(e),
                "done": True
            }
            yield f"data: {json.dumps(error_data)}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",  # Disable nginx buffering
        }
    )


@router.get("/{user_id}/conversations", status_code=status.HTTP_200_OK)
async def list_conversations(
    user_id: int,
    session: Session = Depends(get_session),
    current_user: Dict = Depends(get_current_user)
):
    """
    List all conversations for authenticated user.

    Returns conversations ordered by most recently updated.
    Excludes soft-deleted conversations.

    Args:
        user_id: User identifier from URL (must match JWT)
        session: Database session dependency
        current_user: Authenticated user from JWT token

    Returns:
        List of conversations with metadata

    Raises:
        HTTPException 403: User_id mismatch
    """
    # Verify user_id matches JWT token
    if current_user["user_id"] != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission denied"
        )

    # Query conversations for user
    statement = (
        select(Conversation)
        .where(Conversation.user_id == user_id)
        .where(Conversation.deleted_at.is_(None))
        .order_by(Conversation.updated_at.desc())
    )
    conversations = session.exec(statement).all()

    return {
        "conversations": [
            {
                "id": conv.id,
                "title": conv.title,
                "created_at": conv.created_at,
                "updated_at": conv.updated_at
            }
            for conv in conversations
        ],
        "total": len(conversations)
    }


@router.get("/{user_id}/conversations/{conversation_id}/messages", status_code=status.HTTP_200_OK)
async def get_conversation_messages(
    user_id: int,
    conversation_id: int,
    session: Session = Depends(get_session),
    current_user: Dict = Depends(get_current_user)
):
    """
    Get all messages in a conversation.

    Returns messages ordered chronologically.
    Excludes soft-deleted messages.

    Args:
        user_id: User identifier from URL (must match JWT)
        conversation_id: Conversation identifier
        session: Database session dependency
        current_user: Authenticated user from JWT token

    Returns:
        List of messages with metadata

    Raises:
        HTTPException 403: User_id mismatch or unauthorized conversation access
        HTTPException 404: Conversation not found
    """
    # Verify user_id matches JWT token
    if current_user["user_id"] != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission denied"
        )

    # Load conversation and verify ownership
    conversation = session.get(Conversation, conversation_id)
    if not conversation or conversation.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )

    # Query messages
    statement = (
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .where(Message.deleted_at.is_(None))
        .order_by(Message.created_at.asc())
    )
    messages = session.exec(statement).all()

    return {
        "conversation_id": conversation_id,
        "messages": [
            {
                "id": msg.id,
                "role": msg.role.value,
                "content": msg.content,
                "tool_calls": msg.tool_calls,
                "created_at": msg.created_at
            }
            for msg in messages
        ],
        "total": len(messages)
    }
