# Troubleshooting Guide - KIro Todo

Common issues and solutions for the KIro Todo application.

---

## Table of Contents

1. [Backend Issues](#backend-issues)
2. [Frontend Issues](#frontend-issues)
3. [CORS Errors](#cors-errors)
4. [Authentication Issues](#authentication-issues)
5. [Database Issues](#database-issues)
6. [Port Conflicts](#port-conflicts)

---

## Backend Issues

### Issue: Backend won't start

**Symptoms:**
```
ModuleNotFoundError: No module named 'fastapi'
```

**Solution:**
```powershell
cd backend
# Ensure virtual environment is activated
venv\Scripts\activate  # Windows
source venv/bin/activate  # macOS/Linux

# Reinstall dependencies
pip install -r requirements.txt
```

---

### Issue: Database connection fails

**Symptoms:**
```
sqlalchemy.exc.OperationalError: could not connect to server
```

**Solution:**

1. **Check DATABASE_URL in .env:**
   ```bash
   # backend/.env
   DATABASE_URL=postgresql://user:pass@host/dbname?sslmode=require
   ```

2. **Verify Neon database is accessible:**
   - Login to https://neon.tech
   - Check database status
   - Verify connection string is correct

3. **Test connection manually:**
   ```bash
   python -c "from src.database import engine; print('Connected!' if engine else 'Failed')"
   ```

---

### Issue: JWT verification fails

**Symptoms:**
```
401 Unauthorized: Invalid token
```

**Solution:**

1. **Ensure JWT_SECRET matches between backend and frontend:**
   ```bash
   # backend/.env
   JWT_SECRET=your_secret_here
   BETTER_AUTH_SECRET=your_secret_here  # Must match JWT_SECRET

   # frontend/.env.local
   BETTER_AUTH_SECRET=your_secret_here  # Must match backend
   ```

2. **Generate new secret if needed:**
   ```bash
   python -c "import secrets; print(secrets.token_urlsafe(32))"
   ```

3. **Restart both servers after changing secrets**

---

## Frontend Issues

### Issue: Frontend shows 404 error

**Symptoms:**
- Browser shows "404 This page could not be found"
- Next.js compiles but page doesn't load

**Solution:**

1. **Clear Next.js cache:**
   ```powershell
   cd frontend
   Remove-Item -Recurse -Force .next
   npm run dev
   ```

2. **Check if page file exists:**
   ```powershell
   ls src/app/page.tsx  # Should exist
   ```

3. **Verify no syntax errors:**
   - Check terminal for compilation errors
   - Look for TypeScript errors

---

### Issue: npm install fails

**Symptoms:**
```
npm ERR! code ERESOLVE
npm ERR! ERESOLVE unable to resolve dependency tree
```

**Solution:**

1. **Clear npm cache:**
   ```powershell
   cd frontend
   Remove-Item -Recurse -Force node_modules, package-lock.json
   npm cache clean --force
   npm install
   ```

2. **Use legacy peer deps (if needed):**
   ```powershell
   npm install --legacy-peer-deps
   ```

---

### Issue: Page loads but shows blank screen

**Symptoms:**
- No errors in terminal
- Browser shows blank page
- Console may show errors

**Solution:**

1. **Check browser console (F12):**
   - Look for JavaScript errors
   - Check Network tab for failed requests

2. **Verify environment variables:**
   ```bash
   # frontend/.env.local
   NEXT_PUBLIC_API_URL=http://localhost:8001
   ```

3. **Check if backend is running:**
   ```bash
   curl http://localhost:8001/health
   ```

---

## CORS Errors

### Issue: CORS policy blocks requests

**Symptoms:**
```
Access to fetch at 'http://localhost:8001/api/tasks' from origin
'http://localhost:3000' has been blocked by CORS policy
```

**Solution:**

1. **Update backend CORS_ORIGINS:**
   ```bash
   # backend/.env
   CORS_ORIGINS=http://localhost:3000,http://localhost:3001,http://127.0.0.1:3000,http://127.0.0.1:3001
   ```

2. **Restart backend server:**
   ```powershell
   # Stop with Ctrl+C, then restart
   cd backend
   python -m uvicorn src.main:app --reload --port 8001
   ```

3. **Verify CORS middleware is configured:**
   - Check `backend/src/main.py` has `CORSMiddleware`
   - Ensure `allow_credentials=True`

---

### Issue: OPTIONS request returns 400

**Symptoms:**
```
OPTIONS /api/auth/signin HTTP/1.1" 400 Bad Request
```

**Solution:**

This is a CORS preflight issue. Follow the CORS solution above and ensure:
- `allow_methods=["*"]` in CORS config
- `allow_headers=["*"]` in CORS config
- Backend is restarted after changes

---

## Authentication Issues

### Issue: Cannot sign up or sign in

**Symptoms:**
- Form submits but nothing happens
- Network error in console
- 401 or 500 error

**Solution:**

1. **Check backend is running:**
   ```bash
   curl http://localhost:8001/health
   # Should return: {"status":"healthy"}
   ```

2. **Verify auth endpoints exist:**
   ```bash
   curl http://localhost:8001/docs
   # Open in browser, check for /api/auth/signup and /api/auth/signin
   ```

3. **Check database tables exist:**
   ```bash
   cd backend
   python -m src.database
   # Should create users and tasks tables
   ```

4. **Test signup directly:**
   ```bash
   curl -X POST http://localhost:8001/api/auth/signup \
     -H "Content-Type: application/json" \
     -d '{"email":"test@example.com","password":"Test1234"}'
   ```

---

### Issue: Token not persisting

**Symptoms:**
- User signs in successfully
- Page refresh loses authentication
- User redirected to signin page

**Solution:**

1. **Check localStorage in browser:**
   - Open DevTools (F12)
   - Go to Application > Local Storage
   - Look for `auth_token` and `auth_user`

2. **Verify auth context is working:**
   - Check `frontend/src/lib/auth-context.tsx` exists
   - Ensure `AuthProvider` wraps app in `layout.tsx`

3. **Clear browser storage and retry:**
   - DevTools > Application > Clear storage
   - Sign in again

---

## Database Issues

### Issue: Tables don't exist

**Symptoms:**
```
sqlalchemy.exc.ProgrammingError: relation "users" does not exist
```

**Solution:**

1. **Initialize database:**
   ```bash
   cd backend
   python -m src.database
   ```

2. **Verify tables created:**
   - Login to Neon console
   - Check Tables section
   - Should see `users` and `tasks` tables

3. **If tables still missing, recreate:**
   ```bash
   # Drop and recreate (WARNING: deletes all data)
   python -c "from src.database import drop_db, init_db; drop_db(); init_db()"
   ```

---

### Issue: Foreign key constraint violation

**Symptoms:**
```
IntegrityError: foreign key constraint "tasks_user_id_fkey" violated
```

**Solution:**

This means trying to create a task with invalid user_id. This should never happen if JWT authentication is working correctly.

1. **Verify JWT middleware is active:**
   - Check all task endpoints use `Depends(get_current_user)`
   - Ensure user_id comes from JWT, not request body

2. **Check user exists:**
   ```bash
   # In Python shell
   from src.database import get_session
   from src.models.user import User
   session = next(get_session())
   users = session.query(User).all()
   print(users)
   ```

---

## Port Conflicts

### Issue: Port already in use

**Symptoms:**
```
ERROR: [Errno 10048] error while attempting to bind on address
('127.0.0.1', 8001): only one usage of each socket address
```

**Solution:**

1. **Find process using the port:**
   ```powershell
   # Windows
   netstat -ano | findstr :8001

   # macOS/Linux
   lsof -i :8001
   ```

2. **Kill the process:**
   ```powershell
   # Windows (replace PID with actual process ID)
   taskkill /PID <PID> /F

   # macOS/Linux
   kill -9 <PID>
   ```

3. **Or use a different port:**
   ```bash
   # Backend
   uvicorn src.main:app --reload --port 8002

   # Frontend
   npm run dev -- -p 3001
   ```

4. **Update environment variables if using different ports:**
   ```bash
   # frontend/.env.local
   NEXT_PUBLIC_API_URL=http://localhost:8002  # If backend on 8002
   ```

---

### Issue: Frontend runs on wrong port

**Symptoms:**
```
⚠ Port 3000 is in use, using available port 3001 instead
```

**Solution:**

1. **This is usually fine** - Frontend will work on 3001

2. **Update backend CORS if needed:**
   ```bash
   # backend/.env
   CORS_ORIGINS=http://localhost:3000,http://localhost:3001
   ```

3. **Or stop process on port 3000:**
   ```powershell
   # Windows
   netstat -ano | findstr :3000
   taskkill /PID <PID> /F
   ```

---

## General Debugging Tips

### Enable Debug Mode

**Backend:**
```bash
# backend/.env
DEBUG=true
ENVIRONMENT=development
```

**Frontend:**
```bash
# frontend/.env.local
NODE_ENV=development
```

---

### Check Logs

**Backend logs:**
- Terminal where `uvicorn` is running
- Look for stack traces and error messages

**Frontend logs:**
- Browser console (F12 > Console)
- Terminal where `npm run dev` is running

---

### Test API Endpoints

**Using curl:**
```bash
# Health check
curl http://localhost:8001/health

# Signup
curl -X POST http://localhost:8001/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"email":"test@test.com","password":"Test1234"}'

# List tasks (with token)
curl http://localhost:8001/api/tasks \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

**Using Swagger UI:**
1. Open http://localhost:8001/docs
2. Click "Authorize" button
3. Enter JWT token
4. Test endpoints interactively

---

### Reset Everything

If all else fails, complete reset:

```powershell
# Backend
cd backend
Remove-Item -Recurse -Force venv, __pycache__, .pytest_cache
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python -m src.database

# Frontend
cd frontend
Remove-Item -Recurse -Force node_modules, .next, package-lock.json
npm install
npm run dev
```

---

## Getting Help

If you're still stuck:

1. **Check the logs** - Most errors have helpful messages
2. **Review the documentation** - [API Documentation](./backend/API_DOCUMENTATION.md)
3. **Test with Swagger UI** - http://localhost:8001/docs
4. **Check environment variables** - Ensure all required vars are set
5. **Verify both servers are running** - Backend on 8001, Frontend on 3000/3001

---

**Last Updated:** 2026-02-03
