from sqlmodel import SQLModel, create_engine, Session
from sqlalchemy.pool import NullPool
from .config import settings

# Import models to register them with SQLModel metadata
from .models.user import User  # noqa: F401
from .models.task import Task  # noqa: F401
from .models.conversation import Conversation  # noqa: F401
from .models.message import Message  # noqa: F401


# Create engine with appropriate pooling for serverless
engine = create_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    poolclass=NullPool  # Let Neon handle connection pooling
)


def init_db():
    """Initialize database by creating all tables."""
    SQLModel.metadata.create_all(engine)
    print("Database tables created successfully")


def get_session():
    """Dependency for getting database session."""
    with Session(engine) as session:
        yield session
