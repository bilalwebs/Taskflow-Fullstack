# Data Model: Chat API & UI

**Feature**: 003-chat-api-ui
**Date**: 2026-02-04
**Purpose**: Define database entities, relationships, and validation rules for conversation persistence

---

## Entity Definitions

### 1. Conversation

**Purpose**: Represents a chat session between a user and the AI assistant.

**Attributes**:
- `id` (int, primary key): Auto-generated unique identifier
- `user_id` (int, foreign key → users.id): Owner of the conversation
- `created_at` (datetime): Timestamp when conversation was created
- `updated_at` (datetime): Timestamp of last message in conversation

**Relationships**:
- **Belongs to**: User (one-to-many: user has many conversations)
- **Has many**: Messages (one-to-many: conversation has many messages)

**Validation Rules**:
- `user_id` MUST reference existing user
- `created_at` MUST be set on creation
- `updated_at` MUST be updated when new message added

**Indexes**:
- Primary key on `id`
- Index on `user_id` for fast user conversation lookup
- Index on `updated_at` for sorting by recency

**SQLModel Definition**:
```python
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from typing import Optional, List

class Conversation(SQLModel, table=True):
    __tablename__ = "conversations"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    user: "User" = Relationship(back_populates="conversations")
    messages: List["Message"] = Relationship(back_populates="conversation")
```

**Business Rules**:
- Each conversation belongs to exactly one user
- Conversations cannot be transferred between users
- Conversations are never deleted (soft delete if needed in future)
- Empty conversations (no messages) are allowed

---

### 2. Message

**Purpose**: Represents a single message within a conversation (user or assistant).

**Attributes**:
- `id` (int, primary key): Auto-generated unique identifier
- `conversation_id` (int, foreign key → conversations.id): Parent conversation
- `role` (str, enum): Message sender - "user" or "assistant"
- `content` (text): Message text content
- `tool_calls` (json, nullable): JSON array of tool invocations (assistant messages only)
- `sequence_number` (int): Message order within conversation (auto-increment)
- `created_at` (datetime): Timestamp when message was created

**Relationships**:
- **Belongs to**: Conversation (many-to-one: many messages in one conversation)

**Validation Rules**:
- `conversation_id` MUST reference existing conversation
- `role` MUST be either "user" or "assistant"
- `content` MUST NOT be empty
- `content` length MUST be ≤ 10,000 characters
- `tool_calls` MUST be valid JSON array if present
- `sequence_number` MUST be unique within conversation
- `created_at` MUST be set on creation

**Indexes**:
- Primary key on `id`
- Index on `conversation_id` for fast conversation message lookup
- Composite index on `(conversation_id, sequence_number)` for ordered retrieval
- Index on `created_at` for temporal queries

**SQLModel Definition**:
```python
from sqlmodel import SQLModel, Field, Relationship, Column
from sqlalchemy import Text, JSON
from datetime import datetime
from typing import Optional, Dict, Any

class Message(SQLModel, table=True):
    __tablename__ = "messages"

    id: Optional[int] = Field(default=None, primary_key=True)
    conversation_id: int = Field(foreign_key="conversations.id", index=True)
    role: str = Field(max_length=20)  # "user" or "assistant"
    content: str = Field(sa_column=Column(Text))
    tool_calls: Optional[str] = Field(default=None, sa_column=Column(JSON))
    sequence_number: int = Field(index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)

    # Relationships
    conversation: "Conversation" = Relationship(back_populates="messages")

    class Config:
        arbitrary_types_allowed = True
```

**Business Rules**:
- Messages are immutable once created (no updates)
- Messages are ordered by `sequence_number` within conversation
- User messages never have `tool_calls`
- Assistant messages may have `tool_calls` if agent invoked tools
- Messages are never deleted (conversation history is permanent)

**Tool Calls Format**:
```json
[
  {
    "tool_name": "create_task",
    "arguments": {"title": "Buy groceries", "description": "Milk, eggs, bread"},
    "result": {"status": "success", "task_id": 123}
  },
  {
    "tool_name": "list_tasks",
    "arguments": {},
    "result": {"status": "success", "tasks": [...]}
  }
]
```

---

### 3. ToolCallLog (Optional - for audit trail)

**Purpose**: Audit log of all MCP tool invocations for debugging and analytics.

