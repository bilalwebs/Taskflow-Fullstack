---
id: 001
title: Create KIro Todo Constitution
stage: constitution
date: 2026-02-02
surface: agent
model: claude-sonnet-4-5-20250929
feature: none
branch: master
user: user
command: /sp.constitution
labels: ["constitution", "project-setup", "governance", "security", "spec-driven"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - .specify/memory/constitution.md
tests:
  - none
---

## Prompt

Project: Todo Full-Stack Web Application

Objective:
Transform an existing console-based Todo application into a secure, multi-user, production-grade full-stack web application using a purely spec-driven, agentic development workflow.

Core Principles:
- Spec-Driven Development: All implementation must strictly follow approved specs
- Single Source of Truth: Specs override assumptions, comments, or prior behavior
- Security First: Authentication, authorization, and user isolation are non-negotiable
- Deterministic Output: Same specs must always yield the same behavior
- Full-Stack Consistency: Frontend, backend, and database behavior must align
- Zero Manual Coding: All implementation is performed via Claude Code agents

Key Standards:
- Every feature must be traceable to a written specification
- No undocumented behavior or "implicit logic" is allowed
- All API behavior must be explicitly defined in specs
- User data must always be scoped to the authenticated user
- Errors must be intentional, documented, and predictable
- Environment variables must be used for secrets and configuration
- Code must be production-safe (no hardcoded secrets, no debug logic)

Architecture Constraints:
- Frontend: Next.js 16+ using App Router
- Backend: Python FastAPI
- ORM: SQLModel
- Database: Neon Serverless PostgreSQL
- Authentication: Better Auth (Frontend) + JWT verification (Backend)
- Repository: Monorepo with GitHub Spec-Kit structure
- Communication: RESTful APIs over HTTP with JSON

Authentication & Security Rules:
- All API endpoints require a valid JWT token
- JWT must be verified on every request in the backend
- User identity must be extracted from the JWT, not from client input
- Backend must reject requests where URL user_id does not match JWT user
- Requests without valid tokens must return 401 Unauthorized
- Task ownership must be enforced on every CRUD operation
- JWT secret must be shared via environment variable (BETTER_AUTH_SECRET)

API Standards:
- RESTful design with clear HTTP methods
- Predictable status codes (200, 201, 400, 401, 403, 404)
- JSON request/response bodies only
- No frontend-only business logic
- Backend is the source of truth for validation and authorization

Database Standards:
- All persistence must use SQLModel
- Schema must match specs exactly
- Foreign key relationships must enforce user ownership
- No direct database access from frontend
- Migrations or schema changes must be reflected in specs first

Frontend Standards:
- Responsive UI (desktop + mobile)
- Clear loading, empty, and error states
- JWT must be attached to every API request
- API calls must go through a centralized client
- UI must never assume success without backend confirmation

Spec-Kit Rules:
- Specs live under /specs and follow Spec-Kit conventions
- Features, API, database, and UI specs must be separate and referenced
- Specs are referenced using @specs/... paths
- Any change in behavior requires a spec update before implementation

Constraints:
- Phase: Hackathon Phase II (Web Application)
- Features: Task CRUD operations with multi-user support

## Response snapshot

Created KIro Todo Full-Stack Web Application Constitution v1.0.0

**Core Principles Established:**
1. Spec-Driven Development (NON-NEGOTIABLE) - Single source of truth
2. Security First (NON-NEGOTIABLE) - JWT auth, user isolation mandatory
3. Deterministic Output - Reproducible behavior across environments
4. Full-Stack Consistency - Frontend/backend/database alignment
5. Zero Manual Coding - All work via Claude Code agents
6. Test-First Development - Red-Green-Refactor cycle
7. Production Safety - No hardcoded secrets, env vars only

**Key Sections:**
- Architecture Constraints: Defined mandatory tech stack (Next.js 16+, FastAPI, SQLModel, Neon PostgreSQL, Better Auth)
- Authentication & Security Rules: Complete JWT token flow with 6-step process
- API Standards: RESTful design with predictable status codes
- Database Standards: SQLModel requirements with data isolation rules
- Frontend Standards: Next.js App Router with component guidelines
- Development Workflow: Agentic Dev Stack (specify → plan → tasks → implement)
- Governance: Amendment process and compliance review

**Template Consistency:**
✅ spec-template.md - Aligned with user story priorities
✅ plan-template.md - Aligned with constitution check gates
✅ tasks-template.md - Aligned with user story organization

**File Created:** `.specify/memory/constitution.md`

## Outcome

- ✅ Impact: Established foundational governance document for entire project. All future development must comply with these principles.
- 🧪 Tests: N/A (governance document)
- 📁 Files: Created .specify/memory/constitution.md (257 lines)
- 🔁 Next prompts: /sp.specify to create first feature specification following constitution principles
- 🧠 Reflection: Constitution successfully captures all project requirements including security-first approach, mandatory JWT authentication, and agent delegation rules. Ready for feature specification phase.

## Evaluation notes (flywheel)

- Failure modes observed: None - constitution created successfully on first attempt
- Graders run and results (PASS/FAIL): PASS - All placeholders filled, no template tokens remaining, version semantics correct
- Prompt variant (if applicable): N/A (initial creation)
- Next experiment (smallest change to try): Validate constitution compliance during first feature specification creation
