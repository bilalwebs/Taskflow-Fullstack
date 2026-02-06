# Technical Research: Chat API & UI

**Feature**: 003-chat-api-ui
**Date**: 2026-02-04
**Purpose**: Document technical decisions, integration patterns, and best practices for implementing stateless conversational chat interface

---

## 1. OpenAI Agents SDK Integration with FastAPI

### Decision: Async Agent Execution in FastAPI Endpoint

**Pattern Selected**: Initialize OpenAI Agent SDK client at application startup, execute agent runs within async endpoint handlers.

**Implementation Approach**:
```python
# backend/src/agents/task_agent.py
from openai import AsyncOpenAI
from typing import List, Dict

class TaskAgent:
    def __init__(self, api_key: str):
        self.client = AsyncOpenAI(api_key=api_key)
        self.model = "gpt-4-turbo-preview"

    async def run(self, messages: List[Dict], tools: List[Dict], user_id: str):
        """Execute agent with conversation history and available tools"""
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            tools=tools,
            tool_choice="auto"
        )
        return response

# backend/src/api/chat.py
@router.post("/{user_id}/chat")
async def chat_endpoint(user_id: str, request: ChatRequest, token: str = Depends(verify_jwt)):
    # Load conversation history from database
    # Execute agent with history and tools
    # Persist response
    pass
```

**Rationale**:
- Async execution prevents blocking FastAPI event loop during agent processing
- Agent client initialized once at startup for efficiency
- Conversation history passed as messages array to agent
- Tools registered with agent for dynamic invocation

**Alternatives Considered**:
- **Synchronous execution**: Rejected - would block FastAPI and reduce throughput
- **Background tasks**: Rejected - violates stateless requirement and complicates error handling
- **Separate agent service**: Rejected - adds unnecessary complexity for MVP

**Best Practices**:
- Set reasonable timeout for agent execution (30 seconds)
- Implement retry logic for transient OpenAI API failures
- Log all agent requests/responses for debugging
- Use structured output format for consistent parsing

---

## 2. Official MCP SDK Usage and Tool Registration

### Decision: Python MCP SDK with Decorator-Based Tool Registration

**Pattern Selected**: Use official MCP Python SDK with function decorators to register tools, initialize MCP server at FastAPI startup.

**Implementation Approach**:
```python
# backend/src/tools/mcp_server.py
from mcp import MCPServer, tool
from typing import Dict, Any

mcp_server = MCPServer()

@mcp_server.tool()
async def list_tasks(user_id: str) -> Dict[str, Any]:
    """List all tasks for authenticated user"""
    # Query database filtered by user_id
    # Return structured task list
    pass

@mcp_server.tool()
async def create_task(user_id: str, title: str, description: str = "") -> Dict[str, Any]:
    """Create new task for authenticated user"""
    # Validate input
    # Insert into database with user_id
    # Return created task
    pass

# Register all tools at startup
def get_mcp_tools():
    return mcp_server.get_tools()
```

**Rationale**:
- Decorator pattern provides clean, declarative tool registration
- MCP SDK handles tool schema generation automatically
- Tools are stateless functions that receive user_id from context
- Structured return types enable agent reasoning

**Alternatives Considered**:
- **Manual tool schema definition**: Rejected - error-prone and duplicates code
- **Class-based tools**: Rejected - adds unnecessary state management complexity
- **REST API for tools**: Rejected - MCP protocol more efficient for agent-tool communication

**Best Practices**:
- Each tool function validates user_id before database operations
- Tools return structured dictionaries with success/error status
- Tool descriptions are clear and guide agent selection
- Tools log all invocations for audit trail

**Tool Schema Requirements**:
- Input parameters: typed with validation rules
- Output format: consistent structure (status, data, message)
- Error handling: return actionable error messages, not exceptions
- User scoping: user_id always first parameter

---

## 3. OpenAI ChatKit Integration with Next.js App Router

### Decision: ChatKit as Client Component with Server-Side Data Fetching

**Pattern Selected**: Use ChatKit React components in Next.js Client Component, fetch conversation history via Server Component, handle message sending client-side.

