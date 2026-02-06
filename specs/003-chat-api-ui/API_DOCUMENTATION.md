# Chat API Documentation

**Feature**: 003-chat-api-ui
**Version**: 1.0.0
**Base URL**: `http://localhost:8000` (development) | `https://api.kirotodo.com` (production)

---

## Authentication

All chat endpoints require JWT authentication via Bearer token.

```http
Authorization: Bearer <jwt_token>
```

**Getting a JWT Token:**

```bash
# Login
POST /api/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "password123"
}

# Response
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": 1,
    "email": "user@example.com"
  }
}
```

---

## Endpoints

### 1. Send Chat Message

Send a message to the AI agent and receive a response.

**Endpoint:** `POST /api/{user_id}/chat`

**Headers:**
```http
Authorization: Bearer <jwt_token>
Content-Type: application/json
```

**Request Body:**
```json
{
  "message": "Show me my tasks",
  "conversation_id": 1  // Optional: omit for new conversation
}
```

**Response (200 OK):**
```json
{
  "conversation_id": 1,
  "message_id": 5,
  "assistant_message": "You have 3 tasks:\n1. Buy groceries (incomplete)\n2. Call dentist (incomplete)\n3. Finish report (completed)",
  "tool_calls": [
    {
      "tool": "list_tasks",
      "parameters": {},
      "result": {
        "tasks": [
          {
            "id": 1,
            "title": "Buy groceries",
            "description": null,
            "completed": false,
            "created_at": "2026-02-04T10:00:00Z",
            "updated_at": "2026-02-04T10:00:00Z"
          }
        ],
        "total": 3,
        "completed_count": 1,
        "pending_count": 2
      },
      "duration_ms": 45
    }
  ],
  "timestamp": "2026-02-04T10:30:00Z"
}
```

**Error Responses:**

```json
// 400 Bad Request - Invalid message
{
  "detail": "Message cannot be empty or whitespace-only"
}

// 401 Unauthorized - Missing/invalid token
{
  "detail": "Could not validate credentials"
}

// 403 Forbidden - User ID mismatch
{
  "detail": "Permission denied"
}

// 404 Not Found - Conversation not found
{
  "detail": "Conversation not found"
}

// 429 Too Many Requests - Rate limit exceeded
{
  "detail": "Rate limit exceeded",
  "headers": {
    "X-RateLimit-Limit": "60",
    "X-RateLimit-Remaining": "0",
    "X-RateLimit-Reset": "1707048000",
    "Retry-After": "30"
  }
}

// 500 Internal Server Error - Agent processing failure
{
  "detail": "AI service is currently busy. Please try again in a moment."
}

// 504 Gateway Timeout - Agent timeout
{
  "detail": "Agent processing timeout - request took longer than 30 seconds"
}
```

**Example Usage:**

```bash
# Create new conversation
curl -X POST http://localhost:8000/api/1/chat \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Create a task to buy milk"
  }'

# Continue existing conversation
curl -X POST http://localhost:8000/api/1/chat \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Mark the first task as complete",
    "conversation_id": 1
  }'
```

---

### 2. Stream Chat Response (SSE)

Stream chat response with Server-Sent Events for progressive rendering.

**Endpoint:** `POST /api/{user_id}/chat/stream`

**Headers:**
```http
Authorization: Bearer <jwt_token>
Content-Type: application/json
```

**Request Body:**
```json
{
  "message": "Show me my tasks",
  "conversation_id": 1  // Optional
}
```

**Response (200 OK - text/event-stream):**
```
data: {"content": "You have ", "done": false}

data: {"content": "3 tasks:\n", "done": false}

data: {"content": "1. Buy gr", "done": false}

data: {"content": "oceries\n", "done": false}

data: {"done": true, "conversation_id": 1, "message_id": 5, "tool_calls": [...], "timestamp": "2026-02-04T10:30:00Z"}
```

**Example Usage:**

```javascript
// Frontend JavaScript
const response = await fetch('http://localhost:8000/api/1/chat/stream', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    message: 'Show my tasks',
    conversation_id: 1
  })
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
      if (data.content) {
        console.log(data.content); // Stream content
      }
      if (data.done) {
        console.log('Complete:', data);
      }
    }
  }
}
```

