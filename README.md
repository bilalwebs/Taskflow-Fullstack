# KIro Todo - Multi-User Web Application

A secure, full-stack todo application built with Next.js and FastAPI, featuring JWT-based authentication and complete user data isolation.

## Features

- **User Authentication**: Secure signup and signin with JWT tokens
- **Task Management**: Create, read, update, and delete personal tasks
- **Task Completion**: Mark tasks as complete or incomplete
- **Data Isolation**: Each user can only access their own tasks
- **Responsive Design**: Works on desktop and mobile devices (320px-1920px)

## Technology Stack

### Frontend
- Next.js 16+ (App Router)
- React 19+
- Better Auth (JWT authentication)
- TypeScript
- Tailwind CSS

### Backend
- Python 3.11+
- FastAPI
- SQLModel (ORM)
- Neon Serverless PostgreSQL
- JWT verification with python-jose

## Quick Start

> 💡 **Having issues?** Check the [Troubleshooting Guide](./TROUBLESHOOTING.md)

### Prerequisites
- Node.js 18+
- Python 3.11+
- Neon PostgreSQL account (free at neon.tech)

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your database URL and secrets

# Initialize database
python -m src.database

# Start server
uvicorn src.main:app --reload --port 8000
```

Backend runs at: http://localhost:8000

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Configure environment
cp .env.local.example .env.local
# Edit .env.local with your API URL and secrets

# Start development server
npm run dev
```

Frontend runs at: http://localhost:3000

## Project Structure

```
KIro_Todo/
├── backend/              # FastAPI backend
│   ├── src/
│   │   ├── models/      # SQLModel entities
│   │   ├── api/         # API endpoints
│   │   ├── middleware/  # JWT verification
│   │   └── schemas/     # Pydantic schemas
│   └── tests/
├── frontend/            # Next.js frontend
│   ├── src/
│   │   ├── app/        # App Router pages
│   │   ├── components/ # React components
│   │   └── lib/        # Utilities
│   └── tests/
└── specs/              # Feature specifications
```

## Development

See detailed setup instructions in:
- [Backend README](./backend/README.md)
- [Frontend README](./frontend/README.md)
- [Quickstart Guide](./specs/001-multi-user-todo-app/quickstart.md)

## Security

- Passwords are hashed with bcrypt before storage
- JWT tokens required for all protected endpoints
- User identity extracted from tokens, never from client input
- Complete data isolation between users
- All secrets stored in environment variables

## Documentation

### API Documentation
- 📚 **[Complete API Documentation](./backend/API_DOCUMENTATION.md)** - Comprehensive REST API guide with examples
- 🔗 [Interactive Swagger UI](http://localhost:8001/docs) - Test API endpoints (when backend is running)
- 📖 [ReDoc Documentation](http://localhost:8001/redoc) - Alternative API documentation view

### Project Documentation
- [Feature Specification](./specs/001-multi-user-todo-app/spec.md) - Requirements and user stories
- [Implementation Plan](./specs/001-multi-user-todo-app/plan.md) - Technical architecture and approach
- [Implementation Tasks](./specs/001-multi-user-todo-app/tasks.md) - Detailed task breakdown
- [Data Model](./specs/001-multi-user-todo-app/data-model.md) - Database schema and relationships
- [API Contracts](./specs/001-multi-user-todo-app/contracts/) - Endpoint specifications

## License

MIT
