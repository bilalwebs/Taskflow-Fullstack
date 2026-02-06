# MCP Tool Contracts

**Feature**: 002-ai-agent-behavior
**Date**: 2026-02-03
**Version**: 1.0

## Overview

This document defines the 6 MCP tools that enable the AI agent to perform task operations. All tools enforce user_id scoping and return structured results suitable for agent reasoning.

---

## Tool 1: list_tasks

**Purpose**: Retrieve all tasks for the authenticated user.

**Parameters**: None (user_id pre-bound by AgentService)

**Returns**:
```json
{
  "tasks": [
    {
      "id": 123,
      "title": "Buy groceries",
      "description": "Milk, eggs, bread",
      "completed": false,
      "created_at": "2026-02-03T10:00:00Z",
      "updated_at": "2026-02-03T10:00:00Z"
    }
  ],
  "total": 1,
  "completed_count": 0,
  "pending_count": 1
}
```

**Error Cases**:
- Database connection failure: Returns error with message
- No tasks found: Returns empty array (not an error)

**Example Usage**:
```
User: "What are my tasks?"
Agent: Calls list_tasks() → Receives task list → Responds conversationally
```

---

## Tool 2: create_task

**Purpose**: Create a new task for the authenticated user.

**Parameters**:
```json
{
  "title": "string (required, 1-200 chars)",
  "description": "string (optional, max 2000 chars)"
}
```

**Returns**:
```json
{
  "task": {
    "id": 124,
    "title": "Buy groceries",
    "description": "Milk, eggs, bread",
    "completed": false,
    "created_at": "2026-02-03T10:30:00Z",
    "updated_at": "2026-02-03T10:30:00Z"
  },
  "status": "success"
}
```

**Error Cases**:
- Empty title: Returns error "Title is required"
- Title too long: Returns error "Title exceeds 200 characters"
- Database error: Returns error with message

**Example Usage**:
```
User: "Remind me to buy groceries"
Agent: Calls create_task(title="Buy groceries") → Confirms creation
```

---

## Tool 3: get_task

**Purpose**: Retrieve a specific task by ID.

**Parameters**:
```json
{
  "task_id": "integer (required)"
}
```

**Returns**:
```json
{
  "task": {
    "id": 123,
    "title": "Buy groceries",
    "description": "Milk, eggs, bread",
    "completed": false,
    "created_at": "2026-02-03T10:00:00Z",
    "updated_at": "2026-02-03T10:00:00Z"
  }
}
```

**Error Cases**:
- Task not found: Returns error "Task not found"
- Task belongs to different user: Returns error "Task not found" (security)
- Invalid task_id: Returns error "Invalid task ID"

**Example Usage**:
```
User: "Show me details of task 123"
Agent: Calls get_task(task_id=123) → Returns task details
```

---

## Tool 4: update_task

**Purpose**: Update an existing task's title or description.

**Parameters**:
```json
{
  "task_id": "integer (required)",
  "title": "string (optional, 1-200 chars)",
  "description": "string (optional, max 2000 chars)"
}
```

**Returns**:
```json
{
  "task": {
    "id": 123,
    "title": "Buy groceries and cook dinner",
    "description": "Updated description",
    "completed": false,
    "created_at": "2026-02-03T10:00:00Z",
    "updated_at": "2026-02-03T10:35:00Z"
  },
  "status": "success"
}
```

**Error Cases**:
- Task not found: Returns error "Task not found"
- Empty title: Returns error "Title cannot be empty"
- Title too long: Returns error "Title exceeds 200 characters"
- No fields to update: Returns error "No fields provided to update"

**Example Usage**:
```
User: "Change the groceries task to include cooking dinner"
Agent: Calls update_task(task_id=123, title="Buy groceries and cook dinner")
```

---

## Tool 5: delete_task

**Purpose**: Permanently delete a task.

**Parameters**:
```json
{
  "task_id": "integer (required)"
}
```

**Returns**:
```json
{
  "status": "success",
  "message": "Task deleted successfully",
  "deleted_task_id": 123
}
```

