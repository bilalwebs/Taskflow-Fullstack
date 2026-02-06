# Implementation Plan: Multi-User Todo Web Application

**Branch**: `001-multi-user-todo-app` | **Date**: 2026-02-02 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-multi-user-todo-app/spec.md`

## Summary

Transform a console-based Todo application into a secure, multi-user web application with JWT-based authentication and complete user data isolation. Users can create accounts, sign in, and manage their personal tasks (create, read, update, delete, complete) through a responsive web interface. All API endpoints enforce authentication and authorization, ensuring users can only access their own data.

**Technical Approach**: Monorepo architecture with Next.js frontend (App Router) and FastAPI backend, connected via RESTful JSON APIs. Better Auth handles frontend authentication with JWT tokens. Backend verifies JWTs on every request and enforces user-scoped database queries using SQLModel ORM with Neon Serverless PostgreSQL.

## Technical Context

**Language/Version**: Python 3.11+ (backend), TypeScript/JavaScript (frontend with Next.js 16+)
**Primary Dependencies**: FastAPI, SQLModel, psycopg2-binary, python-jose (backend); Next.js 16+, Better Auth, React 19+ (frontend)
**Storage**: Neon Serverless PostgreSQL (cloud-hosted, connection pooling built-in)
**Testing**: pytest (backend), Jest/React Testing Library (frontend)
**Target Platform**: Web browsers (desktop and mobile), deployed on cloud platforms (Vercel for frontend, cloud hosting for backend)
**Project Type**: Web application (frontend + backend monorepo)
**Performance Goals**: <2s task list load, <1s user action feedback, <200ms API response p95
**Constraints**: JWT verification on 100% of protected endpoints, complete user data isolation, responsive design 320px-1920px
**Scale/Scope**: Support up to 1000 tasks per user, designed for hackathon demonstration and judge review

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### ✅ Principle I: Spec-Driven Development
- **Status**: PASS
- **Evidence**: All implementation decisions traced to spec.md functional requirements (FR-001 through FR-024)
- **Verification**: No undocumented features; all behavior defined in spec

### ✅ Principle II: Security First
- **Status**: PASS
- **Evidence**: JWT verification mandatory (FR-006), user identity from token only (FR-007), ownership enforcement (FR-010, FR-012, FR-014)
- **Verification**: API contracts will include authentication requirements; data model enforces user_id foreign keys

### ✅ Principle III: Deterministic Output
- **Status**: PASS
- **Evidence**: Specs define exact behavior for all scenarios; no random or environment-dependent logic
- **Verification**: Success criteria SC-004 requires 100% JWT verification; SC-005 requires 0% cross-user access

### ✅ Principle IV: Full-Stack Consistency
- **Status**: PASS
- **Evidence**: API contracts will be defined before implementation; backend validates all inputs; frontend displays backend errors
- **Verification**: Contracts will specify request/response schemas; both layers implement same validation rules

### ✅ Principle V: Zero Manual Coding
- **Status**: PASS
- **Evidence**: Implementation via Claude Code agents (auth-skill, frontend-skill, database-skill, backend-skill)
- **Verification**: Tasks.md will assign work to appropriate agents

### ✅ Principle VI: Test-First Development
- **Status**: N/A (tests not requested in spec)
- **Evidence**: Spec does not require tests; acceptance scenarios defined for manual validation
- **Verification**: Each user story has independent test criteria

### ✅ Principle VII: Production Safety
- **Status**: PASS
- **Evidence**: Environment variables for secrets (FR-017 password hashing, JWT secret via BETTER_AUTH_SECRET), parameterized queries via SQLModel
- **Verification**: No hardcoded credentials; .env files in .gitignore

### Technology Stack Compliance

| Requirement | Specified | Compliant |
|-------------|-----------|-----------|
| Frontend | Next.js 16+ App Router | ✅ |
| Backend | Python FastAPI | ✅ |
| ORM | SQLModel | ✅ |
| Database | Neon Serverless PostgreSQL | ✅ |
| Authentication | Better Auth + JWT | ✅ |
| Repository | Monorepo with Spec-Kit | ✅ |
| Communication | RESTful JSON APIs | ✅ |

**Gate Result**: ✅ PASS - All principles satisfied, no violations to justify

## Project Structure

### Documentation (this feature)

```text
specs/001-multi-user-todo-app/
├── spec.md              # Feature requirements (COMPLETE)
├── plan.md              # This file (IN PROGRESS)
├── research.md          # Phase 0 output (PENDING)
├── data-model.md        # Phase 1 output (PENDING)
├── quickstart.md        # Phase 1 output (PENDING)
├── contracts/           # Phase 1 output (PENDING)
│   ├── auth.yaml       # Authentication endpoints
│   └── tasks.yaml      # Task CRUD endpoints
├── checklists/
│   └── requirements.md  # Spec validation (COMPLETE)
└── tasks.md             # Phase 2 output via /sp.tasks (NOT YET)
```

### Source Code (repository root)

```text
backend/
├── src/
│   ├── main.py              # FastAPI application entry point
│   ├── config.py            # Environment configuration
│   ├── database.py          # Database connection and session management
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py          # User SQLModel
│   │   └── task.py          # Task SQLModel
│   ├── middleware/
│   │   ├── __init__.py
│   │   └── auth.py          # JWT verification middleware
│   ├── api/
│   │   ├── __init__.py
│   │   ├── auth.py          # Authentication endpoints (if needed)
│   │   └── tasks.py         # Task CRUD endpoints
│   └── schemas/
│       ├── __init__.py
│       ├── task.py          # Pydantic request/response schemas
│       └── error.py         # Error response schemas
├── tests/
│   ├── test_auth.py
│   └── test_tasks.py
├── requirements.txt         # Python dependencies
├── .env.example            # Environment variable template
└── README.md               # Backend setup instructions

