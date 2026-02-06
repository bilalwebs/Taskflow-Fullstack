# Research: MCP Server & Tools

**Feature**: 001-mcp-server-tools
**Date**: 2026-02-03
**Status**: Complete

## Overview

This document captures the research and architectural decisions made during Phase 0 of the MCP Server & Tools implementation. The goal was to design a stateless, secure, and deterministic tool system for AI agents to manage tasks.

## Research Questions

### Q1: How should MCP tools be deployed and integrated?

**Options Evaluated:**

1. **Standalone MCP Server Process**
   - Separate process running MCP SDK server
   - Tools exposed via network protocol
   - Agent communicates with MCP server over HTTP/WebSocket

2. **Embedded MCP Server (Custom Implementation)**
   - MCP server logic embedded in FastAPI process
   - Tools registered at application startup
   - Direct function calls (no network overhead)

3. **Official MCP SDK Server**
   - Use official MCP SDK to create standalone server
   - Follow MCP protocol specification
   - Agent connects as MCP client

**Decision**: Embedded MCP Server (Custom Implementation)

**Rationale**:
- **Security**: User_id can be pre-bound from JWT without transmitting over network
- **Performance**: No network latency for tool invocations (50-200ms saved per call)
- **Simplicity**: Single deployment unit, no inter-process communication complexity
- **Development**: Easier debugging and testing (single process)
- **Control**: Full control over tool lifecycle and context management

**Trade-offs Accepted**:
- Couples MCP server to FastAPI lifecycle (acceptable for this use case)
- Cannot independently scale MCP server (not needed for current requirements)
- Tools must be thread-safe (achieved via stateless design)

**Implementation Approach**:
- Created `MCPServer` class for tool registration
- Created `MCPContext` class for user-scoped database access
- Tools registered at module import time in `tools/__init__.py`
- AgentService creates user-scoped context per request

---

### Q2: Which AI framework should orchestrate tool invocations?

**Options Evaluated:**

1. **OpenAI Agents SDK with Function Calling**
   - Native OpenAI SDK support for function calling
   - Well-documented and widely adopted
   - Models trained specifically for function calling

2. **LangChain Agents**
   - Higher-level abstraction over LLM interactions
   - Built-in tool management and chains
   - Additional framework dependency

3. **Custom Agent Implementation**
   - Build custom prompt engineering for tool selection
   - Parse model responses to extract tool calls
   - Full control over agent behavior

**Decision**: OpenAI Agents SDK with Function Calling

**Rationale**:
- **Native Integration**: OpenAI SDK has first-class function calling support
- **Proven Pattern**: Function calling is production-ready and well-tested
- **Model Quality**: GPT-4 and GPT-3.5 are trained for function calling
- **Simplicity**: No additional framework dependencies (LangChain avoided)
- **Flexibility**: Can define custom tool schemas with full control

**Implementation Details**:
- Use `client.chat.completions.create()` with `tools` parameter
- Define tool schemas in OpenAI function calling format
- Handle tool calls in response and execute via MCP server
- Send tool results back to model for natural language response

**Example Tool Definition**:
```python
{
    "type": "function",
    "function": {
        "name": "create_task",
        "description": "Create a new task for the user...",
        "parameters": {
            "type": "object",
            "properties": {
                "title": {"type": "string", "description": "..."},
                "description": {"type": "string", "description": "..."}
            },
            "required": ["title"]
        }
    }
}
```

---

### Q3: How should user context be passed to tools securely?

**Options Evaluated:**

1. **User_id as Tool Parameter**
   - Agent passes user_id as parameter to each tool
   - Tools validate user_id matches authenticated user
   - Requires validation in every tool

2. **User Context Pre-Binding**
   - Create user-scoped context at request start
   - Context contains user_id from JWT
   - Tools receive context with user_id pre-bound

3. **Global User Context (Thread-Local)**
   - Store user_id in thread-local storage
   - Tools access user_id from thread context
   - Requires careful thread management

**Decision**: User Context Pre-Binding