---

### 3. List Conversations

Get all conversations for the authenticated user.

**Endpoint:** `GET /api/{user_id}/conversations`

**Headers:**
```http
Authorization: Bearer <jwt_token>
```

**Response (200 OK):**
```json
{
  "conversations": [
    {
      "id": 1,
      "title": null,
      "created_at": "2026-02-04T10:00:00Z",
      "updated_at": "2026-02-04T10:30:00Z"
    },
    {
      "id": 2,
      "title": "Task Management",
      "created_at": "2026-02-03T15:00:00Z",
      "updated_at": "2026-02-03T16:00:00Z"
    }
  ],
  "total": 2
}
```

**Example Usage:**

```bash
curl -X GET http://localhost:8000/api/1/conversations \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

---

### 4. Get Conversation Messages

Get all messages in a specific conversation.

**Endpoint:** `GET /api/{user_id}/conversations/{conversation_id}/messages`

**Headers:**
```http
Authorization: Bearer <jwt_token>
```

**Response (200 OK):**
```json
{
  "conversation_id": 1,
  "messages": [
    {
      "id": 1,
      "role": "user",
      "content": "Show me my tasks",
      "tool_calls": null,
      "created_at": "2026-02-04T10:00:00Z"
    },
    {
      "id": 2,
      "role": "assistant",
      "content": "You have 3 tasks...",
      "tool_calls": [
        {
          "tool": "list_tasks",
          "parameters": {},
          "result": {...},
          "duration_ms": 45
        }
      ],
      "created_at": "2026-02-04T10:00:05Z"
    }
  ],
  "total": 2
}
```

**Example Usage:**

```bash
curl -X GET http://localhost:8000/api/1/conversations/1/messages \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

---

## MCP Tools

The AI agent has access to the following tools for task management:

### 1. list_tasks

**Description:** Retrieve all tasks for the user

**Parameters:** None

**Example Agent Usage:**
```
User: "Show me my tasks"
Agent calls: list_tasks()
Agent responds: "You have 3 tasks: ..."
```

### 2. create_task

**Description:** Create a new task

**Parameters:**
- `title` (string, required): Task title (1-200 chars)
- `description` (string, optional): Task description (max 2000 chars)

**Example Agent Usage:**
```
User: "Remind me to buy milk"
Agent calls: create_task(title="Buy milk")
Agent responds: "I've created a task 'Buy milk' for you."
```

### 3. mark_complete

**Description:** Toggle task completion status

**Parameters:**
- `task_id` (integer, required): ID of the task

**Example Agent Usage:**
```
User: "I finished buying milk"
Agent calls: list_tasks() → finds task ID
Agent calls: mark_complete(task_id=5)
Agent responds: "Great! I've marked 'Buy milk' as complete."
```

### 4. update_task

**Description:** Update task details

**Parameters:**
- `task_id` (integer, required): ID of the task
- `title` (string, optional): New title
- `description` (string, optional): New description

**Example Agent Usage:**
```
User: "Change 'buy milk' to 'buy milk and eggs'"
Agent calls: list_tasks() → finds task ID
Agent calls: update_task(task_id=5, title="Buy milk and eggs")
Agent responds: "I've updated the task to 'Buy milk and eggs'."
```

### 5. delete_task

**Description:** Delete a task

**Parameters:**
- `task_id` (integer, required): ID of the task

**Example Agent Usage:**
```
User: "Delete the milk task"
Agent calls: list_tasks() → finds task ID
Agent calls: delete_task(task_id=5)
Agent responds: "I've deleted the 'Buy milk' task."
```

### 6. get_task

**Description:** Get details of a specific task

**Parameters:**
- `task_id` (integer, required): ID of the task

**Example Agent Usage:**
```
User: "Tell me about task 5"
Agent calls: get_task(task_id=5)
Agent responds: "Task 5 is 'Buy milk', created on..."
```

---

## Rate Limiting

**Limits:**
- 60 requests per minute per user
- Burst capacity: 10 additional requests

**Headers:**
```http
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 45
X-RateLimit-Reset: 1707048000
```

**When rate limit is exceeded:**
```http
HTTP/1.1 429 Too Many Requests
Retry-After: 30

{
  "detail": "Rate limit exceeded"
}
```

