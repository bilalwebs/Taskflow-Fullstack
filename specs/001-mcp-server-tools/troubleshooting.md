# Troubleshooting Guide: MCP Server & Tools

**Feature**: MCP Server & Tools for AI Agent Task Management
**Version**: 1.0.0
**Last Updated**: 2026-02-03

## Overview

This guide provides solutions to common issues encountered when deploying and operating the MCP Server & Tools feature.

## Common Issues

### Database Connection Issues

#### Issue: "Connection refused" or "Connection timeout"

**Symptoms:**
- Application fails to start
- Error: `sqlalchemy.exc.OperationalError: could not connect to server`

**Causes:**
- Incorrect DATABASE_URL
- Database server not running
- Network/firewall blocking connection
- SSL/TLS configuration issue

**Solutions:**

1. **Verify DATABASE_URL format:**
   ```bash
   echo $DATABASE_URL
   # Should be: postgresql://user:pass@host/db?sslmode=require
   ```

2. **Test connection manually:**
   ```bash
   psql $DATABASE_URL -c "SELECT 1"
   ```

3. **Check SSL requirement:**
   ```bash
   # Neon requires SSL - ensure ?sslmode=require is present
   DATABASE_URL="postgresql://...?sslmode=require"
   ```

4. **Verify network connectivity:**
   ```bash
   # Extract host from DATABASE_URL
   HOST=$(echo $DATABASE_URL | sed -n 's/.*@\([^/]*\).*/\1/p')
   ping $HOST
   telnet $HOST 5432
   ```

#### Issue: "Connection pool exhausted"

**Symptoms:**
- Requests timeout
- Error: `TimeoutError: QueuePool limit of size X overflow Y reached`

**Causes:**
- Too many concurrent requests
- Connection leaks (not properly closed)
- Pool size too small

**Solutions:**

1. **Increase pool size:**
   ```bash
   # In .env
   DB_POOL_SIZE=20
   DB_MAX_OVERFLOW=10
   ```

2. **Check for connection leaks:**
   ```python
   # Monitor active connections
   from src.database import engine
   print(engine.pool.status())
   ```

3. **Implement connection timeout:**
   ```bash
   DB_POOL_TIMEOUT=30
   DB_POOL_RECYCLE=3600
   ```

### Authentication Issues

#### Issue: "Unauthorized" (401) on chat endpoint

**Symptoms:**
- All requests return 401
- Error: `{"detail": "Not authenticated"}`

**Causes:**
- Missing Authorization header
- Invalid JWT token
- JWT_SECRET mismatch
- Token expired

**Solutions:**

1. **Verify Authorization header:**
   ```bash
   curl -X POST https://api.example.com/chat \
     -H "Authorization: Bearer YOUR_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"user_id": 1, "message": "test"}'
   ```

2. **Check JWT_SECRET:**
   ```bash
   # Ensure frontend and backend use same secret
   echo $JWT_SECRET
   ```

3. **Verify token format:**
   ```bash
   # Token should be: eyJ... (JWT format)
   # Decode token to check expiration
   echo $TOKEN | cut -d. -f2 | base64 -d
   ```

4. **Generate new token:**
   ```python
   # Use Better Auth to generate fresh token
   # Ensure user_id matches request body
   ```

#### Issue: "Forbidden" (403) - User ID mismatch

**Symptoms:**
- Request authenticated but rejected
- Error: `{"detail": "User ID mismatch"}`

**Causes:**
- user_id in request body doesn't match JWT token
- Token contains wrong user_id

**Solutions:**

1. **Verify user_id consistency:**
   ```bash
   # Decode JWT to check user_id
   # Ensure request body user_id matches
   ```

2. **Check token generation:**
   ```python
   # Ensure Better Auth generates token with correct user_id
   ```

### OpenAI API Issues

#### Issue: "OpenAI API error" or "Rate limit exceeded"

**Symptoms:**
- Agent requests fail
- Error: `openai.error.RateLimitError`

