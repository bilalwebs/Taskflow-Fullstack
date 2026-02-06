# Quickstart Guide: Multi-User Todo Web Application

**Feature**: Multi-User Todo Web Application
**Branch**: 001-multi-user-todo-app
**Date**: 2026-02-02
**Status**: Complete

## Overview

This guide provides step-by-step instructions for setting up and running the Multi-User Todo Web Application in your local development environment. The application consists of a Next.js frontend and FastAPI backend connected to a Neon PostgreSQL database.

---

## Prerequisites

Before starting, ensure you have the following installed:

- **Node.js**: Version 18+ (for Next.js frontend)
- **Python**: Version 3.11+ (for FastAPI backend)
- **Git**: For cloning the repository
- **Code Editor**: VS Code, Cursor, or your preferred editor
- **Neon Account**: Free account at [neon.tech](https://neon.tech) for PostgreSQL database

---

## Quick Start (5 Minutes)

### 1. Clone Repository

```bash
git clone <repository-url>
cd KIro_Todo
git checkout 001-multi-user-todo-app
```

### 2. Set Up Database

1. Create a free Neon PostgreSQL database at [neon.tech](https://neon.tech)
2. Copy your connection string (looks like: `postgresql://user:pass@host/dbname`)
3. Save it for the next steps

### 3. Set Up Backend

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env

# Edit .env and add your values:
# DATABASE_URL=<your-neon-connection-string>
# JWT_SECRET=<generate-a-random-secret>
# BETTER_AUTH_SECRET=<same-as-jwt-secret>

# Run database migrations
python -m src.database  # Creates tables

# Start backend server
uvicorn src.main:app --reload --port 8000
```

Backend should now be running at `http://localhost:8000`

### 4. Set Up Frontend

Open a new terminal:

```bash
cd frontend

# Install dependencies
npm install

# Create .env.local file
cp .env.local.example .env.local

# Edit .env.local and add:
# NEXT_PUBLIC_API_URL=http://localhost:8000
# BETTER_AUTH_SECRET=<same-secret-as-backend>

# Start frontend development server
npm run dev
```

Frontend should now be running at `http://localhost:3000`

### 5. Test the Application

1. Open browser to `http://localhost:3000`
2. Click "Sign Up" and create an account
3. Sign in with your credentials
4. Create, edit, and complete tasks
5. Sign out and create a second account to verify data isolation

---

## Detailed Setup Instructions

### Backend Setup (FastAPI)

#### Step 1: Create Virtual Environment

```bash
cd backend
python -m venv venv
```

**Why**: Isolates Python dependencies from system packages

#### Step 2: Activate Virtual Environment

**Windows**:
```bash
venv\Scripts\activate
```

**macOS/Linux**:
```bash
source venv/bin/activate
```

**Verify**: Your terminal prompt should show `(venv)` prefix

#### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

**Expected packages**:
- fastapi
- uvicorn[standard]
- sqlmodel
- psycopg2-binary
- python-jose[cryptography]
- passlib[bcrypt]
- python-dotenv
- pydantic-settings

#### Step 4: Configure Environment Variables

Create `.env` file in `backend/` directory:

```env
# Database
DATABASE_URL=postgresql://user:password@host:5432/dbname

# JWT Configuration
JWT_SECRET=your-super-secret-jwt-key-min-32-chars
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=168

# Better Auth Secret (must match frontend)
BETTER_AUTH_SECRET=your-super-secret-jwt-key-min-32-chars

# CORS
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000

# Environment
ENVIRONMENT=development
DEBUG=true
```

**Generate JWT Secret**:
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

#### Step 5: Initialize Database

```bash
# Run database initialization script
python -m src.database

# Or use Python shell:
python
>>> from src.database import init_db
>>> init_db()
>>> exit()
```

**What this does**:
- Creates `users` table
- Creates `tasks` table
- Sets up foreign key relationships
- Creates indexes

#### Step 6: Start Backend Server

```bash
uvicorn src.main:app --reload --port 8000
```

**Verify**:
- Open `http://localhost:8000/docs` to see API documentation
- You should see Swagger UI with all endpoints

---

### Frontend Setup (Next.js)

#### Step 1: Install Dependencies

```bash
cd frontend
npm install
```

**Expected packages**:
- next (16+)
- react (19+)
- react-dom
- better-auth
- typescript
- tailwindcss

#### Step 2: Configure Environment Variables

Create `.env.local` file in `frontend/` directory:

```env
# API Configuration
NEXT_PUBLIC_API_URL=http://localhost:8000

# Better Auth Configuration
BETTER_AUTH_SECRET=your-super-secret-jwt-key-min-32-chars
BETTER_AUTH_URL=http://localhost:3000

# Environment
NODE_ENV=development
```

**Important**: `BETTER_AUTH_SECRET` must match backend's `JWT_SECRET`

#### Step 3: Start Development Server

```bash
npm run dev
```

**Verify**:
- Open `http://localhost:3000`
- You should see the landing page

---

## Verification Checklist

### Backend Verification

- [ ] Backend server starts without errors
- [ ] API documentation accessible at `http://localhost:8000/docs`
- [ ] Database connection successful (check logs)
- [ ] Environment variables loaded correctly

**Test API manually**:
```bash
# Health check (if implemented)
curl http://localhost:8000/health

# Should return 401 (authentication required)
curl http://localhost:8000/api/tasks
```

### Frontend Verification

- [ ] Frontend server starts without errors
- [ ] Landing page loads at `http://localhost:3000`
- [ ] No console errors in browser DevTools
- [ ] Environment variables loaded (check Network tab for API calls)

### Integration Verification

- [ ] Sign up creates new user account
- [ ] Sign in returns JWT token
- [ ] Dashboard loads after authentication
- [ ] Can create new tasks
- [ ] Can edit existing tasks
- [ ] Can mark tasks as complete
- [ ] Can delete tasks
- [ ] Sign out clears session
- [ ] Second user cannot see first user's tasks

---

## Common Issues and Solutions

### Issue: Backend won't start - "ModuleNotFoundError"

**Solution**: Ensure virtual environment is activated and dependencies installed
```bash
# Activate venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Reinstall dependencies
pip install -r requirements.txt
```

### Issue: Database connection fails

**Solution**: Verify DATABASE_URL in `.env`
- Check connection string format
- Ensure Neon database is running
- Test connection with psql or database client

### Issue: Frontend can't connect to backend

**Solution**: Check CORS configuration
- Verify `CORS_ORIGINS` in backend `.env` includes `http://localhost:3000`
- Check `NEXT_PUBLIC_API_URL` in frontend `.env.local`
- Ensure backend is running on port 8000

### Issue: JWT verification fails

**Solution**: Ensure secrets match
- `JWT_SECRET` in backend `.env`
- `BETTER_AUTH_SECRET` in backend `.env`
- `BETTER_AUTH_SECRET` in frontend `.env.local`
- All three must be identical

### Issue: Tasks from other users are visible

**Solution**: This is a critical security bug
- Check backend code filters tasks by `user_id`
- Verify JWT middleware extracts user ID correctly
- Review query patterns in `src/api/tasks.py`

---

## Development Workflow

### Making Changes

1. **Backend changes**: Server auto-reloads with `--reload` flag
2. **Frontend changes**: Next.js hot-reloads automatically
3. **Database schema changes**: Update models, then run migrations

### Testing Changes

1. **Manual testing**: Use browser and API docs
2. **API testing**: Use Swagger UI at `/docs`
3. **Database inspection**: Use Neon dashboard or psql

### Debugging

**Backend debugging**:
- Check terminal logs for errors
- Add print statements or use debugger
- Check `http://localhost:8000/docs` for API issues

**Frontend debugging**:
- Open browser DevTools (F12)
- Check Console tab for errors
- Check Network tab for API calls
- Use React DevTools extension

---

## Next Steps

After successful setup:

1. **Review Specifications**: Read `spec.md` to understand requirements
2. **Review Data Model**: Read `data-model.md` to understand entities
3. **Review API Contracts**: Read `contracts/tasks.yaml` for endpoint details
4. **Start Implementation**: Run `/sp.tasks` to generate implementation tasks
5. **Follow Tasks**: Implement features using specialized agents

---

## Environment Variables Reference

### Backend (.env)

| Variable | Required | Description | Example |
|----------|----------|-------------|---------|
| DATABASE_URL | Yes | Neon PostgreSQL connection string | `postgresql://user:pass@host/db` |
| JWT_SECRET | Yes | Secret for JWT signing (min 32 chars) | `generated-secret-key` |
| BETTER_AUTH_SECRET | Yes | Must match frontend (same as JWT_SECRET) | `generated-secret-key` |
| JWT_ALGORITHM | No | JWT algorithm (default: HS256) | `HS256` |
| JWT_EXPIRATION_HOURS | No | Token expiration (default: 168 = 7 days) | `168` |
| CORS_ORIGINS | Yes | Allowed frontend origins | `http://localhost:3000` |
| ENVIRONMENT | No | Environment name | `development` |
| DEBUG | No | Enable debug logging | `true` |

### Frontend (.env.local)

| Variable | Required | Description | Example |
|----------|----------|-------------|---------|
| NEXT_PUBLIC_API_URL | Yes | Backend API base URL | `http://localhost:8000` |
| BETTER_AUTH_SECRET | Yes | Must match backend JWT_SECRET | `generated-secret-key` |
| BETTER_AUTH_URL | Yes | Frontend base URL | `http://localhost:3000` |
| NODE_ENV | No | Node environment | `development` |

---

## Port Reference

| Service | Port | URL |
|---------|------|-----|
| Frontend | 3000 | http://localhost:3000 |
| Backend API | 8000 | http://localhost:8000 |
| API Docs | 8000 | http://localhost:8000/docs |
| Database | 5432 | Neon cloud (no local port) |

---

## Support

If you encounter issues not covered in this guide:

1. Check the specification documents in `specs/001-multi-user-todo-app/`
2. Review error messages carefully
3. Verify all environment variables are set correctly
4. Ensure all prerequisites are installed
5. Check that both frontend and backend are running

---

## Security Notes

**Development Environment**:
- Use strong JWT secrets (min 32 characters)
- Never commit `.env` or `.env.local` files
- Use HTTPS in production
- Rotate secrets regularly

**Production Deployment**:
- Use environment-specific secrets
- Enable HTTPS/TLS
- Configure proper CORS origins
- Use production database with backups
- Enable rate limiting
- Monitor for security issues
