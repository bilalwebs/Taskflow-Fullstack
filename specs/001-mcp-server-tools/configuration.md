# Configuration Guide: MCP Server & Tools

**Feature**: MCP Server & Tools for AI Agent Task Management
**Version**: 1.0.0
**Last Updated**: 2026-02-03

## Overview

This guide documents all configuration options, environment variables, and settings for the MCP Server & Tools feature.

## Environment Variables

### Required Variables

#### Database Configuration

```bash
# Neon PostgreSQL connection string
DATABASE_URL=postgresql://user:password@host/database?sslmode=require

# Example:
DATABASE_URL=postgresql://user:pass@ep-cool-name-123456.us-east-2.aws.neon.tech/neondb?sslmode=require
```

**Format**: `postgresql://[user]:[password]@[host]/[database]?sslmode=require`
**Required**: Yes
**Default**: None

#### OpenAI Configuration

```bash
# OpenAI API key for AI agent functionality
OPENAI_API_KEY=sk-proj-...

# OpenAI model to use
OPENAI_MODEL=gpt-4
```

**OPENAI_API_KEY**:
- Required: Yes
- Format: `sk-proj-...` or `sk-...`
- Obtain from: https://platform.openai.com/api-keys

**OPENAI_MODEL**:
- Required: No
- Default: `gpt-4`
- Options: `gpt-4`, `gpt-4-turbo`, `gpt-3.5-turbo`

#### Authentication Configuration

```bash
# JWT secret for token verification
JWT_SECRET=your-secure-random-string-here

# Better Auth secret
BETTER_AUTH_SECRET=your-better-auth-secret-here
```

**JWT_SECRET**:
- Required: Yes
- Format: Random string (min 32 characters)
- Generate: `openssl rand -hex 32`

**BETTER_AUTH_SECRET**:
- Required: Yes
- Format: Random string (min 32 characters)
- Generate: `openssl rand -hex 32`

### Optional Variables

#### Application Configuration

```bash
# Environment mode
ENVIRONMENT=production
# Options: development, staging, production
# Default: development

# Log level
LOG_LEVEL=INFO
# Options: DEBUG, INFO, WARNING, ERROR, CRITICAL
# Default: INFO

# CORS allowed origins (comma-separated)
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
# Default: http://localhost:3000
```

#### Database Connection Pool

```bash
# Maximum number of connections in pool
DB_POOL_SIZE=20
# Default: 10
# Recommended: 20 for production

# Maximum overflow connections
DB_MAX_OVERFLOW=10
# Default: 5
# Recommended: 10 for production

# Connection timeout (seconds)
DB_POOL_TIMEOUT=30
# Default: 30
# Range: 10-60

# Connection recycle time (seconds)
DB_POOL_RECYCLE=3600
# Default: 3600 (1 hour)
# Recommended: 3600 for Neon serverless
```

#### Performance Configuration

```bash
# Agent timeout (seconds)
AGENT_TIMEOUT=30
# Default: 30
# Range: 10-120

# Maximum conversation history length
MAX_CONVERSATION_HISTORY=20
# Default: 20
# Range: 5-50

# Rate limit (requests per minute)
RATE_LIMIT=60
# Default: 60
# Range: 10-1000
```

#### Monitoring Configuration

```bash
# Sentry DSN for error tracking
SENTRY_DSN=https://...@sentry.io/...
# Required: No
# Default: None

# Enable performance monitoring
ENABLE_PERFORMANCE_MONITORING=true
# Default: false

# Enable query logging
ENABLE_QUERY_LOGGING=false
# Default: false (enable only for debugging)
```

## Configuration Files

### pytest.ini

Location: `backend/pytest.ini`

```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts =
    -v
    --strict-markers
    --tb=short
    --cov=src
    --cov-report=term-missing
    --cov-report=html
markers =
    unit: Unit tests
    integration: Integration tests
    contract: Contract tests
    security: Security tests
    performance: Performance tests
```

### alembic.ini

Location: `backend/alembic.ini`