**Causes:**
- Invalid OPENAI_API_KEY
- Rate limit exceeded
- Insufficient quota
- Network issues

**Solutions:**

1. **Verify API key:**
   ```bash
   curl https://api.openai.com/v1/models \
     -H "Authorization: Bearer $OPENAI_API_KEY"
   ```

2. **Check quota and limits:**
   - Visit: https://platform.openai.com/account/usage
   - Verify billing and limits

3. **Implement retry logic:**
   ```python
   # Add exponential backoff for rate limits
   from tenacity import retry, wait_exponential

   @retry(wait=wait_exponential(multiplier=1, min=4, max=10))
   def call_openai_api():
       # API call here
   ```

4. **Use different model:**
   ```bash
   # Switch to gpt-3.5-turbo if gpt-4 rate limited
   OPENAI_MODEL=gpt-3.5-turbo
   ```

#### Issue: "Agent timeout"

**Symptoms:**
- Requests take too long
- Error: `TimeoutError: Agent execution exceeded 30 seconds`

**Causes:**
- OpenAI API slow response
- Complex agent reasoning
- Network latency

**Solutions:**

1. **Increase timeout:**
   ```bash
   AGENT_TIMEOUT=60
   ```

2. **Optimize prompts:**
   - Reduce conversation history length
   - Simplify tool descriptions

3. **Use faster model:**
   ```bash
   OPENAI_MODEL=gpt-3.5-turbo
   ```

### Tool Execution Issues

#### Issue: "Task not found" when it exists

**Symptoms:**
- User can create tasks but not retrieve them
- Error: `{"status": "error", "error": "Task not found"}`

**Causes:**
- User ID mismatch
- Task belongs to different user
- Database query filtering issue

**Solutions:**

1. **Verify user_id in context:**
   ```python
   # Check MCPContext.user_id matches task.user_id
   print(f"Context user_id: {ctx.user_id}")
   print(f"Task user_id: {task.user_id}")
   ```

2. **Check database query:**
   ```python
   # Ensure query filters by user_id
   statement = select(Task).where(
       Task.id == task_id,
       Task.user_id == ctx.user_id  # Critical!
   )
   ```

3. **Verify JWT token user_id:**
   ```bash
   # Decode token and check user_id claim
   ```

#### Issue: "Validation error" on valid input

**Symptoms:**
- Valid task creation fails
- Error: `{"status": "error", "error": "Title exceeds 200 characters"}`

**Causes:**
- Input encoding issues
- Unicode character counting
- Whitespace handling

**Solutions:**

1. **Check character encoding:**
   ```python
   # Ensure UTF-8 encoding
   title = title.encode('utf-8').decode('utf-8')
   ```

2. **Trim whitespace:**
   ```python
   title = title.strip()
   ```

3. **Count characters correctly:**
   ```python
   # Use len() not byte length
   if len(title) > 200:
       raise ValidationError()
   ```

### Performance Issues

#### Issue: "Slow response times"

**Symptoms:**
- Requests take >1 second
- P95 latency >1000ms

**Causes:**
- Database query inefficiency
- Missing indexes
- N+1 query problem
- Large result sets

**Solutions:**

1. **Add database indexes:**
   ```sql
   CREATE INDEX idx_tasks_user_id ON tasks(user_id);
   CREATE INDEX idx_tasks_completed ON tasks(completed);
   ```

2. **Optimize queries:**
   ```python
   # Use select specific columns, not SELECT *
   statement = select(Task.id, Task.title, Task.completed)
   ```

3. **Enable query logging:**
   ```bash
   ENABLE_QUERY_LOGGING=true
   # Check logs for slow queries
   ```

4. **Implement caching:**
   ```python
   # Cache frequently accessed data
   from functools import lru_cache

   @lru_cache(maxsize=100)
   def get_user_tasks(user_id: int):
       # Query here
   ```

#### Issue: "High memory usage"

**Symptoms:**
- Memory usage grows over time
- Application crashes with OOM

