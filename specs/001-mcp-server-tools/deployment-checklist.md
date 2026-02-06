# Deployment Checklist & Runbook

**Feature**: MCP Server & Tools for AI Agent Task Management
**Version**: 1.0.0
**Last Updated**: 2026-02-03

## Pre-Deployment Checklist

### Code Quality & Testing

- [ ] All unit tests passing (100% pass rate)
- [ ] All integration tests passing (100% pass rate)
- [ ] All contract tests passing (100% pass rate)
- [ ] All security tests passing (100% pass rate)
- [ ] Code coverage ≥ 80%
- [ ] No critical security vulnerabilities
- [ ] Code reviewed and approved
- [ ] All acceptance scenarios from spec.md covered by tests

### Configuration

- [ ] `.env.production` file created with all required variables
- [ ] `DATABASE_URL` configured and tested
- [ ] `OPENAI_API_KEY` configured and tested
- [ ] `JWT_SECRET` generated (min 32 chars) and configured
- [ ] `BETTER_AUTH_SECRET` generated (min 32 chars) and configured
- [ ] `CORS_ORIGINS` configured with production domains
- [ ] Database connection pool settings configured
- [ ] Logging level set to WARNING or ERROR
- [ ] Monitoring/error tracking configured (Sentry)

### Database

- [ ] Database migrations completed successfully
- [ ] Database indexes created
- [ ] Database connection tested from production environment
- [ ] Database backup strategy implemented
- [ ] Database connection pool tested under load

### Security

- [ ] SSL/TLS certificates installed and valid
- [ ] HTTPS enforced (no HTTP access)
- [ ] JWT authentication tested
- [ ] User data isolation verified
- [ ] Cross-user access prevention tested
- [ ] SQL injection prevention verified
- [ ] Error messages sanitized (no internal details exposed)
- [ ] Rate limiting configured
- [ ] Security headers configured (CORS, CSP, etc.)

### Infrastructure

- [ ] Production server/container provisioned
- [ ] Required ports opened (8000 or configured port)
- [ ] Firewall rules configured
- [ ] Load balancer configured (if applicable)
- [ ] Health check endpoint tested
- [ ] Auto-scaling configured (if applicable)
- [ ] Backup and disaster recovery plan in place

### Monitoring & Logging

- [ ] Application logging configured
- [ ] Error tracking configured (Sentry)
- [ ] Performance monitoring configured
- [ ] Database monitoring configured
- [ ] Alerting rules configured
- [ ] On-call rotation configured
- [ ] Dashboards created (Grafana/CloudWatch)
- [ ] Log aggregation configured

### Documentation

- [ ] API documentation complete and accurate
- [ ] Deployment guide reviewed
- [ ] Configuration guide reviewed
- [ ] Troubleshooting guide reviewed
- [ ] Monitoring guide reviewed
- [ ] Runbook created and tested

## Deployment Runbook

### Step 1: Pre-Deployment Verification

**Time**: 30 minutes before deployment

```bash
# 1. Verify all tests pass
cd backend
pytest tests/ --cov=src --cov-report=term

# 2. Verify code coverage
# Expected: ≥ 80% coverage

# 3. Check for security vulnerabilities
pip-audit

# 4. Verify environment configuration
python -c "import os; assert os.getenv('DATABASE_URL'), 'DATABASE_URL missing'"
python -c "import os; assert os.getenv('OPENAI_API_KEY'), 'OPENAI_API_KEY missing'"
python -c "import os; assert os.getenv('JWT_SECRET'), 'JWT_SECRET missing'"
```

**Checklist:**
- [ ] All tests passing
- [ ] Coverage ≥ 80%
- [ ] No security vulnerabilities
- [ ] All environment variables set

### Step 2: Database Preparation

**Time**: 15 minutes before deployment

```bash
# 1. Backup current database
pg_dump $DATABASE_URL > backup_$(date +%Y%m%d_%H%M%S).sql

# 2. Run migrations
alembic upgrade head

# 3. Verify migrations
alembic current

# 4. Test database connection
psql $DATABASE_URL -c "SELECT COUNT(*) FROM tasks;"
```

**Checklist:**
- [ ] Database backed up
- [ ] Migrations completed successfully
- [ ] Database connection verified

### Step 3: Build & Deploy Application

**Time**: Deployment window start

#### Option A: Docker Deployment

```bash
# 1. Build Docker image
docker build -t mcp-server:v1.0.0 .

# 2. Tag image
docker tag mcp-server:v1.0.0 mcp-server:latest

# 3. Stop old container (if exists)
docker stop mcp-server || true
docker rm mcp-server || true

# 4. Start new container
docker run -d \
  --name mcp-server \
  -p 8000:8000 \
  --env-file .env.production \
  --restart unless-stopped \
  mcp-server:v1.0.0

# 5. Verify container running
docker ps | grep mcp-server
docker logs mcp-server --tail 50
```

#### Option B: Direct Deployment

```bash
# 1. Pull latest code
git pull origin main

# 2. Install dependencies
pip install -r requirements.txt

# 3. Stop old service
sudo systemctl stop mcp-server

# 4. Start new service
sudo systemctl start mcp-server

# 5. Verify service running
sudo systemctl status mcp-server
```

**Checklist:**
- [ ] Application deployed
- [ ] Service/container running
- [ ] No errors in startup logs

### Step 4: Post-Deployment Verification

**Time**: Immediately after deployment

```bash
# 1. Health check
curl https://api.yourdomain.com/health
# Expected: {"status": "healthy", "database": "connected"}

# 2. Test authentication endpoint
curl -X POST https://api.yourdomain.com/api/auth/signin \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "TestPass123"}'
# Expected: 200 OK with JWT token

# 3. Test MCP tools endpoint
curl https://api.yourdomain.com/mcp/tools
# Expected: List of 6 tools

# 4. Test chat endpoint (with valid JWT)
curl -X POST https://api.yourdomain.com/chat \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"user_id": 1, "message": "List my tasks"}'
# Expected: 200 OK with agent response
```

