# Monitoring and Logging Guide: MCP Server & Tools

**Feature**: MCP Server & Tools for AI Agent Task Management
**Version**: 1.0.0
**Last Updated**: 2026-02-03

## Overview

This guide provides comprehensive monitoring and logging strategies for the MCP Server & Tools feature in production environments.

## Monitoring Strategy

### Key Metrics to Monitor

#### Application Metrics

1. **Request Metrics**
   - Total requests per minute
   - Request success rate (%)
   - Request failure rate (%)
   - Average response time (ms)
   - P95/P99 response time (ms)

2. **Tool Execution Metrics**
   - Tool invocation count by type
   - Tool success rate by type
   - Tool execution time by type
   - Tool error rate by type

3. **Agent Metrics**
   - Agent invocations per minute
   - Agent timeout rate
   - Average conversation length
   - Token usage per request

#### Database Metrics

1. **Connection Pool**
   - Active connections
   - Idle connections
   - Connection wait time
   - Pool exhaustion events

2. **Query Performance**
   - Query execution time
   - Slow query count (>100ms)
   - Failed query count
   - Deadlock count

3. **Data Metrics**
   - Total tasks count
   - Tasks created per hour
   - Tasks completed per hour
   - Active users count

#### System Metrics

1. **Resource Usage**
   - CPU utilization (%)
   - Memory usage (MB)
   - Disk I/O
   - Network I/O

2. **Error Rates**
   - 4xx error rate
   - 5xx error rate
   - Exception count
   - Timeout count

## Logging Configuration

### Log Levels

```python
# src/logging_config.py

import logging
import sys
from datetime import datetime

def setup_logging(log_level: str = "INFO"):
    """Configure application logging."""

    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)

    # Root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level))
    root_logger.addHandler(console_handler)

    return root_logger
```

### Structured Logging

```python
# src/structured_logging.py

import json
import logging
from typing import Dict, Any

class StructuredLogger:
    """Structured JSON logger for production."""

    def __init__(self, name: str):
        self.logger = logging.getLogger(name)

    def log_event(self, event: str, level: str = "INFO", **kwargs):
        """Log structured event."""
        log_data = {
            "event": event,
            "timestamp": datetime.utcnow().isoformat(),
            **kwargs
        }

        log_method = getattr(self.logger, level.lower())
        log_method(json.dumps(log_data))

    def log_tool_execution(self, tool_name: str, user_id: int,
                          duration_ms: float, status: str):
        """Log tool execution."""
        self.log_event(
            "tool_execution",
            level="INFO",
            tool_name=tool_name,
            user_id=user_id,
            duration_ms=duration_ms,
            status=status
        )

    def log_error(self, error: Exception, context: Dict[str, Any]):
        """Log error with context."""
        self.log_event(
            "error",
            level="ERROR",
            error_type=type(error).__name__,
            error_message=str(error),
            context=context
        )
```

### Log Categories

1. **Request Logs**
   ```json
   {
     "event": "http_request",
     "method": "POST",
     "path": "/chat",
     "user_id": 123,
     "status_code": 200,
     "duration_ms": 245
   }
   ```

2. **Tool Execution Logs**
   ```json
   {
     "event": "tool_execution",
     "tool_name": "create_task",
     "user_id": 123,
     "duration_ms": 45,
     "status": "success"
   }
   ```

3. **Error Logs**
   ```json
   {
     "event": "error",
     "error_type": "DatabaseError",
     "error_message": "Connection timeout",
     "user_id": 123,
     "context": {"tool": "list_tasks"}
   }
   ```

4. **Performance Logs**
   ```json
   {
     "event": "slow_query",
     "query": "SELECT * FROM tasks WHERE user_id = ?",
     "duration_ms": 523,
     "threshold_ms": 100
   }
   ```

## Monitoring Tools

### Sentry (Error Tracking)

```python
# src/main.py

import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration

# Initialize Sentry
sentry_sdk.init(
    dsn=os.getenv("SENTRY_DSN"),
    integrations=[FastApiIntegration()],
    traces_sample_rate=0.1,
    environment=os.getenv("ENVIRONMENT", "production")
)
```

**Configuration:**
- Set `SENTRY_DSN` environment variable
- Configure sample rate (0.1 = 10% of requests)
- Set environment (production, staging, development)

**Alerts:**
- New error types
- Error rate > 1%
- Specific error patterns

### Prometheus (Metrics)

```python
# src/metrics.py

from prometheus_client import Counter, Histogram, Gauge

# Request metrics
request_count = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

request_duration = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration',
    ['method', 'endpoint']
)

# Tool metrics
tool_execution_count = Counter(
    'tool_executions_total',
    'Total tool executions',
    ['tool_name', 'status']
)

tool_execution_duration = Histogram(
    'tool_execution_duration_seconds',
    'Tool execution duration',
    ['tool_name']
)

# Database metrics
db_connections_active = Gauge(
    'db_connections_active',
    'Active database connections'
)
```

### Grafana (Dashboards)

**Dashboard 1: Application Overview**
- Request rate (requests/min)
- Error rate (%)
- Response time (P50, P95, P99)
- Active users

