# Deployment Guide: MCP Server & Tools

**Feature**: MCP Server & Tools for AI Agent Task Management
**Version**: 1.0.0
**Last Updated**: 2026-02-03

## Overview

This guide provides step-by-step instructions for deploying the MCP Server & Tools feature to production environments.

## Prerequisites

### System Requirements
- Python 3.11 or higher
- PostgreSQL 14+ (Neon Serverless PostgreSQL recommended)
- 2GB RAM minimum (4GB recommended)
- 10GB disk space

### Required Services
- Neon PostgreSQL database (serverless)
- OpenAI API access (for AI agent functionality)
- Better Auth service (for user authentication)

### Required Credentials
- `DATABASE_URL`: Neon PostgreSQL connection string
- `OPENAI_API_KEY`: OpenAI API key
- `JWT_SECRET`: Secret key for JWT token verification
- `BETTER_AUTH_SECRET`: Better Auth secret key

## Deployment Steps

### 1. Environment Setup

Create a `.env.production` file with the following variables:

```bash
# Database Configuration
DATABASE_URL=postgresql://user:password@host/database?sslmode=require

# OpenAI Configuration
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4

# Authentication Configuration
JWT_SECRET=your-secure-jwt-secret-here
BETTER_AUTH_SECRET=your-better-auth-secret-here

# Application Configuration
ENVIRONMENT=production
LOG_LEVEL=INFO
CORS_ORIGINS=https://yourdomain.com

# Database Connection Pool
DB_POOL_SIZE=20
DB_MAX_OVERFLOW=10
DB_POOL_TIMEOUT=30
```

### 2. Database Migration

Run database migrations to create required tables:

```bash
# Navigate to backend directory
cd backend

# Run migrations
alembic upgrade head

# Verify tables created
psql $DATABASE_URL -c "\dt"
```

Expected tables:
- `users`
- `tasks`
- `messages`

### 3. Install Dependencies

```bash
# Install Python dependencies
pip install -r requirements.txt

# Verify installation
python -c "import fastapi, sqlmodel, openai; print('Dependencies OK')"
```

### 4. Run Tests

Before deployment, verify all tests pass:

```bash
# Run full test suite
pytest backend/tests/ --cov=backend/src --cov-report=html

# Verify coverage > 80%
# Check coverage report in htmlcov/index.html
```

### 5. Start Application

```bash
# Production mode with Gunicorn
gunicorn src.main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --timeout 120 \
  --access-logfile - \
  --error-logfile -
```

### 6. Verify Deployment

```bash
# Health check
curl https://your-domain.com/health

# Expected response:
# {"status": "healthy", "database": "connected"}

# Test MCP tools endpoint
curl https://your-domain.com/mcp/tools

# Expected: List of 6 MCP tools
```

## Docker Deployment

### Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY backend/src ./src

# Expose port
EXPOSE 8000

# Run application
CMD ["gunicorn", "src.main:app", \
     "--workers", "4", \
     "--worker-class", "uvicorn.workers.UvicornWorker", \
     "--bind", "0.0.0.0:8000"]
```

### Docker Compose

```yaml
version: '3.8'

services:
  backend:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - JWT_SECRET=${JWT_SECRET}
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
```

### Deploy with Docker

```bash
# Build image
docker build -t mcp-server:latest .

# Run container
docker run -d \
  --name mcp-server \
  -p 8000:8000 \
  --env-file .env.production \
  mcp-server:latest

# Verify running
docker ps
docker logs mcp-server
```

## Cloud Platform Deployment

### Vercel (Recommended for Next.js Frontend)

```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
vercel --prod
```

### Railway (Recommended for FastAPI Backend)

```bash
# Install Railway CLI
npm i -g @railway/cli

# Login
railway login

# Deploy
railway up
```

### AWS EC2

1. Launch EC2 instance (t3.medium recommended)
2. Install Docker
3. Clone repository
4. Run Docker Compose
5. Configure security groups (allow port 8000)
6. Setup SSL with Let's Encrypt

## Post-Deployment Verification

### 1. Functional Tests

```bash
# Test create_task
curl -X POST https://your-domain.com/chat \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"user_id": 1, "message": "Add a task to test deployment"}'

# Test list_tasks
curl -X POST https://your-domain.com/chat \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"user_id": 1, "message": "Show my tasks"}'
```

### 2. Performance Tests

```bash
# Run load test
cd backend/tests/load
locust -f locustfile.py --host=https://your-domain.com
```

### 3. Security Verification

- [ ] HTTPS enabled
- [ ] JWT authentication working
- [ ] CORS configured correctly
- [ ] Rate limiting enabled
- [ ] Error messages sanitized

## Rollback Procedure

If deployment fails:

```bash
# Docker rollback
docker stop mcp-server
docker rm mcp-server
docker run -d --name mcp-server mcp-server:previous-version

# Database rollback
alembic downgrade -1

# Verify rollback
curl https://your-domain.com/health
```

## Monitoring Setup

See [monitoring.md](./monitoring.md) for detailed monitoring configuration.

## Troubleshooting

See [troubleshooting.md](./troubleshooting.md) for common issues and solutions.

## Support

For deployment issues:
- Check logs: `docker logs mcp-server`
- Review error messages in monitoring dashboard
- Consult troubleshooting guide
- Contact DevOps team

## Checklist

- [ ] Environment variables configured
- [ ] Database migrations completed
- [ ] All tests passing
- [ ] Application deployed
- [ ] Health checks passing
- [ ] Monitoring configured
- [ ] SSL certificates installed
- [ ] Backup strategy implemented
- [ ] Rollback procedure tested
- [ ] Documentation updated
