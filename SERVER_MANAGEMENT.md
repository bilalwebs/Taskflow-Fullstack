# KIro Todo - Server Management Guide

## 🚀 Quick Start Commands

### Start Both Servers

**Backend (Terminal 1):**
```bash
cd backend
uvicorn src.main:app --reload --port 8000
```

**Frontend (Terminal 2):**
```bash
cd frontend
npm run dev
```

---

## 🔧 Server Management

### Current Running Servers

- **Backend Task ID**: b485791
- **Frontend Task ID**: b0c48f2

### Stop Servers

**Option 1: Using Task IDs (via Claude Code)**
Ask Claude to stop the tasks:
```
Stop task b485791  # Backend
Stop task b0c48f2  # Frontend
```

**Option 2: Manual Stop (Windows)**
```bash
# Find and kill processes
netstat -ano | findstr :8000  # Find backend PID
netstat -ano | findstr :3000  # Find frontend PID
taskkill /PID <PID> /F        # Kill the process
```

**Option 3: Ctrl+C in Terminal**
If running in foreground, press `Ctrl+C` in each terminal

---

## 🌐 Access URLs

| Service | URL | Description |
|---------|-----|-------------|
| Frontend | http://localhost:3000 | Main application |
| Backend API | http://localhost:8000 | REST API |
| API Docs | http://localhost:8000/docs | Swagger UI |
| Health Check | http://localhost:8000/health | Backend status |

---

## 📱 Application Pages

| Page | URL | Purpose |
|------|-----|---------|
| Home | http://localhost:3000 | Landing page |
| Sign Up | http://localhost:3000/signup | Create account |
| Sign In | http://localhost:3000/signin | Login |
| Dashboard | http://localhost:3000/dashboard | Task management |
| **Chat** | http://localhost:3000/chat | **AI Assistant (Main Feature)** |

---

## 🧪 Testing the Chat Feature

### 1. Create Account
```
URL: http://localhost:3000/signup
Email: test@example.com
Password: password123
```

### 2. Login
```
URL: http://localhost:3000/signin
Use credentials from step 1
```

### 3. Open Chat
```
URL: http://localhost:3000/chat
```

### 4. Test Commands

**Basic Greeting:**
```
"Hello"
"Hi there"
```

**List Tasks:**
```
"Show my tasks"
"What do I need to do?"
"List all my tasks"
```

**Create Tasks:**
```
"Create a task to buy groceries"
"Remind me to call dentist"
"Add task: finish report"
```

**Complete Tasks:**
```
"I finished buying groceries"
"Mark the first task as done"
"Complete task 1"
```

**Update Tasks:**
```
"Change 'buy milk' to 'buy milk and eggs'"
"Update the groceries task"
```

**Delete Tasks:**
```
"Delete the groceries task"
"Remove task 1"
```

---

## 🔍 Troubleshooting

### Backend Not Starting

**Check if port 8000 is in use:**
```bash
netstat -ano | findstr :8000
```

**Check database connection:**
```bash
cd backend
python -c "from src.database import engine; print('Database connected!')"
```

**Check environment variables:**
```bash
cd backend
type .env
```

### Frontend Not Starting

**Check if port 3000 is in use:**
```bash
netstat -ano | findstr :3000
```

**Clear Next.js cache:**
```bash
cd frontend
rmdir /s /q .next
npm run dev
```

**Reinstall dependencies:**
```bash
cd frontend
rmdir /s /q node_modules
npm install
```

### Chat Not Working

**1. Check OpenAI API Key:**
```bash
cd backend
type .env | findstr OPENAI_API_KEY
```

**2. Test backend health:**
```bash
curl http://localhost:8000/health
```

**3. Check browser console:**
- Open browser DevTools (F12)
- Check Console tab for errors
- Check Network tab for failed requests

**4. Verify JWT token:**
- Login first
- Check if token is stored in localStorage
- Open DevTools → Application → Local Storage

---

## 📊 Monitor Logs

