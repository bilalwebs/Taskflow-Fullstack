# Quickstart Guide: AI Agent Behavior

**Feature**: 002-ai-agent-behavior
**Date**: 2026-02-03
**Audience**: Developers implementing the conversational task management feature

## Overview

This guide provides step-by-step instructions for implementing the AI agent behavior feature, including database setup, MCP tools, agent configuration, and frontend integration.

---

## Prerequisites

- Phase I-II complete (user authentication, task CRUD APIs, database schema)
- Python 3.11+ with FastAPI backend running
- Next.js 16+ frontend with App Router
- Neon Serverless PostgreSQL database
- OpenAI API key with access to GPT-4o-mini or GPT-3.5-turbo

---

## Step 1: Install Dependencies

### Backend Dependencies

```bash
cd backend
pip install openai-agents-sdk mcp-sdk sqlalchemy alembic
```

Add to `requirements.txt`:
```
openai-agents-sdk>=1.0.0
mcp-sdk>=1.0.0
sqlalchemy>=2.0.0
alembic>=1.12.0
```

### Frontend Dependencies

```bash
cd frontend
npm install @openai/chatkit
```

---

## Step 2: Database Migration

### Create Migration File

```bash
cd backend
alembic revision -m "add_conversations_and_messages"
```

### Apply Migration

```bash
alembic upgrade head
```

**Verify Tables Created**:
```sql
SELECT table_name FROM information_schema.tables
WHERE table_schema = 'public'
AND table_name IN ('conversations', 'messages');
```

---

## Step 3: Implement MCP Tools

### Create Tool Files

**File Structure**:
```
backend/src/tools/
├── __init__.py
├── mcp_server.py       # MCP server setup
├── list_tasks.py       # Tool implementation
├── create_task.py      # Tool implementation
├── update_task.py      # Tool implementation
├── delete_task.py      # Tool implementation
├── get_task.py         # Tool implementation
└── mark_complete.py    # Tool implementation
```

### Example Tool Implementation

**File**: `backend/src/tools/list_tasks.py`

```python
from mcp import tool, Context
from sqlmodel import Session, select
from ..models.task import Task

@tool()
async def _list_tasks_internal(ctx: Context, user_id: int) -> dict:
    """Internal tool - requires user_id parameter"""
    with ctx.db_engine.session() as session:
        statement = select(Task).where(Task.user_id == user_id)
        tasks = session.exec(statement).all()

        return {
            "tasks": [task.dict() for task in tasks],
            "total": len(tasks),
            "completed_count": sum(1 for t in tasks if t.completed),
            "pending_count": sum(1 for t in tasks if not t.completed)
        }
```

**Repeat for all 6 tools** following the contracts in `contracts/mcp-tools.md`.

---

## Step 4: Create Agent Service

**File**: `backend/src/services/agent_service.py`

```python
from openai import OpenAI
from ..tools import mcp_tools
from ..database import engine

class AgentService:
    def __init__(self, user_id: int):
        self.user_id = user_id
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)

    def create_user_scoped_tools(self):
        """Wrap MCP tools with user_id pre-bound"""
        async def list_tasks():
            return await mcp_tools._list_tasks_internal(
                ctx=Context(db_engine=engine),
                user_id=self.user_id
            )

        async def create_task(title: str, description: str = ""):
            return await mcp_tools._create_task_internal(
                ctx=Context(db_engine=engine),
                user_id=self.user_id,
                title=title,
                description=description
            )

        # ... repeat for all 6 tools

        return [list_tasks, create_task, ...]

    async def process_message(self, message: str, conversation_history: list):
        """Process user message and return agent response"""
        tools = self.create_user_scoped_tools()

        response = await self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=conversation_history + [{"role": "user", "content": message}],
            tools=tools,
            temperature=0.3
        )

        return response
```

---

## Step 5: Implement Chat Endpoint

**File**: `backend/src/api/chat.py`

```python
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from ..database import get_session
from ..middleware.auth import get_current_user
from ..services.agent_service import AgentService
from ..models.conversation import Conversation
from ..models.message import Message, MessageRole

router = APIRouter(prefix="/api", tags=["Chat"])

@router.post("/{user_id}/chat")
async def chat(
    user_id: int,
    message: str,
    conversation_id: int = None,
    session: Session = Depends(get_session),
    current_user: dict = Depends(get_current_user)
):
    # Verify user_id matches JWT
    if current_user["user_id"] != user_id:
        raise HTTPException(status_code=403, detail="Permission denied")

    # Load or create conversation
    if conversation_id:
        conversation = session.get(Conversation, conversation_id)
        if not conversation or conversation.user_id != user_id:
            raise HTTPException(status_code=404, detail="Conversation not found")
    else:
        conversation = Conversation(user_id=user_id)
        session.add(conversation)
        session.commit()
        session.refresh(conversation)

    # Save user message
    user_message = Message(
        conversation_id=conversation.id,
        role=MessageRole.USER,
        content=message
    )
    session.add(user_message)
    session.commit()

    # Load conversation history
    history = session.exec(
        select(Message)
        .where(Message.conversation_id == conversation.id)
        .order_by(Message.created_at.asc())
    ).all()

    # Process with agent
    agent = AgentService(user_id=user_id)
    response = await agent.process_message(message, history)

    # Save assistant response
    assistant_message = Message(
        conversation_id=conversation.id,
        role=MessageRole.ASSISTANT,
        content=response.content,
        tool_calls=response.tool_calls
    )
    session.add(assistant_message)
    session.commit()

    return {
        "conversation_id": conversation.id,
        "message_id": assistant_message.id,
        "assistant_message": response.content,
        "tool_calls": response.tool_calls
    }
```