---

## Error Handling

### Common Error Codes

| Code | Meaning | Common Causes |
|------|---------|---------------|
| 400 | Bad Request | Invalid message format, empty message |
| 401 | Unauthorized | Missing/invalid JWT token |
| 403 | Forbidden | User ID mismatch, accessing other user's data |
| 404 | Not Found | Conversation not found, deleted conversation |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Internal Server Error | Agent processing failure, OpenAI API error |
| 504 | Gateway Timeout | Agent took longer than 30 seconds |

### Error Response Format

All errors follow this format:

```json
{
  "detail": "Human-readable error message"
}
```

Some errors include additional headers:

```json
{
  "detail": "Error message",
  "headers": {
    "X-Error-Details": "Technical details for debugging"
  }
}
```

---

## Best Practices

### 1. Token Management

```javascript
// Store token securely
localStorage.setItem('jwt_token', token);

// Include in all requests
const headers = {
  'Authorization': `Bearer ${localStorage.getItem('jwt_token')}`,
  'Content-Type': 'application/json'
};

// Handle token expiration
if (response.status === 401) {
  // Redirect to login
  window.location.href = '/login';
}
```

### 2. Conversation Persistence

```javascript
// Store conversation ID for continuity
const [conversationId, setConversationId] = useState(null);

// Use conversation ID in subsequent messages
const response = await sendMessage(message, conversationId);

// Update conversation ID if new conversation created
if (!conversationId && response.conversation_id) {
  setConversationId(response.conversation_id);
}
```

### 3. Error Handling

```javascript
try {
  const response = await fetch('/api/1/chat', {
    method: 'POST',
    headers: headers,
    body: JSON.stringify({ message })
  });

  if (!response.ok) {
    if (response.status === 429) {
      // Rate limit - show retry message
      const retryAfter = response.headers.get('Retry-After');
      alert(`Rate limit exceeded. Retry in ${retryAfter} seconds.`);
    } else if (response.status === 401) {
      // Unauthorized - redirect to login
      window.location.href = '/login';
    } else {
      // Other errors
      const error = await response.json();
      alert(error.detail);
    }
    return;
  }

  const data = await response.json();
  // Handle success
} catch (error) {
  // Network error
  alert('Network error. Please check your connection.');
}
```

### 4. Loading States

```javascript
const [loading, setLoading] = useState(false);

const sendMessage = async (message) => {
  setLoading(true);
  try {
    const response = await chatClient.sendMessage(message);
    // Handle response
  } finally {
    setLoading(false);
  }
};

// Disable input while loading
<input disabled={loading} />
```

---

## Testing

### cURL Examples

```bash
# Set variables
export API_URL="http://localhost:8000"
export JWT_TOKEN="your-token-here"
export USER_ID=1

# Test chat endpoint
curl -X POST $API_URL/api/$USER_ID/chat \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message":"Show my tasks"}'

# Test conversation list
curl -X GET $API_URL/api/$USER_ID/conversations \
  -H "Authorization: Bearer $JWT_TOKEN"

# Test conversation history
curl -X GET $API_URL/api/$USER_ID/conversations/1/messages \
  -H "Authorization: Bearer $JWT_TOKEN"
```

### Postman Collection

Import this collection for testing:

```json
{
  "info": {
    "name": "KIro Todo Chat API",
    "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
  },
  "variable": [
    {
      "key": "base_url",
      "value": "http://localhost:8000"
    },
    {
      "key": "jwt_token",
      "value": "your-token-here"
    },
    {
      "key": "user_id",
      "value": "1"
    }
  ],
  "item": [
    {
      "name": "Send Chat Message",
      "request": {
        "method": "POST",
        "header": [
          {
            "key": "Authorization",
            "value": "Bearer {{jwt_token}}"
          }
        ],
        "body": {
          "mode": "raw",
          "raw": "{\"message\":\"Show my tasks\"}"
        },
        "url": "{{base_url}}/api/{{user_id}}/chat"
      }
    }
  ]
}
```

---

## Support

For issues or questions:
- Check troubleshooting in `quickstart.md`
- Review error logs in `backend/logs/`
- Verify environment variables are set correctly
- Test individual components in isolation
