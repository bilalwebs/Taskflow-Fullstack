# Implementation Plan: Chat API & UI

**Branch**: `003-chat-api-ui` | **Date**: 2026-02-04 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/003-chat-api-ui/spec.md`

**Note**: This template is filled in by the `/sp.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Implement a stateless conversational chat interface that enables users to manage their todo tasks through natural language. The system integrates OpenAI Agents SDK with MCP tools to provide AI-native task management, persisting all conversation state in PostgreSQL to maintain stateless backend architecture. Users interact via OpenAI ChatKit frontend, sending messages to a single FastAPI endpoint that orchestrates the flow: UI → API → Agent → MCP Tools → Database.

## Technical Context

**Language/Version**: Python 3.11+ (Backend), TypeScript/Node.js 18+ (Frontend)
**Primary Dependencies**:
- Backend: FastAPI, SQLModel, OpenAI Agents SDK, Official MCP SDK, python-jose (JWT)
- Frontend: Next.js 16+, React 18+, OpenAI ChatKit, TypeScript
**Storage**: Neon Serverless PostgreSQL (conversations, messages, tool_call_logs tables)
**Testing**: pytest (Backend), Jest/React Testing Library (Frontend)
**Target Platform**: Web application (Linux server backend, modern browsers frontend)
**Project Type**: Web (frontend + backend)
**Performance Goals**:
- Chat response time: <5 seconds (P95)
- Conversation history load: <2 seconds
- Concurrent users: 10+ without degradation
**Constraints**:
- Stateless backend (no in-memory session state)
- JWT authentication required on all requests
- User data isolation enforced at database and tool level
- Conversation history limit: 1000 messages per conversation (MVP)
**Scale/Scope**:
- MVP: 10-50 concurrent users
- Single chat endpoint with conversation persistence
- 6 MCP tools for task operations
- ChatKit-based conversational UI

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Phase III Principles Compliance

✅ **Principle VIII: Agent-First Design**
- All task operations initiated by AI agent via MCP tools
- Agent selects tools based on user intent analysis
- Agent confirms actions in natural language
- Agent handles ambiguity and errors gracefully

✅ **Principle IX: Tool-Mediated State Changes**
- AI agent never mutates state directly
- All task operations exposed as MCP tools
- Tools enforce user ownership and authorization
- Tools return structured results for agent reasoning

✅ **Principle X: Stateless Execution**
- No in-memory state between requests
- Chat endpoint reconstructs context from database
- System restart-safe with database persistence
- Conversation state persisted before and after agent execution

### Security Compliance

✅ **JWT Authentication** (Principle II)
- Chat endpoint verifies JWT on every request
- User ID extracted from JWT, never from client input
- URL user_id must match JWT user_id
- MCP tools enforce user_id scoping

✅ **Data Isolation** (Principle II)
- Conversations table has user_id foreign key
- Messages table linked to user-owned conversations
- All queries filter by authenticated user_id
- Cross-user data access explicitly forbidden

### Technology Stack Compliance

✅ **Phase III Mandatory Stack**
- OpenAI Agents SDK for AI reasoning ✓
- Official MCP SDK for tool protocol ✓
- OpenAI ChatKit for conversational UI ✓
- FastAPI with stateless chat endpoint ✓
- SQLModel for conversation persistence ✓

### Architecture Compliance

✅ **Conversational API Design** (Constitution §191-201)
- Single endpoint: POST /api/{user_id}/chat ✓
- Supports conversation_id for resumption ✓
- Request includes message and optional conversation_id ✓
- Response includes assistant_message, conversation_id, tool_calls ✓
- Reconstructs context from database before execution ✓
- Persists messages before and after agent execution ✓

✅ **MCP Tool Requirements** (Constitution §213-241)
- 6 required tools: list_tasks, create_task, update_task, delete_task, get_task, mark_complete ✓
- Tools are stateless with no instance variables ✓
- Tools validate user ownership before mutations ✓
- Tools return structured results suitable for agent reasoning ✓

✅ **Conversation Persistence** (Constitution §271-287)
- conversations table: id, user_id, created_at, updated_at ✓
- messages table: id, conversation_id, role, content, tool_calls, created_at ✓
- Foreign keys enforce user ownership ✓
- User message persisted before agent execution ✓
- Assistant response persisted after agent execution ✓
- No in-memory conversation state ✓

### Gate Result: ✅ PASS

All Phase III principles and requirements satisfied. No constitution violations. Proceed to Phase 0 research.

