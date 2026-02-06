# Implementation Plan: AI Agent Behavior for Conversational Task Management

**Branch**: `002-ai-agent-behavior` | **Date**: 2026-02-03 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/002-ai-agent-behavior/spec.md`

**Note**: This template is filled in by the `/sp.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Implement a robust AI agent that interprets natural language commands for task management, maps user intent to MCP tools, and produces user-friendly conversational responses. The agent integrates with a stateless FastAPI chat endpoint and OpenAI ChatKit frontend UI, enabling users to create, view, update, complete, and delete tasks through natural conversation while maintaining strict security boundaries and data isolation.

## Technical Context

**Language/Version**: Python 3.11+ (backend), TypeScript/Next.js 16+ (frontend)
**Primary Dependencies**:
- Backend: OpenAI Agents SDK (exclusive), Official MCP SDK, FastAPI, SQLModel, Pydantic
- Frontend: OpenAI ChatKit, React 18+, Next.js App Router
**Storage**: Neon Serverless PostgreSQL (new tables: conversations, messages)
**Testing**: pytest (backend unit/integration), Jest + React Testing Library (frontend)
**Target Platform**: Web application (Linux/Windows server backend, modern browsers frontend)
**Project Type**: Web (existing backend + frontend with new AI layer)
**Performance Goals**:
- Agent response time <3 seconds for 95% of requests
- Intent classification accuracy >90% without clarification
- Database query time <100ms for conversation history retrieval
**Constraints**:
- Stateless execution (no in-memory session state)
- Restart-safe (all state in database)
- User data isolation (all operations scoped to authenticated user)
- Deterministic tool behavior (same input → same output)
**Scale/Scope**:
- Multi-user conversational interface
- Support for 100+ messages per conversation
- 6 core MCP tools (list, create, update, delete, get, mark_complete)
- Single AI agent configuration with intent classification
- Integration with existing REST API infrastructure

**Clarifications Needed**:
- NEEDS CLARIFICATION: Specific OpenAI model (GPT-4, GPT-4-turbo, or GPT-3.5-turbo)
- NEEDS CLARIFICATION: MCP server hosting approach (embedded in FastAPI vs separate process)
- NEEDS CLARIFICATION: Message streaming implementation (SSE, WebSocket, or polling)
- NEEDS CLARIFICATION: Conversation history retention policy (30 days, 90 days, indefinite)
- NEEDS CLARIFICATION: Rate limiting strategy for chat endpoint
- NEEDS CLARIFICATION: Tool call logging and audit trail requirements

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Applicable Principles

✅ **Principle I: Spec-Driven Development** - This plan follows approved spec.md; all behavior is documented and traceable.

✅ **Principle II: Security First** - MCP tools will enforce user_id scoping from JWT context; agent cannot bypass authentication; all operations validate ownership.

✅ **Principle III: Deterministic Output** - MCP tools designed to be deterministic (same input → same output); agent behavior rule-driven, not random.

✅ **Principle IV: Full-Stack Consistency** - Agent layer, FastAPI backend, and ChatKit frontend will align on conversation contract; no layer-specific business logic.

✅ **Principle V: Zero Manual Coding** - Implementation via specialized agents (backend-skill for API, database-skill for schema, frontend-skill for ChatKit).

✅ **Principle VIII: Agent-First Design** - All task operations initiated via MCP tools; agent selects tools based on intent; natural language confirmations.

✅ **Principle IX: Tool-Mediated State Changes** - Agent never mutates database directly; all operations through MCP tools; tools enforce authorization.

✅ **Principle X: Stateless Execution** - Chat endpoint reconstructs context from database; no in-memory session state; restart-safe design.

✅ **MCP Tooling Standards** - Tools will have clear purpose, strict validation, deterministic outputs, user scoping, structured results, error handling.

✅ **AI Agent Standards** - Using OpenAI Agents SDK exclusively; agent has tool access; intent-based selection; natural language responses; no hallucination.

✅ **Conversation Persistence Standards** - Database schema for conversations and messages; persistence before/after agent execution; history loaded per request.

### Gate Evaluation

**Status**: ✅ PASS

**Justification**: No constitution violations detected. Feature design fully aligns with Phase III architecture constraints. All security, statelessness, and tool-mediation requirements are met by design.

**Re-evaluation Required**: After Phase 1 design artifacts are complete, verify that data models, API contracts, and MCP tool specifications maintain compliance.

## Project Structure

### Documentation (this feature)

```text
specs/[###-feature]/
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output (/sp.plan command)
├── data-model.md        # Phase 1 output (/sp.plan command)
├── quickstart.md        # Phase 1 output (/sp.plan command)
├── contracts/           # Phase 1 output (/sp.plan command)
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

```text
backend/
├── src/
│   ├── models/
│   │   ├── conversation.py      # NEW: Conversation entity
│   │   ├── message.py           # NEW: Message entity
│   │   ├── task.py              # EXISTING: Task entity
│   │   └── user.py              # EXISTING: User entity
│   ├── services/
│   │   └── agent_service.py     # NEW: Agent orchestration logic
│   ├── api/
│   │   ├── chat.py              # NEW: Chat endpoint
│   │   ├── tasks.py             # EXISTING: Task REST endpoints
│   │   └── auth.py              # EXISTING: Auth endpoints
│   ├── agents/
│   │   └── task_agent.py        # NEW: OpenAI agent configuration
│   ├── tools/
│   │   ├── mcp_server.py        # NEW: MCP server setup
│   │   ├── list_tasks.py        # NEW: MCP tool
│   │   ├── create_task.py       # NEW: MCP tool
│   │   ├── update_task.py       # NEW: MCP tool
│   │   ├── delete_task.py       # NEW: MCP tool
│   │   ├── get_task.py          # NEW: MCP tool
│   │   └── mark_complete.py     # NEW: MCP tool
│   ├── middleware/
│   │   └── auth.py              # EXISTING: JWT verification
│   └── main.py                  # MODIFIED: Register chat router
└── tests/
    ├── unit/
    │   ├── test_agent_service.py
    │   ├── test_mcp_tools.py
    │   └── test_chat_api.py
    └── integration/
        └── test_conversation_flow.py

