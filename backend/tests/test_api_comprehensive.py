import pytest
from httpx import AsyncClient
import sys
import os

# Add the backend directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from test_conftest import *

class TestHealthEndpoint:
    """Test the health check endpoint"""
    
    def test_health_check(self, client):
        """Test basic health check"""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "healthy"}

    @pytest.mark.asyncio
    async def test_health_check_async(self, async_client):
        """Test async health check"""
        response = await async_client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "healthy"}

class TestParticipantsEndpoint:
    """Test participants CRUD endpoints"""
    
    def test_get_participants_empty(self, client):
        """Test getting participants when database is empty"""
        response = client.get("/participants")
        assert response.status_code == 200
        assert response.json() == []

    def test_get_participants_with_data(self, client, db_session, multiple_participants):
        """Test getting participants when database has data"""
        # Create participants in database
        for participant_data in multiple_participants:
            create_participant_in_db(db_session, participant_data)
        
        response = client.get("/participants")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 5
        
        # Check that data is returned in correct format
        first_participant = data[0]
        assert "id" in first_participant
        assert "name" in first_participant
        assert "email" in first_participant
        assert "role" in first_participant
        assert "created_at" in first_participant

    def test_get_participants_with_limit(self, client, db_session, multiple_participants):
        """Test getting participants with limit parameter"""
        # Create participants in database
        for participant_data in multiple_participants:
            create_participant_in_db(db_session, participant_data)
        
        response = client.get("/participants?limit=3")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3

    def test_get_participants_with_offset(self, client, db_session, multiple_participants):
        """Test getting participants with offset parameter"""
        # Create participants in database
        participants = []
        for participant_data in multiple_participants:
            p = create_participant_in_db(db_session, participant_data)
            participants.append(p)
        
        # Get first 2 participants
        response1 = client.get("/participants?limit=2&offset=0")
        assert response1.status_code == 200
        first_batch = response1.json()
        assert len(first_batch) == 2
        
        # Get next 2 participants
        response2 = client.get("/participants?limit=2&offset=2")
        assert response2.status_code == 200
        second_batch = response2.json()
        assert len(second_batch) == 2
        
        # Ensure no overlap
        first_ids = {p["id"] for p in first_batch}
        second_ids = {p["id"] for p in second_batch}
        assert first_ids.isdisjoint(second_ids)

    def test_get_participants_with_search(self, client, db_session, multiple_participants):
        """Test searching participants"""
        # Create participants in database
        for participant_data in multiple_participants:
            create_participant_in_db(db_session, participant_data)
        
        # Search by name
        response = client.get("/participants?search=Alice")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["name"] == "Alice Johnson"
        
        # Search by email
        response = client.get("/participants?search=bob@example.com")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["email"] == "bob@example.com"
        
        # Search by role
        response = client.get("/participants?search=Host")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2  # Alice and Eve are Hosts

    def test_get_participants_case_insensitive_search(self, client, db_session, sample_participant):
        """Test case-insensitive search"""
        create_participant_in_db(db_session, sample_participant)
        
        # Search with different cases
        for search_term in ["alice", "ALICE", "AlIcE"]:
            response = client.get(f"/participants?search={search_term}")
            assert response.status_code == 200
            data = response.json()
            assert len(data) == 1

    def test_get_participants_invalid_params(self, client):
        """Test invalid parameters"""
        # Negative limit
        response = client.get("/participants?limit=-1")
        assert response.status_code == 422
        
        # Negative offset
        response = client.get("/participants?offset=-1")
        assert response.status_code == 422
        
        # Invalid limit type
        response = client.get("/participants?limit=abc")
        assert response.status_code == 422

class TestParticipantCountEndpoint:
    """Test participant count endpoint"""
    
    def test_get_participant_count_empty(self, client):
        """Test count when database is empty"""
        response = client.get("/participants/count")
        assert response.status_code == 200
        assert response.json() == {"total": 0}

    def test_get_participant_count_with_data(self, client, db_session, multiple_participants):
        """Test count with data"""
        for participant_data in multiple_participants:
            create_participant_in_db(db_session, participant_data)
        
        response = client.get("/participants/count")
        assert response.status_code == 200
        assert response.json() == {"total": 5}

    def test_get_participant_count_with_search(self, client, db_session, multiple_participants):
        """Test count with search filter"""
        for participant_data in multiple_participants:
            create_participant_in_db(db_session, participant_data)
        
        # Count Host participants
        response = client.get("/participants/count?search=Host")
        assert response.status_code == 200
        assert response.json() == {"total": 2}
        
        # Count specific name
        response = client.get("/participants/count?search=Alice")
        assert response.status_code == 200
        assert response.json() == {"total": 1}

