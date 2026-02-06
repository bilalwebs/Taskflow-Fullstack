# Implementation Tasks: Multi-User Todo Web Application

**Feature**: Multi-User Todo Web Application
**Branch**: `001-multi-user-todo-app`
**Spec**: [spec.md](./spec.md) | **Plan**: [plan.md](./plan.md)
**Generated**: 2026-02-02

## Overview

This document contains actionable implementation tasks organized by user story. Each phase represents a complete, independently testable increment of functionality. Tasks are assigned to specialized agents (auth-skill, database-skill, backend-skill, frontend-skill) based on their domain expertise.

**Total Tasks**: 45
**Estimated Phases**: 6
**MVP Scope**: Phase 3 (User Story 1 - Authentication)

---

## Phase 1: Project Setup & Infrastructure

**Goal**: Initialize monorepo structure with backend and frontend projects, configure development environment, and set up foundational tooling.

**Tasks**:

- [x] T001 Create backend directory structure per plan.md at backend/src/
- [x] T002 Create frontend directory structure per plan.md at frontend/src/
- [x] T003 [P] Create backend requirements.txt with FastAPI, SQLModel, psycopg2-binary, python-jose[cryptography], passlib[bcrypt], python-dotenv, pydantic-settings, uvicorn[standard]
- [x] T004 [P] Create frontend package.json with next@16+, react@19+, react-dom@19+, better-auth, typescript, @types/node, @types/react, tailwindcss
- [x] T005 [P] Create backend .env.example with DATABASE_URL, JWT_SECRET, BETTER_AUTH_SECRET, JWT_ALGORITHM, JWT_EXPIRATION_HOURS, CORS_ORIGINS, ENVIRONMENT, DEBUG
- [x] T006 [P] Create frontend .env.local.example with NEXT_PUBLIC_API_URL, BETTER_AUTH_SECRET, BETTER_AUTH_URL, NODE_ENV
- [x] T007 [P] Create backend .gitignore with venv/, __pycache__/, .env, *.pyc, .pytest_cache/
- [x] T008 [P] Create frontend .gitignore with node_modules/, .next/, .env.local, out/, build/
- [x] T009 [P] Create root README.md with project overview and quickstart instructions
- [x] T010 [P] Create backend README.md with setup instructions from quickstart.md
- [x] T011 [P] Create frontend README.md with setup instructions from quickstart.md

**Acceptance**: Backend and frontend directories exist with proper structure, dependency files, environment templates, and documentation. Both projects can be initialized (pip install, npm install) without errors.

---

## Phase 2: Foundational Layer (Blocking Prerequisites)

**Goal**: Implement core infrastructure that all user stories depend on: database connection, configuration management, and error handling schemas.

**Tasks**:

- [x] T012 [P] Create backend/src/config.py with Pydantic Settings for environment variables (DATABASE_URL, JWT_SECRET, CORS_ORIGINS, etc.)
- [x] T013 Create backend/src/database.py with SQLModel engine creation, session management, and init_db() function
- [x] T014 [P] Create backend/src/schemas/__init__.py (empty module initializer)
- [x] T015 [P] Create backend/src/schemas/error.py with ErrorResponse Pydantic model (error, message, details fields)
- [x] T016 Create backend/src/main.py with FastAPI app initialization, CORS middleware configuration, and health check endpoint
- [x] T017 [P] Create frontend/src/lib/types.ts with TypeScript interfaces for User, Task, ApiError
- [x] T018 [P] Create frontend/next.config.js with basic Next.js configuration
- [x] T019 [P] Create frontend/tsconfig.json with TypeScript compiler options for Next.js App Router

**Acceptance**: Backend server starts successfully with CORS configured. Database connection can be established. Configuration loads from environment variables. TypeScript types are defined for frontend.

**Dependencies**: None (foundational layer)

---

## Phase 3: User Story 1 - User Authentication (P1) 🎯 MVP

**User Story**: Users need to create accounts and securely sign in to access their personal todo lists. Each user must have their own isolated workspace where only they can see and manage their tasks.

**Independent Test Criteria**:
- ✅ New user can create account with valid email and password
- ✅ Existing user can sign in with correct credentials
- ✅ User receives error message for invalid credentials
- ✅ JWT token is issued on successful authentication
- ✅ Weak passwords are rejected with helpful guidance
- ✅ Authentication token expires appropriately

