# Data Model: MCP Server & Tools

**Feature**: 001-mcp-server-tools
**Date**: 2026-02-03
**Status**: Complete

## Overview

This document defines the data entities used by the MCP Server & Tools feature. All entities are implemented using SQLModel ORM and stored in Neon Serverless PostgreSQL.

## Entity Relationship Diagram

```
┌─────────────┐
│    User     │
│ (existing)  │
└──────┬──────┘
       │
       │ 1:N
       │
       ├──────────────────┬──────────────────┐
       │                  │                  │
       ▼                  ▼                  ▼
┌─────────────┐    ┌──────────────┐   ┌──────────────┐
│    Task     │    │ Conversation │   │   (other)    │
└─────────────┘    └──────┬───────┘   └──────────────┘
                          │
                          │ 1:N
                          │
                          ▼
                   ┌──────────────┐
                   │   Message    │
                   └──────────────┘
```

## Core Entities

### Task

Represents a todo item belonging to a specific user. Tasks are the primary data managed by MCP tools.

**Table Name**: `tasks`

**Fields**:

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | Integer | Primary Key, Auto-increment | Unique task identifier |
| user_id | Integer | Foreign Key (users.id), Indexed, NOT NULL | Owner of the task |
| title | String(200) | NOT NULL, Min length: 1 | Task title or main description |
| description | String(2000) | Nullable | Additional details or notes |
| completed | Boolean | NOT NULL, Default: False | Completion status |
| created_at | DateTime | NOT NULL, Default: utcnow() | Task creation timestamp |
| updated_at | DateTime | NOT NULL, Default: utcnow() | Last modification timestamp |

**Relationships**:
- `owner`: Many-to-One relationship with User (back_populates="tasks")

**Indexes**:
- Primary key index on `id`
- Index on `user_id` (for efficient user-scoped queries)

**Validation Rules**:
- Title must be 1-200 characters
- Description must be 0-2000 characters (if provided)
- User_id must reference existing user
- Completed is boolean (True/False)

**SQLModel Definition**:
```python
class Task(SQLModel, table=True):
    __tablename__ = "tasks"

    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(max_length=200, min_length=1)
    description: Optional[str] = Field(default=None, max_length=2000)
    completed: bool = Field(default=False)
    user_id: int = Field(foreign_key="users.id", index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    owner: "User" = Relationship(back_populates="tasks")
```

**Business Rules**:
1. Tasks are always scoped to a single user (no sharing)
2. Completed status can be toggled multiple times (idempotent)
3. Updated_at timestamp must be updated on any modification
4. Deletion is permanent (no soft delete for tasks)

**Query Patterns**:
```python
# List all tasks for user
select(Task).where(Task.user_id == user_id)

# List pending tasks for user
select(Task).where(Task.user_id == user_id, Task.completed == False)

# Get specific task with ownership validation
select(Task).where(Task.id == task_id, Task.user_id == user_id)
```

---

### Conversation

Represents a chat session between a user and the AI agent. Conversations group related messages together.

**Table Name**: `conversations`

**Fields**:

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | Integer | Primary Key, Auto-increment | Unique conversation identifier |
| user_id | Integer | Foreign Key (users.id), Indexed, NOT NULL | Owner of the conversation |
| title | String(200) | Nullable | Conversation title (optional) |
| created_at | DateTime | NOT NULL, Indexed, Default: utcnow() | Conversation start timestamp |
| updated_at | DateTime | NOT NULL, Indexed, Default: utcnow() | Last message timestamp |
| deleted_at | DateTime | Nullable, Indexed | Soft delete timestamp |

**Relationships**:
- `owner`: Many-to-One relationship with User (back_populates="conversations")
- `messages`: One-to-Many relationship with Message (cascade_delete=True, ordered by created_at)

**Indexes**:
- Primary key index on `id`
- Index on `user_id` (for efficient user-scoped queries)
- Index on `created_at` (for sorting by recency)
- Index on `updated_at` (for sorting by activity)
- Index on `deleted_at` (for filtering soft-deleted conversations)

