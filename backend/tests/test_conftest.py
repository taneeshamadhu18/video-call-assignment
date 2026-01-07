import pytest
from httpx import AsyncClient
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
import sys
import os

# Add the backend directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from main import app, get_db
from database import Base
from models import Participant

# Test database configuration
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function")
def test_db():
    """Create a test database for each test"""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def db_session(test_db):
    """Create a database session for testing"""
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()

@pytest.fixture(scope="function")
def override_get_db(db_session):
    """Override the get_db dependency for testing"""
    def _override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = _override_get_db
    yield
    app.dependency_overrides.clear()

@pytest.fixture(scope="function")
def client(override_get_db):
    """Create a test client"""
    return TestClient(app)

@pytest.fixture(scope="function")
async def async_client(override_get_db):
    """Create an async test client"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client

@pytest.fixture
def sample_participant():
    """Create a sample participant for testing"""
    return {
        "name": "Alice Johnson",
        "email": "alice@example.com",
        "role": "Host",
        "mic_on": True,
        "camera_on": True,
        "online": True,
        "avatar_url": "https://api.dicebear.com/7.x/avataaars/svg?seed=Alice"
    }

@pytest.fixture
def multiple_participants():
    """Create multiple participants for testing"""
    return [
        {
            "name": "Alice Johnson",
            "email": "alice@example.com",
            "role": "Host",
            "mic_on": True,
            "camera_on": True,
            "online": True,
            "avatar_url": "https://api.dicebear.com/7.x/avataaars/svg?seed=Alice"
        },
        {
            "name": "Bob Smith",
            "email": "bob@example.com",
            "role": "Guest",
            "mic_on": False,
            "camera_on": True,
            "online": True,
            "avatar_url": "https://api.dicebear.com/7.x/avataaars/svg?seed=Bob"
        },
        {
            "name": "Charlie Brown",
            "email": "charlie@example.com",
            "role": "Moderator",
            "mic_on": True,
            "camera_on": False,
            "online": False,
            "avatar_url": "https://api.dicebear.com/7.x/avataaars/svg?seed=Charlie"
        },
        {
            "name": "Diana Prince",
            "email": "diana@example.com",
            "role": "Guest",
            "mic_on": True,
            "camera_on": True,
            "online": True,
            "avatar_url": "https://api.dicebear.com/7.x/avataaars/svg?seed=Diana"
        },
        {
            "name": "Eve Wilson",
            "email": "eve@example.com",
            "role": "Host",
            "mic_on": False,
            "camera_on": False,
            "online": False,
            "avatar_url": "https://api.dicebear.com/7.x/avataaars/svg?seed=Eve"
        }
    ]

def create_participant_in_db(db_session: Session, participant_data: dict):
    """Helper function to create a participant in the database"""
    participant = Participant(**participant_data)
    db_session.add(participant)
    db_session.commit()
    db_session.refresh(participant)
    return participant