**Agent Assignment**: auth-skill (authentication), database-skill (User model), backend-skill (JWT middleware), frontend-skill (auth pages)

### Backend - Database Layer

- [x] T020 [US1] Create backend/src/models/__init__.py (empty module initializer)
- [x] T021 [US1] Create backend/src/models/user.py with User SQLModel (id, email, password_hash, created_at) per data-model.md
- [ ] T022 [US1] Run database initialization to create users table (execute init_db() from database.py)

### Backend - Authentication & Middleware

- [x] T023 [US1] Create backend/src/middleware/__init__.py (empty module initializer)
- [x] T024 [US1] Create backend/src/middleware/auth.py with JWT verification dependency (get_current_user) using python-jose per research.md
- [x] T025 [US1] Add HTTPException handler to backend/src/main.py for consistent error responses using ErrorResponse schema

### Frontend - Authentication Setup

- [x] T026 [P] [US1] Create frontend/src/lib/auth.ts with Better Auth configuration (JWT enabled, session settings) per research.md
- [x] T027 [P] [US1] Create frontend/src/lib/api-client.ts with centralized API client that attaches JWT tokens to requests
- [x] T028 [P] [US1] Create frontend/src/app/layout.tsx with root layout and Better Auth provider

### Frontend - Authentication Pages

- [x] T029 [P] [US1] Create frontend/src/app/page.tsx with landing page and navigation to signup/signin
- [x] T030 [US1] Create frontend/src/components/AuthForm.tsx with reusable form component for email/password input and validation
- [x] T031 [US1] Create frontend/src/app/signup/page.tsx using AuthForm component with Better Auth signup integration
- [x] T032 [US1] Create frontend/src/app/signin/page.tsx using AuthForm component with Better Auth signin integration

### Integration & Validation

- [ ] T033 [US1] Test complete authentication flow: signup → signin → JWT token issuance → token verification
- [ ] T034 [US1] Verify password strength validation rejects weak passwords with helpful error messages
- [ ] T035 [US1] Verify invalid credentials return appropriate error messages

**Phase Completion Criteria**:
- ✅ Users can create accounts via signup page
- ✅ Users can sign in via signin page
- ✅ JWT tokens are issued and stored securely
- ✅ Backend verifies JWT tokens on protected endpoints
- ✅ Password validation enforces strength requirements
- ✅ Error messages are clear and helpful

**Dependencies**: Phase 2 (Foundational Layer) must be complete

---

## Phase 4: User Story 2 - Task Management (P2)

**User Story**: Users need to create, view, update, and delete their personal tasks. Each task should have a title and description. Users must only be able to access their own tasks, never seeing or modifying tasks belonging to other users.

**Independent Test Criteria**:
- ✅ Authenticated user can create task with title and description
- ✅ User sees only their own tasks in task list
- ✅ User can edit their own task's title and description
- ✅ User can delete their own task
- ✅ User cannot view, edit, or delete another user's tasks
- ✅ Task creation without title shows validation error

**Agent Assignment**: database-skill (Task model), backend-skill (Task API), frontend-skill (Task UI)

### Backend - Database Layer

- [x] T036 [US2] Create backend/src/models/task.py with Task SQLModel (id, title, description, completed, user_id, created_at, updated_at) per data-model.md
- [x] T037 [US2] Update backend/src/models/user.py to add tasks relationship (back_populates="owner")
- [x] T038 [US2] Run database migration to create tasks table with foreign key to users

### Backend - API Schemas

- [x] T039 [P] [US2] Create backend/src/schemas/task.py with TaskCreate, TaskUpdate, and TaskResponse Pydantic models per contracts/tasks.yaml

### Backend - API Endpoints