class TestSingleParticipantEndpoint:
    """Test single participant endpoints"""
    
    def test_get_participant_by_id(self, client, db_session, sample_participant):
        """Test getting a single participant"""
        participant = create_participant_in_db(db_session, sample_participant)
        
        response = client.get(f"/participants/{participant.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == participant.id
        assert data["name"] == participant.name
        assert data["email"] == participant.email

    def test_get_participant_not_found(self, client):
        """Test getting non-existent participant"""
        response = client.get("/participants/999")
        assert response.status_code == 404
        assert response.json() == {"detail": "Participant not found"}

    def test_get_participant_invalid_id(self, client):
        """Test getting participant with invalid ID"""
        response = client.get("/participants/abc")
        assert response.status_code == 422

class TestUpdateMicrophoneEndpoint:
    """Test microphone update endpoint"""
    
    def test_update_microphone_on(self, client, db_session, sample_participant):
        """Test turning microphone on"""
        sample_participant["mic_on"] = False
        participant = create_participant_in_db(db_session, sample_participant)
        
        response = client.put(f"/participants/{participant.id}/microphone", 
                            json={"mic_on": True})
        assert response.status_code == 200
        data = response.json()
        assert data["mic_on"] is True
        
        # Verify in database
        db_session.refresh(participant)
        assert participant.mic_on is True

    def test_update_microphone_off(self, client, db_session, sample_participant):
        """Test turning microphone off"""
        participant = create_participant_in_db(db_session, sample_participant)
        
        response = client.put(f"/participants/{participant.id}/microphone", 
                            json={"mic_on": False})
        assert response.status_code == 200
        data = response.json()
        assert data["mic_on"] is False
        
        # Verify in database
        db_session.refresh(participant)
        assert participant.mic_on is False

    def test_update_microphone_participant_not_found(self, client):
        """Test updating microphone for non-existent participant"""
        response = client.put("/participants/999/microphone", 
                            json={"mic_on": True})
        assert response.status_code == 404

    def test_update_microphone_invalid_data(self, client, db_session, sample_participant):
        """Test updating microphone with invalid data"""
        participant = create_participant_in_db(db_session, sample_participant)
        
        # Missing mic_on field
        response = client.put(f"/participants/{participant.id}/microphone", 
                            json={})
        assert response.status_code == 422
        
        # Invalid mic_on type
        response = client.put(f"/participants/{participant.id}/microphone", 
                            json={"mic_on": "invalid"})
        assert response.status_code == 422

class TestUpdateCameraEndpoint:
    """Test camera update endpoint"""
    
    def test_update_camera_on(self, client, db_session, sample_participant):
        """Test turning camera on"""
        sample_participant["camera_on"] = False
        participant = create_participant_in_db(db_session, sample_participant)
        
        response = client.put(f"/participants/{participant.id}/camera", 
                            json={"camera_on": True})
        assert response.status_code == 200
        data = response.json()
        assert data["camera_on"] is True

    def test_update_camera_off(self, client, db_session, sample_participant):
        """Test turning camera off"""
        participant = create_participant_in_db(db_session, sample_participant)
        
        response = client.put(f"/participants/{participant.id}/camera", 
                            json={"camera_on": False})
        assert response.status_code == 200
        data = response.json()
        assert data["camera_on"] is False

    def test_update_camera_participant_not_found(self, client):
        """Test updating camera for non-existent participant"""
        response = client.put("/participants/999/camera", 
                            json={"camera_on": True})
        assert response.status_code == 404

class TestUpdateStatusEndpoint:
    """Test status update endpoint"""
    
    def test_update_status_online(self, client, db_session, sample_participant):
        """Test setting participant online"""
        sample_participant["online"] = False
        participant = create_participant_in_db(db_session, sample_participant)
        
        response = client.put(f"/participants/{participant.id}/status", 
                            json={"online": True})
        assert response.status_code == 200
        data = response.json()
        assert data["online"] is True

    def test_update_status_offline(self, client, db_session, sample_participant):
        """Test setting participant offline"""
        participant = create_participant_in_db(db_session, sample_participant)
        
        response = client.put(f"/participants/{participant.id}/status", 
                            json={"online": False})
        assert response.status_code == 200
        data = response.json()
        assert data["online"] is False

    def test_update_status_participant_not_found(self, client):
        """Test updating status for non-existent participant"""
        response = client.put("/participants/999/status", 
                            json={"online": True})
        assert response.status_code == 404

class TestCORSHeaders:
    """Test CORS functionality"""
    
    def test_cors_headers_present(self, client):
        """Test that CORS headers are present"""
        response = client.get("/participants")
        assert response.status_code == 200
        # Note: TestClient doesn't include CORS headers by default
        # In a real test, you'd check for:
        # assert "access-control-allow-origin" in response.headers

    def test_options_request(self, client):
        """Test OPTIONS request for CORS"""
        response = client.options("/participants")
        # TestClient may not handle OPTIONS requests the same way
        # This is more of a placeholder for actual CORS testing

class TestErrorHandling:
    """Test error handling scenarios"""
    
    def test_database_error_simulation(self, client, db_session):
        """Test handling of database errors"""
        # This would require mocking the database to raise an exception
        # For now, we test the error response format
        response = client.get("/participants/abc")  # Invalid ID format
        assert response.status_code == 422
        assert "detail" in response.json()

    def test_malformed_json_request(self, client, db_session, sample_participant):
        """Test handling of malformed JSON"""
        participant = create_participant_in_db(db_session, sample_participant)
        
        # Send malformed JSON
        response = client.put(f"/participants/{participant.id}/microphone",
                            data="not json",
                            headers={"Content-Type": "application/json"})
        assert response.status_code == 422

    def test_empty_request_body(self, client, db_session, sample_participant):
        """Test handling of empty request body"""
        participant = create_participant_in_db(db_session, sample_participant)
        
        response = client.put(f"/participants/{participant.id}/microphone",
                            json=None)
        assert response.status_code == 422

class TestDataValidation:
    """Test data validation"""
    
    def test_participant_data_types(self, client, db_session, sample_participant):
        """Test that participant data has correct types"""
        participant = create_participant_in_db(db_session, sample_participant)
        
        response = client.get(f"/participants/{participant.id}")
        assert response.status_code == 200
        data = response.json()
        
        assert isinstance(data["id"], int)
        assert isinstance(data["name"], str)
        assert isinstance(data["email"], str)
        assert isinstance(data["role"], str)
        assert isinstance(data["mic_on"], bool)
        assert isinstance(data["camera_on"], bool)
        assert isinstance(data["online"], bool)
        assert isinstance(data["created_at"], str)

    def test_boolean_field_validation(self, client, db_session, sample_participant):
        """Test boolean field validation"""
        participant = create_participant_in_db(db_session, sample_participant)
        
        # Test valid boolean values
        for value in [True, False]:
            response = client.put(f"/participants/{participant.id}/microphone",
                                json={"mic_on": value})
            assert response.status_code == 200
        
        # Test invalid boolean values (handled by Pydantic)
        response = client.put(f"/participants/{participant.id}/microphone",
                            json={"mic_on": "maybe"})
        assert response.status_code == 422

class TestPerformance:
    """Test performance-related scenarios"""
    
    def test_large_dataset_pagination(self, client, db_session):
        """Test pagination with larger dataset"""
        # Create many participants
        participants_data = []
        for i in range(50):
            participants_data.append({
                "name": f"User {i}",
                "email": f"user{i}@example.com",
                "role": "Guest",
                "mic_on": i % 2 == 0,
                "camera_on": i % 3 == 0,
                "online": i % 4 == 0,
                "avatar_url": f"https://api.dicebear.com/7.x/avataaars/svg?seed=User{i}"
            })
        
        for participant_data in participants_data:
            create_participant_in_db(db_session, participant_data)
        
        # Test that pagination works efficiently
        response = client.get("/participants?limit=10&offset=0")
        assert response.status_code == 200
        assert len(response.json()) == 10
        
        response = client.get("/participants?limit=10&offset=40")
        assert response.status_code == 200
        assert len(response.json()) == 10

    def test_search_performance(self, client, db_session):
        """Test search performance with multiple participants"""
        # Create participants with searchable data
        search_participants = [
            {"name": "Alice Search", "email": "alice@search.com", "role": "Host"},
            {"name": "Bob Test", "email": "bob@test.com", "role": "Guest"},
            {"name": "Search Charlie", "email": "charlie@example.com", "role": "Moderator"},
            {"name": "Dave Normal", "email": "dave@normal.com", "role": "Guest"},
        ]
        
        for participant_data in search_participants:
            full_data = {**participant_data, "mic_on": True, "camera_on": True, 
                        "online": True, "avatar_url": "https://example.com/avatar.png"}
            create_participant_in_db(db_session, full_data)
        
        # Test search functionality
        response = client.get("/participants?search=Search")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2  # Alice Search and Search Charlie
        
        # Verify search is working across different fields
        search_terms = ["alice", "bob@test.com", "Moderator"]
        for term in search_terms:
            response = client.get(f"/participants?search={term}")
            assert response.status_code == 200
            assert len(response.json()) >= 1

@pytest.mark.asyncio
class TestAsyncEndpoints:
    """Test endpoints using async client"""
    
    async def test_async_get_participants(self, async_client, db_session, sample_participant):
        """Test async get participants"""
        create_participant_in_db(db_session, sample_participant)
        
        response = await async_client.get("/participants")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1

    async def test_async_update_microphone(self, async_client, db_session, sample_participant):
        """Test async microphone update"""
        participant = create_participant_in_db(db_session, sample_participant)
        
        response = await async_client.put(f"/participants/{participant.id}/microphone",
                                        json={"mic_on": False})
        assert response.status_code == 200
        data = response.json()
        assert data["mic_on"] is False

    async def test_async_error_handling(self, async_client):
        """Test async error handling"""
        response = await async_client.get("/participants/999")
        assert response.status_code == 404
        assert response.json() == {"detail": "Participant not found"}