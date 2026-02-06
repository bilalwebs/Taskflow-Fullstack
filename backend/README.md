# Backend - FastAPI Todo API

RESTful API for the KIro Todo application with JWT authentication and user data isolation.

## Setup

### 1. Create Virtual Environment

```bash
python -m venv venv
```

### 2. Activate Virtual Environment

**Windows:**
```bash
venv\Scripts\activate
```

**macOS/Linux:**
```bash
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment

```bash
cp .env.example .env
```

Edit `.env` and set:
- `DATABASE_URL`: Your Neon PostgreSQL connection string
- `JWT_SECRET`: Generate with `python -c "import secrets; print(secrets.token_urlsafe(32))"`
- `BETTER_AUTH_SECRET`: Same as JWT_SECRET (must match frontend)

### 5. Initialize Database

```bash
python -m src.database
```

This creates the `users` and `tasks` tables.

### 6. Start Server

```bash
uvicorn src.main:app --reload --port 8000
```

Server runs at: http://localhost:8000

API documentation: http://localhost:8000/docs

## Project Structure

```
backend/
├── src/
│   ├── main.py           # FastAPI app entry point
│   ├── config.py         # Environment configuration
│   ├── database.py       # Database connection
│   ├── models/
│   │   ├── user.py       # User SQLModel
│   │   └── task.py       # Task SQLModel
│   ├── middleware/
│   │   └── auth.py       # JWT verification
│   ├── api/
│   │   └── tasks.py      # Task CRUD endpoints
│   └── schemas/
│       ├── task.py       # Request/response schemas
│       └── error.py      # Error schemas
├── tests/
├── requirements.txt
├── .env.example
└── README.md
```

## API Endpoints

📚 **[Complete API Documentation](./API_DOCUMENTATION.md)** - Comprehensive guide with examples, security details, and error handling

### Quick Reference

**Authentication:**
- `POST /api/auth/signup` - Create new account
- `POST /api/auth/signin` - Sign in and get JWT token

**Tasks** (All require JWT authentication):
- `GET /api/tasks` - List user's tasks
- `POST /api/tasks` - Create new task
- `GET /api/tasks/{id}` - Get specific task
- `PUT /api/tasks/{id}` - Update task
- `DELETE /api/tasks/{id}` - Delete task
- `PATCH /api/tasks/{id}/complete` - Toggle completion status

**Interactive Documentation:**
- Swagger UI: http://localhost:8001/docs
- ReDoc: http://localhost:8001/redoc

## Development

### Run Tests
```bash
pytest
```

### Check Code Quality
```bash
# Format code
black src/

# Type checking
mypy src/
```

## Security

- JWT verification on all protected endpoints
- User identity from token only (never from client)
- All queries filtered by authenticated user_id
- Passwords hashed with bcrypt
- Parameterized queries via SQLModel

## Troubleshooting

**Database connection fails:**
- Verify DATABASE_URL in .env
- Check Neon database is running
- Test connection with psql

**JWT verification fails:**
- Ensure JWT_SECRET matches frontend BETTER_AUTH_SECRET
- Check token format in Authorization header

**CORS errors:**
- Verify CORS_ORIGINS includes frontend URL
- Check frontend is running on expected port
