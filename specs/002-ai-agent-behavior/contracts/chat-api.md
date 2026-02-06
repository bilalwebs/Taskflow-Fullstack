# Chat API Contract

**Endpoint**: `POST /api/{user_id}/chat`
**Version**: 1.0
**Authentication**: Required (JWT Bearer token)

## Overview

This endpoint enables conversational task management through natural language. Users send messages, and the AI agent responds with task operations performed via MCP tools.

---

## Request

### URL Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| user_id | integer | Yes | User identifier (must match JWT user_id) |

### Headers

| Header | Value | Required | Description |
|--------|-------|----------|-------------|
| Authorization | Bearer {token} | Yes | JWT authentication token |
| Content-Type | application/json | Yes | Request body format |

### Request Body

```json
{
  "message": "string (required, 1-2000 chars)",
  "conversation_id": "integer (optional)"
}
```

**Fields**:
- `message`: User's natural language input
- `conversation_id`: Existing conversation ID to continue (omit for new conversation)

**Validation Rules**:
- `message` cannot be empty or whitespace-only
- `message` max length: 2000 characters
- `conversation_id` must belong to authenticated user (if provided)

### Example Request

```http
POST /api/123/chat HTTP/1.1
Host: api.kirotodo.com
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Content-Type: application/json

{
  "message": "remind me to buy groceries tomorrow",
  "conversation_id": 456
}
```

---

## Response

### Success Response (200 OK)

```json
{
  "conversation_id": 456,
  "message_id": 789,
  "assistant_message": "I've added 'Buy groceries tomorrow' to your tasks. Task created successfully!",
  "tool_calls": [
    {
      "tool": "create_task",
      "parameters": {
        "title": "Buy groceries tomorrow",
        "description": ""
      },
      "result": {
        "task_id": 101,
        "status": "success"
      },
      "duration_ms": 45
    }
  ],
  "timestamp": "2026-02-03T10:30:00Z"
}
```

**Response Fields**:
- `conversation_id`: Conversation identifier (new or existing)
- `message_id`: ID of the assistant's response message
- `assistant_message`: Natural language response from agent
- `tool_calls`: Array of MCP tool invocations (empty if no tools used)
- `timestamp`: Response generation timestamp (ISO 8601)

### Tool Call Object Schema

```json
{
  "tool": "string (tool name)",
  "parameters": {
    "key": "value (tool-specific parameters)"
  },
  "result": {
    "status": "success | error",
    "data": "object (tool-specific result)"
  },
  "duration_ms": "integer (execution time)"
}
```

---

## Error Responses

### 400 Bad Request - Invalid Input

```json
{
  "error": "Invalid message format",
  "message": "The request contains invalid data",
  "details": {
    "field": "message",
    "issue": "Message cannot be empty"
  }
}
```

**Causes**:
- Empty or whitespace-only message
- Message exceeds 2000 characters
- Invalid conversation_id format
- Malformed JSON body

### 401 Unauthorized - Missing/Invalid Token

```json
{
  "error": "Authentication required",
  "message": "Authentication is required to access this resource"
}
```

**Causes**:
- Missing Authorization header
- Invalid JWT token
- Expired JWT token

### 403 Forbidden - User Mismatch

```json
{
  "error": "Permission denied",
  "message": "You do not have permission to access this resource",
  "details": {
    "reason": "URL user_id does not match authenticated user"
  }
}
```

**Causes**:
- URL user_id does not match JWT user_id
- Conversation belongs to different user

### 404 Not Found - Conversation Not Found

```json
{
  "error": "Conversation not found",
  "message": "The requested resource was not found",
  "details": {
    "conversation_id": 456
  }
}
```

**Causes**:
- Conversation ID does not exist
- Conversation was deleted

### 429 Too Many Requests - Rate Limit Exceeded

```json
{
  "error": "Rate limit exceeded",
  "message": "Too many requests. Please try again later.",
  "details": {
    "limit": 60,
    "window": "1 minute",
    "retry_after": 30
  }
}
```

**Causes**:
- User exceeded 60 requests per minute

### 500 Internal Server Error - Agent Failure

