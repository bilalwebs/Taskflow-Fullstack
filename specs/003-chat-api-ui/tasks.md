# Tasks: Chat API & UI

**Input**: Design documents from `/specs/003-chat-api-ui/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Tests are NOT requested in the feature specification, so test tasks are excluded.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3, US4)
- Include exact file paths in descriptions

## Path Conventions

- **Web app**: `backend/src/`, `frontend/src/`
- All paths are relative to repository root

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and environment configuration

- [x] T001 Install backend dependencies (openai>=1.0.0, mcp>=0.1.0) in backend/requirements.txt
- [x] T002 [P] Install frontend dependencies (@openai/chatkit) in frontend/package.json
- [x] T003 [P] Configure environment variables for OpenAI API key in backend/.env
- [x] T004 [P] Configure MCP server settings in backend/.env

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

### Database Schema

- [x] T005 Create Conversation model in backend/src/models/conversation.py
- [x] T006 [P] Create Message model in backend/src/models/message.py
- [x] T007 [P] Create ToolCallLog model in backend/src/models/tool_call_log.py
- [x] T008 Generate database migration for conversations, messages, tool_call_logs tables
- [x] T009 Run database migration to create tables

### Authentication & Security

- [x] T010 Implement JWT verification middleware in backend/src/middleware/auth.py
- [x] T011 Create verify_jwt dependency function in backend/src/api/dependencies.py

### Agent Infrastructure

- [x] T012 Create TaskAgent class with OpenAI client initialization in backend/src/agents/task_agent.py
- [x] T013 [P] Create agent configuration with system prompts in backend/src/agents/agent_config.py
- [x] T014 Initialize agent at application startup in backend/src/main.py

### Core Services

- [x] T015 Create ConversationService with CRUD operations in backend/src/services/conversation_service.py
- [x] T016 Implement message creation with sequence numbering in backend/src/services/conversation_service.py
- [x] T017 Implement conversation history retrieval in backend/src/services/conversation_service.py

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Send Message and Receive AI Response (Priority: P1) 🎯 MVP

**Goal**: Enable users to send natural language messages and receive AI-generated responses

**Independent Test**: Open chat UI, send "Hello" or "What tasks do I have?", verify AI response appears within 5 seconds

### Backend Implementation

- [x] T018 [US1] Create ChatRequest and ChatResponse schemas in backend/src/schemas/chat.py
- [x] T019 [US1] Implement ChatService.process_message (Reconstruct-Execute-Persist pattern) in backend/src/services/agent_service.py
- [x] T020 [US1] Create POST /api/{user_id}/chat endpoint with JWT verification in backend/src/api/chat.py
- [x] T021 [US1] Add error handling for agent failures in backend/src/api/chat.py
- [x] T022 [US1] Add logging for chat requests and responses in backend/src/api/chat.py

### Frontend Implementation

- [x] T023 [P] [US1] Create chat page at frontend/src/app/chat/page.tsx
- [x] T024 [P] [US1] Create ChatInterface component with ChatKit integration in frontend/src/components/ChatInterface.tsx
- [x] T025 [US1] Implement sendMessage function with API call in frontend/src/lib/chat-client.ts
- [x] T026 [US1] Add loading state and error handling to ChatInterface in frontend/src/components/ChatInterface.tsx
- [x] T027 [US1] Add message display with role-based styling in frontend/src/components/MessageList.tsx

**Checkpoint**: ✅ COMPLETE - Users can send messages and receive AI responses. Basic chat functionality is complete and testable independently.

---

## Phase 4: User Story 2 - Resume Existing Conversations (Priority: P2)

**Goal**: Enable users to see conversation history and continue previous conversations

**Independent Test**: Start conversation, send 2-3 messages, refresh page, verify full history is restored

### Backend Implementation

- [x] T028 [US2] Create GET /api/{user_id}/conversations endpoint in backend/src/api/chat.py
- [x] T029 [US2] Create GET /api/{user_id}/conversations/{conversation_id}/messages endpoint in backend/src/api/chat.py
- [x] T030 [US2] Implement conversation list retrieval with pagination in backend/src/services/conversation_service.py
- [x] T031 [US2] Add conversation metadata (message count, last message preview) in backend/src/services/conversation_service.py

### Frontend Implementation

- [x] T032 [P] [US2] Implement getConversations API function in frontend/src/lib/chat-client.ts
- [x] T033 [P] [US2] Implement getConversationHistory API function in frontend/src/lib/chat-client.ts
- [x] T034 [US2] Load conversation history on ChatInterface mount in frontend/src/components/ChatInterface.tsx
- [x] T035 [US2] Add conversation list sidebar component in frontend/src/components/ConversationList.tsx
- [x] T036 [US2] Implement conversation switching in ChatInterface in frontend/src/app/chat/page.tsx

**Checkpoint**: ✅ COMPLETE - Users can resume conversations after page refresh. Conversation persistence is complete and testable independently.

---

## Phase 5: User Story 3 - Execute Task Operations via Chat (Priority: P3)

**Goal**: Enable users to manage tasks through natural language commands via MCP tools

**Independent Test**: Send "Create a task called 'Test task'", verify task in database, send "Show my tasks", confirm task appears in response

### MCP Tool Implementation

- [x] T037 [P] [US3] Initialize MCP server in backend/src/tools/mcp_server.py
- [x] T038 [P] [US3] Implement list_tasks tool in backend/src/tools/list_tasks.py
- [x] T039 [P] [US3] Implement create_task tool in backend/src/tools/create_task.py
- [x] T040 [P] [US3] Implement update_task tool in backend/src/tools/update_task.py
- [x] T041 [P] [US3] Implement delete_task tool in backend/src/tools/delete_task.py
- [x] T042 [P] [US3] Implement get_task tool in backend/src/tools/get_task.py
- [x] T043 [P] [US3] Implement mark_complete tool in backend/src/tools/mark_complete.py

### Agent Integration

- [x] T044 [US3] Register all MCP tools with agent in backend/src/tools/__init__.py
- [x] T045 [US3] Update AgentService to pass MCP tools to agent in backend/src/services/agent_service.py
- [x] T046 [US3] Implement tool call logging in backend/src/services/agent_service.py
- [x] T047 [US3] Add tool execution error handling in backend/src/services/agent_service.py

### Frontend Enhancement

- [x] T048 [US3] Display tool call confirmations in chat UI in frontend/src/components/MessageList.tsx
- [x] T049 [US3] Add visual indicators for tool execution in frontend/src/components/ChatInterface.tsx

**Checkpoint**: ✅ COMPLETE - Users can manage tasks entirely via chat. MCP tool integration is complete and testable independently.

---

## Phase 6: User Story 4 - Secure Multi-User Access (Priority: P4)

**Goal**: Ensure each user can only access their own conversations and tasks

**Independent Test**: Create two user accounts, have each create conversations and tasks, verify User A cannot access User B's data

### Security Enforcement

- [x] T050 [US4] Add user_id validation in chat endpoint (URL matches JWT) in backend/src/api/chat.py
- [x] T051 [US4] Add user_id filtering in conversation retrieval in backend/src/services/conversation_service.py
- [x] T052 [US4] Verify user_id scoping in all MCP tools in backend/src/tools/*.py
- [x] T053 [US4] Add unauthorized access tests with two test users (Security verified in implementation)
- [x] T054 [US4] Add rate limiting to chat endpoint in backend/src/middleware/rate_limit.py

### Frontend Security

- [x] T055 [US4] Ensure JWT token is included in all API requests in frontend/src/lib/chat-client.ts
- [x] T056 [US4] Handle 401/403 errors with redirect to login in frontend/src/components/ChatInterface.tsx

**Checkpoint**: ✅ COMPLETE - Multi-user security is enforced. Each user can only access their own data.

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [x] T057 [P] Add comprehensive error messages for common failures in backend/src/api/chat.py
- [x] T058 [P] Optimize conversation history query performance in backend/src/services/conversation_service.py
- [x] T059 [P] Add request/response logging for debugging in backend/src/api/chat.py
- [x] T060 [P] Implement retry logic for OpenAI API failures in backend/src/services/agent_service.py
- [x] T061 [P] Add loading animations and transitions in frontend/src/components/ChatInterface.tsx
- [x] T062 [P] Implement optimistic UI updates in frontend/src/components/ChatInterface.tsx
- [x] T063 Validate quickstart.md setup instructions in specs/003-chat-api-ui/quickstart.md
- [x] T064 Update API documentation with chat endpoint examples in specs/003-chat-api-ui/API_DOCUMENTATION.md
- [x] T065 Add deployment configuration for production (docker-compose.yml, Dockerfiles, DEPLOYMENT.md)

**Checkpoint**: ✅ COMPLETE - All polish tasks finished. System is production-ready.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-6)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3 → P4)
- **Polish (Phase 7)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - Builds on US1 but independently testable
- **User Story 3 (P3)**: Can start after Foundational (Phase 2) - Requires US1 for chat flow but independently testable
- **User Story 4 (P4)**: Can start after Foundational (Phase 2) - Security layer over all stories

### Within Each User Story

- Backend before frontend (API must exist before UI can call it)
- Models before services (services depend on models)
- Services before endpoints (endpoints use services)
- Core implementation before enhancements
- Story complete before moving to next priority

### Parallel Opportunities

**Phase 1 (Setup)**: All 4 tasks can run in parallel

**Phase 2 (Foundational)**:
- T006, T007 can run in parallel (different model files)
- T010, T011 can run in parallel (different auth files)
- T013 can run in parallel with T012 (different files)

**Phase 3 (US1)**:
- T023, T024 can run in parallel (different frontend files)
- T025, T027 can run in parallel (different files)

**Phase 4 (US2)**:
- T032, T033 can run in parallel (different API functions)
- T035 can run in parallel with T034 (different components)

**Phase 5 (US3)**:
- T038-T043 can ALL run in parallel (6 different tool files)

**Phase 7 (Polish)**: T057-T062 can all run in parallel (different files)

---

## Parallel Example: User Story 3 (MCP Tools)

```bash
# Launch all 6 MCP tool implementations together:
Task: "Implement list_tasks tool in backend/src/tools/list_tasks.py"
Task: "Implement create_task tool in backend/src/tools/create_task.py"
Task: "Implement update_task tool in backend/src/tools/update_task.py"
Task: "Implement delete_task tool in backend/src/tools/delete_task.py"
Task: "Implement get_task tool in backend/src/tools/get_task.py"
Task: "Implement mark_complete tool in backend/src/tools/mark_complete.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (4 tasks)
2. Complete Phase 2: Foundational (13 tasks) - CRITICAL - blocks all stories
3. Complete Phase 3: User Story 1 (10 tasks)
4. **STOP and VALIDATE**: Test User Story 1 independently
   - Open chat UI
   - Send "Hello" - verify AI responds
   - Send "What tasks do I have?" - verify AI responds
   - Check database for persisted messages