**Rationale**:
- **Security**: User_id cannot be tampered with by agent or client
- **Simplicity**: Tools don't need to validate user_id on every call
- **Performance**: Single validation point at context creation
- **Correctness**: Impossible for agent to access wrong user's data
- **Testability**: Easy to test with mock contexts

**Implementation**:
```python
# AgentService creates user-scoped context
self.mcp_context = mcp_server.create_context(user_id=user_id)

# Tools receive context with user_id pre-bound
async def list_tasks_internal(ctx: MCPContext) -> Dict[str, Any]:
    statement = select(Task).where(Task.user_id == ctx.user_id)
```

**Security Flow**:
1. JWT verified by middleware → user_id extracted
2. Chat endpoint validates URL user_id matches JWT user_id
3. AgentService initialized with validated user_id
4. MCPContext created with user_id pre-bound
5. Tools query database with ctx.user_id (no validation needed)

---

### Q4: Should tools be synchronous or asynchronous?

**Options Evaluated:**

1. **Synchronous Tools**
   - Tools use blocking database operations
   - Simpler implementation
   - May block event loop in FastAPI

2. **Asynchronous Tools**
   - Tools use async/await syntax
   - Compatible with FastAPI async endpoints
   - Enables concurrent tool execution

3. **Hybrid Approach**
   - Async tool signatures
   - Synchronous database operations inside
   - Future-proof for async database drivers

**Decision**: Hybrid Approach (Async signatures, sync operations)

**Rationale**:
- **Compatibility**: FastAPI endpoints are async
- **Future-Proofing**: Can migrate to async database operations later
- **Simplicity**: Current scale doesn't require async database operations
- **Concurrency**: Supports concurrent tool invocations if needed

**Implementation**:
```python
async def create_task_internal(ctx: MCPContext, title: str, description: str = "") -> Dict[str, Any]:
    # Synchronous database operations inside async function
    with ctx.get_session() as session:
        task = Task(...)
        session.add(task)
        session.commit()
```

**Future Migration Path**:
- Replace `Session` with `AsyncSession`
- Replace `session.exec()` with `await session.exec()`
- Replace `session.commit()` with `await session.commit()`

---

### Q5: How should conversation history be managed for context?

**Options Evaluated:**

1. **In-Memory Conversation State**
   - Store conversation history in memory (Redis, in-process cache)
   - Fast access for context reconstruction
   - Requires state management and synchronization

2. **Database-Persisted Conversations**
   - Store all messages in database
   - Load conversation history from database per request
   - Stateless server (restart-safe)

3. **Hybrid Approach**
   - Cache recent conversations in memory
   - Fall back to database for older conversations
   - Complexity of cache invalidation

**Decision**: Database-Persisted Conversations

**Rationale**:
- **Stateless Execution**: Aligns with Phase III constitution principle
- **Restart-Safe**: Server can restart without losing conversation state
- **Simplicity**: No cache invalidation or synchronization logic
- **Correctness**: Database is single source of truth
- **Performance**: Acceptable with proper indexing (user_id, conversation_id)

**Implementation**:
- `Conversation` model: id, user_id, title, timestamps
- `Message` model: id, conversation_id, role, content, tool_calls, timestamp
- Load last 20 messages per request for context (performance optimization)
- Persist user message before agent execution
- Persist assistant message after agent execution

**Performance Optimization**:
```python
statement = (
    select(Message)
    .where(Message.conversation_id == conversation.id)
    .order_by(Message.created_at.desc())
    .limit(20)  # Limit to recent messages
)
```

---

## Technology Stack Summary

| Component | Technology | Version | Rationale |
|-----------|-----------|---------|-----------|
| API Framework | FastAPI | 0.109.0+ | Async support, automatic docs, type validation |
| AI Orchestration | OpenAI SDK | 1.12.0+ | Native function calling, proven reliability |
| Tool Protocol | Custom MCP | N/A | Embedded for security and performance |
| ORM | SQLModel | 0.0.14+ | Type-safe, Pydantic integration, simple API |
| Database | PostgreSQL | 14+ | Neon Serverless, ACID compliance, JSON support |
| Validation | Pydantic | 2.0+ | Type validation, schema generation |
| Authentication | JWT | N/A | Stateless, standard, Better Auth compatible |