---

## Step 6: Frontend Chat Interface

**File**: `frontend/src/app/chat/page.tsx`

```typescript
'use client';

import { useState } from 'react';
import { ChatInterface } from '@/components/ChatInterface';

export default function ChatPage() {
  const [conversationId, setConversationId] = useState<number | null>(null);

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-2xl font-bold mb-4">Task Assistant</h1>
      <ChatInterface
        conversationId={conversationId}
        onConversationCreated={setConversationId}
      />
    </div>
  );
}
```

**File**: `frontend/src/components/ChatInterface.tsx`

```typescript
'use client';

import { useState } from 'react';

export function ChatInterface({ conversationId, onConversationCreated }) {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);

  const sendMessage = async () => {
    if (!input.trim()) return;

    setLoading(true);
    const userMessage = { role: 'user', content: input };
    setMessages(prev => [...prev, userMessage]);
    setInput('');

    try {
      const response = await fetch(`/api/${userId}/chat`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: input,
          conversation_id: conversationId,
        }),
      });

      const data = await response.json();

      if (!conversationId) {
        onConversationCreated(data.conversation_id);
      }

      setMessages(prev => [...prev, {
        role: 'assistant',
        content: data.assistant_message,
      }]);
    } catch (error) {
      console.error('Chat error:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-[600px] border rounded-lg">
      <div className="flex-1 overflow-y-auto p-4">
        {messages.map((msg, idx) => (
          <div key={idx} className={`mb-4 ${msg.role === 'user' ? 'text-right' : 'text-left'}`}>
            <div className={`inline-block p-3 rounded-lg ${
              msg.role === 'user' ? 'bg-blue-500 text-white' : 'bg-gray-200'
            }`}>
              {msg.content}
            </div>
          </div>
        ))}
      </div>

      <div className="border-t p-4">
        <div className="flex gap-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
            placeholder="Type a message..."
            className="flex-1 border rounded px-3 py-2"
            disabled={loading}
          />
          <button
            onClick={sendMessage}
            disabled={loading}
            className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600 disabled:opacity-50"
          >
            {loading ? 'Sending...' : 'Send'}
          </button>
        </div>
      </div>
    </div>
  );
}
```

---

## Step 7: Environment Configuration

**File**: `backend/.env`

```bash
# OpenAI Configuration
OPENAI_API_KEY=sk-...your-key-here...
OPENAI_MODEL=gpt-4o-mini

# Database (existing)
DATABASE_URL=postgresql://...

# JWT (existing)
BETTER_AUTH_SECRET=...
```

---

## Step 8: Testing

### Test MCP Tools

```bash
cd backend
pytest tests/unit/test_mcp_tools.py -v
```

### Test Chat Endpoint

```bash
pytest tests/integration/test_chat_api.py -v
```

### Manual Testing

```bash
# Start backend
cd backend
uvicorn src.main:app --reload

# Start frontend
cd frontend
npm run dev

# Open browser to http://localhost:3000/chat
# Try: "remind me to buy groceries"
```

---

## Common Issues

### Issue 1: OpenAI API Key Invalid
**Solution**: Verify API key in `.env` and restart backend

### Issue 2: Database Connection Error
**Solution**: Check DATABASE_URL and ensure migrations applied

### Issue 3: Agent Not Calling Tools
**Solution**: Verify tool definitions match OpenAI function calling format

### Issue 4: Cross-User Data Access
**Solution**: Verify AgentService wraps tools with correct user_id

---

## Next Steps

1. Implement SSE streaming for better UX (see `contracts/chat-api.md`)
2. Add rate limiting (60 req/min per user)
3. Implement conversation history UI
4. Add typing indicators and loading states
5. Deploy to production with monitoring

---

## Resources

- [OpenAI Agents SDK Documentation](https://platform.openai.com/docs/agents)
- [MCP SDK Documentation](https://modelcontextprotocol.io/docs)
- [FastAPI StreamingResponse](https://fastapi.tiangolo.com/advanced/custom-response/#streamingresponse)
- [Constitution v1.1.0](../../.specify/memory/constitution.md)