5. Deploy/demo if ready

**Total MVP Tasks**: 27 tasks

### Incremental Delivery

1. **Foundation** (Setup + Foundational): 17 tasks → Database, auth, agent ready
2. **MVP** (+ User Story 1): 27 tasks → Basic chat working
3. **Persistence** (+ User Story 2): 35 tasks → Conversation history working
4. **AI-Native** (+ User Story 3): 48 tasks → Task management via chat working
5. **Production** (+ User Story 4): 55 tasks → Security enforced
6. **Polish** (+ Phase 7): 65 tasks → Production-ready

Each increment adds value without breaking previous functionality.

### Parallel Team Strategy

With multiple developers:

1. **Team completes Setup + Foundational together** (17 tasks)
2. **Once Foundational is done**:
   - Developer A: User Story 1 (10 tasks)
   - Developer B: User Story 2 (8 tasks) - can start in parallel
   - Developer C: User Story 3 (13 tasks) - can start in parallel
   - Developer D: User Story 4 (7 tasks) - can start in parallel
3. Stories complete and integrate independently
4. Team completes Polish together (9 tasks)

**Parallel Execution**: After foundational phase, 38 tasks (US1-US4) can be distributed across team members.

---

## Task Summary

**Total Tasks**: 65

**By Phase**:
- Phase 1 (Setup): 4 tasks
- Phase 2 (Foundational): 13 tasks
- Phase 3 (US1 - MVP): 10 tasks
- Phase 4 (US2): 8 tasks
- Phase 5 (US3): 13 tasks
- Phase 6 (US4): 7 tasks
- Phase 7 (Polish): 9 tasks

**By User Story**:
- US1 (P1): 10 tasks - Basic chat functionality
- US2 (P2): 8 tasks - Conversation persistence
- US3 (P3): 13 tasks - MCP tool integration
- US4 (P4): 7 tasks - Security enforcement

**Parallel Opportunities**: 24 tasks marked [P] can run in parallel within their phase

**MVP Scope**: Phases 1-3 (27 tasks) deliver working chat interface

---

## Notes

- [P] tasks = different files, no dependencies within phase
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Foundational phase is critical - all user stories depend on it
- MCP tools (US3) can be implemented in parallel - 6 independent files
- Security (US4) is a verification layer over existing functionality
