# Quickstart Guide: MCP Server & Tools

**Feature**: 001-mcp-server-tools
**Date**: 2026-02-03
**Audience**: Developers setting up local development environment

## Overview

This guide helps developers set up and test the MCP Server & Tools feature locally. The MCP server provides AI agents with stateless, user-scoped tools for task management.

## Prerequisites

- Python 3.11 or higher
- PostgreSQL 14+ (or Neon Serverless account)
- OpenAI API key
- Git

## Environment Setup

### 1. Clone Repository

```bash
git clone <repository-url>
cd KIro_Todo
git checkout 001-mcp-server-tools
```

### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Environment Variables

Create `backend/.env` file:

```env
# Database Configuration
DATABASE_URL=postgresql://user:password@localhost:5432/kiro_todo
# Or use Neon Serverless:
# DATABASE_URL=postgresql://user:password@ep-xxx.us-east-2.aws.neon.tech/kiro_todo

# JWT Configuration
JWT_SECRET=your-secret-key-here
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=168

# Better Auth Secret (must match frontend)
BETTER_AUTH_SECRET=your-better-auth-secret

# OpenAI Configuration
OPENAI_API_KEY=sk-your-openai-api-key-here
OPENAI_MODEL=gpt-4o-mini

# CORS Configuration
CORS_ORIGINS=http://localhost:3000

# Environment
ENVIRONMENT=development
DEBUG=true
```

**Important**: Never commit `.env` file to version control!

### 4. Database Setup

```bash
# Run migrations
alembic upgrade head

# Verify tables created
psql $DATABASE_URL -c "\dt"
# Should show: users, tasks, conversations, messages
```

### 5. Start Backend Server

```bash
# From backend/ directory
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

Server should start at: http://localhost:8000

**Verify**:
- Health check: http://localhost:8000/health
- API docs: http://localhost:8000/docs

## Testing MCP Tools

### Option 1: Using FastAPI Docs (Recommended for Testing)

1. Open http://localhost:8000/docs
2. Create a test user via `/api/auth/signup`
3. Login via `/api/auth/signin` to get JWT token
4. Click "Authorize" button and enter: `Bearer <your-jwt-token>`
5. Test chat endpoint: `POST /api/{user_id}/chat`

**Example Request**:
```json
{
  "message": "Add a task to buy groceries",
  "conversation_id": null
}
```

**Expected Response**:
```json
{
  "conversation_id": 1,
  "message_id": 2,
  "assistant_message": "I've added 'Buy groceries' to your tasks.",
  "tool_calls": [
    {
      "tool": "create_task",
      "parameters": {"title": "Buy groceries"},
      "result": {"status": "success", "task": {...}},
      "duration_ms": 45
    }
  ],
  "timestamp": "2026-02-03T12:00:00Z"
}
```

### Option 2: Using cURL

```bash
# 1. Signup
curl -X POST http://localhost:8000/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "password123", "name": "Test User"}'

# 2. Login
curl -X POST http://localhost:8000/api/auth/signin \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "password123"}'
# Save the token from response

# 3. Chat with agent
curl -X POST http://localhost:8000/api/1/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <your-jwt-token>" \
  -d '{"message": "Show me my tasks"}'
```

### Option 3: Using Python Script

Create `test_mcp.py`:

```python
import requests
import json

BASE_URL = "http://localhost:8000"

# 1. Signup
signup_response = requests.post(f"{BASE_URL}/api/auth/signup", json={
    "email": "test@example.com",
    "password": "password123",
    "name": "Test User"
})
print("Signup:", signup_response.json())

# 2. Login
login_response = requests.post(f"{BASE_URL}/api/auth/signin", json={
    "email": "test@example.com",
    "password": "password123"
})
token = login_response.json()["access_token"]
user_id = login_response.json()["user"]["id"]
print(f"Logged in as user {user_id}")

# 3. Chat with agent
headers = {"Authorization": f"Bearer {token}"}
chat_response = requests.post(
    f"{BASE_URL}/api/{user_id}/chat",
    headers=headers,
    json={"message": "Add a task to buy groceries"}
)
print("Agent response:", json.dumps(chat_response.json(), indent=2))
```

Run: `python test_mcp.py`

## Testing Individual MCP Tools

### Direct Tool Testing (Unit Tests)

Create `test_tools.py`:

```python
import asyncio
from backend.src.tools.mcp_server import mcp_server
from backend.src.database import engine

async def test_create_task():
    # Create user-scoped context
    ctx = mcp_server.create_context(user_id=1)

    # Get create_task tool
    create_task = mcp_server.get_tool("create_task")

    # Execute tool
    result = await create_task(ctx, title="Test Task", description="Test description")

    print("Create Task Result:", result)
    assert result["status"] == "success"
    assert result["task"]["title"] == "Test Task"

async def test_list_tasks():
    ctx = mcp_server.create_context(user_id=1)
    list_tasks = mcp_server.get_tool("list_tasks")

    result = await list_tasks(ctx)

    print("List Tasks Result:", result)
    assert "tasks" in result
    assert "total" in result

# Run tests
asyncio.run(test_create_task())
asyncio.run(test_list_tasks())
```

Run: `python test_tools.py`

## Common Test Scenarios

### Scenario 1: Create and List Tasks

```
User: "Add a task to buy groceries"
Agent: Creates task via create_task tool
Agent: "I've added 'Buy groceries' to your tasks."

