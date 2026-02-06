# Data Model: Multi-User Todo Web Application

**Feature**: Multi-User Todo Web Application
**Branch**: 001-multi-user-todo-app
**Date**: 2026-02-02
**Status**: Complete

## Overview

This document defines the data entities, relationships, and validation rules for the multi-user todo application. All entities are implemented using SQLModel with PostgreSQL as the backing database.

---

## Entity Definitions

### User

Represents a person with an account in the system. Each user can own multiple tasks.

**Attributes**:

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | Integer | Primary Key, Auto-increment | Unique identifier for the user |
| email | String | Unique, Not Null, Max 255 chars, Indexed | User's email address (used for login) |
| password_hash | String | Not Null | Bcrypt/Argon2 hashed password (never store plain text) |
| created_at | DateTime | Not Null, Default: UTC now | Timestamp when account was created |

**Relationships**:
- One-to-Many with Task (one user owns many tasks)

**Validation Rules**:
- Email must be valid email format (validated by Better Auth on frontend)
- Email must be unique across all users
- Password must meet strength requirements before hashing:
  - Minimum 8 characters
  - At least one uppercase letter
  - At least one lowercase letter
  - At least one number

**Indexes**:
- Primary index on `id`
- Unique index on `email` (for fast login lookups)

**SQLModel Definition**:
```python
from sqlmodel import Field, SQLModel, Relationship
from typing import Optional, List
from datetime import datetime

class User(SQLModel, table=True):
    __tablename__ = "users"

    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True, max_length=255)
    password_hash: str = Field(max_length=255)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    tasks: List["Task"] = Relationship(back_populates="owner", cascade_delete=True)
```

---

### Task

Represents a todo item belonging to a specific user. Each task has a title, optional description, and completion status.

**Attributes**:

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | Integer | Primary Key, Auto-increment | Unique identifier for the task |
| title | String | Not Null, Max 200 chars | Task title (required) |
| description | String | Nullable, Max 2000 chars | Optional detailed description |
| completed | Boolean | Not Null, Default: False | Whether task is marked as complete |
| user_id | Integer | Foreign Key (users.id), Not Null, Indexed | Owner of this task |
| created_at | DateTime | Not Null, Default: UTC now | Timestamp when task was created |
| updated_at | DateTime | Not Null, Default: UTC now | Timestamp when task was last modified |

**Relationships**:
- Many-to-One with User (many tasks belong to one user)

**Validation Rules**:
- Title is required and cannot be empty string
- Title maximum length: 200 characters
- Description maximum length: 2000 characters (if provided)
- user_id must reference an existing user
- completed defaults to False for new tasks

**Indexes**:
- Primary index on `id`
- Index on `user_id` (for fast user-scoped queries)
- Composite index on `(user_id, created_at)` for sorted task lists

**SQLModel Definition**:
```python
from sqlmodel import Field, SQLModel, Relationship
from typing import Optional
from datetime import datetime

class Task(SQLModel, table=True):
    __tablename__ = "tasks"

    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(max_length=200, min_length=1)
    description: Optional[str] = Field(default=None, max_length=2000)
    completed: bool = Field(default=False)
    user_id: int = Field(foreign_key="users.id", index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    owner: User = Relationship(back_populates="tasks")
```

---

## Relationships

### User → Task (One-to-Many)

- **Cardinality**: One user can have zero or many tasks
- **Foreign Key**: Task.user_id references User.id
- **Cascade**: When a user is deleted, all their tasks are deleted (cascade delete)
- **Enforcement**: Database-level foreign key constraint + application-level validation

**Query Pattern**:
```python
# Get all tasks for a user
user_tasks = session.exec(
    select(Task)
    .where(Task.user_id == user_id)
    .order_by(Task.created_at.desc())
).all()

# Get user with their tasks
user = session.exec(
    select(User)
    .where(User.id == user_id)
).first()
tasks = user.tasks  # Relationship automatically loaded
```

---

## Data Isolation Rules

**Critical Security Requirement**: All task queries MUST filter by authenticated user's ID.

### Query Patterns for User Isolation