```json
{
  "error": "Agent processing failed",
  "message": "An internal server error occurred",
  "details": {
    "request_id": "abc123"
  }
}
```

**Causes**:
- OpenAI API failure
- Database connection error
- MCP tool execution error

---

## Streaming Endpoint (Alternative)

### Endpoint: `POST /api/{user_id}/chat/stream`

**Response**: Server-Sent Events (text/event-stream)

### SSE Event Format

```
data: {"content": "I've added ", "done": false}

data: {"content": "'Buy groceries tomorrow' ", "done": false}

data: {"content": "to your tasks.", "done": false}

data: {"content": "", "done": true, "conversation_id": 456, "tool_calls": [...]}
```

**Event Fields**:
- `content`: Partial response text (streamed progressively)
- `done`: Boolean indicating completion
- `conversation_id`: Included in final event
- `tool_calls`: Included in final event

### Example Client Code

```typescript
const response = await fetch('/api/123/chat/stream', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({ message: 'show my tasks' }),
});

const reader = response.body.getReader();
const decoder = new TextDecoder();

while (true) {
  const { done, value } = await reader.read();
  if (done) break;

  const chunk = decoder.decode(value);
  const lines = chunk.split('\n');

  for (const line of lines) {
    if (line.startsWith('data: ')) {
      const data = JSON.parse(line.slice(6));
      if (data.done) {
        console.log('Conversation ID:', data.conversation_id);
        break;
      }
      console.log('Chunk:', data.content);
    }
  }
}
```

---

## Rate Limiting

- **Limit**: 60 requests per minute per user
- **Strategy**: Token bucket algorithm
- **Headers**: Response includes rate limit headers

```http
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 45
X-RateLimit-Reset: 1675430400
```

---

## Security Requirements

1. **Authentication**: JWT token required for all requests
2. **Authorization**: URL user_id must match JWT user_id
3. **User Isolation**: Agent can only access authenticated user's tasks
4. **Input Validation**: Message content sanitized to prevent injection
5. **Rate Limiting**: Prevents abuse and ensures fair usage

---

## Performance Characteristics

- **Target Latency**: <3 seconds for 95% of requests
- **Timeout**: 30 seconds (returns 504 if exceeded)
- **Concurrent Requests**: Stateless design supports unlimited concurrency
- **Database Queries**: Optimized with indexes on user_id and conversation_id

---

## Example Conversation Flow

### 1. Create First Task (New Conversation)

**Request**:
```json
POST /api/123/chat
{
  "message": "remind me to buy milk"
}
```

**Response**:
```json
{
  "conversation_id": 1,
  "message_id": 2,
  "assistant_message": "I've added 'Buy milk' to your tasks!",
  "tool_calls": [
    {
      "tool": "create_task",
      "parameters": {"title": "Buy milk"},
      "result": {"task_id": 50, "status": "success"}
    }
  ]
}
```

### 2. List Tasks (Continue Conversation)

**Request**:
```json
POST /api/123/chat
{
  "message": "what are my tasks?",
  "conversation_id": 1
}
```

**Response**:
```json
{
  "conversation_id": 1,
  "message_id": 4,
  "assistant_message": "You have 1 task:\n- Buy milk (incomplete)",
  "tool_calls": [
    {
      "tool": "list_tasks",
      "parameters": {},
      "result": {
        "tasks": [
          {"id": 50, "title": "Buy milk", "completed": false}
        ]
      }
    }
  ]
}
```

### 3. Complete Task

**Request**:
```json
POST /api/123/chat
{
  "message": "I finished buying milk",
  "conversation_id": 1
}
```

**Response**:
```json
{
  "conversation_id": 1,
  "message_id": 6,
  "assistant_message": "Great! I've marked 'Buy milk' as complete.",
  "tool_calls": [
    {
      "tool": "mark_complete",
      "parameters": {"task_id": 50},
      "result": {"status": "success"}
    }
  ]
}
```

---

## Notes

- All timestamps use ISO 8601 format (UTC)
- Conversation history loaded from database on each request (stateless)
- Agent responses are deterministic for same conversation context
- Tool calls logged for audit trail and debugging