**Implementation Approach**:
```typescript
// frontend/src/app/chat/page.tsx (Server Component)
export default async function ChatPage() {
  const session = await getServerSession();
  const conversationId = await getLatestConversation(session.user.id);

  return <ChatInterface userId={session.user.id} conversationId={conversationId} />;
}

// frontend/src/components/ChatInterface.tsx (Client Component)
'use client';
import { ChatKit } from '@openai/chatkit';

export function ChatInterface({ userId, conversationId }) {
  const [messages, setMessages] = useState([]);

  const handleSendMessage = async (message: string) => {
    const response = await fetch(`/api/${userId}/chat`, {
      method: 'POST',
      headers: { 'Authorization': `Bearer ${token}` },
      body: JSON.stringify({ message, conversation_id: conversationId })
    });
    const data = await response.json();
    setMessages([...messages, { role: 'user', content: message }, { role: 'assistant', content: data.assistant_message }]);
  };

  return <ChatKit messages={messages} onSendMessage={handleSendMessage} />;
}
```

**Rationale**:
- Server Component fetches initial data with authentication
- Client Component handles interactive chat functionality
- ChatKit provides pre-built UI components for messages, input, loading states
- JWT token stored in httpOnly cookie, accessed via API route

**Alternatives Considered**:
- **Fully client-side rendering**: Rejected - loses SSR benefits and complicates auth
- **Custom chat UI**: Rejected - ChatKit provides production-ready components
- **WebSocket streaming**: Rejected - out of scope for MVP, adds complexity

**Best Practices**:
- Use optimistic updates for immediate user feedback
- Show loading spinner during agent execution
- Handle errors gracefully with user-friendly messages
- Persist conversation_id in URL for shareable links

---

## 4. Conversation History Management Strategies

### Decision: Full History Loading with Pagination Fallback

**Pattern Selected**: Load complete conversation history for conversations under 100 messages, implement pagination for larger conversations.

**Implementation Approach**:
```python
# backend/src/services/conversation_service.py
async def get_conversation_history(conversation_id: str, user_id: str, limit: int = 100):
    """Load conversation history with pagination support"""
    messages = await db.query(Message).filter(
        Message.conversation_id == conversation_id,
        Message.conversation.user_id == user_id  # Enforce ownership
    ).order_by(Message.created_at.desc()).limit(limit).all()

    return list(reversed(messages))  # Chronological order

async def format_for_agent(messages: List[Message]) -> List[Dict]:
    """Convert database messages to agent format"""
    return [
        {"role": msg.role, "content": msg.content}
        for msg in messages
    ]
```

**Rationale**:
- Full history provides complete context for agent reasoning
- 100 message limit prevents performance degradation
- Pagination available for edge cases (very long conversations)
- Chronological order maintains conversation flow

**Alternatives Considered**:
- **Sliding window (last N messages)**: Rejected - loses important context
- **Conversation summarization**: Rejected - adds complexity and potential information loss
- **Unlimited history**: Rejected - performance risk for large conversations

**Best Practices**:
- Index conversation_id and created_at for fast queries
- Cache recent conversations in Redis (future optimization)
- Implement conversation archiving for old/inactive conversations
- Monitor conversation length and warn users approaching limits

**Performance Considerations**:
- 100 messages ≈ 50KB payload (acceptable for API response)
- Database query optimized with indexes
- Consider lazy loading older messages in UI

---

## 5. Stateless Agent Execution Patterns with Database Context

### Decision: Reconstruct-Execute-Persist Pattern

**Pattern Selected**: Load conversation from database → Execute agent with full history → Persist new messages → Return response. No in-memory state between requests.

**Implementation Approach**:
```python
# backend/src/services/chat_service.py
async def process_chat_message(user_id: str, message: str, conversation_id: Optional[str]):
    # 1. Get or create conversation
    if conversation_id:
        conversation = await get_conversation(conversation_id, user_id)
    else:
        conversation = await create_conversation(user_id)

    # 2. Load conversation history
    history = await get_conversation_history(conversation.id, user_id)

    # 3. Persist user message
    user_msg = await create_message(conversation.id, "user", message)

    # 4. Execute agent with full context
    agent_messages = format_for_agent(history + [user_msg])
    agent_response = await agent.run(agent_messages, mcp_tools, user_id)

    # 5. Persist assistant response
    assistant_msg = await create_message(
        conversation.id,
        "assistant",
        agent_response.content,
        tool_calls=agent_response.tool_calls
    )

    # 6. Return response
    return {
        "conversation_id": conversation.id,
        "assistant_message": assistant_msg.content,
        "tool_calls": assistant_msg.tool_calls
    }
```

**Rationale**:
- Complete state reconstruction from database ensures consistency
- No server memory dependencies enable horizontal scaling
- Persisting user message before agent execution prevents data loss
- Persisting assistant response after execution ensures atomicity

**Alternatives Considered**:
- **In-memory conversation cache**: Rejected - violates stateless requirement
- **Session-based state**: Rejected - not restart-safe
- **Event sourcing**: Rejected - over-engineered for MVP

