# Tasks: AI Agent Behavior for Conversational Task Management

**Input**: Design documents from `/specs/002-ai-agent-behavior/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: Not explicitly requested in specification - tasks focus on implementation only.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

---

## Format: `- [ ] [ID] [P?] [Story?] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and dependency installation

- [X] T001 Install backend dependencies: openai, mcp-sdk, sqlalchemy, alembic in backend/requirements.txt
- [X] T002 [P] Install frontend dependencies: @openai/chatkit in frontend/package.json
- [X] T003 [P] Configure environment variables for OpenAI API key in backend/.env
- [X] T004 [P] Update backend/src/config.py to load OPENAI_API_KEY and OPENAI_MODEL settings

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

### Database Schema

- [X] T005 Create Conversation model in backend/src/models/conversation.py with SQLModel
- [X] T006 [P] Create Message model with MessageRole enum in backend/src/models/message.py
- [X] T007 Create Alembic migration for conversations and messages tables in backend/alembic/versions/
- [X] T008 Apply database migration to create conversations and messages tables

### MCP Infrastructure

- [X] T009 Create MCP server setup module in backend/src/tools/mcp_server.py
- [X] T010 [P] Create MCP Context configuration with database engine in backend/src/tools/mcp_server.py
- [X] T011 [P] Create tools __init__.py to export all MCP tools in backend/src/tools/__init__.py

### Agent Service Foundation

- [X] T012 Create AgentService base class in backend/src/services/agent_service.py
- [X] T013 Implement user-scoped tool wrapper pattern in AgentService.create_user_scoped_tools()
- [X] T014 Configure OpenAI client initialization in AgentService.__init__()

### Chat API Foundation

- [X] T015 Create chat router in backend/src/api/chat.py with POST /api/{user_id}/chat endpoint
- [X] T016 Implement JWT authentication verification for chat endpoint
- [X] T017 Implement conversation loading/creation logic in chat endpoint
- [X] T018 Implement message persistence (user message before agent, assistant message after agent)
- [X] T019 Register chat router in backend/src/main.py

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Natural Language Task Creation (Priority: P1) 🎯 MVP

**Goal**: Users can create tasks by describing what they want to remember in natural conversation

**Independent Test**: Send messages like "remind me to buy milk" and verify task is created with agent confirmation

### Implementation for User Story 1

- [X] T020 [P] [US1] Implement create_task MCP tool in backend/src/tools/create_task.py
- [X] T021 [US1] Add create_task tool to AgentService.create_user_scoped_tools() with user_id pre-bound
- [X] T022 [US1] Configure agent system prompt for task creation intent recognition in backend/src/agents/task_agent.py
- [X] T023 [US1] Integrate create_task tool with OpenAI agent in AgentService.process_message()
- [X] T024 [US1] Add error handling for empty titles and validation in create_task tool
- [X] T025 [US1] Test agent response for task creation confirmation messages

**Checkpoint**: Users can create tasks via conversation - MVP core functionality complete

---

## Phase 4: User Story 2 - Task Retrieval and Status Inquiry (Priority: P1) 🎯 MVP

**Goal**: Users can ask about their tasks and receive clear, conversational responses with completion status

**Independent Test**: Create tasks, then ask "what are my tasks?" and verify agent lists all tasks with status

### Implementation for User Story 2

- [X] T026 [P] [US2] Implement list_tasks MCP tool in backend/src/tools/list_tasks.py
- [X] T027 [US2] Add list_tasks tool to AgentService.create_user_scoped_tools() with user_id pre-bound
- [X] T028 [US2] Update agent system prompt for task listing intent recognition in backend/src/agents/task_agent.py
- [X] T029 [US2] Integrate list_tasks tool with OpenAI agent in AgentService.process_message()
- [X] T030 [US2] Format agent responses to display tasks in readable format (completed vs incomplete)
- [X] T031 [US2] Handle empty task list scenario with helpful agent response

**Checkpoint**: Users can view their tasks via conversation - MVP fully functional (US1 + US2)

---

## Phase 5: User Story 3 - Task Completion via Conversation (Priority: P2)

**Goal**: Users can mark tasks complete by describing what they finished in natural language

**Independent Test**: Create task, then say "I finished buying milk" and verify task marked complete with confirmation

### Implementation for User Story 3

