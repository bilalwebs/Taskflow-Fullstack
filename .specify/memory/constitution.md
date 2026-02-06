<!--
Sync Impact Report:
- Version Change: 1.0.0 → 1.1.0 (Phase III: AI-Native Architecture)
- Modified Principles:
  - Principle II: Security First - Extended to include MCP tool authorization
  - Principle IV: Full-Stack Consistency - Extended to include AI agent layer
- Added Sections:
  - Principle VIII: Agent-First Design (NEW)
  - Principle IX: Tool-Mediated State Changes (NEW)
  - Principle X: Stateless Execution (NEW)
  - MCP Tooling Standards (NEW)
  - AI Agent Standards (NEW)
  - Conversation Persistence Standards (NEW)
  - Phase III Architecture Constraints (NEW)
- Removed Sections: None
- Templates Status:
  ✅ spec-template.md - Requires update for Phase III features
  ✅ plan-template.md - Requires update for MCP tool planning
  ✅ tasks-template.md - Requires update for agent/tool task types
- Follow-up TODOs:
  - Update spec template to include conversational interface patterns
  - Update plan template to include MCP tool design phase
  - Update tasks template to include tool implementation tasks
-->

# KIro Todo Full-Stack Web Application Constitution

## Core Principles

### I. Spec-Driven Development (NON-NEGOTIABLE)

All implementation MUST strictly follow approved specifications. Specs are the single source of truth and override assumptions, comments, or prior behavior. Every feature MUST be traceable to a written specification. No undocumented behavior or "implicit logic" is allowed.

**Rationale**: Ensures predictable, auditable development where all stakeholders understand what is being built and why.

### II. Security First (NON-NEGOTIABLE)

Authentication, authorization, and user data isolation are mandatory for all features. All API endpoints MUST require valid JWT tokens. User identity MUST be extracted from JWT, never from client input. Backend MUST reject requests where URL user_id does not match JWT user. Task ownership MUST be enforced on every CRUD operation. MCP tools MUST enforce user_id scoping at tool boundaries.

**Rationale**: Multi-user applications require strict security boundaries to prevent unauthorized data access and maintain user trust. AI agents must not bypass security controls.

### III. Deterministic Output

Same specifications MUST always yield the same behavior across all environments. Implementation MUST be reproducible and predictable. Errors MUST be intentional, documented, and predictable. No random or environment-dependent behavior unless explicitly specified. MCP tools MUST be deterministic and return consistent results for identical inputs.

**Rationale**: Enables reliable testing, debugging, and deployment. Reduces production incidents caused by environmental differences. Critical for AI agent reliability.

### IV. Full-Stack Consistency

Frontend, backend, AI agent layer, and database behavior MUST align with specifications. API contracts MUST be explicitly defined and followed by all layers. Backend is the source of truth for validation and authorization. No frontend-only or agent-only business logic is permitted. AI agents MUST rely on tool responses, not hallucinated state.

**Rationale**: Prevents drift between layers that leads to bugs, security vulnerabilities, and maintenance nightmares. Ensures AI agents operate on factual data.

### V. Zero Manual Coding

All implementation MUST be performed via Claude Code agents using the Agentic Dev Stack workflow. Manual coding is prohibited. Agents MUST be used for their specialized domains (auth-skill, frontend-skill, database-skill, backend-skill).

**Rationale**: Ensures consistent code quality, adherence to patterns, and leverages specialized agent expertise for each domain.

### VI. Test-First Development

When tests are requested in specifications, they MUST be written first, approved by user, and verified to fail before implementation begins. Red-Green-Refactor cycle MUST be followed. Each user story MUST be independently testable.

**Rationale**: Prevents implementation drift from requirements and ensures features work as specified before being marked complete.

### VII. Production Safety

Code MUST be production-safe at all times. No hardcoded secrets or tokens. All configuration MUST use environment variables. No debug logic in production code. All database queries MUST use parameterized statements to prevent SQL injection. AI prompts MUST NOT expose sensitive user data beyond required context.

**Rationale**: Protects against security breaches, data leaks, and production incidents caused by development artifacts.

### VIII. Agent-First Design (Phase III)

All business actions MUST be initiated by AI agents via MCP tools. AI agents MUST select tools based on user intent, not hard-coded rules. Agent responses MUST confirm actions in natural language. Agents MUST gracefully handle ambiguity, missing data, and errors. Agents MUST never hallucinate task state or IDs.

