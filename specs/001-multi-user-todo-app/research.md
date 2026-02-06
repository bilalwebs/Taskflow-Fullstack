# Technical Research: Multi-User Todo Web Application

**Feature**: Multi-User Todo Web Application
**Branch**: 001-multi-user-todo-app
**Date**: 2026-02-02
**Status**: Complete

## Overview

This document captures technical research and decisions for implementing a secure, multi-user todo application with JWT-based authentication. Research focuses on integration patterns between Next.js 16+ (App Router), FastAPI, SQLModel, and Neon Serverless PostgreSQL.

---

## 1. Better Auth JWT Configuration for Next.js 16+

### Decision
Use Better Auth with JWT token generation enabled. Configure Better Auth to issue JWT tokens on successful authentication that include user ID and email in the payload.

### Rationale
- Better Auth provides built-in session management and JWT support for Next.js
- JWT tokens enable stateless authentication, allowing backend to verify requests without session storage
- Tokens can be passed in Authorization headers for API requests
- Better Auth handles token refresh and expiration automatically

### Implementation Approach
```typescript
// Better Auth configuration
export const auth = betterAuth({
  jwt: {
    enabled: true,
    secret: process.env.BETTER_AUTH_SECRET,
    expiresIn: '7d'
  },
  session: {
    cookieOptions: {
      httpOnly: true,
      secure: process.env.NODE_ENV === 'production',
      sameSite: 'lax'
    }
  }
})
```

### Alternatives Considered
- **NextAuth.js**: More popular but heavier; Better Auth is lighter and JWT-focused
- **Custom JWT implementation**: More control but requires building session management from scratch
- **Clerk/Auth0**: Third-party services add external dependencies and cost

### Key Considerations
- JWT secret must be shared between frontend and backend via environment variable
- Token payload should be minimal (user ID, email) to keep token size small
- Frontend stores token in httpOnly cookie for security
- Token expiration should balance security (shorter) vs UX (longer)

---

## 2. FastAPI JWT Verification with python-jose

### Decision
Use `python-jose[cryptography]` library for JWT verification in FastAPI middleware. Verify token signature and extract user identity on every protected endpoint request.

### Rationale
- python-jose is the standard JWT library for Python, well-maintained and secure
- Integrates cleanly with FastAPI dependency injection system
- Supports multiple JWT algorithms (HS256, RS256)
- Provides clear error messages for invalid tokens

### Implementation Approach
```python
from jose import jwt, JWTError
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> dict:
    try:
        payload = jwt.decode(
            credentials.credentials,
            settings.JWT_SECRET,
            algorithms=["HS256"]
        )
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return {"user_id": user_id, "email": payload.get("email")}
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
```

### Alternatives Considered
- **PyJWT**: Similar functionality but python-jose has better FastAPI integration
- **Authlib**: More comprehensive but overkill for simple JWT verification
- **Custom verification**: Error-prone and security-risky

### Key Considerations
- JWT secret must match Better Auth secret exactly
- Use dependency injection to make `get_current_user` available to all protected routes
- Return 401 Unauthorized for missing/invalid tokens
- Extract user_id from token payload, never trust client-provided user_id

---

## 3. SQLModel Relationship Patterns for User-Owned Resources

### Decision
Use SQLModel with explicit foreign key relationships. Every Task model includes a `user_id` field with foreign key constraint to User model. All queries filter by authenticated user's ID.

### Rationale
- SQLModel combines Pydantic validation with SQLAlchemy ORM
- Foreign key constraints enforce referential integrity at database level
- Relationship definitions enable easy joins and cascading deletes
- Type hints provide IDE autocomplete and type checking

### Implementation Approach
```python
from sqlmodel import Field, SQLModel, Relationship
from typing import Optional, List
from datetime import datetime

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True)
    password_hash: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

    tasks: List["Task"] = Relationship(back_populates="owner")

class Task(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(max_length=200)
    description: Optional[str] = Field(default=None, max_length=2000)
    completed: bool = Field(default=False)
    user_id: int = Field(foreign_key="user.id", index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    owner: User = Relationship(back_populates="tasks")
```

### Query Pattern for User Isolation
```python
# Always filter by authenticated user_id
tasks = session.exec(
    select(Task).where(Task.user_id == current_user["user_id"])
).all()
```

### Alternatives Considered
- **Raw SQL**: More control but loses type safety and validation
- **SQLAlchemy Core**: Lower-level, more verbose
- **Django ORM**: Requires Django framework

### Key Considerations
- Index user_id column for query performance
- Use cascading deletes if user deletion should remove their tasks
- Always include user_id in WHERE clause for SELECT, UPDATE, DELETE
- Validate user_id from JWT matches user_id in request path/body

---

## 4. Neon Serverless PostgreSQL Connection Pooling

### Decision
Use Neon's built-in connection pooling with psycopg2-binary driver. Configure SQLModel engine with appropriate pool settings for serverless environment.

### Rationale
- Neon provides connection pooling at the platform level
- Serverless environments benefit from connection reuse across requests
- psycopg2-binary is the standard PostgreSQL driver for Python
- SQLModel/SQLAlchemy handle connection lifecycle automatically