- [X] T032 [P] [US3] Implement mark_complete MCP tool in backend/src/tools/mark_complete.py
- [X] T033 [US3] Add mark_complete tool to AgentService.create_user_scoped_tools() with user_id pre-bound
- [X] T034 [US3] Update agent system prompt for completion intent recognition in backend/src/agents/task_agent.py
- [X] T035 [US3] Implement multi-step flow: list_tasks → identify task → mark_complete in agent logic
- [X] T036 [US3] Add clarification logic when multiple tasks match user reference
- [X] T037 [US3] Handle task-not-found scenario with helpful agent response

**Checkpoint**: Users can complete tasks via conversation - Core task management complete (US1 + US2 + US3)

---

## Phase 6: User Story 4 - Task Modification Through Conversation (Priority: P3)

**Goal**: Users can update task details (title, description) by describing changes in natural language

**Independent Test**: Create task, then say "change 'buy milk' to 'buy milk and eggs'" and verify update with confirmation

### Implementation for User Story 4

- [X] T038 [P] [US4] Implement update_task MCP tool in backend/src/tools/update_task.py
- [X] T039 [US4] Add update_task tool to AgentService.create_user_scoped_tools() with user_id pre-bound
- [X] T040 [US4] Update agent system prompt for update intent recognition in backend/src/agents/task_agent.py
- [X] T041 [US4] Implement multi-step flow: list_tasks → identify task → update_task in agent logic
- [X] T042 [US4] Add validation for empty title and field requirements in update_task tool
- [X] T043 [US4] Handle ambiguous update requests with clarification questions

**Checkpoint**: Users can update tasks via conversation - Full CRUD operations available

---

## Phase 7: User Story 5 - Task Deletion via Conversation (Priority: P3)

**Goal**: Users can remove tasks by describing what to delete in natural language

**Independent Test**: Create task, then say "delete the groceries task" and verify removal with confirmation

### Implementation for User Story 5

- [X] T044 [P] [US5] Implement delete_task MCP tool in backend/src/tools/delete_task.py
- [X] T045 [US5] Add delete_task tool to AgentService.create_user_scoped_tools() with user_id pre-bound
- [X] T046 [US5] Update agent system prompt for deletion intent recognition in backend/src/agents/task_agent.py
- [X] T047 [US5] Implement multi-step flow: list_tasks → identify task → delete_task in agent logic
- [X] T048 [US5] Add confirmation logic for bulk deletion requests
- [X] T049 [US5] Handle task-not-found scenario for deletion attempts

**Checkpoint**: Users can delete tasks via conversation - Complete task lifecycle management

---

## Phase 8: User Story 6 - Multi-Step Task Operations (Priority: P3)

**Goal**: Users can perform sequences of operations with context maintained across multiple exchanges

**Independent Test**: Say "show my tasks" → "mark the second one as done" → verify agent maintains context

### Implementation for User Story 6

- [X] T050 [P] [US6] Implement get_task MCP tool in backend/src/tools/get_task.py
- [X] T051 [US6] Add get_task tool to AgentService.create_user_scoped_tools() with user_id pre-bound
- [X] T052 [US6] Enhance conversation history loading to include sufficient context (last 20 messages)
- [X] T053 [US6] Update agent system prompt to maintain context across multi-turn conversations
- [X] T054 [US6] Implement context-aware task reference resolution (e.g., "the report task" after listing)
- [X] T055 [US6] Add conversation resumption logic to handle interrupted conversations
- [X] T056 [US6] Test multi-step flows: list → select → operate across all operations

**Checkpoint**: Users can perform complex multi-step operations - Full conversational experience complete

---

## Phase 9: Frontend Integration

**Purpose**: Build chat interface for user interaction

### Chat Interface Components

- [X] T057 [P] Create chat page in frontend/src/app/chat/page.tsx
- [X] T058 [P] Create ChatInterface component in frontend/src/components/ChatInterface.tsx
- [X] T059 [P] Create MessageList component in frontend/src/components/MessageList.tsx
- [X] T060 [P] Add conversation types to frontend/src/lib/types.ts
- [X] T061 Create chat API client in frontend/src/lib/chat-client.ts
- [X] T062 Implement message sending with JWT authentication in ChatInterface
- [X] T063 Implement message display with user/assistant role styling in MessageList
- [X] T064 Add loading state and error handling to ChatInterface
- [X] T065 Implement conversation persistence (store conversation_id in state)