User: "Show me my tasks"
Agent: Calls list_tasks tool
Agent: "You have 1 task: 1. Buy groceries (pending)"
```

### Scenario 2: Mark Task Complete

```
User: "I finished buying groceries"
Agent: Calls list_tasks to find task
Agent: Calls mark_complete with task_id
Agent: "Great! I've marked 'Buy groceries' as complete."
```

### Scenario 3: Update Task

```
User: "Change the groceries task to 'Buy organic groceries'"
Agent: Calls list_tasks to find task
Agent: Calls update_task with new title
Agent: "I've updated the task to 'Buy organic groceries'."
```

### Scenario 4: Delete Task

```
User: "Delete the groceries task"
Agent: Calls list_tasks to find task
Agent: Calls delete_task with task_id
Agent: "I've deleted the 'Buy organic groceries' task."
```

## Debugging

### Enable Debug Logging

Add to `backend/src/main.py`:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Check Tool Registration

```python
from backend.src.tools import mcp_server

print("Registered tools:", mcp_server.list_tools())
# Should show: ['list_tasks', 'create_task', 'mark_complete', 'update_task', 'delete_task', 'get_task']
```

### Verify Database Queries

Add to tool files:

```python
print(f"Executing query: {statement}")
```

### Test User Isolation

```python
# Create tasks for user 1
ctx1 = mcp_server.create_context(user_id=1)
await create_task(ctx1, title="User 1 Task")

# Create tasks for user 2
ctx2 = mcp_server.create_context(user_id=2)
await create_task(ctx2, title="User 2 Task")

# List tasks for user 1 (should only see user 1's task)
result = await list_tasks(ctx1)
assert len(result["tasks"]) == 1
assert result["tasks"][0]["title"] == "User 1 Task"
```

## Troubleshooting

### Issue: "OpenAI API key not found"

**Solution**: Verify `OPENAI_API_KEY` in `.env` file

```bash
# Check environment variable
python -c "from backend.src.config import settings; print(settings.OPENAI_API_KEY)"
```

### Issue: "Database connection failed"

**Solution**: Verify `DATABASE_URL` and database is running

```bash
# Test connection
psql $DATABASE_URL -c "SELECT 1"
```

### Issue: "JWT token invalid"

**Solution**: Verify `JWT_SECRET` matches between signup and signin

```bash
# Check JWT secret
python -c "from backend.src.config import settings; print(settings.JWT_SECRET)"
```

### Issue: "Tool not found"

**Solution**: Verify tool registration in `backend/src/tools/__init__.py`

```python
from backend.src.tools import mcp_server
print(mcp_server.list_tools())
```

### Issue: "Cross-user data access"

**Solution**: Verify user_id in MCPContext matches authenticated user

```python
# Check context user_id
print(f"Context user_id: {ctx.user_id}")
print(f"Authenticated user_id: {current_user['user_id']}")
```

## Performance Testing

### Load Testing with Locust

Create `locustfile.py`:

```python
from locust import HttpUser, task, between

class ChatUser(HttpUser):
    wait_time = between(1, 3)

    def on_start(self):
        # Login and get token
        response = self.client.post("/api/auth/signin", json={
            "email": "test@example.com",
            "password": "password123"
        })
        self.token = response.json()["access_token"]
        self.user_id = response.json()["user"]["id"]

    @task
    def chat_create_task(self):
        self.client.post(
            f"/api/{self.user_id}/chat",
            headers={"Authorization": f"Bearer {self.token}"},
            json={"message": "Add a task to test performance"}
        )

    @task
    def chat_list_tasks(self):
        self.client.post(
            f"/api/{self.user_id}/chat",
            headers={"Authorization": f"Bearer {self.token}"},
            json={"message": "Show me my tasks"}
        )
```

Run: `locust -f locustfile.py`

Open: http://localhost:8089

## Next Steps

1. **Run Unit Tests**: `pytest backend/tests/unit/`
2. **Run Integration Tests**: `pytest backend/tests/integration/`
3. **Review Code**: Check `backend/src/tools/` for tool implementations
4. **Read Documentation**: See `plan.md`, `research.md`, `data-model.md`
5. **Implement Frontend**: Use OpenAI ChatKit for conversational UI

## Useful Commands

```bash
# Start backend with auto-reload
uvicorn src.main:app --reload

# Run database migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1

# Generate new migration
alembic revision --autogenerate -m "Description"

# Run tests
pytest backend/tests/

# Run tests with coverage
pytest --cov=backend/src backend/tests/

# Format code
black backend/src/

# Lint code
flake8 backend/src/

# Type check
mypy backend/src/
```

## Resources

- **API Documentation**: http://localhost:8000/docs
- **OpenAI Function Calling**: https://platform.openai.com/docs/guides/function-calling
- **SQLModel Docs**: https://sqlmodel.tiangolo.com/
- **FastAPI Docs**: https://fastapi.tiangolo.com/

## Support

For issues or questions:
1. Check `TROUBLESHOOTING.md` in repository root
2. Review existing GitHub issues
3. Create new issue with reproduction steps