**SQLModel Definition**:
```python
class Conversation(SQLModel, table=True):
    __tablename__ = "conversations"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    title: Optional[str] = Field(default=None, max_length=200)
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)
    updated_at: datetime = Field(default_factory=datetime.utcnow, index=True)
    deleted_at: Optional[datetime] = Field(default=None, index=True)

    owner: "User" = Relationship(back_populates="conversations")
    messages: List["Message"] = Relationship(
        back_populates="conversation",
        cascade_delete=True,
        sa_relationship_kwargs={"order_by": "Message.created_at"}
    )
```

**Business Rules**:
1. Conversations are always scoped to a single user
2. Title is optional (can be auto-generated from first message)
3. Updated_at timestamp updated when new message added
4. Soft delete used (deleted_at timestamp) to preserve history
5. Deleting conversation cascades to all messages

**Query Patterns**:
```python
# List active conversations for user (most recent first)
select(Conversation).where(
    Conversation.user_id == user_id,
    Conversation.deleted_at.is_(None)
).order_by(Conversation.updated_at.desc())

# Get conversation with ownership validation
select(Conversation).where(
    Conversation.id == conversation_id,
    Conversation.user_id == user_id,
    Conversation.deleted_at.is_(None)
)
```

---

### Message

Represents a single message in a conversation (either from user or AI assistant).

**Table Name**: `messages`

**Fields**:

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | Integer | Primary Key, Auto-increment | Unique message identifier |
| conversation_id | Integer | Foreign Key (conversations.id), Indexed, NOT NULL | Parent conversation |
| role | Enum(MessageRole) | NOT NULL | Message sender (user/assistant) |
| content | Text | NOT NULL | Message text content |
| tool_calls | JSON | Nullable | Tool invocations metadata (if any) |
| created_at | DateTime | NOT NULL, Indexed, Default: utcnow() | Message timestamp |
| deleted_at | DateTime | Nullable, Indexed | Soft delete timestamp |

**Enums**:
```python
class MessageRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"
```

**Relationships**:
- `conversation`: Many-to-One relationship with Conversation (back_populates="messages")

**Indexes**:
- Primary key index on `id`
- Index on `conversation_id` (for efficient conversation history queries)
- Index on `created_at` (for chronological ordering)
- Index on `deleted_at` (for filtering soft-deleted messages)

**SQLModel Definition**:
```python
class MessageRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"

class Message(SQLModel, table=True):
    __tablename__ = "messages"

    id: Optional[int] = Field(default=None, primary_key=True)
    conversation_id: int = Field(foreign_key="conversations.id", index=True)
    role: MessageRole = Field(sa_column=Column(Enum(MessageRole)))
    content: str = Field(sa_column=Column(Text))
    tool_calls: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column(JSON))
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)
    deleted_at: Optional[datetime] = Field(default=None, index=True)

    conversation: "Conversation" = Relationship(back_populates="messages")
```

**Tool Calls JSON Schema**:
```json
{
  "type": "array",
  "items": {
    "type": "object",
    "properties": {
      "tool": {"type": "string"},
      "parameters": {"type": "object"},
      "result": {"type": "object"},
      "duration_ms": {"type": "integer"}
    }
  }
}
```

**Business Rules**:
1. Messages are always part of a conversation
2. Role must be either "user" or "assistant"
3. Content is required (cannot be empty)
4. Tool_calls only present for assistant messages that invoked tools
5. Messages are immutable after creation (no updates)
6. Soft delete used to preserve conversation history

**Query Patterns**:
```python
# Get conversation history (chronological order)
select(Message).where(
    Message.conversation_id == conversation_id,
    Message.deleted_at.is_(None)
).order_by(Message.created_at.asc())

# Get recent messages for context (last 20)
select(Message).where(
    Message.conversation_id == conversation_id,
    Message.deleted_at.is_(None)
).order_by(Message.created_at.desc()).limit(20)
```

---

## Database Migrations

**Migration Tool**: Alembic

**Migration Files Location**: `backend/alembic/versions/`

**Key Migrations**:

1. **Initial Schema** (existing):
   - Create users table
   - Create tasks table with user_id foreign key

2. **Conversation Support** (Phase III):
   - Create conversations table with user_id foreign key
   - Create messages table with conversation_id foreign key
   - Add indexes for performance

