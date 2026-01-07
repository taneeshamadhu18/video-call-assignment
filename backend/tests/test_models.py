import pytest
from datetime import datetime, timedelta
from models import Participant
from sqlalchemy.exc import IntegrityError

class TestParticipantModel:
    """Test suite for Participant model."""

    def test_create_participant(self, db_session):
        """Test creating a new participant."""
        participant = Participant(
            name="Test User",
            email="test@example.com",
            role="Guest",
            online=True,
            mic_on=False,
            camera_on=False,
            about_me="Test description",
            resume_url="https://example.com/resume.pdf"
        )
        
        db_session.add(participant)
        db_session.commit()
        db_session.refresh(participant)
        
        assert participant.id is not None
        assert participant.name == "Test User"
        assert participant.email == "test@example.com"
        assert participant.role == "Guest"
        assert participant.online == True
        assert participant.mic_on == False
        assert participant.camera_on == False
        assert participant.created_at is not None
        assert participant.updated_at is not None

    def test_participant_with_minimal_data(self, db_session):
        """Test creating participant with minimal required data."""
        participant = Participant(
            name="Minimal User",
            email="minimal@example.com",
            role="Guest",
            online=False,
            mic_on=False,
            camera_on=False
        )
        
        db_session.add(participant)
        db_session.commit()
        db_session.refresh(participant)
        
        assert participant.id is not None
        assert participant.name == "Minimal User"
        assert participant.about_me is None
        assert participant.resume_url is None

    def test_participant_timestamps(self, db_session):
        """Test that timestamps are properly set."""
        before_creation = datetime.utcnow()
        
        participant = Participant(
            name="Timestamp User",
            email="timestamp@example.com",
            role="Host",
            online=True,
            mic_on=False,
            camera_on=False
        )
        
        db_session.add(participant)
        db_session.commit()
        db_session.refresh(participant)
        
        after_creation = datetime.utcnow()
        
        assert before_creation <= participant.created_at <= after_creation
        assert before_creation <= participant.updated_at <= after_creation

    def test_participant_string_representation(self, db_session):
        """Test participant string representation."""
        participant = Participant(
            name="String Test User",
            email="string@example.com",
            role="Guest",
            online=False,
            mic_on=False,
            camera_on=False
        )
        
        db_session.add(participant)
        db_session.commit()
        db_session.refresh(participant)
        
        str_repr = str(participant)
        assert "String Test User" in str_repr

    def test_participant_boolean_fields(self, db_session):
        """Test boolean field handling."""
        participant = Participant(
            name="Boolean User",
            email="boolean@example.com",
            role="Guest",
            online=True,
            mic_on=True,
            camera_on=True
        )
        
        db_session.add(participant)
        db_session.commit()
        db_session.refresh(participant)
        
        assert isinstance(participant.online, bool)
        assert isinstance(participant.mic_on, bool)
        assert isinstance(participant.camera_on, bool)
        assert participant.online == True
        assert participant.mic_on == True
        assert participant.camera_on == True

    def test_participant_role_values(self, db_session):
        """Test different role values."""
        roles = ["Host", "Guest", "Admin", "Moderator"]
        
        for i, role in enumerate(roles):
            participant = Participant(
                name=f"Role User {i}",
                email=f"role{i}@example.com",
                role=role,
                online=True,
                mic_on=False,
                camera_on=False
            )
            
            db_session.add(participant)
        
        db_session.commit()
        
        # Query and verify
        participants = db_session.query(Participant).all()
        retrieved_roles = [p.role for p in participants]
        
        for role in roles:
            assert role in retrieved_roles

    def test_participant_optional_fields(self, db_session):
        """Test participants with and without optional fields."""
        # Participant with optional fields
        participant_with_extras = Participant(
            name="Full User",
            email="full@example.com",
            role="Guest",
            online=True,
            mic_on=False,
            camera_on=False,
            about_me="Detailed description",
            resume_url="https://example.com/resume.pdf"
        )
        
        # Participant without optional fields
        participant_minimal = Participant(
            name="Basic User",
            email="basic@example.com",
            role="Guest",
            online=True,
            mic_on=False,
            camera_on=False
        )
        
        db_session.add(participant_with_extras)
        db_session.add(participant_minimal)
        db_session.commit()
        
        db_session.refresh(participant_with_extras)
        db_session.refresh(participant_minimal)
        
        assert participant_with_extras.about_me == "Detailed description"
        assert participant_with_extras.resume_url == "https://example.com/resume.pdf"
        assert participant_minimal.about_me is None
        assert participant_minimal.resume_url is None

    def test_participant_update(self, db_session):
        """Test updating participant fields."""
        participant = Participant(
            name="Update User",
            email="update@example.com",
            role="Guest",
            online=False,
            mic_on=False,
            camera_on=False
        )
        
        db_session.add(participant)
        db_session.commit()
        db_session.refresh(participant)
        
        original_updated_at = participant.updated_at
        
        # Update participant
        participant.online = True
        participant.mic_on = True
        participant.updated_at = datetime.utcnow()
        
        db_session.commit()
        db_session.refresh(participant)
        
        assert participant.online == True
        assert participant.mic_on == True
        assert participant.updated_at > original_updated_at

class TestDatabaseIntegrity:
    """Test suite for database integrity and constraints."""

    def test_participant_query_operations(self, db_session):
        """Test various query operations on participants."""
        # Create multiple participants
        participants_data = [
            {"name": "Alice Johnson", "email": "alice@test.com", "role": "Host", "online": True},
            {"name": "Bob Smith", "email": "bob@test.com", "role": "Guest", "online": False},
            {"name": "Carol White", "email": "carol@test.com", "role": "Guest", "online": True},
            {"name": "David Brown", "email": "david@test.com", "role": "Admin", "online": False}
        ]
        
        for data in participants_data:
            participant = Participant(
                name=data["name"],
                email=data["email"],
                role=data["role"],
                online=data["online"],
                mic_on=False,
                camera_on=False
            )
            db_session.add(participant)
        
        db_session.commit()
        
        # Test various queries
        all_participants = db_session.query(Participant).all()
        assert len(all_participants) == 4
        
        online_participants = db_session.query(Participant).filter(Participant.online == True).all()
        assert len(online_participants) == 2
        
        guest_participants = db_session.query(Participant).filter(Participant.role == "Guest").all()
        assert len(guest_participants) == 2
        
        alice = db_session.query(Participant).filter(Participant.name.like("%Alice%")).first()
        assert alice is not None
        assert alice.name == "Alice Johnson"