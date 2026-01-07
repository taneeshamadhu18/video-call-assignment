import pytest
import asyncio
from httpx import AsyncClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from datetime import datetime, timedelta

from main import app, get_db
from models import Base, Participant

# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session", autouse=True)
async def setup_database():
    """Set up test database"""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
async def client():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


@pytest.fixture
async def db_session():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
async def sample_participants(db_session):
    """Create sample participants for testing"""
    base_time = datetime.utcnow() - timedelta(days=1)
    
    participants = [
        Participant(
            name="Alice Johnson",
            email="alice@test.com",
            role="Host",
            online=True,
            mic_on=True,
            camera_on=True,
            about_me="Frontend engineer",
            resume_url="https://example.com/alice.pdf",
            created_at=base_time,
            updated_at=base_time + timedelta(hours=1)
        ),
        Participant(
            name="Bob Smith",
            email="bob@test.com",
            role="Guest",
            online=False,
            mic_on=False,
            camera_on=False,
            about_me="Backend developer",
            resume_url=None,
            created_at=base_time + timedelta(hours=1),
            updated_at=base_time + timedelta(hours=2)
        ),
        Participant(
            name="Carol White",
            email="carol@test.com",
            role="Guest",
            online=True,
            mic_on=True,
            camera_on=False,
            about_me="UI/UX designer",
            resume_url=None,
            created_at=base_time + timedelta(hours=2),
            updated_at=base_time + timedelta(hours=3)
        )
    ]
    
    for participant in participants:
        db_session.add(participant)
    db_session.commit()
    
    # Refresh to get IDs
    for participant in participants:
        db_session.refresh(participant)
    
    yield participants
    
    # Cleanup
    for participant in participants:
        db_session.delete(participant)
    db_session.commit()