**Attributes**:
- `id` (int, primary key): Auto-generated unique identifier
- `message_id` (int, foreign key → messages.id, nullable): Associated assistant message
- `conversation_id` (int, foreign key → conversations.id): Parent conversation
- `user_id` (int, foreign key → users.id): User who triggered the tool call
- `tool_name` (str): Name of MCP tool invoked
- `arguments` (json): Tool input parameters
- `result` (json): Tool output/result
- `status` (str, enum): "success" or "error"
- `execution_time_ms` (int): Tool execution duration in milliseconds
- `created_at` (datetime): Timestamp of tool invocation

**Relationships**:
- **Belongs to**: Message (many-to-one: many tool calls per assistant message)
- **Belongs to**: Conversation (many-to-one: many tool calls per conversation)
- **Belongs to**: User (many-to-one: many tool calls per user)

**Validation Rules**:
- `tool_name` MUST be one of: list_tasks, create_task, update_task, delete_task, get_task, mark_complete
- `arguments` MUST be valid JSON object
- `result` MUST be valid JSON object
- `status` MUST be either "success" or "error"
- `execution_time_ms` MUST be ≥ 0

**Indexes**:
- Primary key on `id`
- Index on `user_id` for user-specific analytics
- Index on `tool_name` for tool usage analytics
- Index on `created_at` for temporal analysis

**SQLModel Definition**:
```python
from sqlmodel import SQLModel, Field, Relationship, Column
from sqlalchemy import JSON
from datetime import datetime
from typing import Optional

class ToolCallLog(SQLModel, table=True):
    __tablename__ = "tool_call_logs"

    id: Optional[int] = Field(default=None, primary_key=True)
    message_id: Optional[int] = Field(default=None, foreign_key="messages.id")
    conversation_id: int = Field(foreign_key="conversations.id", index=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    tool_name: str = Field(max_length=50, index=True)
    arguments: str = Field(sa_column=Column(JSON))
    result: str = Field(sa_column=Column(JSON))
    status: str = Field(max_length=20)  # "success" or "error"
    execution_time_ms: int = Field(default=0)
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)

    # Relationships
    message: Optional["Message"] = Relationship()
    conversation: "Conversation" = Relationship()
    user: "User" = Relationship()
```

**Business Rules**:
- Tool calls are logged regardless of success/failure
- Tool call logs are immutable (no updates or deletes)
- Used for debugging, analytics, and audit compliance
- Optional for MVP but recommended for production

---

## Entity Relationships Diagram

```
┌─────────────────┐
│     User        │
│  (existing)     │
└────────┬────────┘
         │ 1
         │
         │ has many
         │
         ▼ *
┌─────────────────┐
│  Conversation   │
│─────────────────│
│ id (PK)         │
│ user_id (FK)    │
│ created_at      │
│ updated_at      │
└────────┬────────┘
         │ 1
         │
         │ has many
         │
         ▼ *
┌─────────────────┐
│    Message      │
│─────────────────│
│ id (PK)         │
│ conversation_id │
│ role            │
│ content         │
│ tool_calls      │
│ sequence_number │
│ created_at      │
└────────┬────────┘
         │ 1
         │
         │ has many (optional)
         │
         ▼ *
┌─────────────────┐
│ ToolCallLog     │
│─────────────────│
│ id (PK)         │
│ message_id (FK) │
│ conversation_id │
│ user_id (FK)    │
│ tool_name       │
│ arguments       │
│ result          │
│ status          │
│ execution_time  │
│ created_at      │
└─────────────────┘
```

---

## Database Migration Strategy

### Initial Migration (Create Tables)

```sql
-- Create conversations table
CREATE TABLE conversations (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_conversations_user_id ON conversations(user_id);
CREATE INDEX idx_conversations_updated_at ON conversations(updated_at);

-- Create messages table
CREATE TABLE messages (
    id SERIAL PRIMARY KEY,
    conversation_id INTEGER NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL CHECK (role IN ('user', 'assistant')),
    content TEXT NOT NULL,
    tool_calls JSONB,
    sequence_number INTEGER NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    UNIQUE(conversation_id, sequence_number)
);

CREATE INDEX idx_messages_conversation_id ON messages(conversation_id);
CREATE INDEX idx_messages_conversation_seq ON messages(conversation_id, sequence_number);
CREATE INDEX idx_messages_created_at ON messages(created_at);

-- Create tool_call_logs table (optional)
CREATE TABLE tool_call_logs (
    id SERIAL PRIMARY KEY,
    message_id INTEGER REFERENCES messages(id) ON DELETE SET NULL,
    conversation_id INTEGER NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    tool_name VARCHAR(50) NOT NULL,
    arguments JSONB NOT NULL,
    result JSONB NOT NULL,
    status VARCHAR(20) NOT NULL CHECK (status IN ('success', 'error')),
    execution_time_ms INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_tool_call_logs_user_id ON tool_call_logs(user_id);
CREATE INDEX idx_tool_call_logs_tool_name ON tool_call_logs(tool_name);
CREATE INDEX idx_tool_call_logs_created_at ON tool_call_logs(created_at);
```