### Implementation Approach
```python
from sqlmodel import create_engine, Session
from sqlalchemy.pool import NullPool

# For serverless/development
engine = create_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    poolclass=NullPool  # Let Neon handle pooling
)

# For traditional deployment
engine = create_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    pool_size=5,
    max_overflow=10,
    pool_pre_ping=True  # Verify connections before use
)
```

### Alternatives Considered
- **asyncpg**: Async driver but requires async/await throughout codebase
- **pg8000**: Pure Python but slower than psycopg2
- **Custom pooling**: Unnecessary with Neon's built-in pooling

### Key Considerations
- Use connection string from Neon dashboard (includes pooling parameters)
- Enable SSL for production connections
- Use NullPool for serverless to avoid connection exhaustion
- Set pool_pre_ping=True to handle stale connections

---

## 5. Next.js App Router Authentication Patterns

### Decision
Use Server Components for initial page loads with authentication checks. Use Client Components for interactive forms and API calls. Store authentication state in Better Auth session.

### Rationale
- Server Components reduce client-side JavaScript and improve performance
- Authentication checks on server prevent unauthorized page access
- Client Components handle user interactions and API calls
- Better Auth provides hooks for both server and client contexts

### Implementation Approach
```typescript
// Server Component (app/dashboard/page.tsx)
import { auth } from '@/lib/auth'
import { redirect } from 'next/navigation'

export default async function DashboardPage() {
  const session = await auth.getSession()
  if (!session) {
    redirect('/signin')
  }

  return <TaskList userId={session.user.id} />
}

// Client Component (components/TaskList.tsx)
'use client'
import { useAuth } from '@/lib/auth'
import { apiClient } from '@/lib/api-client'

export function TaskList() {
  const { token } = useAuth()
  const [tasks, setTasks] = useState([])

  useEffect(() => {
    apiClient.getTasks(token).then(setTasks)
  }, [token])

  return <div>{/* render tasks */}</div>
}
```

### Alternatives Considered
- **Client-only authentication**: Slower initial load, SEO issues
- **Middleware-based auth**: Works but less granular control
- **Pages Router**: Older pattern, App Router is recommended for Next.js 16+

### Key Considerations
- Use Server Components for authentication checks and initial data fetching
- Use Client Components for forms, buttons, and interactive elements
- Pass authentication token from server to client securely
- Handle token expiration gracefully with redirect to signin

---

## 6. Error Handling Standards for RESTful APIs

### Decision
Use consistent error response format with HTTP status codes, error messages, and optional error codes. Return JSON error responses for all failures.

### Rationale
- Consistent error format simplifies frontend error handling
- HTTP status codes provide semantic meaning (401, 403, 404, 500)
- Error messages help with debugging and user feedback
- Error codes enable programmatic error handling

### Implementation Approach
```python
# Error response schema
class ErrorResponse(BaseModel):
    error: str
    message: str
    details: Optional[dict] = None

# FastAPI exception handler
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "message": get_user_friendly_message(exc.status_code),
            "details": getattr(exc, "details", None)
        }
    )

# Usage in endpoints
@app.get("/api/tasks/{task_id}")
async def get_task(
    task_id: int,
    current_user: dict = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    if task.user_id != current_user["user_id"]:
        raise HTTPException(status_code=403, detail="Access denied")
    return task
```

### Status Code Standards
- **200 OK**: Successful GET, PUT, DELETE
- **201 Created**: Successful POST
- **400 Bad Request**: Invalid input, validation errors
- **401 Unauthorized**: Missing or invalid authentication token
- **403 Forbidden**: Valid token but insufficient permissions
- **404 Not Found**: Resource does not exist
- **500 Internal Server Error**: Unexpected server errors

### Alternatives Considered
- **Problem Details (RFC 7807)**: More structured but overkill for simple API
- **GraphQL errors**: Different paradigm, not RESTful
- **Plain text errors**: Harder to parse programmatically

### Key Considerations
- Always return JSON, never HTML error pages
- Include user-friendly messages for frontend display
- Log detailed errors server-side, return sanitized errors to client
- Use 401 for authentication failures, 403 for authorization failures
- Validate inputs and return 400 with specific validation errors

---

## Summary of Key Decisions

| Area | Technology | Rationale |
|------|-----------|-----------|
| Frontend Auth | Better Auth with JWT | Lightweight, JWT-focused, Next.js integration |
| Backend Auth | python-jose | Standard Python JWT library, FastAPI compatible |
| ORM | SQLModel | Type-safe, Pydantic validation, SQLAlchemy power |
| Database | Neon PostgreSQL | Serverless, built-in pooling, PostgreSQL compatible |
| API Pattern | RESTful JSON | Simple, standard, well-understood |
| Error Handling | HTTP status codes + JSON | Consistent, semantic, easy to handle |

## Risk Mitigation

1. **JWT Secret Mismatch**: Use same environment variable for both frontend and backend
2. **Connection Exhaustion**: Use Neon's pooling, configure appropriate pool sizes
3. **Token Expiration**: Implement token refresh or graceful re-authentication
4. **SQL Injection**: Use SQLModel parameterized queries exclusively
5. **CORS Issues**: Configure FastAPI CORS middleware for frontend origin

## Next Steps

Proceed to Phase 1: Design
- Generate data-model.md with complete entity definitions
- Create API contracts in contracts/ directory
- Write quickstart.md for local development setup