frontend/
├── src/
│   ├── app/
│   │   ├── chat/
│   │   │   └── page.tsx         # NEW: Chat interface page
│   │   ├── dashboard/
│   │   │   └── page.tsx         # EXISTING: Traditional task UI
│   │   └── layout.tsx           # EXISTING: Root layout
│   ├── components/
│   │   ├── ChatInterface.tsx    # NEW: ChatKit integration
│   │   ├── MessageList.tsx      # NEW: Message display
│   │   ├── TaskList.tsx         # EXISTING: Traditional task list
│   │   └── TaskItem.tsx         # EXISTING: Task item component
│   └── lib/
│       ├── chat-client.ts       # NEW: Chat API client
│       ├── api-client.ts        # EXISTING: REST API client
│       └── types.ts             # MODIFIED: Add conversation types
└── tests/
    └── components/
        └── ChatInterface.test.tsx
```

**Structure Decision**: Web application structure (Option 2) selected. Existing backend/frontend directories extended with new AI agent layer. Backend adds agents/, tools/, and chat API. Frontend adds chat interface using ChatKit. Traditional REST API and UI remain functional alongside conversational interface.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

**Status**: No violations detected. All design decisions align with constitution principles.

---

## Phase 0: Research (Complete)

**Output**: `research.md`

**Key Decisions**:
1. **MCP Hosting**: Embedded in FastAPI process (security, performance, simplicity)
2. **AI Model**: GPT-4o-mini primary, GPT-3.5-turbo fallback (speed, cost, accuracy)
3. **Streaming**: Server-Sent Events (stateless, simple, industry standard)
4. **Retention**: 90-day conversation history with soft delete
5. **Rate Limiting**: 60 requests/minute per user (token bucket)
6. **Audit Trail**: Tool calls logged in messages metadata

---

## Phase 1: Design & Contracts (Complete)

**Outputs**:
- `data-model.md` - Conversation and Message entities with SQLModel definitions
- `contracts/chat-api.md` - Chat endpoint specification with SSE streaming
- `contracts/mcp-tools.md` - 6 MCP tool contracts with security model
- `quickstart.md` - Step-by-step implementation guide

**Key Design Elements**:
1. **Database Schema**: Two new tables (conversations, messages) with user_id foreign keys
2. **API Contract**: POST /api/{user_id}/chat with conversation_id support
3. **MCP Tools**: list_tasks, create_task, get_task, update_task, delete_task, mark_complete
4. **Security Pattern**: AgentService wraps tools with user_id pre-bound
5. **Stateless Design**: Conversation history loaded from database per request

---

## Constitution Check Re-evaluation (Post-Design)

**Status**: ✅ PASS - All design artifacts maintain compliance

**Verification**:
- ✅ **Security First**: MCP tools enforce user_id scoping at tool boundaries
- ✅ **Deterministic Output**: Tools designed for same input → same output
- ✅ **Stateless Execution**: No in-memory state, all context from database
- ✅ **Tool-Mediated State**: Agent never mutates database directly
- ✅ **Full-Stack Consistency**: API contracts align across all layers

**No violations introduced during design phase.**

---

## Implementation Readiness

**Status**: Ready for `/sp.tasks` command

**Artifacts Complete**:
- ✅ Research findings documented
- ✅ Data models defined with validation rules
- ✅ API contracts specified with error cases
- ✅ MCP tool contracts with security model
- ✅ Quickstart guide for developers
- ✅ Agent context updated

**Next Steps**:
1. Run `/sp.tasks` to generate actionable task breakdown
2. Assign tasks to specialized agents (database-skill, backend-skill, frontend-skill)
3. Execute implementation via `/sp.implement`

---

## Architectural Decisions Requiring ADR

📋 **Architectural decision detected**: MCP Server Hosting Strategy (Embedded vs Separate Process)
   - **Impact**: Long-term security model and deployment architecture
   - **Alternatives**: Embedded in FastAPI vs separate MCP server process
   - **Decision**: Embedded for security-first design with user_id pre-binding
   - **Document reasoning and tradeoffs?** Run `/sp.adr mcp-server-hosting-strategy`

📋 **Architectural decision detected**: AI Model Selection (GPT-4o-mini vs GPT-4-turbo)
   - **Impact**: Production cost and performance characteristics
   - **Alternatives**: GPT-4o-mini, GPT-3.5-turbo, GPT-4-turbo
   - **Decision**: GPT-4o-mini for optimal speed/cost/accuracy balance
   - **Document reasoning and tradeoffs?** Run `/sp.adr ai-model-selection`

📋 **Architectural decision detected**: Message Streaming Implementation (SSE vs WebSocket)
   - **Impact**: Frontend UX and backend statelessness
   - **Alternatives**: Server-Sent Events, WebSocket, Long Polling
   - **Decision**: SSE for stateless architecture alignment
   - **Document reasoning and tradeoffs?** Run `/sp.adr message-streaming-approach`