**Rationale**: Enables natural language interaction while maintaining system integrity. Ensures AI decisions are auditable and user-friendly.

### IX. Tool-Mediated State Changes (Phase III)

AI agents MUST never mutate state directly. All task operations MUST be exposed as MCP tools. MCP tools MUST be the exclusive interface for data mutations. Tools MUST enforce user ownership and authorization. Tools MUST return structured results suitable for agent reasoning.

**Rationale**: Separates AI reasoning from data persistence, enabling stateless architecture and preventing unauthorized state changes.

### X. Stateless Execution (Phase III)

Server MUST have no in-memory state between requests. Chat endpoint MUST reconstruct context from persisted conversation history. System MUST remain restart-safe with no dependencies on server memory. All conversation state MUST be persisted in database before and after agent execution.

**Rationale**: Enables horizontal scaling, fault tolerance, and predictable behavior. Critical for production reliability.

## Architecture Constraints

### Technology Stack (MANDATORY)

**Phases I-II (REST API + Traditional Frontend):**
- **Frontend**: Next.js 16+ using App Router only
- **Backend**: Python FastAPI
- **ORM**: SQLModel for all database operations
- **Database**: Neon Serverless PostgreSQL
- **Authentication**: Better Auth (Frontend) + JWT verification (Backend)
- **Repository Structure**: Monorepo with Spec-Kit Plus structure
- **Communication**: RESTful APIs over HTTP with JSON payloads

**Phase III (AI-Native Conversational Interface):**
- **AI Framework**: OpenAI Agents SDK (exclusive)
- **Tool Protocol**: Official MCP SDK
- **Frontend**: OpenAI ChatKit for conversational UI
- **Backend**: FastAPI with stateless chat endpoint
- **Persistence**: SQLModel for conversation history and messages
- **Communication**: Single chat endpoint with message streaming

**Rationale**: Standardized stack ensures agent expertise applies consistently and reduces integration complexity. Phase III adds AI capabilities without replacing existing REST infrastructure.

### Project Structure (MANDATORY)

```
specs/                          # Feature specifications
  └── [###-feature]/
      ├── spec.md              # Requirements and user stories
      ├── plan.md              # Architecture decisions
      ├── tasks.md             # Implementation tasks
      ├── research.md          # Technical research
      ├── data-model.md        # Entity definitions
      ├── contracts/           # API contracts
      └── tools/               # MCP tool specifications (Phase III)

backend/                        # FastAPI application
  ├── src/
  │   ├── models/              # SQLModel entities
  │   ├── services/            # Business logic
  │   ├── api/                 # Route handlers
  │   ├── agents/              # AI agent configurations (Phase III)
  │   └── tools/               # MCP tool implementations (Phase III)
  └── tests/

frontend/                       # Next.js application
  ├── src/
  │   ├── app/                 # App Router pages
  │   ├── components/          # React components
  │   └── lib/                 # Utilities and API client
  └── tests/

.specify/                       # Spec-Kit Plus framework
  ├── memory/
  │   └── constitution.md      # This file
  └── templates/               # Spec templates

history/                        # Development records
  ├── prompts/                 # Prompt History Records
  └── adr/                     # Architecture Decision Records
```

## Authentication & Security Rules

### JWT Token Flow (MANDATORY)

1. **User Login**: User submits credentials → Better Auth validates → Issues JWT token
2. **API Request**: Frontend includes `Authorization: Bearer <token>` header
3. **Token Verification**: Backend extracts and verifies token signature using shared secret
4. **User Identification**: Backend decodes JWT to extract user ID and email
5. **Authorization**: Backend matches JWT user_id with request user_id
6. **Data Filtering**: All queries filter by authenticated user ID

### Security Requirements (MANDATORY)

- All API endpoints MUST verify JWT before processing
- Requests without valid tokens MUST return 401 Unauthorized
- Requests with mismatched user_id MUST return 403 Forbidden
- JWT secret MUST be shared via `BETTER_AUTH_SECRET` environment variable
- Passwords MUST be hashed using bcrypt or argon2
- All secrets MUST be stored in `.env` files (never committed)
- HTTPS MUST be used for all authentication requests in production
- Rate limiting MUST be implemented on authentication endpoints
- **Phase III**: MCP tools MUST validate user_id from JWT context before execution
- **Phase III**: AI agents MUST NOT receive raw JWT tokens or passwords