### Rollback Strategy

```sql
-- Drop tables in reverse order (respects foreign keys)
DROP TABLE IF EXISTS tool_call_logs;
DROP TABLE IF EXISTS messages;
DROP TABLE IF EXISTS conversations;
```

---

## Data Access Patterns

### 1. Create New Conversation
```python
conversation = Conversation(user_id=authenticated_user_id)
await db.add(conversation)
await db.commit()
```

### 2. Get User's Conversations (Most Recent First)
```python
conversations = await db.query(Conversation).filter(
    Conversation.user_id == authenticated_user_id
).order_by(Conversation.updated_at.desc()).limit(20).all()
```

### 3. Get Conversation History
```python
messages = await db.query(Message).filter(
    Message.conversation_id == conversation_id
).order_by(Message.sequence_number.asc()).all()
```

### 4. Add Message to Conversation
```python
# Get next sequence number
max_seq = await db.query(func.max(Message.sequence_number)).filter(
    Message.conversation_id == conversation_id
).scalar() or 0

message = Message(
    conversation_id=conversation_id,
    role=role,
    content=content,
    sequence_number=max_seq + 1
)
await db.add(message)

# Update conversation timestamp
conversation.updated_at = datetime.utcnow()
await db.commit()
```

### 5. Log Tool Call
```python
log = ToolCallLog(
    message_id=assistant_message.id,
    conversation_id=conversation_id,
    user_id=authenticated_user_id,
    tool_name=tool_name,
    arguments=json.dumps(arguments),
    result=json.dumps(result),
    status="success" if result["status"] == "success" else "error",
    execution_time_ms=execution_time
)
await db.add(log)
await db.commit()
```

---

## Data Integrity Constraints

### Foreign Key Constraints
- `conversations.user_id` → `users.id` (CASCADE on delete)
- `messages.conversation_id` → `conversations.id` (CASCADE on delete)
- `tool_call_logs.message_id` → `messages.id` (SET NULL on delete)
- `tool_call_logs.conversation_id` → `conversations.id` (CASCADE on delete)
- `tool_call_logs.user_id` → `users.id` (CASCADE on delete)

### Unique Constraints
- `(conversation_id, sequence_number)` in messages table

### Check Constraints
- `messages.role` IN ('user', 'assistant')
- `tool_call_logs.status` IN ('success', 'error')
- `tool_call_logs.execution_time_ms` >= 0

---

## Performance Considerations

### Query Optimization
- Index on `conversations.user_id` for fast user lookup
- Composite index on `(conversation_id, sequence_number)` for ordered message retrieval
- Index on `updated_at` for sorting conversations by recency

### Scalability
- Conversation history limited to 1000 messages (MVP)
- Consider partitioning messages table by conversation_id for large scale
- Consider archiving old conversations (>6 months inactive)

### Caching Strategy (Future)
- Cache recent conversations in Redis (TTL: 1 hour)
- Cache conversation history for active conversations
- Invalidate cache on new message

---

## Security Considerations

### User Data Isolation
- All queries MUST filter by authenticated user_id
- Foreign key constraints enforce ownership
- No cross-user data access possible at database level

### Data Privacy
- Message content stored as plain text (encryption at rest via database)
- Tool call logs may contain sensitive data (user task details)
- Consider GDPR compliance for data retention and deletion

### Audit Trail
- ToolCallLog provides complete audit trail of all operations
- Immutable logs prevent tampering
- Timestamps enable temporal analysis

---

## Testing Strategy

### Unit Tests
- Test entity creation with valid data
- Test validation rules (role enum, content length)
- Test relationship integrity

### Integration Tests
- Test conversation creation and message addition
- Test sequence number generation under concurrency
- Test foreign key cascade behavior

### Performance Tests
- Test conversation history retrieval with 100+ messages
- Test concurrent message creation in same conversation
- Test query performance with 1000+ conversations per user