**Error Cases**:
- Task not found: Returns error "Task not found"
- Task belongs to different user: Returns error "Task not found" (security)
- Database error: Returns error with message

**Example Usage**:
```
User: "Delete the groceries task"
Agent: Calls delete_task(task_id=123) → Confirms deletion
```

---

## Tool 6: mark_complete

**Purpose**: Toggle task completion status (complete ↔ incomplete).

**Parameters**:
```json
{
  "task_id": "integer (required)"
}
```

**Returns**:
```json
{
  "task": {
    "id": 123,
    "title": "Buy groceries",
    "description": "Milk, eggs, bread",
    "completed": true,
    "created_at": "2026-02-03T10:00:00Z",
    "updated_at": "2026-02-03T10:40:00Z"
  },
  "status": "success",
  "action": "marked_complete"
}
```

**Error Cases**:
- Task not found: Returns error "Task not found"
- Task belongs to different user: Returns error "Task not found" (security)
- Database error: Returns error with message

**Example Usage**:
```
User: "I finished buying groceries"
Agent: Calls mark_complete(task_id=123) → Confirms completion
```

---

## Security Model

All tools implement the following security pattern:

1. **User Scoping**: Tools receive pre-bound user_id from AgentService
2. **Ownership Validation**: All queries filter by user_id
3. **Error Masking**: Cross-user access returns "not found" (not "forbidden")
4. **No Direct Access**: Agent cannot modify user_id parameter

**Implementation Pattern**:
```python
# Internal tool with explicit user_id
@mcp.tool()
async def _list_tasks_internal(ctx: Context, user_id: int):
    session = ctx.db_engine.session()
    tasks = session.query(Task).filter(Task.user_id == user_id).all()
    return {"tasks": [t.dict() for t in tasks]}

# AgentService wraps with user_id pre-bound
class AgentService:
    def __init__(self, user_id: int):
        self.user_id = user_id

    def create_user_scoped_tools(self):
        async def list_tasks():  # Agent sees this
            return await _list_tasks_internal(user_id=self.user_id)
        return [list_tasks, ...]
```

---

## Tool Selection Logic

The AI agent selects tools based on user intent classification:

| User Intent | Tool(s) Called | Example Phrases |
|-------------|----------------|-----------------|
| View tasks | list_tasks | "show my tasks", "what do I need to do" |
| Create task | create_task | "remind me to", "add task", "I need to" |
| Complete task | list_tasks → mark_complete | "I finished", "mark as done", "completed" |
| Update task | list_tasks → update_task | "change the task", "update description" |
| Delete task | list_tasks → delete_task | "delete task", "remove", "cancel" |
| Get details | get_task | "show task 123", "details of task" |

**Multi-Step Pattern**:
1. User references task by title/keywords (not ID)
2. Agent calls list_tasks to find matching tasks
3. Agent identifies correct task from results
4. Agent calls operation tool (mark_complete, update_task, delete_task)

---

## Performance Characteristics

- **Execution Time**: <50ms per tool call (database query)
- **Concurrent Calls**: Tools are stateless, support unlimited concurrency
- **Database Load**: Indexed queries on user_id for optimal performance
- **Error Handling**: All errors return structured messages for agent interpretation

---

## Testing Requirements

Each tool must have:
1. **Unit Tests**: Verify correct behavior with valid inputs
2. **Security Tests**: Verify user_id scoping prevents cross-user access
3. **Error Tests**: Verify all error cases return appropriate messages
4. **Integration Tests**: Verify tools work with real database

**Example Test**:
```python
def test_list_tasks_user_isolation():
    # User 1 creates task
    create_task(user_id=1, title="User 1 task")

    # User 2 should not see User 1's task
    result = list_tasks(user_id=2)
    assert len(result["tasks"]) == 0
```

---

## Summary

Six MCP tools provide complete task management functionality with strict user isolation. All tools return structured results suitable for agent reasoning and natural language response generation.