## API Standards

### RESTful Design (MANDATORY - Phases I-II)

- Use standard HTTP methods: GET (read), POST (create), PUT (update), DELETE (delete)
- Use predictable status codes:
  - 200 OK: Successful GET/PUT/DELETE
  - 201 Created: Successful POST
  - 400 Bad Request: Invalid input
  - 401 Unauthorized: Missing or invalid token
  - 403 Forbidden: Valid token but insufficient permissions
  - 404 Not Found: Resource does not exist
- JSON request and response bodies only
- Consistent error response format with message and error code

### Conversational API Design (MANDATORY - Phase III)

- Single chat endpoint: `POST /api/{user_id}/chat`
- Endpoint MUST support resuming existing conversations via `conversation_id`
- Request body MUST include: `message` (user input), optional `conversation_id`
- Response MUST include: `assistant_message`, `conversation_id`, `tool_calls` (if any)
- Endpoint MUST reconstruct context from database before agent execution
- Endpoint MUST persist user message before agent execution
- Endpoint MUST persist assistant response after agent execution
- Errors MUST be communicated in user-friendly natural language

### API Contract Requirements (MANDATORY)

- All endpoints MUST be documented in `specs/[feature]/contracts/`
- Request/response schemas MUST be explicitly defined
- Error responses MUST be documented
- Backend MUST validate all inputs against contract
- Frontend MUST handle all documented error cases
- **Phase III**: MCP tools MUST have documented input/output schemas

## MCP Tooling Standards (Phase III)

### Tool Design Requirements (MANDATORY)

Each MCP tool MUST have:
- **Clear Purpose**: Single, well-defined responsibility
- **Strict Input Validation**: Typed parameters with validation rules
- **Deterministic Outputs**: Same inputs always produce same results
- **User Scoping**: Enforce user_id from authentication context
- **Structured Results**: Return data suitable for agent reasoning (not raw database objects)
- **Error Handling**: Return actionable error messages for agent interpretation

### Tool Implementation Requirements (MANDATORY)

- Use Official MCP SDK exclusively
- Tools MUST be stateless (no instance variables or caching)
- Tools MUST persist all state changes via database
- Tools MUST NOT depend on conversation history or context
- Tools MUST validate user ownership before mutations
- Tools MUST return success/failure status with descriptive messages
- Tools MUST log all invocations for audit trail

### Required MCP Tools (Phase III)

- `list_tasks`: Retrieve all tasks for authenticated user
- `create_task`: Create new task with title and optional description
- `update_task`: Update existing task (title, description, or completion)
- `delete_task`: Permanently delete task
- `get_task`: Retrieve single task by ID
- `mark_complete`: Toggle task completion status

## AI Agent Standards (Phase III)

### Agent Configuration (MANDATORY)

- Use OpenAI Agents SDK exclusively for AI reasoning
- Agent MUST have access to all MCP tools
- Agent MUST select tools based on user intent analysis
- Agent MUST NOT have hard-coded decision trees
- Agent MUST confirm all actions in natural language
- Agent MUST ask clarifying questions when intent is ambiguous

### Agent Behavior Requirements (MANDATORY)

- Agent MUST rely only on tool responses for factual state
- Agent MUST never hallucinate task IDs, titles, or completion status
- Agent MUST handle tool errors gracefully with user-friendly explanations
- Agent MUST confirm successful operations explicitly
- Agent MUST suggest next actions when appropriate
- Agent MUST respect user privacy (no logging of sensitive content)

### Agent Response Standards (MANDATORY)

- Responses MUST be conversational and natural
- Responses MUST confirm what action was taken
- Responses MUST include relevant task details after operations
- Responses MUST explain errors in user-friendly language
- Responses MUST NOT expose internal system details or stack traces

## Conversation Persistence Standards (Phase III)

### Database Schema Requirements (MANDATORY)

- `conversations` table: id, user_id, created_at, updated_at
- `messages` table: id, conversation_id, role (user/assistant), content, tool_calls, created_at
- Foreign keys MUST enforce user ownership
- Indexes MUST optimize conversation retrieval by user_id

### Persistence Rules (MANDATORY)

- User message MUST be persisted before agent execution
- Assistant response MUST be persisted after agent execution
- Tool calls MUST be logged in message metadata
- Conversation history MUST be loaded from database on each request
- No in-memory conversation state between requests
- System MUST tolerate duplicate requests safely (idempotency)

