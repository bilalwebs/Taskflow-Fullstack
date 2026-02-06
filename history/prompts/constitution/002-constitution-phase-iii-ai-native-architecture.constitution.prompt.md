---
id: 002
title: Constitution Phase III AI-Native Architecture
stage: constitution
date: 2026-02-03
surface: agent
model: claude-sonnet-4-5
feature: none
branch: 001-multi-user-todo-app
user: system
command: /sp.constitution
labels: ["constitution", "phase-iii", "ai-native", "mcp-tools", "agents", "stateless-architecture"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - .specify/memory/constitution.md
tests:
  - None (constitution update)
---

## Prompt

Project: AI-Native Todo Application with MCP-based Agentic Architecture (Phase III)

Scope of Phase III:
Phase III introduces a production-style, AI-powered conversational interface for task management.
The system must use a stateless server architecture, AI agents for reasoning, and MCP tools for all task mutations.

Core Principles:
- Agent-first design: All business actions are initiated by AI agents via MCP tools
- Tool-mediated state changes: AI must never mutate state directly
- Stateless execution: No server-side memory between requests
- Deterministic tooling: MCP tools are predictable, validated, and auditable
- Separation of concerns: Agent logic, MCP tooling, and UI/API are independently specified
- Natural language first: Users interact exclusively via conversational commands

Architecture Principles:
- All task operations MUST be exposed as MCP tools
- AI agents MUST invoke MCP tools for all task-related actions
- MCP tools MUST be stateless and persist data via the database
- Chat endpoint MUST reconstruct context from persisted conversation history
- Server MUST remain restart-safe with no in-memory state dependencies
- Authentication context MUST be enforced at tool boundaries (user_id scoped)

AI Agent Standards:
- Use OpenAI Agents SDK exclusively for AI reasoning
- Agent must select tools based on user intent, not hard-coded rules
- Agent responses must confirm actions in natural language
- Agent must gracefully handle ambiguity, missing data, and errors
- Agent must never hallucinate task state or IDs
- Agent must rely only on tool responses for factual state

MCP Tooling Standards:
- Use Official MCP SDK
- Each tool must have:
  - Clear purpose
  - Strict input validation
  - Typed parameters
  - Deterministic outputs
- Tools must enforce user ownership (no cross-user access)
- Tools must return structured results suitable for agent reasoning
- Tools must not depend on conversation state

Data & Persistence Standards:
- All conversation state must be persisted in the database
- Message history must be stored before agent execution
- Assistant responses must be stored after agent execution
- Database is the single source of truth for tasks and conversations
- ORM: SQLModel
- Database: Neon Serverless PostgreSQL

API & UI Standards:
- Single chat endpoint: POST /api/{user_id}/chat
- Endpoint must support resuming existing conversations
- Frontend must use OpenAI ChatKit
- UI must clearly show assistant responses and confirmations
- Errors must be communicated in user-friendly language

Security & Reliability:
- Authentication handled via Better Auth
- All API requests must be authenticated
- Tool calls must be authorized using user_id
- System must tolerate retries and duplicate requests safely
- No sensitive data exposed to the AI beyond required context

Development & Evaluation Constraints:
- Development must follow Agentic Dev Stack workflow:
  Write spec → Generate plan → Break into tasks → Implement via Claude Code
- No manual coding outside AI-assisted generation
- Each spec must have clear success criteria and non-goals
- All functionality must be reviewable via specs, plans, and commit history

Success Criteria for Phase III:
- Users can manage todos using natural language only
- AI agent correctly selects and invokes MCP tools

## Response snapshot

Constitution successfully updated from v1.0.0 to v1.1.0 (Phase III: AI-Native Architecture).

**Version Change**: 1.0.0 → 1.1.0 (MINOR bump)
**Rationale**: Added new principles and architecture sections without removing existing functionality. This is an additive change that extends the constitution for Phase III while maintaining backward compatibility with Phases I-II.

**Modified Principles**:
- Principle II (Security First): Extended to include MCP tool authorization requirements
- Principle IV (Full-Stack Consistency): Extended to include AI agent layer and hallucination prevention

**Added Principles**:
- Principle VIII: Agent-First Design - All business actions initiated by AI agents via MCP tools
- Principle IX: Tool-Mediated State Changes - AI agents must never mutate state directly
- Principle X: Stateless Execution - No server-side memory between requests

**New Sections**:
- MCP Tooling Standards: Tool design and implementation requirements
- AI Agent Standards: Agent configuration, behavior, and response standards
- Conversation Persistence Standards: Database schema and persistence rules for chat history
- Conversational API Design: Chat endpoint specifications
- ChatKit Requirements: Frontend conversational UI standards
- Phase III Technology Stack: OpenAI Agents SDK, MCP SDK, ChatKit

**Required MCP Tools Defined**:
- list_tasks, create_task, update_task, delete_task, get_task, mark_complete

**Key Architecture Decisions**:
1. Stateless server architecture with database-backed conversation history
2. MCP tools as exclusive interface for state mutations
3. OpenAI Agents SDK for AI reasoning (no custom agent implementations)
4. Single chat endpoint: POST /api/{user_id}/chat
5. User_id scoping enforced at tool boundaries

**Security Enhancements**:
- MCP tools must validate user_id from JWT context
- AI agents must not receive raw JWT tokens or passwords
- Tool calls must be audited for security and determinism
- No sensitive data exposed to AI beyond required context

**Template Update Requirements**:
- spec-template.md: Add conversational interface patterns
- plan-template.md: Add MCP tool design phase
- tasks-template.md: Add agent/tool implementation task types

## Outcome

- ✅ Impact: Constitution updated to v1.1.0 with Phase III AI-Native Architecture principles
- 🧪 Tests: N/A (constitution document)
- 📁 Files: .specify/memory/constitution.md (updated)
- 🔁 Next prompts: Update spec/plan/tasks templates for Phase III patterns
- 🧠 Reflection: Successfully integrated Phase III requirements while maintaining backward compatibility with existing Phases I-II. The constitution now provides clear guidance for implementing AI-native conversational interfaces with MCP tools and stateless architecture.

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): Manual review - PASS
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Create Phase III feature specification using updated constitution principles