**Causes:**
- Memory leaks
- Large conversation histories
- Connection pool not releasing

**Solutions:**

1. **Limit conversation history:**
   ```bash
   MAX_CONVERSATION_HISTORY=20
   ```

2. **Monitor memory:**
   ```python
   import psutil
   process = psutil.Process()
   print(f"Memory: {process.memory_info().rss / 1024 / 1024} MB")
   ```

3. **Restart workers periodically:**
   ```bash
   # Gunicorn max requests
   gunicorn --max-requests 1000 --max-requests-jitter 50
   ```

### Deployment Issues

#### Issue: "Application won't start"

**Symptoms:**
- Container exits immediately
- Error in logs

**Causes:**
- Missing environment variables
- Port already in use
- Dependency issues

**Solutions:**

1. **Check environment variables:**
   ```bash
   docker exec container_name env | grep -E "DATABASE_URL|OPENAI_API_KEY|JWT_SECRET"
   ```

2. **Check port availability:**
   ```bash
   lsof -i :8000
   # Kill process if needed
   ```

3. **Verify dependencies:**
   ```bash
   pip list | grep -E "fastapi|sqlmodel|openai"
   ```

4. **Check logs:**
   ```bash
   docker logs container_name
   # or
   journalctl -u mcp-server -n 100
   ```

#### Issue: "Health check failing"

**Symptoms:**
- Container marked unhealthy
- Load balancer removes instance

**Causes:**
- Database connection issue
- Application not ready
- Health check timeout

**Solutions:**

1. **Test health endpoint:**
   ```bash
   curl http://localhost:8000/health
   ```

2. **Increase health check timeout:**
   ```yaml
   healthcheck:
     timeout: 10s
     interval: 30s
   ```

3. **Check application logs:**
   ```bash
   docker logs container_name | grep health
   ```

## Debugging Tools

### Enable Debug Logging

```bash
# Set log level to DEBUG
LOG_LEVEL=DEBUG

# Enable query logging
ENABLE_QUERY_LOGGING=true

# Restart application
```

### Database Query Analysis

```sql
-- Check slow queries (PostgreSQL)
SELECT query, calls, total_time, mean_time
FROM pg_stat_statements
ORDER BY mean_time DESC
LIMIT 10;

-- Check active connections
SELECT count(*) FROM pg_stat_activity;

-- Check table sizes
SELECT schemaname, tablename, pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename))
FROM pg_tables
WHERE schemaname = 'public';
```

### Application Metrics

```bash
# Check Prometheus metrics
curl http://localhost:8000/metrics

# Check active connections
curl http://localhost:8000/health | jq .database

# Check memory usage
docker stats container_name
```

## Getting Help

### Before Asking for Help

1. **Check logs:**
   ```bash
   docker logs container_name --tail 100
   ```

2. **Verify configuration:**
   ```bash
   # Check all environment variables are set
   env | grep -E "DATABASE|OPENAI|JWT"
   ```

3. **Test components individually:**
   - Database connection
   - OpenAI API
   - Health endpoint

4. **Review recent changes:**
   - Check git history
   - Review recent deployments

### Information to Provide

When reporting issues, include:

1. **Error message** (full stack trace)
2. **Environment** (production, staging, development)
3. **Configuration** (sanitized - no secrets!)
4. **Steps to reproduce**
5. **Expected vs actual behavior**
6. **Recent changes** (deployments, config updates)
7. **Logs** (relevant sections)

### Contact

- **Slack**: #mcp-server-support
- **Email**: devops@example.com
- **On-call**: PagerDuty escalation

## References

- [Deployment Guide](./deployment.md)
- [Configuration Guide](./configuration.md)
- [Monitoring Guide](./monitoring.md)
- [Neon PostgreSQL Troubleshooting](https://neon.tech/docs/troubleshooting)
- [FastAPI Debugging](https://fastapi.tiangolo.com/tutorial/debugging/)
