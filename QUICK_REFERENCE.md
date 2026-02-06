# KIro Todo - Quick Reference Guide

## 🚀 Quick Start

### Start Servers (2 Terminals)

**Terminal 1 - Backend:**
```bash
cd D:\Hackthon_GIAIC\Hacthon_ALL_phase\KIro_Todo\backend
uvicorn src.main:app --reload --port 8001
```

**Terminal 2 - Frontend:**
```bash
cd D:\Hackthon_GIAIC\Hacthon_ALL_phase\KIro_Todo\frontend
npm run dev
```

---

## 🔗 Application URLs

| Service | URL | Description |
|---------|-----|-------------|
| Frontend | http://localhost:3000 | Main application |
| Signup | http://localhost:3000/signup | Create new account |
| Signin | http://localhost:3000/signin | Login to account |
| Dashboard | http://localhost:3000/dashboard | Task management |
| Chat | http://localhost:3000/chat | AI assistant |
| Backend API | http://localhost:8001 | REST API |
| API Docs | http://localhost:8001/docs | Interactive API documentation |

---

## 🧪 Testing Commands

### Test Everything
```powershell
.\test-application.ps1
```

### Test Chat Fix
```powershell
.\test-chat-fix.ps1
```

### Manual API Test
```bash
# Health check
curl http://localhost:8001/health

# Signup
curl -X POST http://localhost:8001/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"TestPass123"}'

# Signin
curl -X POST http://localhost:8001/api/auth/signin \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"TestPass123"}'
```

---

## 🐛 Common Issues

### Issue: Port Already in Use

**Backend (8001):**
```powershell
netstat -ano | findstr :8001
taskkill /PID <PID> /F
```

**Frontend (3000):**
```powershell
netstat -ano | findstr :3000
taskkill /PID <PID> /F
```

### Issue: Module Not Found

**Backend:**
```bash
cd backend
pip install -r requirements.txt
```

**Frontend:**
```bash
cd frontend
npm install
```

### Issue: Database Connection Error

Check `backend/.env` has correct `DATABASE_URL`

### Issue: Chat Returns 500 Error

**Solution:** Restart backend after applying the fix
```bash
# Stop backend (Ctrl+C)
# Start again
cd backend
uvicorn src.main:app --reload --port 8001
```

### Issue: Signup Returns 400

**Cause:** Email already exists
**Solution:** Use a different email or signin instead

---

## 📝 Password Requirements

For signup, password must have:
- ✅ At least 8 characters
- ✅ At least 1 uppercase letter
- ✅ At least 1 lowercase letter
- ✅ At least 1 number

**Valid examples:**
- `TestPass123`
- `MyPassword1`
- `SecurePass99`

---

## 🤖 Chat Assistant Commands

Try these in the chat interface:

```
"Create a task to buy groceries"
"List all my tasks"
"Mark task 1 as complete"
"Show me incomplete tasks"
"Delete task 2"
"Create a task: Finish the project report"
```

---

## 📊 Database Tables

| Table | Description |
|-------|-------------|
| users | User accounts |
| tasks | Todo items |
| conversations | Chat conversations |
| messages | Chat messages |
| tool_call_logs | AI tool execution logs |

---

## 🔐 Authentication Flow

1. User signs up → Backend creates user with hashed password
2. User signs in → Backend verifies password and returns JWT token
3. Frontend stores JWT in localStorage
4. All API requests include JWT in Authorization header
5. Backend verifies JWT and extracts user_id
6. All data queries filtered by user_id

---

## 🛠️ Development Commands

### Backend

```bash
# Start server
uvicorn src.main:app --reload --port 8001

# Initialize database
python -c "from src.database import init_db; init_db()"

# Run with debug
uvicorn src.main:app --reload --port 8001 --log-level debug
```

### Frontend

```bash
# Start dev server
npm run dev

# Build for production
npm run build

# Start production server
npm start

# Lint code
npm run lint
```

---

## 📁 Project Structure

```
KIro_Todo/
├── backend/
│   ├── src/
│   │   ├── api/          # API routes
│   │   ├── models/       # Database models
│   │   ├── schemas/      # Pydantic schemas
│   │   ├── middleware/   # Auth, rate limiting
│   │   ├── agents/       # AI agent
│   │   ├── services/     # Business logic
│   │   └── main.py       # FastAPI app
│   ├── .env              # Environment variables
│   └── requirements.txt  # Python dependencies
│
├── frontend/
│   ├── src/
│   │   ├── app/          # Next.js pages
│   │   ├── components/   # React components
│   │   └── lib/          # Utilities
│   ├── .env.local        # Environment variables
│   └── package.json      # Node dependencies
│
├── test-application.ps1  # Full test script
├── test-chat-fix.ps1     # Chat fix test
├── start-backend.bat     # Backend starter
├── start-frontend.bat    # Frontend starter
└── ISSUES_FIXED.md       # Fix documentation
```

---

## 🎯 Feature Checklist

### Authentication
- [x] User signup with email/password
- [x] User signin with JWT tokens
- [x] Password hashing with bcrypt
- [x] Token-based authentication
- [x] Protected routes

### Task Management
- [x] Create tasks
- [x] List tasks (filtered by user)
- [x] Update tasks
- [x] Delete tasks
- [x] Mark complete/incomplete
- [x] Multi-user data isolation

### AI Chat Assistant
- [x] Natural language task management
- [x] Conversation history
- [x] Tool calling (MCP)
- [x] Task creation via chat
- [x] Task listing via chat
- [x] Task completion via chat

### Security
- [x] JWT authentication
- [x] Password hashing
- [x] CORS configuration
- [x] Rate limiting
- [x] Input validation
- [x] SQL injection prevention

---

## 📞 Support

If you encounter issues:

1. Check server logs in terminal
2. Check browser console (F12)
3. Run test scripts
4. Review ISSUES_FIXED.md
5. Check TROUBLESHOOTING.md

---

## 🎉 Success Indicators

You'll know everything is working when:

✅ Both servers start without errors
✅ Can access http://localhost:3000
✅ Can access http://localhost:8001/docs
✅ Can signup with new email
✅ Can signin with existing email
✅ Dashboard loads and shows tasks
✅ Can create/edit/delete tasks
✅ Chat page loads without errors
✅ Chat assistant responds to messages
✅ No 500 errors in browser console
✅ No CORS errors in browser console