## Project Structure

### Documentation (this feature)

```text
specs/003-chat-api-ui/
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output (/sp.plan command)
├── data-model.md        # Phase 1 output (/sp.plan command)
├── quickstart.md        # Phase 1 output (/sp.plan command)
├── contracts/           # Phase 1 output (/sp.plan command)
│   ├── chat-api.yaml   # OpenAPI spec for chat endpoint
│   └── mcp-tools.yaml  # MCP tool schemas
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

```text
backend/
├── src/
│   ├── models/
│   │   ├── conversation.py      # Conversation SQLModel
│   │   ├── message.py           # Message SQLModel
│   │   └── tool_call_log.py     # Tool call audit log
│   ├── services/
│   │   ├── chat_service.py      # Chat orchestration logic
│   │   ├── conversation_service.py  # Conversation CRUD
│   │   └── auth_service.py      # JWT verification (existing)
│   ├── agents/
│   │   ├── task_agent.py        # OpenAI Agents SDK configuration
│   │   └── agent_config.py      # Agent system prompts and settings
│   ├── tools/
│   │   ├── mcp_server.py        # MCP server initialization
│   │   ├── list_tasks.py        # MCP tool: list_tasks
│   │   ├── create_task.py       # MCP tool: create_task
│   │   ├── update_task.py       # MCP tool: update_task
│   │   ├── delete_task.py       # MCP tool: delete_task
│   │   ├── get_task.py          # MCP tool: get_task
│   │   └── mark_complete.py     # MCP tool: mark_complete
│   └── api/
│       └── chat.py              # POST /api/{user_id}/chat endpoint
└── tests/
    ├── test_chat_endpoint.py    # Chat API integration tests
    ├── test_mcp_tools.py        # MCP tool unit tests
    └── test_conversation_service.py  # Conversation service tests

frontend/
├── src/
│   ├── app/
│   │   ├── chat/
│   │   │   └── page.tsx         # Chat interface page (ChatKit)
│   │   └── layout.tsx           # Root layout (existing)
│   ├── components/
│   │   ├── ChatInterface.tsx    # ChatKit wrapper component
│   │   ├── MessageList.tsx      # Message display component
│   │   └── ChatInput.tsx        # Message input component
│   └── lib/
│       ├── api-client.ts        # API client (existing, extend for chat)
│       └── chat-api.ts          # Chat-specific API functions
└── tests/
    ├── ChatInterface.test.tsx   # Chat UI component tests
    └── chat-api.test.ts         # Chat API client tests
```

**Structure Decision**: Web application structure (Option 2) selected. Backend contains FastAPI chat endpoint, OpenAI Agents SDK configuration, MCP tool implementations, and conversation persistence services. Frontend contains Next.js ChatKit-based conversational UI. Existing authentication and task management infrastructure reused from previous phases.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

No violations detected. All design decisions align with constitution requirements.

---

## Phase 0: Research & Technical Decisions

**Status**: ✅ Complete

**Research Tasks Completed**:
1. ✅ OpenAI Agents SDK integration patterns for FastAPI
2. ✅ Official MCP SDK usage and tool registration
3. ✅ OpenAI ChatKit integration with Next.js App Router
4. ✅ Conversation history management strategies (pagination, summarization)
5. ✅ Stateless agent execution patterns with database context
6. ✅ JWT token passing from frontend to backend to MCP tools
7. ✅ Error handling patterns for agent and tool failures
8. ✅ Concurrent request handling for same conversation

**Output**: `research.md` - 8 technical decisions documented with rationale and alternatives

---

## Phase 1: Design Artifacts

**Status**: ✅ Complete

**Deliverables Created**:
1. ✅ **data-model.md**: 3 entities (Conversation, Message, ToolCallLog) with relationships, validation rules, and migration strategy
2. ✅ **contracts/chat-api.yaml**: OpenAPI 3.0 spec with 3 endpoints (chat, list conversations, get conversation)
3. ✅ **contracts/mcp-tools.yaml**: Complete schemas for 6 MCP tools with input/output specifications
4. ✅ **quickstart.md**: Comprehensive setup guide with environment configuration, testing procedures, and troubleshooting

**Agent Context Update**: ✅ Completed - CLAUDE.md updated with Phase III technologies

---

## Phase 2: Task Generation

**Status**: Not started (requires `/sp.tasks` command)

**Note**: Task generation happens via separate `/sp.tasks` command after Phase 1 completion.