frontend/
├── src/
│   ├── app/
│   │   ├── layout.tsx       # Root layout
│   │   ├── page.tsx         # Home/landing page
│   │   ├── signup/
│   │   │   └── page.tsx     # Signup page
│   │   ├── signin/
│   │   │   └── page.tsx     # Signin page
│   │   └── dashboard/
│   │       └── page.tsx     # Task list and management
│   ├── components/
│   │   ├── TaskList.tsx     # Task list display
│   │   ├── TaskItem.tsx     # Individual task component
│   │   ├── TaskForm.tsx     # Create/edit task form
│   │   └── AuthForm.tsx     # Reusable auth form
│   ├── lib/
│   │   ├── api-client.ts    # Centralized API client with JWT
│   │   ├── auth.ts          # Better Auth configuration
│   │   └── types.ts         # TypeScript types
│   └── styles/
│       └── globals.css      # Global styles
├── public/
├── tests/
├── package.json
├── tsconfig.json
├── next.config.js
├── .env.local.example
└── README.md

.specify/                    # Spec-Kit Plus framework (existing)
history/                     # Development records (existing)
.gitignore
README.md                    # Project overview
```

**Structure Decision**: Web application monorepo selected based on constitution requirements. Frontend and backend are isolated in separate directories with their own dependencies, tests, and configuration. This enables independent development by specialized agents while maintaining clear API contracts between layers.

## Complexity Tracking

> No violations detected - all constitution principles satisfied without exceptions.

---

## Phase 0: Research ✅ COMPLETE

Research completed and documented in `research.md`:
1. ✅ Better Auth JWT configuration for Next.js 16+
2. ✅ FastAPI JWT verification best practices with python-jose
3. ✅ SQLModel relationship patterns for user-owned resources
4. ✅ Neon Serverless PostgreSQL connection pooling
5. ✅ Next.js App Router authentication patterns
6. ✅ Error handling standards for RESTful APIs

**Output**: `research.md` (6 technical decisions documented with rationale)

## Phase 1: Design ✅ COMPLETE

Design artifacts generated:
1. ✅ `data-model.md` - User and Task entity definitions with relationships, validation rules, and security patterns
2. ✅ `contracts/tasks.yaml` - OpenAPI 3.0 specification for Task CRUD endpoints with JWT authentication
3. ✅ `quickstart.md` - Complete local development setup guide with troubleshooting

**Output**: `data-model.md`, `contracts/tasks.yaml`, `quickstart.md`

**Note**: Authentication API contract (auth.yaml) not needed - Better Auth handles signup/signin on frontend, backend only verifies JWT tokens.

## Post-Design Constitution Re-Check ✅ PASS

All principles remain satisfied after design phase:

- **Principle I (Spec-Driven)**: All design artifacts trace to spec.md requirements ✅
- **Principle II (Security First)**: Data model enforces user_id foreign keys, API contracts require JWT on all endpoints, query patterns filter by user_id ✅
- **Principle III (Deterministic)**: No random behavior in design; all responses defined in contracts ✅
- **Principle IV (Full-Stack Consistency)**: API contracts define exact request/response schemas for both layers ✅
- **Principle V (Zero Manual Coding)**: Design ready for agent implementation ✅
- **Principle VI (Test-First)**: N/A (tests not in spec) ✅
- **Principle VII (Production Safety)**: Environment variables for secrets, parameterized queries via SQLModel ✅

**Gate Result**: ✅ PASS - Design phase complete, ready for task generation

---

## Next Steps

Run `/sp.tasks` to generate implementation tasks based on these design artifacts. Tasks will be assigned to specialized agents:
- **auth-skill**: User authentication and JWT verification
- **database-skill**: SQLModel entities and database setup
- **backend-skill**: FastAPI endpoints and business logic
- **frontend-skill**: Next.js pages, components, and API integration