**✅ CORRECT - Always filter by user_id**:
```python
# Get tasks for authenticated user
tasks = session.exec(
    select(Task).where(Task.user_id == current_user_id)
).all()

# Get specific task (verify ownership)
task = session.exec(
    select(Task)
    .where(Task.id == task_id)
    .where(Task.user_id == current_user_id)
).first()

# Update task (verify ownership)
task = session.get(Task, task_id)
if task and task.user_id == current_user_id:
    task.title = new_title
    session.commit()
else:
    raise HTTPException(status_code=403, detail="Access denied")

# Delete task (verify ownership)
task = session.get(Task, task_id)
if task and task.user_id == current_user_id:
    session.delete(task)
    session.commit()
else:
    raise HTTPException(status_code=403, detail="Access denied")
```

**❌ INCORRECT - Never query without user_id filter**:
```python
# WRONG: Returns all tasks from all users
tasks = session.exec(select(Task)).all()

# WRONG: Could return another user's task
task = session.get(Task, task_id)
```

---

## Database Schema (SQL)

```sql
-- Users table
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_users_email ON users(email);

-- Tasks table
CREATE TABLE tasks (
    id SERIAL PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    description VARCHAR(2000),
    completed BOOLEAN NOT NULL DEFAULT FALSE,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_tasks_user_id ON tasks(user_id);
CREATE INDEX idx_tasks_user_created ON tasks(user_id, created_at DESC);
```

---

## State Transitions

### Task Completion State

Tasks have a simple two-state lifecycle:

```
[Incomplete] ←→ [Complete]
    ↑              ↑
    |              |
  Default      User marks
  state        complete
```

**Transitions**:
1. **Create**: Task starts in `completed = False` state
2. **Mark Complete**: User sets `completed = True`
3. **Mark Incomplete**: User sets `completed = False`
4. **Delete**: Task is removed from database

**Rules**:
- New tasks always start as incomplete
- Users can toggle completion status any number of times
- Completion status does not affect ability to edit or delete
- No automatic state transitions (user-driven only)

---

## Validation Summary

### User Entity
- ✅ Email format validation (handled by Better Auth)
- ✅ Email uniqueness (database constraint)
- ✅ Password strength (validated before hashing)
- ✅ Password hashing (never store plain text)

### Task Entity
- ✅ Title required (not null, min length 1)
- ✅ Title length limit (max 200 characters)
- ✅ Description length limit (max 2000 characters if provided)
- ✅ User ownership (foreign key constraint)
- ✅ Completion status (boolean, defaults to false)

### Security Validation
- ✅ All task queries filter by authenticated user_id
- ✅ JWT token verified before any database access
- ✅ User identity extracted from JWT, never from client input
- ✅ Ownership verified before update/delete operations

---

## Migration Strategy

### Initial Schema Creation

Use SQLModel's `create_all()` for development:
```python
from sqlmodel import SQLModel, create_engine

engine = create_engine(DATABASE_URL)
SQLModel.metadata.create_all(engine)
```

For production, use Alembic migrations:
```bash
alembic init migrations
alembic revision --autogenerate -m "Initial schema"
alembic upgrade head
```

### Future Schema Changes

All schema changes must:
1. Be documented in a new migration file
2. Be reversible (provide downgrade path)
3. Be tested in development before production
4. Update this data-model.md document

---

## Performance Considerations

### Indexes
- `users.email`: Fast login lookups
- `tasks.user_id`: Fast user-scoped queries
- `tasks.(user_id, created_at)`: Sorted task lists

### Query Optimization
- Always use indexed columns in WHERE clauses
- Limit result sets (pagination for large task lists)
- Use `select()` instead of loading all columns when possible
- Avoid N+1 queries by using relationships appropriately

### Scalability
- Current design supports up to 1000 tasks per user efficiently
- For larger datasets, consider pagination and lazy loading
- Database connection pooling handled by Neon

---

## Compliance with Specification

This data model satisfies the following functional requirements:

- **FR-001**: User accounts with email and password ✅
- **FR-002**: Email validation ✅
- **FR-008**: Tasks with title (required) and description (optional) ✅
- **FR-009**: Users view only their own tasks ✅
- **FR-010**: Prevent viewing other users' tasks ✅
- **FR-011**: Update own tasks only ✅
- **FR-012**: Prevent updating other users' tasks ✅
- **FR-013**: Delete own tasks only ✅
- **FR-014**: Prevent deleting other users' tasks ✅
- **FR-015**: Mark tasks complete/incomplete ✅
- **FR-016**: Persist data in database ✅
- **FR-017**: Hash passwords ✅