**Best Practices**:
- Use database transactions for message persistence
- Implement idempotency keys to handle duplicate requests
- Log all state transitions for debugging
- Handle partial failures gracefully (e.g., agent succeeds but persistence fails)

**Restart Safety**:
- Server restart: All state in database, no data loss
- Database restart: Connection pool handles reconnection
- Agent API failure: User message already persisted, can retry

---

## 6. JWT Token Passing: Frontend → Backend → MCP Tools

### Decision: JWT in Authorization Header, User ID Extracted and Passed to Tools

**Pattern Selected**: Frontend sends JWT in Authorization header → Backend verifies JWT and extracts user_id → Backend passes user_id to MCP tools as first parameter.

**Implementation Approach**:
```python
# backend/src/api/chat.py
from fastapi import Depends, HTTPException
from jose import jwt

async def verify_jwt(authorization: str = Header(...)):
    """Extract and verify JWT token"""
    try:
        token = authorization.replace("Bearer ", "")
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return payload["user_id"]
    except:
        raise HTTPException(status_code=401, detail="Invalid token")

@router.post("/{user_id}/chat")
async def chat_endpoint(
    user_id: str,
    request: ChatRequest,
    authenticated_user_id: str = Depends(verify_jwt)
):
    # Verify URL user_id matches JWT user_id
    if user_id != authenticated_user_id:
        raise HTTPException(status_code=403, detail="Forbidden")

    # Pass authenticated_user_id to tools
    response = await chat_service.process_message(
        authenticated_user_id,
        request.message,
        request.conversation_id
    )
    return response

# backend/src/tools/list_tasks.py
@mcp_server.tool()
async def list_tasks(user_id: str):
    """user_id comes from authenticated context, not agent"""
    tasks = await db.query(Task).filter(Task.user_id == user_id).all()
    return {"status": "success", "tasks": [task.dict() for task in tasks]}
```

**Rationale**:
- JWT verification happens once at API boundary
- User ID extracted from trusted JWT, never from client input
- MCP tools receive authenticated user_id, preventing spoofing
- URL user_id validation prevents unauthorized access

**Alternatives Considered**:
- **Pass JWT to tools**: Rejected - tools shouldn't handle authentication
- **Session-based auth**: Rejected - not stateless
- **API key per user**: Rejected - less secure than JWT

**Security Best Practices**:
- JWT secret stored in environment variable
- Token expiration enforced (e.g., 24 hours)
- HTTPS required in production
- Rate limiting on chat endpoint

**Tool Security**:
- Tools never trust agent-provided user_id
- Tools always use user_id from authenticated context
- Database queries always filter by authenticated user_id
- Cross-user data access impossible

---

## 7. Error Handling Patterns for Agent and Tool Failures

### Decision: Graceful Degradation with User-Friendly Messages

**Pattern Selected**: Catch exceptions at each layer, return user-friendly error messages to agent, agent communicates errors naturally to user.

**Implementation Approach**:
```python
# backend/src/tools/create_task.py
@mcp_server.tool()
async def create_task(user_id: str, title: str, description: str = ""):
    try:
        # Validate input
        if not title or len(title) > 200:
            return {
                "status": "error",
                "message": "Task title must be between 1 and 200 characters"
            }

        # Create task
        task = await db.create(Task(user_id=user_id, title=title, description=description))
        return {
            "status": "success",
            "task": task.dict(),
            "message": f"Created task: {title}"
        }
    except DatabaseError as e:
        return {
            "status": "error",
            "message": "Unable to create task due to database error. Please try again."
        }

# backend/src/services/chat_service.py
async def process_chat_message(user_id: str, message: str, conversation_id: Optional[str]):
    try:
        # ... normal flow ...
    except OpenAIAPIError as e:
        # Agent execution failed
        return {
            "conversation_id": conversation_id,
            "assistant_message": "I'm having trouble processing your request right now. Please try again in a moment.",
            "error": "agent_failure"
        }
    except DatabaseError as e:
        # Database failure
        raise HTTPException(status_code=500, detail="Service temporarily unavailable")
```

**Rationale**:
- Tools return structured error responses instead of raising exceptions
- Agent receives error messages and communicates them naturally
- User sees friendly explanations, not technical stack traces
- System remains operational even when individual tools fail

**Error Categories**:
1. **Validation errors**: Return immediately with clear message
2. **Tool execution errors**: Return error status, agent explains to user
3. **Agent API errors**: Fallback message, log for investigation
4. **Database errors**: HTTP 500, retry logic

