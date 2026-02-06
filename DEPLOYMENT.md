# Production Deployment Guide

**Feature**: 003-chat-api-ui
**Version**: 1.0.0
**Last Updated**: 2026-02-04

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Pre-Deployment Checklist](#pre-deployment-checklist)
3. [Deployment Options](#deployment-options)
4. [Docker Deployment](#docker-deployment)
5. [Cloud Deployment](#cloud-deployment)
6. [Post-Deployment](#post-deployment)
7. [Monitoring & Maintenance](#monitoring--maintenance)
8. [Rollback Procedures](#rollback-procedures)
9. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Required Services

- **PostgreSQL Database**: Neon Serverless or managed PostgreSQL
- **OpenAI API Account**: With sufficient credits
- **Domain Name**: For production URL
- **SSL Certificate**: For HTTPS (Let's Encrypt recommended)
- **Container Registry**: Docker Hub, AWS ECR, or GitHub Container Registry

### Required Tools

- Docker & Docker Compose
- Git
- kubectl (for Kubernetes deployment)
- Cloud CLI (AWS CLI, gcloud, or Azure CLI)

---

## Pre-Deployment Checklist

### Security

- [ ] Generate strong `BETTER_AUTH_SECRET` (32+ characters)
- [ ] Use production OpenAI API key with rate limits
- [ ] Configure CORS for production domain only
- [ ] Enable HTTPS/TLS for all endpoints
- [ ] Set secure database password
- [ ] Review and restrict database access
- [ ] Enable rate limiting on API endpoints
- [ ] Configure firewall rules

### Configuration

- [ ] Set `ENVIRONMENT=production` in backend
- [ ] Update `NEXT_PUBLIC_API_URL` to production URL
- [ ] Configure production database connection
- [ ] Set up error tracking (Sentry, Datadog)
- [ ] Configure log aggregation
- [ ] Set up monitoring and alerts
- [ ] Configure backup strategy

### Testing

- [ ] Run full test suite
- [ ] Test with production-like data volume
- [ ] Load test chat endpoint (100+ concurrent users)
- [ ] Test conversation persistence
- [ ] Verify multi-user data isolation
- [ ] Test error handling and recovery
- [ ] Verify rate limiting works correctly

### Documentation

- [ ] Update API documentation with production URLs
- [ ] Document deployment procedures
- [ ] Create runbooks for common issues
- [ ] Document rollback procedures
- [ ] Update README with production info

---

## Deployment Options

### Option 1: Docker Compose (Recommended for Small-Medium Scale)

**Pros:**
- Simple setup
- All services in one configuration
- Easy local testing
- Good for single-server deployments

**Cons:**
- Limited scalability
- Single point of failure
- Manual scaling required

**Best For:** MVP, small teams, <1000 users

### Option 2: Kubernetes (Recommended for Large Scale)

**Pros:**
- Auto-scaling
- High availability
- Rolling updates
- Self-healing

**Cons:**
- Complex setup
- Higher operational overhead
- Requires Kubernetes knowledge

**Best For:** Production, large teams, >1000 users

### Option 3: Serverless (AWS Lambda, Vercel)

**Pros:**
- Auto-scaling
- Pay-per-use
- Zero server management

**Cons:**
- Cold start latency
- Vendor lock-in
- Limited control

**Best For:** Variable traffic, cost optimization

---

## Docker Deployment

### Step 1: Prepare Environment

```bash
# Clone repository
git clone https://github.com/yourusername/kirotodo.git
cd kirotodo

# Checkout production branch
git checkout main

# Copy environment template
cp .env.production.example .env

# Edit .env with production values
nano .env
```

### Step 2: Configure Environment Variables

```bash
# Generate secure secrets
openssl rand -hex 32  # For BETTER_AUTH_SECRET

# Set required variables
export POSTGRES_PASSWORD=$(openssl rand -hex 16)
export BETTER_AUTH_SECRET=$(openssl rand -hex 32)
export OPENAI_API_KEY="sk-proj-your-key-here"
export NEXT_PUBLIC_API_URL="https://api.yourdomain.com"
```

### Step 3: Build and Deploy

```bash
# Build images
docker-compose build

# Start services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f backend
docker-compose logs -f frontend
```

### Step 4: Run Database Migrations

```bash
# Run migrations
docker-compose exec backend alembic upgrade head

# Verify tables
docker-compose exec postgres psql -U postgres -d kirotodo -c "\dt"
```

### Step 5: Verify Deployment

```bash
# Test backend health
curl https://api.yourdomain.com/health

# Test frontend
curl https://yourdomain.com

# Test chat endpoint (with JWT)
curl -X POST https://api.yourdomain.com/api/1/chat \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message":"Hello"}'
```

---

## Cloud Deployment

### AWS Deployment (ECS + RDS)

#### 1. Create RDS PostgreSQL Instance

```bash
# Create RDS instance
aws rds create-db-instance \
  --db-instance-identifier kirotodo-db \
  --db-instance-class db.t3.micro \
  --engine postgres \
  --master-username postgres \
  --master-user-password $POSTGRES_PASSWORD \
  --allocated-storage 20 \
  --vpc-security-group-ids sg-xxxxx \
  --db-subnet-group-name default

# Wait for instance to be available
aws rds wait db-instance-available --db-instance-identifier kirotodo-db

# Get endpoint
aws rds describe-db-instances \
  --db-instance-identifier kirotodo-db \
  --query 'DBInstances[0].Endpoint.Address'
```

#### 2. Push Images to ECR

```bash
# Login to ECR
aws ecr get-login-password --region us-east-1 | \
  docker login --username AWS --password-stdin $AWS_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com

# Create repositories
aws ecr create-repository --repository-name kirotodo-backend
aws ecr create-repository --repository-name kirotodo-frontend

# Tag and push images
docker tag kirotodo-backend:latest $AWS_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/kirotodo-backend:latest
docker push $AWS_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/kirotodo-backend:latest

docker tag kirotodo-frontend:latest $AWS_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/kirotodo-frontend:latest
docker push $AWS_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/kirotodo-frontend:latest
```

#### 3. Create ECS Cluster and Services

```bash
# Create cluster
aws ecs create-cluster --cluster-name kirotodo-cluster

# Register task definitions (see task-definition.json)
aws ecs register-task-definition --cli-input-json file://backend-task-definition.json
aws ecs register-task-definition --cli-input-json file://frontend-task-definition.json

# Create services
aws ecs create-service \
  --cluster kirotodo-cluster \
  --service-name kirotodo-backend \
  --task-definition kirotodo-backend:1 \
  --desired-count 2 \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[subnet-xxxxx],securityGroups=[sg-xxxxx],assignPublicIp=ENABLED}"

aws ecs create-service \
  --cluster kirotodo-cluster \
  --service-name kirotodo-frontend \
  --task-definition kirotodo-frontend:1 \
  --desired-count 2 \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[subnet-xxxxx],securityGroups=[sg-xxxxx],assignPublicIp=ENABLED}"
```

### Vercel Deployment (Frontend Only)

```bash
# Install Vercel CLI
npm install -g vercel

# Deploy frontend
cd frontend
vercel --prod

# Set environment variables
vercel env add NEXT_PUBLIC_API_URL production
vercel env add NEXT_PUBLIC_CHATKIT_ENABLED production
```

---

## Post-Deployment

### 1. Configure DNS

```bash
# Add A records
api.yourdomain.com -> Backend IP
yourdomain.com -> Frontend IP

# Or CNAME for load balancer
api.yourdomain.com -> backend-lb.us-east-1.elb.amazonaws.com
yourdomain.com -> frontend-lb.us-east-1.elb.amazonaws.com
```

### 2. Set Up SSL/TLS

```bash
# Using Let's Encrypt with Certbot
sudo certbot --nginx -d yourdomain.com -d api.yourdomain.com

# Or use AWS Certificate Manager
aws acm request-certificate \
  --domain-name yourdomain.com \
  --subject-alternative-names api.yourdomain.com \
  --validation-method DNS
```

### 3. Configure Monitoring

```bash
# Set up CloudWatch alarms (AWS)
aws cloudwatch put-metric-alarm \
  --alarm-name kirotodo-backend-cpu \
  --alarm-description "Alert when CPU exceeds 80%" \
  --metric-name CPUUtilization \
  --namespace AWS/ECS \
  --statistic Average \
  --period 300 \
  --threshold 80 \
  --comparison-operator GreaterThanThreshold

# Set up error tracking (Sentry)
# Add SENTRY_DSN to environment variables
```

### 4. Set Up Backups

```bash
# Automated database backups (AWS RDS)
aws rds modify-db-instance \
  --db-instance-identifier kirotodo-db \
  --backup-retention-period 7 \
  --preferred-backup-window "03:00-04:00"

# Manual backup
docker-compose exec postgres pg_dump -U postgres kirotodo > backup.sql
```

---

## Monitoring & Maintenance

### Health Checks

```bash
# Backend health
curl https://api.yourdomain.com/health

# Frontend health
curl https://yourdomain.com

# Database health
docker-compose exec postgres pg_isready
```

### Log Monitoring

```bash
# View real-time logs
docker-compose logs -f backend
docker-compose logs -f frontend

# Search logs
docker-compose logs backend | grep ERROR

# Export logs
docker-compose logs --since 24h > logs-$(date +%Y%m%d).txt
```

### Performance Monitoring

```bash
# Check response times
curl -w "@curl-format.txt" -o /dev/null -s https://api.yourdomain.com/api/1/chat

# Monitor database connections
docker-compose exec postgres psql -U postgres -c "SELECT count(*) FROM pg_stat_activity;"

# Check container resource usage
docker stats
```

---

## Rollback Procedures

### Quick Rollback (Docker)

```bash
# Stop current deployment
docker-compose down

# Checkout previous version
git checkout <previous-commit-hash>

# Rebuild and deploy
docker-compose build
docker-compose up -d

# Verify
curl https://api.yourdomain.com/health
```

### Database Rollback

```bash
# Restore from backup
docker-compose exec postgres psql -U postgres kirotodo < backup.sql

# Or rollback migration
docker-compose exec backend alembic downgrade -1
```

---

## Troubleshooting

### Issue: Backend Not Starting

```bash
# Check logs
docker-compose logs backend

# Common causes:
# 1. Database connection failed
docker-compose exec postgres pg_isready

# 2. Missing environment variables
docker-compose exec backend env | grep OPENAI_API_KEY

# 3. Port already in use
sudo lsof -i :8000
```

### Issue: High Response Times

```bash
# Check database query performance
docker-compose exec postgres psql -U postgres -d kirotodo -c "
SELECT query, mean_exec_time, calls
FROM pg_stat_statements
ORDER BY mean_exec_time DESC
LIMIT 10;"

# Check OpenAI API latency
# Review logs for "Agent execution time"

# Scale up if needed
docker-compose up -d --scale backend=4
```

### Issue: Rate Limit Errors

```bash
# Check rate limit configuration
docker-compose exec backend env | grep RATE_LIMIT

# Increase limits if needed
# Edit .env and restart
docker-compose restart backend
```

---

## Security Best Practices

1. **Never commit secrets to Git**
   - Use `.env` files (gitignored)
   - Use secret management services (AWS Secrets Manager, HashiCorp Vault)

2. **Rotate credentials regularly**
   - Database passwords: Every 90 days
   - JWT secrets: Every 180 days
   - API keys: As recommended by provider

3. **Monitor for security issues**
   - Enable security scanning (Snyk, Dependabot)
   - Review logs for suspicious activity
   - Set up alerts for failed authentication attempts

4. **Keep dependencies updated**
   ```bash
   # Backend
   pip list --outdated
   pip install --upgrade <package>

   # Frontend
   npm outdated
   npm update
   ```

---

## Support

For deployment issues:
- Check logs: `docker-compose logs`
- Review troubleshooting section above
- Check health endpoints
- Verify environment variables
- Test database connectivity

For urgent production issues:
- Follow incident response procedures
- Check monitoring dashboards
- Review recent deployments
- Prepare rollback if needed