class TestParticipantAPI:
    """Test participant API endpoints"""

    async def test_root_endpoint(self, client):
        """Test root endpoint"""
        response = await client.get("/")
        assert response.status_code == 200
        assert response.json() == {"status": "Backend running"}

    async def test_get_participants(self, client, sample_participants):
        """Test getting participants list"""
        response = await client.get("/participants")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data) == 3
        assert data[0]["name"] == "Alice Johnson"
        assert data[1]["name"] == "Bob Smith"
        assert data[2]["name"] == "Carol White"

    async def test_get_participants_with_search(self, client, sample_participants):
        """Test searching participants by name"""
        response = await client.get("/participants?search=Alice")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data) == 1
        assert data[0]["name"] == "Alice Johnson"

    async def test_get_participants_with_pagination(self, client, sample_participants):
        """Test participant pagination"""
        response = await client.get("/participants?limit=2&offset=0")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data) == 2
        assert data[0]["name"] == "Alice Johnson"
        assert data[1]["name"] == "Bob Smith"
        
        # Get next page
        response = await client.get("/participants?limit=2&offset=2")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data) == 1
        assert data[0]["name"] == "Carol White"

    async def test_get_participants_count(self, client, sample_participants):
        """Test getting participant count"""
        response = await client.get("/participants/count")
        assert response.status_code == 200
        
        data = response.json()
        assert data["total"] == 3

    async def test_get_participants_count_with_search(self, client, sample_participants):
        """Test getting participant count with search"""
        response = await client.get("/participants/count?search=Alice")
        assert response.status_code == 200
        
        data = response.json()
        assert data["total"] == 1

    async def test_get_single_participant(self, client, sample_participants):
        """Test getting single participant"""
        participant_id = sample_participants[0].id
        
        response = await client.get(f"/participants/{participant_id}")
        assert response.status_code == 200
        
        data = response.json()
        assert data["name"] == "Alice Johnson"
        assert data["email"] == "alice@test.com"
        assert data["role"] == "Host"
        assert data["online"] == True
        assert data["mic_on"] == True
        assert data["camera_on"] == True

    async def test_get_nonexistent_participant(self, client):
        """Test getting participant that doesn't exist"""
        response = await client.get("/participants/99999")
        assert response.status_code == 404
        assert response.json()["detail"] == "Participant not found"

    async def test_update_participant_media(self, client, sample_participants):
        """Test updating participant media state"""
        participant_id = sample_participants[0].id
        
        response = await client.patch(
            f"/participants/{participant_id}/media",
            json={"mic_on": False, "camera_on": False}
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["mic_on"] == False
        assert data["camera_on"] == False
        assert data["name"] == "Alice Johnson"

    async def test_update_participant_microphone(self, client, sample_participants):
        """Test updating participant microphone"""
        participant_id = sample_participants[0].id
        
        response = await client.patch(
            f"/participants/{participant_id}/microphone",
            json={"mic_on": False}
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["mic_on"] == False
        assert data["name"] == "Alice Johnson"

    async def test_update_participant_camera(self, client, sample_participants):
        """Test updating participant camera"""
        participant_id = sample_participants[0].id
        
        response = await client.patch(
            f"/participants/{participant_id}/camera",
            json={"camera_on": False}
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["camera_on"] == False
        assert data["name"] == "Alice Johnson"

    async def test_update_participant_status(self, client, sample_participants):
        """Test updating participant online status"""
        participant_id = sample_participants[0].id
        
        response = await client.patch(
            f"/participants/{participant_id}/status",
            json={"online": False}
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["online"] == False
        assert data["name"] == "Alice Johnson"

    async def test_update_nonexistent_participant(self, client):
        """Test updating participant that doesn't exist"""
        response = await client.patch(
            "/participants/99999/microphone",
            json={"mic_on": False}
        )
        assert response.status_code == 404
        assert response.json()["detail"] == "Participant not found"

    async def test_invalid_payload_validation(self, client, sample_participants):
        """Test API validation with invalid payloads"""
        participant_id = sample_participants[0].id
        
        # Test missing required field
        response = await client.patch(
            f"/participants/{participant_id}/microphone",
            json={}
        )
        assert response.status_code == 422

        # Test wrong data type
        response = await client.patch(
            f"/participants/{participant_id}/microphone",
            json={"mic_on": "not_a_boolean"}
        )
        assert response.status_code == 422

    async def test_timestamp_updates(self, client, sample_participants, db_session):
        """Test that updated_at timestamp changes on updates"""
        participant = sample_participants[0]
        original_updated_at = participant.updated_at
        
        # Small delay to ensure timestamp difference
        await asyncio.sleep(0.1)
        
        response = await client.patch(
            f"/participants/{participant.id}/microphone",
            json={"mic_on": False}
        )
        assert response.status_code == 200
        
        # Refresh participant from database
        db_session.refresh(participant)
        
        # Check that updated_at has changed
        assert participant.updated_at > original_updated_at


class TestParticipantFiltering:
    """Test participant search and filtering functionality"""

    async def test_case_insensitive_search(self, client, sample_participants):
        """Test case insensitive search"""
        response = await client.get("/participants?search=alice")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data) == 1
        assert data[0]["name"] == "Alice Johnson"

    async def test_partial_name_search(self, client, sample_participants):
        """Test partial name matching"""
        response = await client.get("/participants?search=John")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data) == 1
        assert data[0]["name"] == "Alice Johnson"

    async def test_empty_search_returns_all(self, client, sample_participants):
        """Test empty search returns all participants"""
        response = await client.get("/participants?search=")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data) == 3

    async def test_no_matches_returns_empty(self, client, sample_participants):
        """Test search with no matches returns empty list"""
        response = await client.get("/participants?search=NonexistentName")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data) == 0


class TestDataIntegrity:
    """Test data integrity and state consistency"""

    async def test_state_persistence_across_requests(self, client, sample_participants):
        """Test that state changes persist across requests"""
        participant_id = sample_participants[0].id
        
        # Update microphone state
        response = await client.patch(
            f"/participants/{participant_id}/microphone",
            json={"mic_on": False}
        )
        assert response.status_code == 200
        
        # Get participant and verify change persisted
        response = await client.get(f"/participants/{participant_id}")
        assert response.status_code == 200
        
        data = response.json()
        assert data["mic_on"] == False
        assert data["camera_on"] == True  # Should remain unchanged

    async def test_concurrent_updates(self, client, sample_participants):
        """Test handling of concurrent updates to same participant"""
        participant_id = sample_participants[0].id
        
        # Simulate concurrent updates
        tasks = [
            client.patch(f"/participants/{participant_id}/microphone", json={"mic_on": False}),
            client.patch(f"/participants/{participant_id}/camera", json={"camera_on": False})
        ]
        
        responses = await asyncio.gather(*tasks)
        
        # Both requests should succeed
        assert all(r.status_code == 200 for r in responses)
        
        # Verify final state
        response = await client.get(f"/participants/{participant_id}")
        data = response.json()
        assert data["mic_on"] == False
        assert data["camera_on"] == False