**Best Practices**:
- Log all errors with context (user_id, conversation_id, timestamp)
- Distinguish transient errors (retry) from permanent errors (user action needed)
- Never expose internal details (database schema, API keys) in error messages
- Provide actionable guidance ("Please try again" vs "Contact support")

**User Experience**:
- Agent: "I encountered an error creating that task. Could you try again?"
- Agent: "I'm having trouble connecting to the task system right now. Please wait a moment and try again."
- Agent: "I couldn't find a task with that description. Could you be more specific?"

---

## 8. Concurrent Request Handling for Same Conversation

### Decision: Optimistic Locking with Message Ordering

**Pattern Selected**: Use database-level message ordering (auto-increment ID or timestamp), detect concurrent modifications, handle gracefully.

**Implementation Approach**:
```python
# backend/src/models/message.py
class Message(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    conversation_id: int = Field(foreign_key="conversation.id")
    role: str  # "user" or "assistant"
    content: str
    tool_calls: Optional[str] = None  # JSON string
    created_at: datetime = Field(default_factory=datetime.utcnow)
    sequence_number: int  # Auto-increment per conversation

# backend/src/services/conversation_service.py
async def create_message(conversation_id: int, role: str, content: str):
    async with db.transaction():
        # Get next sequence number
        max_seq = await db.query(func.max(Message.sequence_number)).filter(
            Message.conversation_id == conversation_id
        ).scalar()

        message = Message(
            conversation_id=conversation_id,
            role=role,
            content=content,
            sequence_number=(max_seq or 0) + 1
        )
        await db.add(message)
        await db.commit()
        return message
```

**Rationale**:
- Sequence numbers ensure message ordering even with concurrent requests
- Database transaction prevents race conditions
- Each request processes independently with its own snapshot
- Messages always appear in correct chronological order

**Alternatives Considered**:
- **Request queuing**: Rejected - adds latency and complexity
- **Conversation locking**: Rejected - reduces throughput
- **Last-write-wins**: Rejected - could lose messages

**Concurrency Scenarios**:
1. **Two users, different conversations**: No conflict, fully parallel
2. **Same user, same conversation, rapid messages**: Both processed, ordered by sequence_number
3. **Same user, different conversations**: No conflict, fully parallel

**Best Practices**:
- Use database transactions for atomic message creation
- Return conversation history sorted by sequence_number
- Handle duplicate message detection (idempotency keys)
- Monitor for conversation "hot spots" (many concurrent requests)

**Performance Considerations**:
- Database handles concurrency via MVCC (Multi-Version Concurrency Control)
- No application-level locking required
- Acceptable for MVP scale (10-50 concurrent users)
- Consider message queue for higher scale (100+ concurrent users)

---

## Summary of Key Decisions

| Area | Decision | Rationale |
|------|----------|-----------|
| Agent Integration | Async execution in FastAPI endpoint | Non-blocking, efficient |
| MCP Tools | Decorator-based registration | Clean, declarative |
| ChatKit | Client Component with Server data | SSR benefits + interactivity |
| History Management | Full load with pagination fallback | Complete context, performance safe |
| Stateless Pattern | Reconstruct-Execute-Persist | Restart-safe, scalable |
| JWT Flow | Header → Backend → Tools | Secure, prevents spoofing |
| Error Handling | Graceful degradation | User-friendly, operational |
| Concurrency | Optimistic locking + sequencing | Correct ordering, no blocking |

---

## Implementation Priorities

**Phase 1 (MVP)**:
1. Basic agent execution with MCP tools
2. Conversation persistence and retrieval
3. ChatKit UI with message display
4. JWT authentication flow
5. Error handling for common failures

**Phase 2 (Enhancements)**:
1. Conversation pagination for large histories
2. Retry logic for transient failures
3. Performance monitoring and optimization
4. Advanced error recovery

**Phase 3 (Scale)**:
1. Redis caching for recent conversations
2. Message queue for high concurrency
3. Conversation summarization for very long histories
4. Advanced analytics and monitoring

---

## Open Questions for Implementation

1. **Message retention**: How long to keep conversation history? (Assumption: indefinite for MVP)
2. **Conversation limits**: Max conversations per user? (Assumption: unlimited for MVP)
3. **Tool timeout**: How long to wait for tool execution? (Recommendation: 10 seconds)
4. **Agent timeout**: How long to wait for agent response? (Recommendation: 30 seconds)
5. **Rate limiting**: Requests per user per minute? (Recommendation: 10 requests/minute)

These questions should be addressed during implementation based on testing and user feedback.
