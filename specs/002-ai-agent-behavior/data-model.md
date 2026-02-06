# Data Model: AI Agent Behavior

**Feature**: 002-ai-agent-behavior
**Date**: 2026-02-03
**Status**: Design Complete

## Overview

This document defines the database entities required for conversational task management with AI agent integration. All entities enforce user ownership and support stateless conversation persistence.

---

## Entity Definitions

### 1. Conversation

Represents a chat session between a user and the AI agent.

**Table**: `conversations`

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | Integer | PRIMARY KEY, AUTO_INCREMENT | Unique conversation identifier |
| user_id | Integer | FOREIGN KEY → users.id, NOT NULL, INDEX | Owner of the conversation |
| title | String(200) | NULLABLE | Optional conversation title (auto-generated from first message) |
| created_at | DateTime | NOT NULL, DEFAULT NOW() | Conversation creation timestamp |
| updated_at | DateTime | NOT NULL, DEFAULT NOW() | Last message timestamp |
| deleted_at | DateTime | NULLABLE | Soft delete timestamp (NULL = active) |

**Relationships**:
- `user_id` → `users.id` (Many-to-One)
- `messages` ← One-to-Many

**Indexes**:
- `idx_conversations_user_id` on `user_id` (for user conversation list)
- `idx_conversations_updated_at` on `updated_at` (for sorting)
- `idx_conversations_deleted_at` on `deleted_at` (for filtering active)

**Validation Rules**:
- `user_id` must reference existing user
- `title` max length 200 characters
- `deleted_at` must be NULL or >= `created_at`

**State Transitions**:
- Created → Active (on first message)
- Active → Deleted (soft delete after 90 days or user request)

---

### 2. Message

Represents a single exchange in a conversation (user message or agent response).

**Table**: `messages`

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | Integer | PRIMARY KEY, AUTO_INCREMENT | Unique message identifier |
| conversation_id | Integer | FOREIGN KEY → conversations.id, NOT NULL, INDEX | Parent conversation |
| role | Enum('user', 'assistant') | NOT NULL | Message sender role |
| content | Text | NOT NULL | Message text content |
| tool_calls | JSONB | NULLABLE | Tool invocations metadata (assistant messages only) |
| created_at | DateTime | NOT NULL, DEFAULT NOW() | Message creation timestamp |
| deleted_at | DateTime | NULLABLE | Soft delete timestamp |

**Relationships**:
- `conversation_id` → `conversations.id` (Many-to-One)

**Indexes**:
- `idx_messages_conversation_id` on `conversation_id` (for conversation history)
- `idx_messages_created_at` on `created_at` (for chronological ordering)
- `idx_messages_deleted_at` on `deleted_at` (for filtering active)

**Validation Rules**:
- `conversation_id` must reference existing conversation
- `role` must be 'user' or 'assistant'
- `content` cannot be empty string
- `tool_calls` must be valid JSON array (if present)
- `deleted_at` must be NULL or >= `created_at`

---

### 3. Task (Existing - No Changes)

Existing task entity remains unchanged. AI agent interacts with tasks via MCP tools.

**Table**: `tasks` - No schema changes required.

---

### 4. User (Existing - No Changes)

Existing user entity remains unchanged.

**Table**: `users` - No schema changes required.

---

## Entity Relationships

```
users (existing)
  ├─── conversations (new)
  │      └─── messages (new)
  └─── tasks (existing)
```

**Relationship Details**:
- One User has Many Conversations
- One User has Many Tasks
- One Conversation has Many Messages
- Conversations and Tasks are independent (no direct relationship)

---

## Storage Estimates

### Assumptions
- Average conversation: 20 messages
- Average message length: 150 characters
- Tool calls metadata: ~500 bytes per assistant message
- 1,000 active users, 5 conversations per user per month

### Monthly Storage
- Conversations: 5,000 × 200 bytes = 1 MB
- Messages: 100,000 × 300 bytes = 30 MB
- Tool calls: 50,000 × 500 bytes = 25 MB
- **Total: ~56 MB/month**

### 90-Day Retention
- **Total: ~168 MB** (well within Neon free tier limits)

---

## Security Considerations

1. **User Isolation**: All queries MUST filter by `user_id` from JWT
2. **Soft Delete**: Use `deleted_at` for recovery, hard delete after 90 days
3. **Tool Call Logging**: Audit trail for debugging and compliance
4. **No PII in Tool Calls**: Task titles/descriptions only, no passwords or tokens
5. **Cascade Delete**: When user deleted, conversations and messages cascade