## Database Standards

### SQLModel Requirements (MANDATORY)

- All database access MUST use SQLModel ORM
- Schema MUST match specifications exactly
- Foreign key relationships MUST enforce user ownership
- All queries MUST filter by authenticated user ID
- No raw SQL queries unless explicitly justified in ADR
- Migrations MUST be version-controlled
- Schema changes MUST be reflected in specs before implementation

### Data Isolation (MANDATORY)

- Every table with user data MUST have a `user_id` foreign key
- All SELECT queries MUST include `WHERE user_id = <authenticated_user_id>`
- All INSERT operations MUST set `user_id` from JWT
- All UPDATE/DELETE operations MUST verify ownership before execution
- Cross-user data access MUST be explicitly forbidden
- **Phase III**: MCP tools MUST enforce user_id scoping on all operations

## Frontend Standards

### Next.js Requirements (MANDATORY - Phases I-II)

- Use App Router only (no Pages Router)
- Responsive UI for desktop and mobile
- Clear loading, empty, and error states for all data fetching
- JWT MUST be attached to every API request via centralized client
- API calls MUST go through `frontend/src/lib/api-client.ts`
- UI MUST never assume success without backend confirmation
- Forms MUST show validation errors from backend

### ChatKit Requirements (MANDATORY - Phase III)

- Use OpenAI ChatKit for conversational interface
- UI MUST clearly show user messages and assistant responses
- UI MUST display loading state during agent execution
- UI MUST handle streaming responses if implemented
- UI MUST show tool invocations transparently (optional)
- UI MUST provide clear error messages for failed operations
- UI MUST support conversation history navigation

### Component Standards (MANDATORY)

- Server Components by default
- Client Components only when interactivity required
- Props MUST be typed with TypeScript
- No business logic in components (use API calls)
- Consistent styling system (Tailwind CSS or similar)

## Development Workflow

### Agentic Dev Stack (MANDATORY)

1. **Specification Phase**: Use `/sp.specify` to create detailed feature specs
2. **Planning Phase**: Use `/sp.plan` to generate architectural plan
3. **Task Generation**: Use `/sp.tasks` to break plan into actionable tasks
4. **Implementation Phase**: Use `/sp.implement` to execute via specialized agents

### Agent Delegation (MANDATORY)

- **auth-skill**: All authentication and authorization work
- **frontend-skill**: All Next.js frontend development
- **database-skill**: All schema design and migrations
- **backend-skill**: All FastAPI endpoint and service implementation
- **Phase III**: Specialized agents for MCP tool implementation and AI agent configuration

### Prompt History Records (MANDATORY)

- PHR MUST be created after every user interaction
- PHRs MUST capture full user input (not truncated)
- PHRs MUST be routed to appropriate subdirectory:
  - Constitution work → `history/prompts/constitution/`
  - Feature work → `history/prompts/<feature-name>/`
  - General work → `history/prompts/general/`

### Architecture Decision Records (MANDATORY)

When architecturally significant decisions are made (framework choice, authentication method, database schema, API design, MCP tool design, AI agent configuration), suggest creating ADR:

"📋 Architectural decision detected: [brief description]. Document reasoning and tradeoffs? Run `/sp.adr [decision-title]`"

Wait for user consent; never auto-create ADRs.

## Governance

### Constitution Authority

This constitution supersedes all other development practices, conventions, and assumptions. When conflicts arise, constitution rules take precedence.

### Amendment Process

1. Proposed changes MUST be documented with rationale
2. User approval MUST be obtained before amendments
3. Version MUST be incremented according to semantic versioning:
   - MAJOR: Backward incompatible principle changes
   - MINOR: New principles or sections added
   - PATCH: Clarifications and wording improvements
4. All dependent templates MUST be updated for consistency
5. Migration plan MUST be provided for breaking changes

### Compliance Review

- All specifications MUST reference constitution principles
- All PRs MUST verify compliance with constitution
- Complexity violations MUST be explicitly justified
- Regular audits MUST verify adherence to security rules
- **Phase III**: MCP tools MUST be audited for security and determinism

### Runtime Guidance

For day-to-day development guidance, refer to `CLAUDE.md` in repository root. That file provides operational instructions for Claude Code agents and complements this constitution.

**Version**: 1.1.0 | **Ratified**: 2026-02-02 | **Last Amended**: 2026-02-03
