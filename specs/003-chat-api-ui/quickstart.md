# Quickstart Guide: Chat API & UI

**Feature**: 003-chat-api-ui
**Date**: 2026-02-04
**Purpose**: Setup instructions for developers implementing the Chat API & UI feature

---

## Prerequisites

### Required Accounts & API Keys

1. **OpenAI API Account**
   - Sign up at https://platform.openai.com
   - Generate API key from API Keys section
   - Ensure sufficient credits for GPT-4 Turbo usage
   - Store key in `.env` file as `OPENAI_API_KEY`

2. **Neon PostgreSQL Database**
   - Already configured from previous phases
   - Ensure database is accessible and credentials are in `.env`

3. **Better Auth Configuration**
   - Already configured from previous phases
   - JWT secret available in `.env` as `BETTER_AUTH_SECRET`

### Required Software

- Python 3.11+ (Backend)
- Node.js 18+ (Frontend)
- PostgreSQL client (for database migrations)
- Git (for version control)

---

## Environment Setup

### 1. Backend Environment Variables

Create or update `backend/.env`:

```bash
# Database (existing)
DATABASE_URL=postgresql://user:password@host:5432/kirotodo

# Authentication (existing)
BETTER_AUTH_SECRET=your-jwt-secret-here

# OpenAI API (NEW)
OPENAI_API_KEY=sk-proj-...your-key-here
OPENAI_MODEL=gpt-4-turbo-preview

# MCP Server (NEW)
MCP_SERVER_PORT=8001
MCP_SERVER_HOST=localhost

# Application
ENVIRONMENT=development
LOG_LEVEL=INFO
```

### 2. Frontend Environment Variables

Create or update `frontend/.env.local`:

```bash
# API Base URL (existing)
NEXT_PUBLIC_API_URL=http://localhost:8000

# OpenAI ChatKit (NEW)
NEXT_PUBLIC_CHATKIT_ENABLED=true
```

---

## Backend Setup

### 1. Install Dependencies

```bash
cd backend

# Install Python dependencies
pip install -r requirements.txt

# New dependencies for this feature:
# - openai>=1.0.0 (OpenAI Agents SDK)
# - mcp>=0.1.0 (Official MCP SDK)
# - python-jose[cryptography] (JWT verification - may already be installed)
```

Update `backend/requirements.txt`:
```txt
fastapi>=0.104.0
sqlmodel>=0.0.14
uvicorn>=0.24.0
python-jose[cryptography]>=3.3.0
openai>=1.0.0
mcp>=0.1.0
psycopg2-binary>=2.9.9
python-dotenv>=1.0.0
```

### 2. Run Database Migrations

```bash
# Create migration for new tables
alembic revision --autogenerate -m "Add conversation and message tables"

# Review the generated migration file
# Ensure it includes: conversations, messages, tool_call_logs tables

# Apply migration
alembic upgrade head

# Verify tables were created
psql $DATABASE_URL -c "\dt"
# Should show: conversations, messages, tool_call_logs
```

### 3. Initialize MCP Server

```bash
# Test MCP server initialization
python -c "from src.tools.mcp_server import mcp_server; print(mcp_server.get_tools())"

# Should output list of 6 registered tools
```

### 4. Start Backend Server

```bash
# Development mode with auto-reload
uvicorn src.main:app --reload --port 8000

# Server should start at http://localhost:8000
# Check health: curl http://localhost:8000/health
```

---

## Frontend Setup

### 1. Install Dependencies

```bash
cd frontend

# Install Node dependencies
npm install

# New dependencies for this feature:
npm install @openai/chatkit
npm install @types/react @types/node --save-dev
```

Update `frontend/package.json`:
```json
{
  "dependencies": {
    "next": "^14.0.0",
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "@openai/chatkit": "^1.0.0",
    "typescript": "^5.0.0"
  }
}
```

### 2. Start Frontend Development Server

```bash
npm run dev

# Server should start at http://localhost:3000
# Navigate to http://localhost:3000/chat
```

---

## Testing the Integration

### 1. Test Authentication Flow

