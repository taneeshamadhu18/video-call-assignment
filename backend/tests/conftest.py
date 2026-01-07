import sys
import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from main import app, get_db
from models import Base, Participant

# Create a test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture
def client():
    # Create the database tables
    Base.metadata.create_all(bind=engine)
    
    # Create test client
    with TestClient(app) as test_client:
        yield test_client
    
    # Drop tables after tests
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def sample_participant():
    return {
        "name": "Test User",
        "email": "test@example.com", 
        "role": "Guest",
        "online": True,
        "mic_on": False,
        "camera_on": False,
        "about_me": "Test participant for testing",
        "resume_url": "https://example.com/resume.pdf"
    }

@pytest.fixture
def db_session():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)
