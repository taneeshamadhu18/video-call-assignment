import pytest
from fastapi.testclient import TestClient
from models import Participant

class TestParticipantsAPI:
    """Test suite for participants API endpoints."""

    def test_get_participants_empty(self, client):
        """Test getting participants when database is empty."""
        response = client.get("/participants")
        assert response.status_code == 200
        assert response.json() == []

    def test_get_participants_with_data(self, client, db_session, sample_participant):
        """Test getting participants when database has data."""
        # Add test participant to database
        participant = Participant(**sample_participant)
        db_session.add(participant)
        db_session.commit()
        db_session.refresh(participant)

        response = client.get("/participants")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["name"] == sample_participant["name"]
        assert data[0]["email"] == sample_participant["email"]

    def test_get_participants_with_search(self, client, db_session):
        """Test searching participants by name."""
        # Add multiple participants
        participants = [
            Participant(name="Alice Johnson", email="alice@test.com", role="Host", online=True, mic_on=False, camera_on=False),
            Participant(name="Bob Smith", email="bob@test.com", role="Guest", online=False, mic_on=False, camera_on=False),
            Participant(name="Carol White", email="carol@test.com", role="Guest", online=True, mic_on=False, camera_on=False)
        ]
        
        for participant in participants:
            db_session.add(participant)
        db_session.commit()

        # Test search functionality
        response = client.get("/participants?search=alice")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["name"] == "Alice Johnson"

    def test_get_participants_with_pagination(self, client, db_session):
        """Test participants pagination."""
        # Add multiple participants
        participants = [
            Participant(name=f"User {i}", email=f"user{i}@test.com", role="Guest", 
                       online=True, mic_on=False, camera_on=False) 
            for i in range(10)
        ]
        
        for participant in participants:
            db_session.add(participant)
        db_session.commit()

        # Test pagination
        response = client.get("/participants?limit=5&offset=0")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 5

        response = client.get("/participants?limit=5&offset=5")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 5

    def test_get_participant_count(self, client, db_session):
        """Test getting participant count."""
        response = client.get("/participants/count")
        assert response.status_code == 200
        assert response.json()["total"] == 0

        # Add participants
        participants = [
            Participant(name="User 1", email="user1@test.com", role="Guest", online=True, mic_on=False, camera_on=False),
            Participant(name="User 2", email="user2@test.com", role="Host", online=False, mic_on=False, camera_on=False)
        ]
        
        for participant in participants:
            db_session.add(participant)
        db_session.commit()

        response = client.get("/participants/count")
        assert response.status_code == 200
        assert response.json()["total"] == 2

    def test_get_participant_by_id(self, client, db_session, sample_participant):
        """Test getting a specific participant by ID."""
        # Add participant
        participant = Participant(**sample_participant)
        db_session.add(participant)
        db_session.commit()
        db_session.refresh(participant)

        response = client.get(f"/participants/{participant.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == participant.id
        assert data["name"] == sample_participant["name"]

    def test_get_participant_not_found(self, client):
        """Test getting a participant that doesn't exist."""
        response = client.get("/participants/999")
        assert response.status_code == 404

    def test_update_participant_microphone(self, client, db_session, sample_participant):
        """Test updating participant microphone status."""
        # Add participant
        participant = Participant(**sample_participant)
        db_session.add(participant)
        db_session.commit()
        db_session.refresh(participant)

        # Update microphone status
        response = client.put(f"/participants/{participant.id}/microphone", 
                            json={"mic_on": True})
        assert response.status_code == 200
        data = response.json()
        assert data["mic_on"] == True

    def test_update_participant_camera(self, client, db_session, sample_participant):
        """Test updating participant camera status."""
        # Add participant
        participant = Participant(**sample_participant)
        db_session.add(participant)
        db_session.commit()
        db_session.refresh(participant)

        # Update camera status
        response = client.put(f"/participants/{participant.id}/camera", 
                            json={"camera_on": True})
        assert response.status_code == 200
        data = response.json()
        assert data["camera_on"] == True

    def test_update_participant_status(self, client, db_session, sample_participant):
        """Test updating participant online status."""
        # Add participant
        participant = Participant(**sample_participant)
        participant.online = False
        db_session.add(participant)
        db_session.commit()
        db_session.refresh(participant)

        # Update online status
        response = client.put(f"/participants/{participant.id}/status", 
                            json={"online": True})
        assert response.status_code == 200
        data = response.json()
        assert data["online"] == True

    def test_update_nonexistent_participant(self, client):
        """Test updating a participant that doesn't exist."""
        response = client.put("/participants/999/microphone", 
                            json={"mic_on": True})
        assert response.status_code == 404

    def test_root_endpoint(self, client):
        """Test root endpoint returns status."""
        response = client.get("/")
        assert response.status_code == 200
        assert "status" in response.json()

class TestDataValidation:
    """Test suite for data validation."""

    def test_invalid_microphone_update(self, client, db_session, sample_participant):
        """Test updating microphone with invalid data."""
        # Add participant
        participant = Participant(**sample_participant)
        db_session.add(participant)
        db_session.commit()

        # Invalid data
        response = client.put(f"/participants/{participant.id}/microphone", 
                            json={"mic_on": "invalid"})
        assert response.status_code == 422

    def test_invalid_camera_update(self, client, db_session, sample_participant):
        """Test updating camera with invalid data."""
        # Add participant
        participant = Participant(**sample_participant)
        db_session.add(participant)
        db_session.commit()

        # Invalid data
        response = client.put(f"/participants/{participant.id}/camera", 
                            json={"camera_on": "invalid"})
        assert response.status_code == 422

    def test_invalid_status_update(self, client, db_session, sample_participant):
        """Test updating status with invalid data."""
        # Add participant
        participant = Participant(**sample_participant)
        db_session.add(participant)
        db_session.commit()

        # Invalid data
        response = client.put(f"/participants/{participant.id}/status", 
                            json={"online": "invalid"})
        assert response.status_code == 422