# Research: AI Agent Behavior Implementation

**Feature**: 002-ai-agent-behavior
**Date**: 2026-02-03
**Status**: Complete

## Overview

This document consolidates research findings for implementing a conversational AI agent that manages tasks through natural language. Research focused on three critical technical decisions that impact architecture, performance, and user experience.

---

## Research Area 1: MCP Server Hosting Strategy

### Decision: Embedded MCP Server within FastAPI Process

**Rationale**: Host MCP tools directly within the FastAPI application process rather than as a separate service.

### Implementation Architecture

```python
# Internal MCP tools with explicit user_id parameter
@mcp.tool()
async def _list_tasks_internal(ctx: Context, user_id: int) -> list[dict]:
    """Internal tool - requires user_id parameter"""
    session = ctx.db_engine.session()
    tasks = session.query(Task).filter(Task.user_id == user_id).all()
    return [task.dict() for task in tasks]

# AgentService wraps tools with user_id pre-bound
class AgentService:
    def __init__(self, user_id: int, db_engine):
        self.user_id = user_id
        self.db_engine = db_engine

    def create_user_scoped_tools(self):
        """Create tools with user_id pre-bound for security"""
        async def list_tasks():  # Agent sees this signature
            return await _list_tasks_internal(
                ctx=Context(db_engine=self.db_engine),
                user_id=self.user_id
            )
        return [list_tasks, create_task, ...]
```

### Key Benefits

1. **Security-First Design**: User authentication enforced at FastAPI boundary
2. **Performance**: Direct function calls (<1ms overhead)
3. **Operational Simplicity**: Single process to deploy and monitor
4. **Stateless Architecture**: Tools create database sessions per-request

### Alternatives Considered

**Separate MCP Server Process** - Rejected due to security risks and unnecessary complexity.

---

## Research Area 2: OpenAI Model Selection

### Decision: GPT-4o-mini (Primary) with GPT-3.5-turbo (Fallback)

**Rationale**: GPT-4o-mini provides optimal balance of speed, accuracy, and cost for task management intent classification.

### Model Comparison

| Model | Speed | Cost (per 1M tokens) | Verdict |
|-------|-------|---------------------|---------|
| GPT-4o-mini | 1-2s | $0.15/$0.60 | **Recommended** |
| GPT-3.5-turbo | 1-3s | $0.50/$1.50 | **Fallback** |
| GPT-4-turbo | 3-5s | $10/$30 | Overkill |

### Cost Estimate
- 10,000 requests/day: ~$36/month with GPT-4o-mini
- Compare to GPT-4-turbo: ~$1,950/month (54x more expensive)

---

## Research Area 3: Message Streaming Implementation

### Decision: Server-Sent Events (SSE)

**Rationale**: SSE provides optimal balance of simplicity, user experience, and alignment with stateless architecture.

### Key Benefits

1. **Stateless-Friendly**: Each request is independent
2. **Simple Implementation**: Native browser and FastAPI support
3. **Industry Standard**: Same pattern as OpenAI, Anthropic APIs
4. **Progressive Rendering**: Users see responses as they generate

### Alternatives Considered

- **WebSocket**: Rejected (conflicts with stateless requirement)
- **Long Polling**: Rejected (poor UX, inefficient)

---

## Additional Decisions

- **Conversation Retention**: 90 days with soft delete
- **Rate Limiting**: 60 requests/minute per user (token bucket)
- **Audit Trail**: Log all tool invocations in messages metadata

---

## Summary

All research items resolved. Ready for Phase 1 design artifacts (data-model.md, contracts/, quickstart.md).
