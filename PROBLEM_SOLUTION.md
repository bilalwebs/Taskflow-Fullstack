# KIro Todo - Problem Diagnosis & Solution

## Current Problem

Both servers are NOT running. The test script shows:
- ✗ Backend not accessible on port 8001
- ✗ Frontend not accessible on port 3000

## Solution: Start Both Servers

### Step 1: Start Backend Server

**Open PowerShell/Terminal 1:**

```powershell
cd D:\Hackthon_GIAIC\Hacthon_ALL_phase\KIro_Todo
.\start-backend.bat
```

**OR manually:**

```powershell
cd backend
uvicorn src.main:app --reload --port 8001
```

**Expected Output:**
```
INFO:     Uvicorn running on http://127.0.0.1:8001 (Press CTRL+C to quit)
INFO:     Started reloader process [XXXX] using WatchFiles
INFO:     Started server process [XXXX]
INFO:     Waiting for application startup.
[OK] TaskAgent initialized successfully with model: gpt-4o-mini
INFO:     Application startup complete.
```

✅ **Verify**: Open http://localhost:8001/docs in browser

---

### Step 2: Start Frontend Server

**Open PowerShell/Terminal 2 (NEW WINDOW):**

```powershell
cd D:\Hackthon_GIAIC\Hacthon_ALL_phase\KIro_Todo
.\start-frontend.bat
```

**OR manually:**

```powershell
cd frontend
npm run dev
```

**Expected Output:**
```
▲ Next.js 16.1.6 (Turbopack)
- Local:         http://localhost:3000
- Network:       http://172.29.240.1:3000
✓ Ready in 9.1s
```

✅ **Verify**: Open http://localhost:3000 in browser

---

### Step 3: Test the Application

**Run the test script in a 3rd terminal:**

```powershell
cd D:\Hackthon_GIAIC\Hacthon_ALL_phase\KIro_Todo
.\test-application.ps1
```

**Expected Output:**
```
=== KIro Todo Application Test ===

1. Testing Backend Health...
   ✓ Backend is running and healthy
   Environment: development

2. Testing Backend API Documentation...
   ✓ API docs accessible at http://localhost:8001/docs

3. Testing Frontend...
   ✓ Frontend is running at http://localhost:3000

4. Testing Signup Endpoint...
   ✓ Signup endpoint working
   Created user: test_XXXX@example.com
   Token received: eyJhbGciOiJIUzI1NiIs...

=== Test Complete ===
```

---

## Common Issues & Fixes

### Issue 1: "Port already in use"

**Backend (Port 8001):**
```powershell
# Find process
netstat -ano | findstr :8001
# Kill it (replace XXXX with PID)
taskkill /PID XXXX /F
```

**Frontend (Port 3000):**
```powershell
# Find process
netstat -ano | findstr :3000
# Kill it (replace XXXX with PID)
taskkill /PID XXXX /F
```

### Issue 2: "uvicorn: command not found"

```powershell
cd backend
pip install -r requirements.txt
```

### Issue 3: "npm: command not found"

Install Node.js from: https://nodejs.org/

### Issue 4: Database connection error

Check backend/.env file has correct DATABASE_URL

### Issue 5: Module import errors

**Backend:**
```powershell
cd backend
pip install -r requirements.txt
```

**Frontend:**
```powershell
cd frontend
npm install
```

---

## Quick Checklist

- [ ] Backend running on http://localhost:8001
- [ ] Frontend running on http://localhost:3000
- [ ] Can access http://localhost:8001/docs
- [ ] Can access http://localhost:3000
- [ ] Test script passes all checks
- [ ] Can signup at http://localhost:3000/signup
- [ ] Can signin at http://localhost:3000/signin
- [ ] Can create tasks in dashboard

---

## What to Do Next

1. **Start both servers** (2 separate terminals)
2. **Run test script** to verify everything works
3. **Open browser** and test:
   - Signup: http://localhost:3000/signup
   - Signin: http://localhost:3000/signin
   - Dashboard: http://localhost:3000/dashboard
   - Chat: http://localhost:3000/chat

---

## Need Help?

If servers still won't start:
1. Check the terminal output for error messages
2. Verify Python and Node.js are installed
3. Check .env files exist in backend and frontend directories
4. Try running `pip install -r requirements.txt` in backend
5. Try running `npm install` in frontend