---

## Performance Targets

Based on research and benchmarking:

| Metric | Target | Rationale |
|--------|--------|-----------|
| Tool Response Time | <500ms p95 | Database operations typically 50-200ms |
| Agent Response Time | 1-3 seconds | OpenAI API latency dominates |
| Concurrent Users | 100+ | Stateless design enables horizontal scaling |
| Tasks per User | 1000+ | Indexed queries on user_id remain fast |
| Conversation History | 20 messages | Balance context quality vs performance |

---

## Security Model

**Authentication Flow**:
1. User logs in via Better Auth → JWT token issued
2. Frontend includes JWT in `Authorization: Bearer <token>` header
3. Backend middleware verifies JWT signature
4. User_id extracted from JWT payload
5. Chat endpoint validates URL user_id matches JWT user_id
6. AgentService creates user-scoped MCPContext
7. Tools query database with pre-bound user_id

**Data Isolation**:
- All database queries filter by `user_id`
- User_id indexed on all user-scoped tables
- Tools cannot access data from other users
- Agent cannot override user_id (pre-bound in context)

**Error Handling**:
- Tool errors return structured responses (no stack traces)
- Database errors sanitized (no schema details exposed)
- OpenAI API errors mapped to user-friendly messages

---

## Alternatives Rejected

### LangChain Framework
**Rejected Because**:
- Additional dependency and learning curve
- Abstractions not needed for our use case
- OpenAI SDK sufficient for function calling
- Prefer minimal dependencies for maintainability

### Standalone MCP Server
**Rejected Because**:
- Network latency for every tool call
- Complexity of passing user_id securely across process boundary
- Additional deployment and monitoring overhead
- No clear benefit for single-tenant tool usage

### In-Memory Conversation State
**Rejected Because**:
- Violates Phase III stateless execution principle
- Requires state synchronization across instances
- Not restart-safe (lose conversations on crash)
- Cache invalidation complexity

### Async Database Operations
**Deferred Because**:
- Current scale doesn't require async database operations
- Synchronous operations simpler to implement and debug
- Can migrate later if performance requires it
- Hybrid approach (async signatures) enables future migration

---

## Open Questions & Future Research

### Q1: Should we implement tool result caching?
**Status**: Deferred
**Rationale**: Premature optimization. Tools are deterministic but time-dependent (timestamps). Caching adds complexity without clear benefit.

### Q2: Should we support streaming tool execution?
**Status**: Deferred
**Rationale**: Current tools execute quickly (<500ms). Streaming adds complexity. Revisit if long-running tools are added.

### Q3: Should we implement tool usage analytics?
**Status**: Deferred
**Rationale**: Useful for monitoring but not critical for MVP. Can add logging/metrics later.

### Q4: Should we support tool chaining (one tool calling another)?
**Status**: Not Needed
**Rationale**: Agent orchestrates tool calls. Tools should remain simple and single-purpose.

---

## References

- [OpenAI Function Calling Documentation](https://platform.openai.com/docs/guides/function-calling)
- [MCP Protocol Specification](https://modelcontextprotocol.io/)
- [FastAPI Async Documentation](https://fastapi.tiangolo.com/async/)
- [SQLModel Documentation](https://sqlmodel.tiangolo.com/)
- [Phase III Constitution Principles](../../.specify/memory/constitution.md)

---

## Conclusion

The research phase successfully identified an architecture that balances security, performance, and simplicity:

- **Embedded MCP server** for security and performance
- **OpenAI function calling** for proven AI orchestration
- **User context pre-binding** for secure data isolation
- **Database-persisted conversations** for stateless execution
- **Hybrid async approach** for future-proofing

All decisions align with Phase III constitution principles (stateless execution, tool-mediated state changes, agent-first design) and provide a solid foundation for implementation.