**Running Migrations**:
```bash
# Generate migration
alembic revision --autogenerate -m "Add conversations and messages"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

---

## Data Integrity Constraints

### Foreign Key Constraints

1. **Task.user_id → User.id**
   - ON DELETE: CASCADE (delete tasks when user deleted)
   - Ensures tasks always belong to valid user

2. **Conversation.user_id → User.id**
   - ON DELETE: CASCADE (delete conversations when user deleted)
   - Ensures conversations always belong to valid user

3. **Message.conversation_id → Conversation.id**
   - ON DELETE: CASCADE (delete messages when conversation deleted)
   - Ensures messages always belong to valid conversation

### Check Constraints

1. **Task.title**: Length between 1 and 200 characters
2. **Task.description**: Length between 0 and 2000 characters (if not null)
3. **Conversation.title**: Length between 0 and 200 characters (if not null)
4. **Message.role**: Must be 'user' or 'assistant'

### Unique Constraints

None required (no natural unique keys beyond primary keys)

---

## Performance Optimization

### Indexes

**Critical Indexes** (already implemented):
- `tasks.user_id` - Enables fast user-scoped task queries
- `conversations.user_id` - Enables fast user-scoped conversation queries
- `conversations.updated_at` - Enables fast sorting by recent activity
- `messages.conversation_id` - Enables fast conversation history retrieval
- `messages.created_at` - Enables chronological message ordering

**Query Performance Targets**:
- List tasks for user: <50ms
- Get conversation history (20 messages): <100ms
- Create task: <50ms
- Create message: <50ms

### Connection Pooling

SQLModel uses SQLAlchemy connection pooling:
- Pool size: 5 connections (default)
- Max overflow: 10 connections
- Pool recycle: 3600 seconds (1 hour)

---

## Data Lifecycle

### Task Lifecycle

```
Created (completed=False)
    ↓
[User marks complete]
    ↓
Completed (completed=True)
    ↓
[User marks incomplete]
    ↓
Created (completed=False)
    ↓
[User deletes]
    ↓
Deleted (permanently removed)
```

### Conversation Lifecycle

```
Created (deleted_at=NULL)
    ↓
[Messages added]
    ↓
Active (updated_at updated)
    ↓
[User soft deletes]
    ↓
Soft Deleted (deleted_at set)
    ↓
[Cleanup job runs]
    ↓
Hard Deleted (permanently removed after 30 days)
```

### Message Lifecycle

```
Created (deleted_at=NULL)
    ↓
Immutable (no updates allowed)
    ↓
[Conversation deleted]
    ↓
Cascade Deleted (removed with conversation)
```

---

## Security Considerations

### User Data Isolation

**Enforcement Points**:
1. All queries MUST filter by authenticated user_id
2. Foreign key constraints prevent orphaned records
3. MCPContext pre-binds user_id to prevent tampering
4. No cross-user data access possible

**Example Secure Query**:
```python
# CORRECT: User-scoped query
statement = select(Task).where(Task.user_id == ctx.user_id)

# INCORRECT: Missing user_id filter (security violation)
statement = select(Task).where(Task.id == task_id)
```

### Sensitive Data

**No Sensitive Data in These Entities**:
- Task titles/descriptions are user-generated content (not sensitive)
- Message content is user-generated (not sensitive)
- No passwords, tokens, or secrets stored

**Sensitive Data in Related Entities** (out of scope):
- User.password_hash (hashed with bcrypt)
- User.email (PII, requires protection)

---

## Future Enhancements

### Potential Schema Changes

1. **Task Categories/Tags**:
   - Add `tags` JSON field to Task
   - Enable filtering by category

2. **Task Priority**:
   - Add `priority` enum field (low/medium/high)
   - Enable sorting by priority

3. **Conversation Summaries**:
   - Add `summary` text field to Conversation
   - Auto-generate from message history

4. **Message Attachments**:
   - Add `attachments` JSON field to Message
   - Support file uploads in conversations

5. **Task Due Dates**:
   - Add `due_date` datetime field to Task
   - Enable deadline tracking

**Note**: All enhancements require spec updates before implementation.

---

## References

- [SQLModel Documentation](https://sqlmodel.tiangolo.com/)
- [Alembic Documentation](https://alembic.sqlalchemy.org/)
- [PostgreSQL JSON Types](https://www.postgresql.org/docs/current/datatype-json.html)
- [Database Schema in backend/src/models/](../../../backend/src/models/)