**Checkpoint**: Frontend chat interface functional - Users can interact with agent via UI

---

## Phase 10: Streaming & Performance

**Purpose**: Enhance user experience with progressive response rendering

### Server-Sent Events Implementation

- [X] T066 Create streaming chat endpoint POST /api/{user_id}/chat/stream in backend/src/api/chat.py
- [X] T067 Implement SSE event generator with progressive response chunks
- [X] T068 Add streaming response support to AgentService.process_message()
- [X] T069 Configure SSE headers (Cache-Control, Connection, X-Accel-Buffering)
- [X] T070 Create useStreamingChat hook in frontend/src/hooks/useStreamingChat.ts
- [X] T071 Implement SSE client with ReadableStream in frontend
- [X] T072 Update ChatInterface to use streaming endpoint for better UX
- [X] T073 Add progressive message rendering in MessageList component

**Checkpoint**: Streaming responses working - Users see agent responses as they generate

---

## Phase 11: Polish & Cross-Cutting Concerns

**Purpose**: Production readiness and quality improvements

### Rate Limiting & Security

- [X] T074 [P] Implement rate limiting middleware (60 req/min per user) in backend/src/middleware/rate_limit.py
- [X] T075 [P] Add rate limit headers to chat endpoint responses
- [X] T076 [P] Implement input sanitization for message content in chat endpoint
- [X] T077 [P] Add request timeout handling (30 seconds) to chat endpoint

### Error Handling & Logging

- [X] T078 [P] Implement user-friendly error messages for OpenAI API failures
- [X] T079 [P] Add tool call logging to messages.tool_calls JSONB field
- [X] T080 [P] Implement graceful degradation for database connection errors
- [X] T081 [P] Add structured logging for agent operations and tool invocations

### Documentation & Validation

- [X] T082 [P] Update API documentation with chat endpoint examples
- [X] T083 [P] Create conversation cleanup job for 90-day retention policy
- [X] T084 [P] Add monitoring for agent response times and accuracy
- [X] T085 Run quickstart.md validation steps to verify end-to-end functionality

**Checkpoint**: Production-ready conversational task management system complete

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-8)**: All depend on Foundational phase completion
  - User stories can proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3)
- **Frontend (Phase 9)**: Can start after US1 and US2 are complete (MVP backend ready)
- **Streaming (Phase 10)**: Depends on Frontend phase completion
- **Polish (Phase 11)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P1)**: Can start after Foundational (Phase 2) - Independent of US1
- **User Story 3 (P2)**: Can start after Foundational (Phase 2) - Uses list_tasks from US2 but independently testable
- **User Story 4 (P3)**: Can start after Foundational (Phase 2) - Uses list_tasks from US2 but independently testable
- **User Story 5 (P3)**: Can start after Foundational (Phase 2) - Uses list_tasks from US2 but independently testable
- **User Story 6 (P3)**: Can start after Foundational (Phase 2) - Uses all tools but independently testable

### Within Each User Story

- MCP tool implementation before AgentService integration
- Agent configuration before testing
- Error handling after core functionality
- Each story should be independently completable and testable

### Parallel Opportunities

**Phase 1 (Setup)**: T002, T003, T004 can run in parallel

**Phase 2 (Foundational)**:
- T006 (Message model) parallel with T005 (Conversation model)
- T010, T011 (MCP setup) parallel with T005-T008 (Database)
- T012-T014 (AgentService) after T009-T011 complete

**Phase 3-8 (User Stories)**: Once Foundational completes, all user stories can start in parallel:
- Developer A: US1 (T020-T025)
- Developer B: US2 (T026-T031)
- Developer C: US3 (T032-T037)
- Developer D: US4 (T038-T043)
- Developer E: US5 (T044-T049)
- Developer F: US6 (T050-T056)

**Phase 9 (Frontend)**: T057-T060 can run in parallel (different components)

**Phase 10 (Streaming)**: T066-T069 (backend) parallel with T070-T073 (frontend)

**Phase 11 (Polish)**: T074-T077 (security) and T078-T081 (logging) and T082-T085 (docs) can all run in parallel

---