```ini
[alembic]
script_location = alembic
sqlalchemy.url = ${DATABASE_URL}

[loggers]
keys = root,sqlalchemy,alembic

[handlers]
keys = console

[formatters]
keys = generic

[logger_root]
level = WARN
handlers = console

[logger_sqlalchemy]
level = WARN
handlers =
qualname = sqlalchemy.engine

[logger_alembic]
level = INFO
handlers =
qualname = alembic

[handler_console]
class = StreamHandler
args = (sys.stderr,)
level = NOTSET
formatter = generic

[formatter_generic]
format = %(levelname)-5.5s [%(name)s] %(message)s
```

## Configuration by Environment

### Development

```bash
ENVIRONMENT=development
LOG_LEVEL=DEBUG
DB_POOL_SIZE=5
ENABLE_QUERY_LOGGING=true
CORS_ORIGINS=http://localhost:3000
```

### Staging

```bash
ENVIRONMENT=staging
LOG_LEVEL=INFO
DB_POOL_SIZE=10
ENABLE_PERFORMANCE_MONITORING=true
CORS_ORIGINS=https://staging.yourdomain.com
```

### Production

```bash
ENVIRONMENT=production
LOG_LEVEL=WARNING
DB_POOL_SIZE=20
DB_MAX_OVERFLOW=10
ENABLE_PERFORMANCE_MONITORING=true
SENTRY_DSN=https://...@sentry.io/...
CORS_ORIGINS=https://yourdomain.com
```

## Security Best Practices

### Secret Management

1. **Never commit secrets to version control**
   - Add `.env*` to `.gitignore`
   - Use environment-specific files (`.env.development`, `.env.production`)

2. **Use secret management services**
   - AWS Secrets Manager
   - HashiCorp Vault
   - Railway/Vercel environment variables

3. **Rotate secrets regularly**
   - JWT_SECRET: Every 90 days
   - BETTER_AUTH_SECRET: Every 90 days
   - OPENAI_API_KEY: As needed

### Database Security

1. **Use SSL/TLS connections**
   - Always include `?sslmode=require` in DATABASE_URL
   - Verify SSL certificate in production

2. **Limit database permissions**
   - Use dedicated database user for application
   - Grant only necessary permissions (SELECT, INSERT, UPDATE, DELETE)

3. **Connection pooling**
   - Configure appropriate pool size for load
   - Set connection timeout to prevent exhaustion

## Validation

### Verify Configuration

```bash
# Check environment variables
python -c "import os; print('DATABASE_URL:', 'SET' if os.getenv('DATABASE_URL') else 'MISSING')"
python -c "import os; print('OPENAI_API_KEY:', 'SET' if os.getenv('OPENAI_API_KEY') else 'MISSING')"
python -c "import os; print('JWT_SECRET:', 'SET' if os.getenv('JWT_SECRET') else 'MISSING')"

# Test database connection
python -c "from src.database import engine; engine.connect(); print('Database: OK')"

# Test OpenAI connection
python -c "from openai import OpenAI; client = OpenAI(); print('OpenAI: OK')"
```

### Configuration Checklist

- [ ] All required environment variables set
- [ ] Database connection successful
- [ ] OpenAI API key valid
- [ ] JWT secret configured (min 32 chars)
- [ ] CORS origins configured correctly
- [ ] Connection pool sized appropriately
- [ ] Logging level appropriate for environment
- [ ] Secrets not committed to version control
- [ ] SSL/TLS enabled for database
- [ ] Error monitoring configured (production)

## Troubleshooting

### Common Issues

**Issue**: Database connection fails
- **Solution**: Verify DATABASE_URL format and credentials
- **Check**: `psql $DATABASE_URL -c "SELECT 1"`

**Issue**: OpenAI API errors
- **Solution**: Verify OPENAI_API_KEY is valid
- **Check**: `curl https://api.openai.com/v1/models -H "Authorization: Bearer $OPENAI_API_KEY"`

**Issue**: JWT authentication fails
- **Solution**: Ensure JWT_SECRET matches between frontend and backend
- **Check**: Verify secret length (min 32 characters)

## References

- [Neon PostgreSQL Documentation](https://neon.tech/docs)
- [OpenAI API Documentation](https://platform.openai.com/docs)
- [FastAPI Configuration](https://fastapi.tiangolo.com/advanced/settings/)
- [SQLModel Documentation](https://sqlmodel.tiangolo.com/)
