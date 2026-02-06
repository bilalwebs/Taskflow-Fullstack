# KIro Todo - Quick Start Guide

## Current Status

Both servers should be running:
- **Backend**: http://localhost:8001
- **Frontend**: http://localhost:3000

## Starting the Application

### 1. Start Backend (Terminal 1)

```powershell
cd backend
uvicorn src.main:app --reload --port 8001
```

Expected output:
```
INFO:     Uvicorn running on http://127.0.0.1:8001
[OK] TaskAgent initialized successfully with model: gpt-4o-mini
INFO:     Application startup complete.
```

### 2. Start Frontend (Terminal 2)

```powershell
cd frontend
npm run dev
```

Expected output:
```
▲ Next.js 16.1.6 (Turbopack)
- Local:         http://localhost:3000
✓ Ready in 9.1s
```

## Testing the Application

### Option 1: Run Test Script

```powershell
.\test-application.ps1
```

### Option 2: Manual Testing

1. **Open Frontend**: http://localhost:3000
2. **Sign Up**: http://localhost:3000/signup
   - Email: test@example.com
   - Password: TestPass123 (must have uppercase, lowercase, number)
3. **Sign In**: http://localhost:3000/signin
4. **Dashboard**: http://localhost:3000/dashboard
5. **Chat Assistant**: http://localhost:3000/chat

### Option 3: API Testing

Visit API documentation: http://localhost:8001/docs

## Common Issues & Solutions

### Issue 1: Backend won't start
**Error**: `Address already in use`
**Solution**:
```powershell
# Find process using port 8001
netstat -ano | findstr :8001
# Kill the process (replace PID with actual process ID)
taskkill /PID <PID> /F
```

### Issue 2: Frontend won't start
**Error**: `Port 3000 is already in use`
**Solution**:
```powershell
# Find process using port 3000
netstat -ano | findstr :3000
# Kill the process
taskkill /PID <PID> /F
```

### Issue 3: Database connection error
**Solution**: Check `.env` file in backend directory has correct DATABASE_URL

### Issue 4: CORS errors in browser
**Solution**: Verify backend CORS_ORIGINS includes http://localhost:3000

### Issue 5: "Failed to fetch" errors
**Solution**:
1. Verify backend is running on port 8001
2. Check frontend .env.local has: `NEXT_PUBLIC_API_URL=http://localhost:8001`
3. Clear browser cache and reload

## Environment Variables

### Backend (.env)
```env
DATABASE_URL=postgresql://...
JWT_SECRET=c93afeb6710d2845
OPENAI_API_KEY=sk-proj-...
CORS_ORIGINS=http://localhost:3000,http://localhost:3001
```

### Frontend (.env.local)
```env
NEXT_PUBLIC_API_URL=http://localhost:8001
BETTER_AUTH_SECRET=3gHSWlEDitVGXMw9B9d1YcXriLhyxltr
```

## Features Available

### Basic Features (Implemented)
- ✅ User signup/signin with JWT authentication
- ✅ Create, read, update, delete tasks
- ✅ Mark tasks as complete/incomplete
- ✅ Multi-user data isolation
- ✅ AI chat assistant for task management
- ✅ Conversation history

### Task Management
- Create tasks with title and description
- Toggle completion status
- Edit task details
- Delete tasks
- View all your tasks

### AI Assistant
- Natural language task management
- Create tasks via chat
- List and search tasks
- Mark tasks complete via chat
- Conversation history

## Architecture

```
Frontend (Next.js 16)
    ↓ HTTP/REST
Backend (FastAPI)
    ↓ SQLModel
Database (Neon PostgreSQL)
    ↓ OpenAI API
AI Agent (GPT-4o-mini)
```

## Next Steps

1. Test signup and signin
2. Create some tasks
3. Try the AI chat assistant
4. Verify data isolation (create another user)

## Support

If you encounter issues:
1. Check both servers are running
2. Run the test script: `.\test-application.ps1`
3. Check browser console for errors (F12)
4. Check backend logs in terminal
