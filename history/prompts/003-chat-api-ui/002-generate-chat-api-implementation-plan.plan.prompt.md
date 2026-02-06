---
id: 002
title: Generate Chat API Implementation Plan
stage: plan
date: 2026-02-04
surface: agent
model: claude-sonnet-4-5-20250929
feature: 003-chat-api-ui
branch: 003-chat-api-ui
user: user
command: /sp.plan
labels: ["planning", "architecture", "chat-api", "mcp-tools", "phase-3"]
links:
  spec: specs/003-chat-api-ui/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/003-chat-api-ui/plan.md
  - specs/003-chat-api-ui/research.md
  - specs/003-chat-api-ui/data-model.md
  - specs/003-chat-api-ui/quickstart.md
  - specs/003-chat-api-ui/contracts/chat-api.yaml
  - specs/003-chat-api-ui/contracts/mcp-tools.yaml
  - CLAUDE.md (updated)
tests:
  - None (planning phase)
---

## Prompt

/sp.plan

Additional context from user:
"t frontend chat component usage
- Document integration flow: ChatKit → API → Agent → MCP → DB
- Verify alignment with Spec 4 (Agent Behavior) and Spec 5 (MCP Tools)

Deliverables:
- Fully functional stateless chat API
- Conversation and message persistence in PostgreSQL
- ChatKit-based frontend UI integrated with API
- Agent execution integrated with MCP tools
- Secure, JWT-authenticated chat flow
- Documentation for implementation, testing, and agent usage

Completion Criteria:
- Users can manage tasks via chat UI
- Conversation state persists across requests and page reloads
- AI agent calls MCP tools correctly for all task operations
- Frontend updates reflect task changes in real-time
- System remains stateless on server between requests"

## Response snapshot

**Planning Phase Completed Successfully**

Generated comprehensive implementation plan for Chat API & UI feature with complete Phase 0 research and Phase 1 design artifacts.

**Constitution Check**: ✅ PASS
- All Phase III principles satisfied (Agent-First Design, Tool-Mediated State Changes, Stateless Execution)
- Security compliance verified (JWT authentication, data isolation)
- Technology stack compliance confirmed (OpenAI Agents SDK, MCP SDK, ChatKit, FastAPI, SQLModel)
- No constitution violations detected

**Phase 0: Research & Technical Decisions** (8 decisions documented)
1. OpenAI Agents SDK integration: Async execution in FastAPI endpoint
2. MCP SDK usage: Decorator-based tool registration with Python MCP SDK
3. ChatKit integration: Client Component with Server-Side data fetching
4. Conversation history: Full history loading with pagination fallback (100 message limit)
5. Stateless execution: Reconstruct-Execute-Persist pattern
6. JWT token flow: Header → Backend verification → Tool parameter injection
7. Error handling: Graceful degradation with user-friendly messages
8. Concurrency: Optimistic locking with message sequence numbers

**Phase 1: Design Artifacts Created**
1. **data-model.md**:
   - 3 entities: Conversation, Message, ToolCallLog
   - Complete SQLModel definitions with relationships
   - Database migration strategy (CREATE/DROP scripts)
   - Data access patterns and integrity constraints

2. **contracts/chat-api.yaml**:
   - OpenAPI 3.0 specification
   - 3 endpoints: POST /api/{user_id}/chat, GET /api/{user_id}/conversations, GET /api/{user_id}/conversations/{id}
   - Complete request/response schemas with examples
   - Error response definitions (400, 401, 403, 404, 500)

3. **contracts/mcp-tools.yaml**:
   - 6 MCP tools: list_tasks, create_task, update_task, delete_task, get_task, mark_complete
   - Input/output schemas for each tool
   - Agent usage guidance and security considerations
   - Python MCP SDK registration examples

4. **quickstart.md**:
   - Environment setup (backend + frontend)
   - Dependency installation instructions
   - Database migration procedures
   - Testing procedures (authentication, chat endpoint, MCP tools, frontend UI)
   - Troubleshooting guide (6 common issues)
   - Production deployment checklist

**Agent Context Update**: ✅ Completed
- Updated CLAUDE.md with Phase III technologies
- Added: Python 3.11+, TypeScript/Node.js 18+, OpenAI Agents SDK, MCP SDK, ChatKit
- Added: Neon PostgreSQL tables (conversations, messages, tool_call_logs)

**Project Structure Defined**:
- Backend: 13 new files (models, services, agents, tools, API endpoints)
- Frontend: 6 new files (pages, components, API client)
- Tests: 6 test files (backend + frontend)

**Key Architectural Decisions**:
- Stateless backend with database-persisted conversation state
- Single POST endpoint for all chat interactions
- AI agent with 6 MCP tools for task operations
- JWT authentication with user_id scoping at all layers
- Conversation history limit: 1000 messages (MVP)
- Performance targets: <5s response time, <2s history load

## Outcome

- ✅ Impact: Complete architectural plan ready for task generation. Establishes technical foundation for AI-native conversational interface with stateless backend, MCP tool integration, and secure multi-user access.
- 🧪 Tests: No tests at planning phase. Test strategy documented in data-model.md and quickstart.md.
- 📁 Files: 6 files created (plan.md, research.md, data-model.md, quickstart.md, 2 contract files), 1 file updated (CLAUDE.md)
- 🔁 Next prompts: `/sp.tasks` to generate actionable implementation tasks with dependencies
- 🧠 Reflection: Planning phase successfully completed all required artifacts. Constitution check passed with zero violations. All Phase III principles (Agent-First Design, Tool-Mediated State Changes, Stateless Execution) properly addressed. Research decisions provide clear implementation guidance. Design artifacts are comprehensive and ready for task generation.

## Evaluation notes (flywheel)

- Failure modes observed: Web search unavailable (used knowledge base instead), bash script for PHR creation not found (used agent-native approach successfully)
- Graders run and results (PASS/FAIL): Constitution Check - PASS (all Phase III principles satisfied)
- Prompt variant (if applicable): Standard /sp.plan workflow with Phase 0 research and Phase 1 design
- Next experiment (smallest change to try): Proceed to /sp.tasks for task generation with dependency ordering