```bash
# 1. Register a test user (if not already done)
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"testpass123"}'

# 2. Login to get JWT token
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"testpass123"}'

# Response will include JWT token
# {"token":"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...","user_id":1}

# 3. Store token for subsequent requests
export JWT_TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
export USER_ID=1
```

### 2. Test Chat Endpoint

```bash
# Send first message (creates new conversation)
curl -X POST http://localhost:8000/api/$USER_ID/chat \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message":"Hello, show me my tasks"}'

# Expected response:
# {
#   "conversation_id": 1,
#   "assistant_message": "Hello! You currently have no tasks. Would you like to create one?",
#   "tool_calls": [
#     {
#       "tool_name": "list_tasks",
#       "arguments": {"user_id": 1, "filter": "all"},
#       "result": {"status": "success", "tasks": [], "count": 0}
#     }
#   ]
# }

# Continue conversation
curl -X POST http://localhost:8000/api/$USER_ID/chat \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message":"Create a task to buy groceries","conversation_id":1}'

# Expected response:
# {
#   "conversation_id": 1,
#   "assistant_message": "I've created a task 'Buy groceries' for you.",
#   "tool_calls": [
#     {
#       "tool_name": "create_task",
#       "arguments": {"user_id": 1, "title": "Buy groceries"},
#       "result": {"status": "success", "task": {...}}
#     }
#   ]
# }
```

### 3. Test MCP Tools Directly

```bash
# Test list_tasks tool
python -c "
from src.tools.list_tasks import list_tasks
import asyncio
result = asyncio.run(list_tasks(user_id=1, filter='all'))
print(result)
"

# Test create_task tool
python -c "
from src.tools.create_task import create_task
import asyncio
result = asyncio.run(create_task(user_id=1, title='Test task'))
print(result)
"
```

### 4. Test Frontend Chat UI

1. Open browser to http://localhost:3000/chat
2. Login with test credentials
3. Type message: "Show me my tasks"
4. Verify AI response appears
5. Type message: "Create a task to test the chat"
6. Verify task is created and confirmed
7. Refresh page and verify conversation history loads

---

## Verification Checklist

### Backend Verification

- [ ] Database tables created (conversations, messages, tool_call_logs)
- [ ] MCP server initializes with 6 tools
- [ ] OpenAI API key is valid and working
- [ ] JWT authentication works on chat endpoint
- [ ] Chat endpoint returns valid responses
- [ ] Tool calls are logged to database
- [ ] Conversation history persists across requests

### Frontend Verification

- [ ] ChatKit components render correctly
- [ ] User can send messages
- [ ] AI responses display in chat
- [ ] Loading states show during agent execution
- [ ] Error messages display gracefully
- [ ] Conversation history loads on page refresh
- [ ] JWT token is included in API requests

### Integration Verification

- [ ] User message persisted before agent execution
- [ ] Agent executes with conversation history
- [ ] MCP tools invoked correctly by agent
- [ ] Assistant response persisted after agent execution
- [ ] Tool calls logged to audit table
- [ ] User data isolation enforced (test with 2 users)
- [ ] Server restart does not lose conversation state

---

## Common Issues & Troubleshooting

### Issue: OpenAI API Key Invalid

**Symptoms**: 401 Unauthorized from OpenAI API

**Solution**:
```bash
# Verify API key is set
echo $OPENAI_API_KEY

# Test API key directly
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer $OPENAI_API_KEY"

# If invalid, generate new key at https://platform.openai.com
```

### Issue: MCP Tools Not Registered

**Symptoms**: Agent cannot invoke tools, "tool not found" errors

**Solution**:
```bash
# Check tool registration
python -c "from src.tools.mcp_server import mcp_server; print(len(mcp_server.get_tools()))"
# Should output: 6

# Verify each tool is decorated with @mcp_server.tool()
# Check src/tools/*.py files
```

### Issue: Conversation History Not Loading

**Symptoms**: Empty chat on page refresh, conversation_id not found

