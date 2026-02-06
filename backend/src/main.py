from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from .config import settings
from .schemas.error import ErrorResponse
from .api import tasks_router, auth_router, chat_router
from .agents import TaskAgent


# Initialize FastAPI application
app = FastAPI(
    title="KIro Todo API",
    description="RESTful API for multi-user todo application with JWT authentication and Cohere AI agent",
    version="1.0.0"
)


# Global agent instance (initialized at startup)
task_agent: TaskAgent = None


@app.on_event("startup")
async def startup_event():
    """
    Initialize application components at startup.

    This includes:
    - Creating the TaskAgent instance
    - Verifying OpenAI/OpenRouter API connectivity
    """
    global task_agent

    # Initialize the task agent
    task_agent = TaskAgent()

    # Verify agent can connect to API
    is_healthy = await task_agent.health_check()
    if is_healthy:
        print(f"[OK] TaskAgent initialized successfully with model: {task_agent.model}")
    else:
        print(f"[WARNING] TaskAgent initialized but API health check failed")


def get_task_agent() -> TaskAgent:
    """
    Get the global TaskAgent instance.

    This function can be used as a dependency in route handlers.

    Returns:
        TaskAgent: The initialized agent instance

    Raises:
        RuntimeError: If agent is not initialized
    """
    if task_agent is None:
        raise RuntimeError("TaskAgent not initialized. Application startup may have failed.")
    return task_agent


# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Include API routers
app.include_router(auth_router)
app.include_router(tasks_router)
app.include_router(chat_router)


# Global exception handler for HTTPException
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc: HTTPException):
    """Handle HTTP exceptions with consistent error response format."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "message": get_user_friendly_message(exc.status_code),
            "details": getattr(exc, "details", None)
        }
    )


def get_user_friendly_message(status_code: int) -> str:
    """Get user-friendly message for HTTP status code."""
    messages = {
        400: "The request contains invalid data",
        401: "Authentication is required to access this resource",
        403: "You do not have permission to access this resource",
        404: "The requested resource was not found",
        500: "An internal server error occurred"
    }
    return messages.get(status_code, "An error occurred")


# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint to verify API is running."""
    return {
        "status": "healthy",
        "environment": settings.ENVIRONMENT
    }


# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    """Root endpoint with API information."""
    return {
        "message": "KIro Todo API",
        "version": "1.0.0",
        "docs": "/docs"
    }