- [x] T040 [US2] Create backend/src/api/__init__.py (empty module initializer)
- [x] T041 [US2] Create backend/src/api/tasks.py with GET /api/tasks endpoint (list user's tasks, filtered by user_id from JWT)
- [x] T042 [US2] Add POST /api/tasks endpoint to backend/src/api/tasks.py (create task with user_id from JWT)
- [x] T043 [US2] Add GET /api/tasks/{task_id} endpoint to backend/src/api/tasks.py (verify ownership before returning)
- [x] T044 [US2] Add PUT /api/tasks/{task_id} endpoint to backend/src/api/tasks.py (verify ownership before updating)
- [x] T045 [US2] Add DELETE /api/tasks/{task_id} endpoint to backend/src/api/tasks.py (verify ownership before deleting)
- [x] T046 [US2] Register task router in backend/src/main.py with /api prefix

### Frontend - Task Components

- [x] T047 [P] [US2] Create frontend/src/components/TaskItem.tsx with individual task display (title, description, edit/delete buttons)
- [x] T048 [P] [US2] Create frontend/src/components/TaskForm.tsx with form for creating/editing tasks (title and description inputs)
- [x] T049 [US2] Create frontend/src/components/TaskList.tsx with task list display using TaskItem components

### Frontend - Dashboard Page

- [x] T050 [US2] Create frontend/src/app/dashboard/page.tsx with authentication check, TaskList component, and TaskForm component
- [x] T051 [US2] Add loading states to frontend/src/app/dashboard/page.tsx while fetching tasks
- [x] T052 [US2] Add empty state to frontend/src/components/TaskList.tsx when user has no tasks
- [x] T053 [US2] Add error states to frontend/src/app/dashboard/page.tsx for failed API requests

### Integration & Validation

- [ ] T054 [US2] Test task creation flow: create task → verify appears in list → verify persisted in database
- [ ] T055 [US2] Test task update flow: edit task → verify changes saved → verify updated_at timestamp changes
- [ ] T056 [US2] Test task deletion flow: delete task → verify removed from list → verify removed from database
- [ ] T057 [US2] Test data isolation: create two users → verify User A cannot see User B's tasks
- [ ] T058 [US2] Test authorization: attempt to access another user's task by ID → verify 403 Forbidden response

**Phase Completion Criteria**:
- ✅ Users can create tasks with title and description
- ✅ Users see only their own tasks
- ✅ Users can edit their own tasks
- ✅ Users can delete their own tasks
- ✅ Complete data isolation between users
- ✅ Validation errors display for invalid input
- ✅ Loading and empty states work correctly

**Dependencies**: Phase 3 (User Story 1) must be complete (requires authentication)

---

## Phase 5: User Story 3 - Task Completion Tracking (P3)

**User Story**: Users need to mark tasks as complete or incomplete to track their progress. Completed tasks should be visually distinguishable from incomplete tasks, helping users understand what work remains.

**Independent Test Criteria**:
- ✅ User can mark incomplete task as complete
- ✅ User can mark completed task as incomplete
- ✅ Completed and incomplete tasks are visually distinct
- ✅ New tasks default to incomplete status
- ✅ Completion status persists across sessions

**Agent Assignment**: backend-skill (completion endpoint), frontend-skill (completion UI)

### Backend - Completion Logic

- [x] T059 [US3] Add PATCH /api/tasks/{task_id}/complete endpoint to backend/src/api/tasks.py (toggle completed status, verify ownership)
- [x] T060 [US3] Ensure Task model completed field defaults to False in backend/src/models/task.py

### Frontend - Completion UI

- [x] T061 [US3] Add completion checkbox to frontend/src/components/TaskItem.tsx with toggle handler
- [x] T062 [US3] Add visual styling to frontend/src/components/TaskItem.tsx to distinguish completed tasks (strikethrough, opacity, color)
- [x] T063 [US3] Update frontend/src/lib/api-client.ts to add toggleTaskComplete method

### Integration & Validation

- [x] T064 [US3] Test completion toggle: mark task complete → verify visual change → verify persisted in database
- [x] T065 [US3] Test incomplete toggle: mark completed task incomplete → verify visual change → verify persisted
- [x] T066 [US3] Verify new tasks default to incomplete status

**Phase Completion Criteria**:
- ✅ Users can toggle task completion status
- ✅ Completed tasks are visually distinct
- ✅ Completion status persists correctly
- ✅ New tasks start as incomplete

**Dependencies**: Phase 4 (User Story 2) must be complete (requires task management)

---

## Phase 6: Polish & Cross-Cutting Concerns

**Goal**: Add responsive design, improve error handling, add global styles, and ensure production readiness.

**Tasks**:

- [x] T067 [P] Create frontend/src/styles/globals.css with base styles and responsive breakpoints (320px-1920px)
- [x] T068 [P] Add responsive design to frontend/src/components/TaskList.tsx for mobile and desktop views
- [x] T069 [P] Add responsive design to frontend/src/components/TaskForm.tsx for mobile and desktop views
- [x] T070 [P] Add responsive navigation to frontend/src/app/layout.tsx with sign out button
- [x] T071 [P] Improve error messages in backend/src/api/tasks.py to be user-friendly per research.md error handling standards
- [x] T072 [P] Add input validation feedback to frontend/src/components/TaskForm.tsx (character counts, required field indicators)
- [x] T073 [P] Add loading spinners to frontend/src/components/TaskList.tsx during API operations
- [ ] T074 Test responsive design on multiple screen sizes (320px, 768px, 1024px, 1920px)
- [ ] T075 Verify all error messages are user-friendly and actionable

**Phase Completion Criteria**:
- ✅ Application works on all screen sizes (320px-1920px)
- ✅ Error messages are clear and helpful
- ✅ Loading states provide feedback during operations
- ✅ UI is polished and professional

**Dependencies**: Phases 3, 4, 5 must be complete

---

## Task Dependencies & Execution Order

### Critical Path (Must Complete in Order)

1. **Phase 1** (Setup) → **Phase 2** (Foundational) → **Phase 3** (US1 Auth)
2. **Phase 3** (US1 Auth) → **Phase 4** (US2 Task Management)
3. **Phase 4** (US2 Task Management) → **Phase 5** (US3 Completion)
4. **Phases 3, 4, 5** → **Phase 6** (Polish)

### User Story Dependencies

- **US1 (Authentication)**: No dependencies (can start after Phase 2)
- **US2 (Task Management)**: Depends on US1 (requires authentication)
- **US3 (Completion)**: Depends on US2 (requires task management)

### Parallel Execution Opportunities

**Within Phase 1 (Setup)**:
- T003, T004, T005, T006, T007, T008, T009, T010, T011 can all run in parallel

**Within Phase 2 (Foundational)**:
- T012, T014, T015, T017, T018, T019 can run in parallel after T013

**Within Phase 3 (US1)**:
- T026, T027, T028, T029 can run in parallel after T024
- T030, T031, T032 can run in parallel after T030

**Within Phase 4 (US2)**:
- T039, T047, T048 can run in parallel
- T041-T045 can be implemented in parallel (different endpoints)

**Within Phase 5 (US3)**:
- T061, T062, T063 can run in parallel after T059

**Within Phase 6 (Polish)**:
- T067, T068, T069, T070, T071, T072, T073 can all run in parallel

---

## Implementation Strategy

### MVP Delivery (Phase 3 Only)

For fastest time-to-value, implement only Phase 3 (User Authentication) first:
- Users can create accounts and sign in
- JWT authentication is working
- Foundation is ready for task management

**MVP Tasks**: T001-T035 (35 tasks)
**Estimated Effort**: Foundational implementation

### Incremental Delivery

After MVP, deliver each user story as a complete increment:
1. **Increment 1** (MVP): Authentication working
2. **Increment 2**: Add Task Management (Phase 4)
3. **Increment 3**: Add Completion Tracking (Phase 5)
4. **Increment 4**: Polish & Production Ready (Phase 6)

### Agent Assignments

- **auth-skill**: T024, T026, T027, T031, T032, T033, T034, T035
- **database-skill**: T013, T021, T022, T036, T037, T038
- **backend-skill**: T012, T016, T025, T040-T046, T059, T060, T071
- **frontend-skill**: T002, T004, T006, T008, T011, T017-T019, T028-T032, T047-T053, T061-T063, T067-T070, T072-T075

---

## Validation Checklist

Before marking this feature complete, verify:

- [ ] All 75 tasks completed and checked off
- [ ] All user stories have passing acceptance scenarios
- [ ] Constitution principles validated (security, spec-driven, deterministic)
- [ ] Success criteria met (SC-001 through SC-010 from spec.md)
- [ ] Data isolation verified (0% cross-user access)
- [ ] JWT verification on 100% of protected endpoints
- [ ] Responsive design works 320px-1920px
- [ ] All error states handled gracefully
- [ ] Documentation updated (README files)
- [ ] Environment variable templates complete

---

## Notes

- **Tests**: Not included per spec.md (tests not requested). Manual validation via acceptance scenarios.
- **Parallelization**: 30+ tasks marked [P] can run in parallel within their phase
- **File Paths**: All tasks include specific file paths for clarity
- **Agent Specialization**: Tasks assigned to appropriate specialized agents
- **Independent Stories**: Each user story can be tested independently
- **Security**: JWT verification and data isolation enforced throughout