## Parallel Example: User Story 1

```bash
# Launch MCP tool and agent config in parallel:
Task T020: "Implement create_task MCP tool in backend/src/tools/create_task.py"
# Then sequentially:
Task T021: "Add create_task tool to AgentService" (depends on T020)
Task T022: "Configure agent system prompt" (can be parallel with T021)
Task T023: "Integrate with OpenAI agent" (depends on T021, T022)
```

---

## Parallel Example: Multiple User Stories

```bash
# After Foundational phase completes, launch all user stories in parallel:
Team Member 1: Phase 3 (US1) - Tasks T020-T025
Team Member 2: Phase 4 (US2) - Tasks T026-T031
Team Member 3: Phase 5 (US3) - Tasks T032-T037
Team Member 4: Phase 6 (US4) - Tasks T038-T043
Team Member 5: Phase 7 (US5) - Tasks T044-T049
Team Member 6: Phase 8 (US6) - Tasks T050-T056
```

---

## Implementation Strategy

### MVP First (User Stories 1 & 2 Only)

1. Complete Phase 1: Setup (T001-T004)
2. Complete Phase 2: Foundational (T005-T019) - CRITICAL
3. Complete Phase 3: User Story 1 (T020-T025) - Create tasks
4. Complete Phase 4: User Story 2 (T026-T031) - List tasks
5. **STOP and VALIDATE**: Test US1 and US2 independently
6. Complete Phase 9: Frontend (T057-T065) - Basic UI
7. Deploy/demo MVP

**MVP Scope**: Users can create and view tasks via conversation

### Incremental Delivery

1. **Foundation** (Phases 1-2) → Database and agent infrastructure ready
2. **MVP** (Phases 3-4 + 9) → Create and list tasks with basic UI → Deploy
3. **Core Operations** (Phase 5) → Add task completion → Deploy
4. **Full CRUD** (Phases 6-7) → Add update and delete → Deploy
5. **Advanced** (Phase 8) → Multi-step operations → Deploy
6. **Production** (Phases 10-11) → Streaming and polish → Deploy

Each increment adds value without breaking previous functionality.

### Parallel Team Strategy

With 6 developers:

1. **Week 1**: All developers complete Setup + Foundational together (Phases 1-2)
2. **Week 2**: Once Foundational is done, split into user stories:
   - Dev A: US1 (Phase 3)
   - Dev B: US2 (Phase 4)
   - Dev C: US3 (Phase 5)
   - Dev D: US4 (Phase 6)
   - Dev E: US5 (Phase 7)
   - Dev F: US6 (Phase 8)
3. **Week 3**: Frontend team (Phases 9-10)
4. **Week 4**: Polish team (Phase 11)

---

## Task Summary

**Total Tasks**: 85 tasks across 11 phases

**Task Count by Phase**:
- Phase 1 (Setup): 4 tasks
- Phase 2 (Foundational): 15 tasks
- Phase 3 (US1 - Create): 6 tasks
- Phase 4 (US2 - List): 6 tasks
- Phase 5 (US3 - Complete): 6 tasks
- Phase 6 (US4 - Update): 6 tasks
- Phase 7 (US5 - Delete): 6 tasks
- Phase 8 (US6 - Multi-step): 7 tasks
- Phase 9 (Frontend): 9 tasks
- Phase 10 (Streaming): 8 tasks
- Phase 11 (Polish): 12 tasks

**Parallel Opportunities**: 35+ tasks marked [P] can run in parallel within their phase

**Independent Test Criteria**:
- US1: Send "remind me to X" → verify task created
- US2: Ask "what are my tasks?" → verify list returned
- US3: Say "I finished X" → verify task marked complete
- US4: Say "change X to Y" → verify task updated
- US5: Say "delete X" → verify task removed
- US6: Multi-turn conversation → verify context maintained

**MVP Scope**: Phases 1-4 + Phase 9 (basic) = 30 tasks for minimal viable product

---

## Notes

- [P] tasks = different files, no dependencies within phase
- [US#] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Tests not included per specification (no explicit test request)
- All file paths use backend/ and frontend/ prefixes per plan.md structure
- MCP tools enforce user_id scoping via AgentService wrapper pattern
- Agent uses GPT-4o-mini model per research.md decision
- Streaming uses SSE per research.md decision
