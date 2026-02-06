# KIro Todo API Documentation

**Version**: 1.0.0
**Base URL**: `http://localhost:8001`
**Authentication**: JWT Bearer Token

---

## Table of Contents

1. [Overview](#overview)
2. [Authentication](#authentication)
3. [Task Management](#task-management)
4. [Data Models](#data-models)
5. [Error Handling](#error-handling)
6. [Security](#security)
7. [Examples](#examples)

---

## Overview

The KIro Todo API is a RESTful API built with FastAPI that provides secure, multi-user task management with complete data isolation. Each user can only access their own tasks, enforced through JWT authentication and database-level filtering.

**Key Features:**
- JWT-based authentication
- User-scoped data isolation
- Complete CRUD operations for tasks
- Task completion tracking
- Comprehensive error handling
- Automatic timestamp management

---

## Authentication

All task endpoints require a valid JWT token in the `Authorization` header.

### User Signup

Create a new user account.

**Endpoint:** `POST /api/auth/signup`

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "SecurePass123"
}
```

**Response:** `201 Created`
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "email": "user@example.com"
  }
}
```

**Validation Rules:**
- Email must be valid format
- Password minimum 8 characters
- Password must contain: uppercase, lowercase, number
- Email must be unique

**Error Responses:**
- `400 Bad Request` - Invalid email format or weak password
- `409 Conflict` - Email already exists

---

### User Signin

Authenticate an existing user.

**Endpoint:** `POST /api/auth/signin`

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "SecurePass123"
}
```

**Response:** `200 OK`
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "email": "user@example.com"
  }
}
```

**Error Responses:**
- `401 Unauthorized` - Invalid credentials

---

## Task Management

All task endpoints require authentication via JWT token.

**Authentication Header:**
```
Authorization: Bearer <your_jwt_token>
```

---

### List All Tasks

Retrieve all tasks for the authenticated user.

**Endpoint:** `GET /api/tasks`

**Headers:**
```
Authorization: Bearer <token>
```

**Response:** `200 OK`
```json
[
  {
    "id": 1,
    "title": "Complete project documentation",
    "description": "Write comprehensive API docs",
    "completed": false,
    "user_id": 1,
    "created_at": "2026-02-03T10:30:00Z",
    "updated_at": "2026-02-03T10:30:00Z"
  },
  {
    "id": 2,
    "title": "Review pull requests",
    "description": null,
    "completed": true,
    "user_id": 1,
    "created_at": "2026-02-03T09:15:00Z",
    "updated_at": "2026-02-03T11:45:00Z"
  }
]
```

**Query Parameters:** None

**Notes:**
- Returns only tasks owned by authenticated user
- Ordered by creation date (newest first)
- Empty array if user has no tasks

---

### Create Task

Create a new task for the authenticated user.

**Endpoint:** `POST /api/tasks`

**Headers:**
```
Authorization: Bearer <token>
Content-Type: application/json
```

**Request Body:**
```json
{
  "title": "Buy groceries",
  "description": "Milk, eggs, bread, and coffee"
}
```

**Response:** `201 Created`
```json
{
  "id": 3,
  "title": "Buy groceries",
  "description": "Milk, eggs, bread, and coffee",
  "completed": false,
  "user_id": 1,
  "created_at": "2026-02-03T12:00:00Z",
  "updated_at": "2026-02-03T12:00:00Z"
}
```

**Field Requirements:**
- `title` (required): 1-200 characters, cannot be empty or whitespace
- `description` (optional): 0-2000 characters, can be null

**Error Responses:**
- `400 Bad Request` - Missing or empty title
- `401 Unauthorized` - Invalid or missing token

**Notes:**
- `user_id` is automatically set from JWT token
- `completed` defaults to `false`
- Timestamps are automatically generated

---

### Get Single Task

Retrieve a specific task by ID.

**Endpoint:** `GET /api/tasks/{task_id}`

**Headers:**
```
Authorization: Bearer <token>
```

**Path Parameters:**
- `task_id` (integer): The task ID

**Response:** `200 OK`
```json
{
  "id": 1,
  "title": "Complete project documentation",
  "description": "Write comprehensive API docs",
  "completed": false,
  "user_id": 1,
  "created_at": "2026-02-03T10:30:00Z",
  "updated_at": "2026-02-03T10:30:00Z"
}
```

**Error Responses:**
- `401 Unauthorized` - Invalid or missing token
- `403 Forbidden` - Task belongs to another user
- `404 Not Found` - Task does not exist

**Security:**
- Ownership is verified before returning task
- Users cannot access other users' tasks

---

### Update Task

Update an existing task's title and/or description.

**Endpoint:** `PUT /api/tasks/{task_id}`

**Headers:**
```
Authorization: Bearer <token>
Content-Type: application/json
```

**Path Parameters:**
- `task_id` (integer): The task ID

**Request Body:**
```json
{
  "title": "Complete project documentation (Updated)",
  "description": "Write comprehensive API docs with examples"
}
```

**Partial Update Supported:**
```json
{
  "title": "New title only"
}
```

**Response:** `200 OK`
```json
{
  "id": 1,
  "title": "Complete project documentation (Updated)",
  "description": "Write comprehensive API docs with examples",
  "completed": false,
  "user_id": 1,
  "created_at": "2026-02-03T10:30:00Z",
  "updated_at": "2026-02-03T12:30:00Z"
}
```

**Field Requirements:**
- `title` (optional): If provided, 1-200 characters, cannot be empty
- `description` (optional): If provided, 0-2000 characters

**Error Responses:**
- `400 Bad Request` - Empty title provided
- `401 Unauthorized` - Invalid or missing token
- `403 Forbidden` - Task belongs to another user
- `404 Not Found` - Task does not exist

**Notes:**
- Only provided fields are updated
- `updated_at` timestamp is automatically updated
- Ownership is verified before update

---

### Delete Task

Permanently delete a task.

**Endpoint:** `DELETE /api/tasks/{task_id}`

**Headers:**
```
Authorization: Bearer <token>
```

**Path Parameters:**
- `task_id` (integer): The task ID

**Response:** `200 OK`
```json
{
  "message": "Task deleted successfully"
}
```

**Error Responses:**
- `401 Unauthorized` - Invalid or missing token
- `403 Forbidden` - Task belongs to another user
- `404 Not Found` - Task does not exist

**Notes:**
- Deletion is permanent (no soft delete)
- Ownership is verified before deletion

---

### Toggle Task Completion

Toggle a task's completion status (complete ↔ incomplete).

**Endpoint:** `PATCH /api/tasks/{task_id}/complete`

**Headers:**
```
Authorization: Bearer <token>
```

**Path Parameters:**
- `task_id` (integer): The task ID

**Request Body:** None

**Response:** `200 OK`
```json
{
  "id": 1,
  "title": "Complete project documentation",
  "description": "Write comprehensive API docs",
  "completed": true,
  "user_id": 1,
  "created_at": "2026-02-03T10:30:00Z",
  "updated_at": "2026-02-03T13:00:00Z"
}
```

**Behavior:**
- `completed: false` → `completed: true`
- `completed: true` → `completed: false`

**Error Responses:**
- `401 Unauthorized` - Invalid or missing token
- `403 Forbidden` - Task belongs to another user
- `404 Not Found` - Task does not exist

**Notes:**
- `updated_at` timestamp is automatically updated
- Ownership is verified before toggle

---

## Data Models

### User

```typescript
{
  id: number;              // Auto-generated primary key
  email: string;           // Unique, valid email format
  password_hash: string;   // Bcrypt hashed password (never exposed in API)
  created_at: datetime;    // Auto-generated timestamp
}
```

### Task

```typescript
{
  id: number;              // Auto-generated primary key
  title: string;           // Required, 1-200 characters
  description: string | null;  // Optional, 0-2000 characters
  completed: boolean;      // Default: false
  user_id: number;         // Foreign key to User (from JWT)
  created_at: datetime;    // Auto-generated timestamp
  updated_at: datetime;    // Auto-updated on changes
}
```

### JWT Token Payload

```typescript
{
  user_id: number;         // User's database ID
  email: string;           // User's email
  exp: number;             // Token expiration timestamp
  iat: number;             // Token issued at timestamp
}
```

---

## Error Handling

All errors follow a consistent format:

```json
{
  "error": "Detailed error message",
  "message": "User-friendly message",
  "details": null
}
```

### HTTP Status Codes

| Code | Meaning | When Used |
|------|---------|-----------|
| `200` | OK | Successful GET, PUT, PATCH, DELETE |
| `201` | Created | Successful POST (resource created) |
| `400` | Bad Request | Invalid input, validation failure |
| `401` | Unauthorized | Missing or invalid JWT token |
| `403` | Forbidden | Valid token but insufficient permissions |
| `404` | Not Found | Resource does not exist |
| `409` | Conflict | Resource already exists (e.g., duplicate email) |
| `500` | Internal Server Error | Unexpected server error |

### Common Error Scenarios

**Missing Authentication:**
```json
{
  "error": "Not authenticated",
  "message": "Authentication is required to access this resource",
  "details": null
}
```

**Invalid Token:**
```json
{
  "error": "Invalid token",
  "message": "Authentication is required to access this resource",
  "details": null
}
```

**Accessing Another User's Task:**
```json
{
  "error": "You do not have permission to access this task",
  "message": "You do not have permission to access this resource",
  "details": null
}
```

**Task Not Found:**
```json
{
  "error": "Task not found",
  "message": "The requested resource was not found",
  "details": null
}
```

**Validation Error:**
```json
{
  "error": "Title is required and cannot be empty",
  "message": "The request contains invalid data",
  "details": null
}
```

---

## Security

### Authentication Flow

1. **User Registration/Login:**
   - User provides email and password
   - Backend validates credentials
   - Backend generates JWT token with user_id
   - Token returned to client

2. **Authenticated Requests:**
   - Client includes token in `Authorization: Bearer <token>` header
   - Backend verifies token signature
   - Backend extracts `user_id` from token payload
   - Backend uses `user_id` for all database queries

### Security Guarantees

✅ **User Identity from JWT Only:**
- User ID is NEVER accepted from client input
- All user identification comes from verified JWT token
- Prevents user impersonation attacks

✅ **Complete Data Isolation:**
- All database queries filtered by authenticated `user_id`
- Users cannot view, edit, or delete other users' tasks
- Ownership verified on every operation

✅ **Password Security:**
- Passwords hashed with bcrypt before storage
- Plain-text passwords never stored
- Password hashes never exposed in API responses

✅ **SQL Injection Prevention:**
- All queries use SQLModel ORM with parameterization
- No raw SQL with string concatenation

✅ **CORS Protection:**
- CORS middleware configured with allowed origins
- Prevents unauthorized cross-origin requests

### Token Management

**Token Expiration:** 7 days (168 hours)

**Token Format:**
```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJlbWFpbCI6InVzZXJAZXhhbXBsZS5jb20iLCJleHAiOjE3MDcwNTI4MDB9.signature
```

**Token Verification:**
- Signature verified using `JWT_SECRET`
- Expiration checked on every request
- Invalid tokens rejected with 401 Unauthorized

---

## Examples

### Complete Workflow Example

#### 1. Create Account

```bash
curl -X POST http://localhost:8001/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john@example.com",
    "password": "SecurePass123"
  }'
```

**Response:**
```json
{
  "access_token": "eyJhbGc...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "email": "john@example.com"
  }
}
```

#### 2. Create Task

```bash
curl -X POST http://localhost:8001/api/tasks \
  -H "Authorization: Bearer eyJhbGc..." \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Learn FastAPI",
    "description": "Build a REST API with authentication"
  }'
```

**Response:**
```json
{
  "id": 1,
  "title": "Learn FastAPI",
  "description": "Build a REST API with authentication",
  "completed": false,
  "user_id": 1,
  "created_at": "2026-02-03T14:00:00Z",
  "updated_at": "2026-02-03T14:00:00Z"
}
```

#### 3. List Tasks

```bash
curl -X GET http://localhost:8001/api/tasks \
  -H "Authorization: Bearer eyJhbGc..."
```

**Response:**
```json
[
  {
    "id": 1,
    "title": "Learn FastAPI",
    "description": "Build a REST API with authentication",
    "completed": false,
    "user_id": 1,
    "created_at": "2026-02-03T14:00:00Z",
    "updated_at": "2026-02-03T14:00:00Z"
  }
]
```

#### 4. Mark Task Complete

```bash
curl -X PATCH http://localhost:8001/api/tasks/1/complete \
  -H "Authorization: Bearer eyJhbGc..."
```

**Response:**
```json
{
  "id": 1,
  "title": "Learn FastAPI",
  "description": "Build a REST API with authentication",
  "completed": true,
  "user_id": 1,
  "created_at": "2026-02-03T14:00:00Z",
  "updated_at": "2026-02-03T14:30:00Z"
}
```

#### 5. Update Task

```bash
curl -X PUT http://localhost:8001/api/tasks/1 \
  -H "Authorization: Bearer eyJhbGc..." \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Master FastAPI",
    "description": "Build production-ready APIs"
  }'
```

#### 6. Delete Task

```bash
curl -X DELETE http://localhost:8001/api/tasks/1 \
  -H "Authorization: Bearer eyJhbGc..."
```

**Response:**
```json
{
  "message": "Task deleted successfully"
}
```

---

### JavaScript/TypeScript Example

```typescript
// API Client Configuration
const API_BASE_URL = 'http://localhost:8001';
let authToken: string | null = null;

// Signup
async function signup(email: string, password: string) {
  const response = await fetch(`${API_BASE_URL}/api/auth/signup`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password })
  });

  const data = await response.json();
  authToken = data.access_token;
  return data;
}

// Create Task
async function createTask(title: string, description?: string) {
  const response = await fetch(`${API_BASE_URL}/api/tasks`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${authToken}`
    },
    body: JSON.stringify({ title, description })
  });

  return response.json();
}

// List Tasks
async function listTasks() {
  const response = await fetch(`${API_BASE_URL}/api/tasks`, {
    headers: {
      'Authorization': `Bearer ${authToken}`
    }
  });

  return response.json();
}

// Toggle Task Completion
async function toggleTaskComplete(taskId: number) {
  const response = await fetch(`${API_BASE_URL}/api/tasks/${taskId}/complete`, {
    method: 'PATCH',
    headers: {
      'Authorization': `Bearer ${authToken}`
    }
  });

  return response.json();
}

// Delete Task
async function deleteTask(taskId: number) {
  const response = await fetch(`${API_BASE_URL}/api/tasks/${taskId}`, {
    method: 'DELETE',
    headers: {
      'Authorization': `Bearer ${authToken}`
    }
  });

  return response.json();
}
```

---

## Testing the API

### Using Swagger UI

FastAPI provides interactive API documentation:

1. Start the backend server
2. Open browser to: http://localhost:8001/docs
3. Click "Authorize" button
4. Enter JWT token from signup/signin response
5. Test endpoints interactively

### Using Postman

1. Import the API endpoints
2. Set `Authorization` header: `Bearer <token>`
3. Set `Content-Type` header: `application/json`
4. Test each endpoint

### Using curl

See examples above for complete curl commands.

---

## Rate Limiting & Performance

**Current Implementation:**
- No rate limiting (suitable for development/hackathon)
- Database connection pooling via Neon PostgreSQL
- Async/await for non-blocking I/O

**Production Recommendations:**
- Add rate limiting middleware
- Implement request caching
- Add database query optimization
- Monitor API performance metrics

---

## Support & Troubleshooting

**Common Issues:**

1. **401 Unauthorized on all requests**
   - Check token is included in Authorization header
   - Verify token format: `Bearer <token>`
   - Ensure JWT_SECRET matches between backend and frontend

2. **403 Forbidden when accessing task**
   - Task belongs to another user
   - Verify you're using correct user's token

3. **CORS errors from frontend**
   - Check CORS_ORIGINS in backend .env
   - Ensure frontend URL is in allowed origins list

4. **Database connection errors**
   - Verify DATABASE_URL in .env
   - Check Neon PostgreSQL is accessible
   - Test connection with database client

---

## API Versioning

**Current Version:** v1.0.0

**Endpoint Prefix:** `/api/`

**Future Versioning Strategy:**
- Breaking changes will use new prefix: `/api/v2/`
- Current endpoints will remain stable
- Deprecation notices will be provided in advance

---

## Changelog

### v1.0.0 (2026-02-03)
- Initial release
- User authentication (signup, signin)
- Task CRUD operations
- Task completion tracking
- JWT-based security
- Complete data isolation

---

**Last Updated:** 2026-02-03
**Maintained By:** KIro Todo Development Team
