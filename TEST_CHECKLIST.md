# Quick Test Checklist

## ✅ Setup Verification

- [x] Backend running on port 8000
- [x] Frontend running on port 3000
- [x] Database migrations applied
- [x] Dependencies installed
- [x] Environment variables configured

## 🧪 Feature Testing

### Authentication
- [ ] Can sign up new user
- [ ] Can login with credentials
- [ ] JWT token is stored
- [ ] Can access protected routes

### Chat Interface
- [ ] Chat page loads at /chat
- [ ] Can send messages
- [ ] AI responds within 5 seconds
- [ ] Messages display correctly
- [ ] Loading states work

### Task Management via Chat
- [ ] Can create tasks ("Create a task to...")
- [ ] Can list tasks ("Show my tasks")
- [ ] Can complete tasks ("I finished...")
- [ ] Can update tasks ("Change... to...")
- [ ] Can delete tasks ("Delete the... task")

### Conversation Persistence
- [ ] Messages persist after page refresh
- [ ] Can see conversation history
- [ ] Can switch between conversations
- [ ] New conversation button works

### UI/UX
- [ ] User messages appear on right (blue)
- [ ] AI messages appear on left (gray)
- [ ] Tool call indicators show
- [ ] Timestamps display
- [ ] Conversation sidebar works
- [ ] Error messages are clear

### Security
- [ ] Cannot access chat without login
- [ ] User A cannot see User B's data
- [ ] JWT token required for API calls
- [ ] Rate limiting works (try 60+ requests)

## 🎯 Success Criteria

All checkboxes above should be checked for full functionality.

## 📝 Notes

- Backend: http://localhost:8000
- Frontend: http://localhost:3000
- Chat: http://localhost:3000/chat
- API Docs: http://localhost:8000/docs

## 🐛 If Something Doesn't Work

1. Check browser console (F12)
2. Check backend logs
3. Verify environment variables
4. Test API directly at /docs
5. Refer to SERVER_MANAGEMENT.md