### Backend Logs
```bash
# View real-time logs
tail -f C:\Users\Bilal\AppData\Local\Temp\claude\D--Hackthon-GIAIC-Hacthon-ALL-phase-KIro-Todo\tasks\b485791.output
```

### Frontend Logs
```bash
# View real-time logs
tail -f C:\Users\Bilal\AppData\Local\Temp\claude\D--Hackthon-GIAIC-Hacthon-ALL-phase-KIro-Todo\tasks\b0c48f2.output
```

### Check Specific Errors
```bash
# Backend errors
cd backend
python src/main.py

# Frontend errors
cd frontend
npm run dev
```

---

## 🔄 Restart Servers

### Quick Restart

**Backend:**
```bash
# Stop (Ctrl+C or kill process)
# Then start again
cd backend
uvicorn src.main:app --reload --port 8000
```

**Frontend:**
```bash
# Stop (Ctrl+C or kill process)
# Then start again
cd frontend
npm run dev
```

---

## 🗄️ Database Management

### Run Migrations
```bash
cd backend
alembic upgrade head
```

### Create New Migration
```bash
cd backend
alembic revision --autogenerate -m "Description"
alembic upgrade head
```

### Rollback Migration
```bash
cd backend
alembic downgrade -1
```

### Check Database Connection
```bash
cd backend
python -c "from src.database import engine; from sqlmodel import Session; session = Session(engine); print('Connected!')"
```

---

## 🔐 Environment Variables

### Backend (.env)
```env
DATABASE_URL=postgresql://...
OPENAI_API_KEY=sk-proj-...
OPENAI_MODEL=gpt-4o-mini
JWT_SECRET=...
BETTER_AUTH_SECRET=...
```

### Frontend (.env)
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
BETTER_AUTH_SECRET=... (must match backend)
```

---

## 📦 Dependencies

### Update Backend Dependencies
```bash
cd backend
pip install --upgrade -r requirements.txt
```

### Update Frontend Dependencies
```bash
cd frontend
npm update
```

---

## 🚨 Common Issues

### Issue: "Port already in use"
**Solution:**
```bash
# Find process using port
netstat -ano | findstr :8000  # or :3000

# Kill process
taskkill /PID <PID> /F
```

### Issue: "Database connection failed"
**Solution:**
1. Check DATABASE_URL in backend/.env
2. Verify Neon database is accessible
3. Check internet connection

### Issue: "OpenAI API error"
**Solution:**
1. Verify OPENAI_API_KEY in backend/.env
2. Check API key has credits
3. Test key at https://platform.openai.com

### Issue: "JWT token invalid"
**Solution:**
1. Logout and login again
2. Clear browser localStorage
3. Verify BETTER_AUTH_SECRET matches in both .env files

---

## 📚 Additional Resources

- **API Documentation**: http://localhost:8000/docs
- **Quickstart Guide**: `specs/003-chat-api-ui/quickstart.md`
- **API Reference**: `specs/003-chat-api-ui/API_DOCUMENTATION.md`
- **Deployment Guide**: `DEPLOYMENT.md`

---

## ✅ Health Check

Run this to verify everything is working:

```bash
# Backend health
curl http://localhost:8000/health

# Frontend health
curl http://localhost:3000

# Database connection
cd backend && python -c "from src.database import engine; print('DB OK')"
```

Expected responses:
- Backend: `{"status":"healthy",...}`
- Frontend: HTML response (200 OK)
- Database: `DB OK`

---

## 🎯 Quick Test Flow

1. ✅ Backend running: http://localhost:8000/health
2. ✅ Frontend running: http://localhost:3000
3. ✅ Sign up: http://localhost:3000/signup
4. ✅ Login: http://localhost:3000/signin
5. ✅ Open chat: http://localhost:3000/chat
6. ✅ Send message: "Hello"
7. ✅ Create task: "Create a task to test the app"
8. ✅ List tasks: "Show my tasks"
9. ✅ Complete task: "I finished testing"

---

**Status**: Both servers are running and ready for testing!

**Backend**: http://localhost:8000 ✅
**Frontend**: http://localhost:3000 ✅
**Chat**: http://localhost:3000/chat ✅