**Checklist:**
- [ ] Health check passing
- [ ] Authentication working
- [ ] MCP tools accessible
- [ ] Chat endpoint responding
- [ ] No errors in logs

### Step 5: Smoke Tests

**Time**: 5-10 minutes after deployment

```bash
# Run automated smoke tests
pytest tests/smoke/ -v

# Or manual smoke tests:
# 1. Create task
# 2. List tasks
# 3. Mark task complete
# 4. Update task
# 5. Delete task
```

**Checklist:**
- [ ] Create task working
- [ ] List tasks working
- [ ] Mark complete working
- [ ] Update task working
- [ ] Delete task working
- [ ] User isolation verified

### Step 6: Monitoring Verification

**Time**: 10 minutes after deployment

```bash
# 1. Check application metrics
curl https://api.yourdomain.com/metrics

# 2. Verify logs flowing
# Check CloudWatch/ELK/Grafana for recent logs

# 3. Verify error tracking
# Check Sentry for any new errors

# 4. Check dashboards
# Open Grafana dashboards and verify data flowing
```

**Checklist:**
- [ ] Metrics being collected
- [ ] Logs flowing to aggregation service
- [ ] Error tracking active
- [ ] Dashboards showing data
- [ ] Alerts configured and active

## Rollback Procedure

### When to Rollback

Rollback immediately if:
- Health checks failing for >2 minutes
- Error rate >5%
- Critical functionality broken
- Database corruption detected
- Security vulnerability discovered

### Rollback Steps

**Time**: 5-10 minutes

```bash
# 1. Stop new deployment
docker stop mcp-server
# or
sudo systemctl stop mcp-server

# 2. Restore previous version
docker run -d \
  --name mcp-server \
  -p 8000:8000 \
  --env-file .env.production \
  mcp-server:previous-version
# or
git checkout previous-tag
sudo systemctl start mcp-server

# 3. Rollback database (if needed)
alembic downgrade -1
# or restore from backup
psql $DATABASE_URL < backup_file.sql

# 4. Verify rollback successful
curl https://api.yourdomain.com/health

# 5. Notify team
# Post in Slack: "Deployment rolled back due to [reason]"
```

**Checklist:**
- [ ] Previous version restored
- [ ] Database rolled back (if needed)
- [ ] Health checks passing
- [ ] Team notified
- [ ] Incident documented

## Post-Deployment Tasks

### Immediate (Within 1 hour)

- [ ] Monitor error rates for 1 hour
- [ ] Monitor response times
- [ ] Check for any user-reported issues
- [ ] Verify all critical paths working
- [ ] Update deployment log

### Within 24 Hours

- [ ] Review all logs for anomalies
- [ ] Check performance metrics
- [ ] Verify database performance
- [ ] Review error tracking dashboard
- [ ] Update documentation if needed
- [ ] Conduct post-deployment review meeting

### Within 1 Week

- [ ] Analyze performance trends
- [ ] Review user feedback
- [ ] Identify optimization opportunities
- [ ] Plan next iteration
- [ ] Update lessons learned

## Emergency Contacts

| Role | Name | Contact | Availability |
|------|------|---------|--------------|
| On-Call Engineer | TBD | PagerDuty | 24/7 |
| DevOps Lead | TBD | Slack/Phone | Business hours |
| Database Admin | TBD | Slack/Phone | Business hours |
| Security Lead | TBD | Slack/Phone | Business hours |

## Common Issues & Solutions

### Issue: Health check failing

**Symptoms**: `/health` endpoint returns 503 or times out

**Quick Fix:**
```bash
# Check logs
docker logs mcp-server --tail 100

# Common causes:
# 1. Database connection issue - verify DATABASE_URL
# 2. OpenAI API issue - verify OPENAI_API_KEY
# 3. Application crash - check logs for errors

# Restart if needed
docker restart mcp-server
```

### Issue: High error rate

**Symptoms**: Error rate >1% in monitoring

**Quick Fix:**
```bash
# Check Sentry for error details
# Check application logs
docker logs mcp-server | grep ERROR

# If critical, consider rollback
```

### Issue: Slow response times

**Symptoms**: P95 latency >1000ms

**Quick Fix:**
```bash
# Check database connection pool
# Check OpenAI API latency
# Check system resources (CPU, memory)

# Scale up if needed
docker-compose up --scale backend=2
```

## Deployment Log Template

```markdown
## Deployment: v1.0.0

**Date**: 2026-02-03
**Time**: 14:00 UTC
**Deployed By**: [Name]
**Duration**: [X minutes]

### Pre-Deployment
- [ ] Tests passed
- [ ] Database backed up
- [ ] Configuration verified

### Deployment
- [ ] Application deployed
- [ ] Health checks passing
- [ ] Smoke tests passed

### Post-Deployment
- [ ] Monitoring verified
- [ ] No errors detected
- [ ] Performance normal

### Issues Encountered
- None / [List issues]

### Rollback Required
- No / Yes - [Reason]

### Notes
- [Any additional notes]
```

## Success Criteria

Deployment is considered successful when:

- [ ] All health checks passing for 30 minutes
- [ ] Error rate <0.1%
- [ ] P95 response time <500ms
- [ ] All smoke tests passing
- [ ] No critical errors in logs
- [ ] Monitoring and alerting active
- [ ] Team notified of successful deployment

---

**Document Version**: 1.0.0
**Last Updated**: 2026-02-03
**Next Review**: Before next deployment