**Dashboard 2: Tool Performance**
- Tool execution count by type
- Tool success rate by type
- Tool execution time by type
- Tool error distribution

**Dashboard 3: Database Health**
- Connection pool usage
- Query performance
- Slow query count
- Database errors

**Dashboard 4: System Resources**
- CPU usage
- Memory usage
- Disk I/O
- Network I/O

## Alerting Rules

### Critical Alerts (Page On-Call)

1. **Service Down**
   - Condition: Health check fails for 2 minutes
   - Action: Page on-call engineer immediately

2. **High Error Rate**
   - Condition: Error rate > 5% for 5 minutes
   - Action: Page on-call engineer

3. **Database Connection Pool Exhausted**
   - Condition: No available connections for 1 minute
   - Action: Page on-call engineer

4. **Agent Timeout Rate High**
   - Condition: Timeout rate > 10% for 5 minutes
   - Action: Page on-call engineer

### Warning Alerts (Slack Notification)

1. **Elevated Error Rate**
   - Condition: Error rate > 1% for 10 minutes
   - Action: Notify team channel

2. **Slow Response Time**
   - Condition: P95 response time > 1000ms for 10 minutes
   - Action: Notify team channel

3. **High Database Load**
   - Condition: Active connections > 80% of pool for 5 minutes
   - Action: Notify team channel

4. **Disk Space Low**
   - Condition: Disk usage > 80%
   - Action: Notify team channel

## Log Aggregation

### CloudWatch Logs (AWS)

```bash
# Install CloudWatch agent
wget https://s3.amazonaws.com/amazoncloudwatch-agent/ubuntu/amd64/latest/amazon-cloudwatch-agent.deb
sudo dpkg -i amazon-cloudwatch-agent.deb

# Configure log groups
aws logs create-log-group --log-group-name /mcp-server/application
aws logs create-log-group --log-group-name /mcp-server/errors
```

### ELK Stack (Self-Hosted)

```yaml
# docker-compose.yml for ELK

version: '3.8'

services:
  elasticsearch:
    image: elasticsearch:8.11.0
    environment:
      - discovery.type=single-node
    ports:
      - "9200:9200"

  logstash:
    image: logstash:8.11.0
    volumes:
      - ./logstash.conf:/usr/share/logstash/pipeline/logstash.conf
    ports:
      - "5000:5000"

  kibana:
    image: kibana:8.11.0
    ports:
      - "5601:5601"
```

## Performance Monitoring

### Application Performance Monitoring (APM)

```python
# src/apm.py

from opentelemetry import trace
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

# Initialize tracer
tracer = trace.get_tracer(__name__)

# Instrument FastAPI
FastAPIInstrumentor.instrument_app(app)

# Custom spans
@tracer.start_as_current_span("tool_execution")
def execute_tool(tool_name: str, **kwargs):
    span = trace.get_current_span()
    span.set_attribute("tool.name", tool_name)
    # ... tool execution logic
```

### Database Query Monitoring

```python
# src/database.py

from sqlalchemy import event
from sqlalchemy.engine import Engine
import time

@event.listens_for(Engine, "before_cursor_execute")
def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    conn.info.setdefault('query_start_time', []).append(time.time())

@event.listens_for(Engine, "after_cursor_execute")
def after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    total = time.time() - conn.info['query_start_time'].pop(-1)
    if total > 0.1:  # Log slow queries (>100ms)
        logger.warning(f"Slow query: {statement[:100]} - {total*1000:.2f}ms")
```

## Health Checks

### Endpoint Implementation

```python
# src/main.py

@app.get("/health")
async def health_check():
    """Health check endpoint."""

    # Check database
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        db_status = "connected"
    except Exception as e:
        db_status = f"error: {str(e)}"

    # Check OpenAI
    try:
        client = OpenAI()
        client.models.list()
        openai_status = "connected"
    except Exception as e:
        openai_status = f"error: {str(e)}"

    return {
        "status": "healthy" if db_status == "connected" else "unhealthy",
        "database": db_status,
        "openai": openai_status,
        "timestamp": datetime.utcnow().isoformat()
    }
```

### Monitoring Health Checks

```bash
# Kubernetes liveness probe
livenessProbe:
  httpGet:
    path: /health
    port: 8000
  initialDelaySeconds: 30
  periodSeconds: 10

# Kubernetes readiness probe
readinessProbe:
  httpGet:
    path: /health
    port: 8000
  initialDelaySeconds: 5
  periodSeconds: 5
```

## Monitoring Checklist

- [ ] Sentry configured for error tracking
- [ ] Prometheus metrics exposed
- [ ] Grafana dashboards created
- [ ] Critical alerts configured
- [ ] Warning alerts configured
- [ ] Log aggregation setup
- [ ] Health check endpoint implemented
- [ ] APM instrumentation added
- [ ] Database query monitoring enabled
- [ ] On-call rotation configured

## References

- [Sentry Documentation](https://docs.sentry.io/)
- [Prometheus Documentation](https://prometheus.io/docs/)
- [Grafana Documentation](https://grafana.com/docs/)
- [OpenTelemetry Documentation](https://opentelemetry.io/docs/)