**Solution**:
```bash
# Check database for conversations
psql $DATABASE_URL -c "SELECT * FROM conversations WHERE user_id=1;"

# Check messages table
psql $DATABASE_URL -c "SELECT * FROM messages WHERE conversation_id=1;"

# Verify foreign key constraints
psql $DATABASE_URL -c "\d messages"
```

### Issue: JWT Token Expired

**Symptoms**: 401 Unauthorized on chat endpoint

**Solution**:
```bash
# Login again to get fresh token
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"testpass123"}'

# Update JWT_TOKEN environment variable
export JWT_TOKEN="new-token-here"
```

### Issue: Agent Takes Too Long to Respond

**Symptoms**: Timeout errors, slow responses (>30 seconds)

**Solution**:
```bash
# Check OpenAI API status
curl https://status.openai.com/api/v2/status.json

# Reduce conversation history size
# Edit backend/src/services/conversation_service.py
# Change limit from 100 to 50 messages

# Monitor agent execution time
# Check logs for "Agent execution time: X ms"
```

### Issue: Cross-User Data Access

**Symptoms**: User A sees User B's conversations or tasks

**Solution**:
```bash
# Verify JWT user_id extraction
# Check backend/src/api/chat.py verify_jwt function

# Verify user_id filtering in tools
# Check each tool in src/tools/*.py
# Ensure all database queries filter by user_id

# Test with two different users
# Verify each can only see their own data
```

---

## Development Workflow

### 1. Making Changes to Agent Behavior

```bash
# Edit agent configuration
vim backend/src/agents/agent_config.py

# Update system prompt or model settings
# Restart backend server
# Test with chat endpoint
```

### 2. Adding New MCP Tool

```bash
# Create new tool file
vim backend/src/tools/new_tool.py

# Register with decorator
@mcp_server.tool(name="new_tool", description="...")
async def new_tool(user_id: int, ...):
    pass

# Restart backend server
# Tool automatically available to agent
```

### 3. Updating Chat UI

```bash
# Edit ChatKit components
vim frontend/src/components/ChatInterface.tsx

# Changes hot-reload automatically
# Test in browser at http://localhost:3000/chat
```

### 4. Running Tests

```bash
# Backend tests
cd backend
pytest tests/test_chat_endpoint.py -v
pytest tests/test_mcp_tools.py -v

# Frontend tests
cd frontend
npm test
```

---

## Production Deployment Checklist

- [ ] Set `ENVIRONMENT=production` in backend .env
- [ ] Use production OpenAI API key with rate limits
- [ ] Enable HTTPS for all API requests
- [ ] Set secure JWT secret (32+ random characters)
- [ ] Configure CORS for production frontend domain
- [ ] Enable database connection pooling
- [ ] Set up monitoring for agent execution time
- [ ] Configure log aggregation (e.g., CloudWatch, Datadog)
- [ ] Set up alerts for API errors and timeouts
- [ ] Test with production-like conversation volumes
- [ ] Implement rate limiting on chat endpoint
- [ ] Configure backup strategy for conversations table

---

## Next Steps

After completing setup:

1. **Review Architecture**: Read `research.md` for technical decisions
2. **Understand Data Model**: Review `data-model.md` for database schema
3. **Study API Contracts**: Review `contracts/` for endpoint specifications
4. **Run Tests**: Execute test suite to verify functionality
5. **Implement Tasks**: Proceed to `/sp.tasks` to generate implementation tasks

---

## Support & Resources

### Documentation
- OpenAI Agents SDK: https://platform.openai.com/docs/agents
- MCP Protocol: https://modelcontextprotocol.io/docs
- OpenAI ChatKit: https://github.com/openai/chatkit
- FastAPI: https://fastapi.tiangolo.com
- Next.js: https://nextjs.org/docs

### Internal Resources
- Constitution: `.specify/memory/constitution.md`
- Feature Spec: `specs/003-chat-api-ui/spec.md`
- Implementation Plan: `specs/003-chat-api-ui/plan.md`

### Getting Help
- Check troubleshooting section above
- Review error logs in `backend/logs/`
- Test individual components in isolation
- Verify environment variables are set correctly
