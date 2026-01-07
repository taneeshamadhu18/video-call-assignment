import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import sys
import os
from datetime import datetime

# Add the backend directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from database import Base
from models import Participant

# Test database configuration
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_models.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class TestParticipantModel:
    """Test the Participant model"""
    
    @pytest.fixture(scope="function")
    def test_db(self):
        """Create a test database for each test"""
        Base.metadata.create_all(bind=engine)
        yield
        Base.metadata.drop_all(bind=engine)

    @pytest.fixture(scope="function")
    def db_session(self, test_db):
        """Create a database session for testing"""
        session = TestingSessionLocal()
        try:
            yield session
        finally:
            session.close()

    def test_create_participant(self, db_session):
        """Test creating a participant"""
        participant = Participant(
            name="Alice Johnson",
            email="alice@example.com",
            role="Host",
            mic_on=True,
            camera_on=True,
            online=True,
            avatar_url="https://api.dicebear.com/7.x/avataaars/svg?seed=Alice"
        )
        
        db_session.add(participant)
        db_session.commit()
        db_session.refresh(participant)
        
        assert participant.id is not None
        assert participant.name == "Alice Johnson"
        assert participant.email == "alice@example.com"
        assert participant.role == "Host"
        assert participant.mic_on is True
        assert participant.camera_on is True
        assert participant.online is True
        assert participant.created_at is not None
        assert isinstance(participant.created_at, datetime)

    def test_participant_defaults(self, db_session):
        """Test participant default values"""
        participant = Participant(
            name="Bob Smith",
            email="bob@example.com",
            role="Guest"
            # Not setting other fields to test defaults
        )
        
        db_session.add(participant)
        db_session.commit()
        db_session.refresh(participant)
        
        # Check default values
        assert participant.mic_on is False  # Default value
        assert participant.camera_on is False  # Default value
        assert participant.online is True  # Default value
        assert participant.avatar_url is not None  # Auto-generated
        assert "dicebear" in participant.avatar_url

    def test_participant_required_fields(self, db_session):
        """Test that required fields are enforced"""
        # Test missing name
        with pytest.raises(Exception):
            participant = Participant(
                email="test@example.com",
                role="Guest"
            )
            db_session.add(participant)
            db_session.commit()
        
        db_session.rollback()
        
        # Test missing email
        with pytest.raises(Exception):
            participant = Participant(
                name="Test User",
                role="Guest"
            )
            db_session.add(participant)
            db_session.commit()
        
        db_session.rollback()
        
        # Test missing role
        with pytest.raises(Exception):
            participant = Participant(
                name="Test User",
                email="test@example.com"
            )
            db_session.add(participant)
            db_session.commit()

    def test_participant_string_representation(self, db_session):
        """Test participant string representation"""
        participant = Participant(
            name="Charlie Brown",
            email="charlie@example.com",
            role="Moderator"
        )
        
        # Test string representation
        expected_repr = f"<Participant(name='Charlie Brown', email='charlie@example.com')>"
        assert str(participant) == expected_repr

    def test_participant_field_lengths(self, db_session):
        """Test field length constraints"""
        # Test very long name (should work within reasonable limits)
        long_name = "A" * 100
        participant = Participant(
            name=long_name,
            email="test@example.com",
            role="Guest"
        )
        
        db_session.add(participant)
        db_session.commit()
        db_session.refresh(participant)
        
        assert participant.name == long_name

    def test_participant_email_field(self, db_session):
        """Test email field behavior"""
        # Test valid email formats
        valid_emails = [
            "test@example.com",
            "user.name@domain.co.uk",
            "user+tag@example-domain.com",
            "123@numbers.com"
        ]
        
        for i, email in enumerate(valid_emails):
            participant = Participant(
                name=f"User {i}",
                email=email,
                role="Guest"
            )
            
            db_session.add(participant)
            db_session.commit()
            db_session.refresh(participant)
            
            assert participant.email == email
            
            # Clean up for next iteration
            db_session.delete(participant)
            db_session.commit()

    def test_participant_role_field(self, db_session):
        """Test role field behavior"""
        valid_roles = ["Host", "Guest", "Moderator", "Admin", "Viewer"]
        
        for i, role in enumerate(valid_roles):
            participant = Participant(
                name=f"User {i}",
                email=f"user{i}@example.com",
                role=role
            )
            
            db_session.add(participant)
            db_session.commit()
            db_session.refresh(participant)
            
            assert participant.role == role
            
            # Clean up for next iteration
            db_session.delete(participant)
            db_session.commit()

    def test_participant_boolean_fields(self, db_session):
        """Test boolean field behavior"""
        # Test all combinations of boolean fields
        boolean_combinations = [
            (True, True, True),
            (True, True, False),
            (True, False, True),
            (True, False, False),
            (False, True, True),
            (False, True, False),
            (False, False, True),
            (False, False, False),
        ]
        
        for i, (mic_on, camera_on, online) in enumerate(boolean_combinations):
            participant = Participant(
                name=f"User {i}",
                email=f"user{i}@example.com",
                role="Guest",
                mic_on=mic_on,
                camera_on=camera_on,
                online=online
            )
            
            db_session.add(participant)
            db_session.commit()
            db_session.refresh(participant)
            
            assert participant.mic_on is mic_on
            assert participant.camera_on is camera_on
            assert participant.online is online
            
            # Clean up for next iteration
            db_session.delete(participant)
            db_session.commit()

    def test_participant_avatar_url_generation(self, db_session):
        """Test avatar URL auto-generation"""
        participant = Participant(
            name="Avatar Test",
            email="avatar@example.com",
            role="Guest"
        )
        
        db_session.add(participant)
        db_session.commit()
        db_session.refresh(participant)
        
        # Check that avatar URL is generated
        assert participant.avatar_url is not None
        assert participant.avatar_url != ""
        assert "dicebear" in participant.avatar_url
        assert "Avatar Test" in participant.avatar_url

    def test_participant_created_at_auto_set(self, db_session):
        """Test that created_at is automatically set"""
        before_creation = datetime.utcnow()
        
        participant = Participant(
            name="Timestamp Test",
            email="timestamp@example.com",
            role="Guest"
        )
        
        db_session.add(participant)
        db_session.commit()
        db_session.refresh(participant)
        
        after_creation = datetime.utcnow()
        
        assert participant.created_at is not None
        assert before_creation <= participant.created_at <= after_creation

class TestParticipantQueries:
    """Test database queries with Participant model"""
    
    @pytest.fixture(scope="function")
    def test_db(self):
        """Create a test database for each test"""
        Base.metadata.create_all(bind=engine)
        yield
        Base.metadata.drop_all(bind=engine)

    @pytest.fixture(scope="function")
    def db_session(self, test_db):
        """Create a database session for testing"""
        session = TestingSessionLocal()
        try:
            yield session
        finally:
            session.close()

    @pytest.fixture
    def sample_participants(self, db_session):
        """Create sample participants for testing"""
        participants_data = [
            {
                "name": "Alice Johnson",
                "email": "alice@example.com",
                "role": "Host",
                "mic_on": True,
                "camera_on": True,
                "online": True
            },
            {
                "name": "Bob Smith",
                "email": "bob@example.com",
                "role": "Guest",
                "mic_on": False,
                "camera_on": True,
                "online": True
            },
            {
                "name": "Charlie Brown",
                "email": "charlie@example.com",
                "role": "Moderator",
                "mic_on": True,
                "camera_on": False,
                "online": False
            },
            {
                "name": "Diana Prince",
                "email": "diana@example.com",
                "role": "Guest",
                "mic_on": True,
                "camera_on": True,
                "online": True
            }
        ]
        
        participants = []
        for data in participants_data:
            participant = Participant(**data)
            db_session.add(participant)
            participants.append(participant)
        
        db_session.commit()
        
        for participant in participants:
            db_session.refresh(participant)
        
        return participants

    def test_query_all_participants(self, db_session, sample_participants):
        """Test querying all participants"""
        participants = db_session.query(Participant).all()
        assert len(participants) == 4
        
        names = [p.name for p in participants]
        assert "Alice Johnson" in names
        assert "Bob Smith" in names
        assert "Charlie Brown" in names
        assert "Diana Prince" in names

    def test_query_participant_by_id(self, db_session, sample_participants):
        """Test querying participant by ID"""
        first_participant = sample_participants[0]
        
        participant = db_session.query(Participant).filter(
            Participant.id == first_participant.id
        ).first()
        
        assert participant is not None
        assert participant.id == first_participant.id
        assert participant.name == first_participant.name

    def test_query_participant_by_email(self, db_session, sample_participants):
        """Test querying participant by email"""
        participant = db_session.query(Participant).filter(
            Participant.email == "alice@example.com"
        ).first()
        
        assert participant is not None
        assert participant.email == "alice@example.com"
        assert participant.name == "Alice Johnson"

    def test_query_participants_by_role(self, db_session, sample_participants):
        """Test querying participants by role"""
        guests = db_session.query(Participant).filter(
            Participant.role == "Guest"
        ).all()
        
        assert len(guests) == 2  # Bob and Diana
        guest_names = [g.name for g in guests]
        assert "Bob Smith" in guest_names
        assert "Diana Prince" in guest_names

    def test_query_participants_by_online_status(self, db_session, sample_participants):
        """Test querying participants by online status"""
        online_participants = db_session.query(Participant).filter(
            Participant.online == True
        ).all()
        
        assert len(online_participants) == 3  # Alice, Bob, Diana
        
        offline_participants = db_session.query(Participant).filter(
            Participant.online == False
        ).all()
        
        assert len(offline_participants) == 1  # Charlie
        assert offline_participants[0].name == "Charlie Brown"

    def test_query_participants_by_mic_status(self, db_session, sample_participants):
        """Test querying participants by microphone status"""
        mic_on_participants = db_session.query(Participant).filter(
            Participant.mic_on == True
        ).all()
        
        assert len(mic_on_participants) == 3  # Alice, Charlie, Diana
        
        mic_off_participants = db_session.query(Participant).filter(
            Participant.mic_on == False
        ).all()
        
        assert len(mic_off_participants) == 1  # Bob
        assert mic_off_participants[0].name == "Bob Smith"

    def test_query_participants_by_camera_status(self, db_session, sample_participants):
        """Test querying participants by camera status"""
        camera_on_participants = db_session.query(Participant).filter(
            Participant.camera_on == True
        ).all()
        
        assert len(camera_on_participants) == 3  # Alice, Bob, Diana
        
        camera_off_participants = db_session.query(Participant).filter(
            Participant.camera_on == False
        ).all()
        
        assert len(camera_off_participants) == 1  # Charlie
        assert camera_off_participants[0].name == "Charlie Brown"

    def test_query_with_multiple_filters(self, db_session, sample_participants):
        """Test querying with multiple filters"""
        # Find online guests
        online_guests = db_session.query(Participant).filter(
            Participant.role == "Guest",
            Participant.online == True
        ).all()
        
        assert len(online_guests) == 2  # Bob and Diana
        
        # Find participants with both mic and camera on
        fully_active = db_session.query(Participant).filter(
            Participant.mic_on == True,
            Participant.camera_on == True
        ).all()
        
        assert len(fully_active) == 2  # Alice and Diana

    def test_query_with_search_like(self, db_session, sample_participants):
        """Test querying with LIKE search"""
        # Search for participants with "John" in name
        john_participants = db_session.query(Participant).filter(
            Participant.name.like("%John%")
        ).all()
        
        assert len(john_participants) == 1
        assert john_participants[0].name == "Alice Johnson"
        
        # Search for participants with "example.com" in email
        example_participants = db_session.query(Participant).filter(
            Participant.email.like("%example.com")
        ).all()
        
        assert len(example_participants) == 4  # All have example.com email

    def test_query_ordering(self, db_session, sample_participants):
        """Test querying with ordering"""
        # Order by name
        participants_by_name = db_session.query(Participant).order_by(
            Participant.name
        ).all()
        
        names = [p.name for p in participants_by_name]
        assert names == ["Alice Johnson", "Bob Smith", "Charlie Brown", "Diana Prince"]
        
        # Order by name descending
        participants_desc = db_session.query(Participant).order_by(
            Participant.name.desc()
        ).all()
        
        names_desc = [p.name for p in participants_desc]
        assert names_desc == ["Diana Prince", "Charlie Brown", "Bob Smith", "Alice Johnson"]

    def test_query_pagination(self, db_session, sample_participants):
        """Test querying with pagination"""
        # Get first 2 participants
        first_page = db_session.query(Participant).limit(2).all()
        assert len(first_page) == 2
        
        # Get next 2 participants
        second_page = db_session.query(Participant).offset(2).limit(2).all()
        assert len(second_page) == 2
        
        # Ensure no overlap
        first_page_ids = {p.id for p in first_page}
        second_page_ids = {p.id for p in second_page}
        assert first_page_ids.isdisjoint(second_page_ids)

    def test_query_count(self, db_session, sample_participants):
        """Test counting queries"""
        # Count all participants
        total_count = db_session.query(Participant).count()
        assert total_count == 4
        
        # Count online participants
        online_count = db_session.query(Participant).filter(
            Participant.online == True
        ).count()
        assert online_count == 3
        
        # Count guests
        guest_count = db_session.query(Participant).filter(
            Participant.role == "Guest"
        ).count()
        assert guest_count == 2

class TestParticipantUpdates:
    """Test updating Participant model data"""
    
    @pytest.fixture(scope="function")
    def test_db(self):
        """Create a test database for each test"""
        Base.metadata.create_all(bind=engine)
        yield
        Base.metadata.drop_all(bind=engine)

    @pytest.fixture(scope="function")
    def db_session(self, test_db):
        """Create a database session for testing"""
        session = TestingSessionLocal()
        try:
            yield session
        finally:
            session.close()

    def test_update_participant_name(self, db_session):
        """Test updating participant name"""
        participant = Participant(
            name="Old Name",
            email="test@example.com",
            role="Guest"
        )
        
        db_session.add(participant)
        db_session.commit()
        db_session.refresh(participant)
        
        # Update name
        participant.name = "New Name"
        db_session.commit()
        db_session.refresh(participant)
        
        assert participant.name == "New Name"

    def test_update_microphone_status(self, db_session):
        """Test updating microphone status"""
        participant = Participant(
            name="Test User",
            email="test@example.com",
            role="Guest",
            mic_on=False
        )
        
        db_session.add(participant)
        db_session.commit()
        db_session.refresh(participant)
        
        # Update mic status
        participant.mic_on = True
        db_session.commit()
        db_session.refresh(participant)
        
        assert participant.mic_on is True

    def test_update_camera_status(self, db_session):
        """Test updating camera status"""
        participant = Participant(
            name="Test User",
            email="test@example.com",
            role="Guest",
            camera_on=False
        )
        
        db_session.add(participant)
        db_session.commit()
        db_session.refresh(participant)
        
        # Update camera status
        participant.camera_on = True
        db_session.commit()
        db_session.refresh(participant)
        
        assert participant.camera_on is True

    def test_update_online_status(self, db_session):
        """Test updating online status"""
        participant = Participant(
            name="Test User",
            email="test@example.com",
            role="Guest",
            online=True
        )
        
        db_session.add(participant)
        db_session.commit()
        db_session.refresh(participant)
        
        # Update online status
        participant.online = False
        db_session.commit()
        db_session.refresh(participant)
        
        assert participant.online is False

    def test_update_multiple_fields(self, db_session):
        """Test updating multiple fields at once"""
        participant = Participant(
            name="Test User",
            email="test@example.com",
            role="Guest",
            mic_on=False,
            camera_on=False,
            online=True
        )
        
        db_session.add(participant)
        db_session.commit()
        db_session.refresh(participant)
        
        # Update multiple fields
        participant.mic_on = True
        participant.camera_on = True
        participant.online = False
        participant.role = "Host"
        
        db_session.commit()
        db_session.refresh(participant)
        
        assert participant.mic_on is True
        assert participant.camera_on is True
        assert participant.online is False
        assert participant.role == "Host"

class TestParticipantDeletion:
    """Test deleting Participant model data"""
    
    @pytest.fixture(scope="function")
    def test_db(self):
        """Create a test database for each test"""
        Base.metadata.create_all(bind=engine)
        yield
        Base.metadata.drop_all(bind=engine)

    @pytest.fixture(scope="function")
    def db_session(self, test_db):
        """Create a database session for testing"""
        session = TestingSessionLocal()
        try:
            yield session
        finally:
            session.close()

    def test_delete_participant(self, db_session):
        """Test deleting a participant"""
        participant = Participant(
            name="To Delete",
            email="delete@example.com",
            role="Guest"
        )
        
        db_session.add(participant)
        db_session.commit()
        db_session.refresh(participant)
        
        participant_id = participant.id
        
        # Delete participant
        db_session.delete(participant)
        db_session.commit()
        
        # Verify deletion
        deleted_participant = db_session.query(Participant).filter(
            Participant.id == participant_id
        ).first()
        
        assert deleted_participant is None

    def test_delete_multiple_participants(self, db_session):
        """Test deleting multiple participants"""
        participants = []
        for i in range(3):
            participant = Participant(
                name=f"User {i}",
                email=f"user{i}@example.com",
                role="Guest"
            )
            participants.append(participant)
            db_session.add(participant)
        
        db_session.commit()
        
        # Delete all participants
        for participant in participants:
            db_session.delete(participant)
        
        db_session.commit()
        
        # Verify all deleted
        remaining_count = db_session.query(Participant).count()
        assert remaining_count == 0

class TestDatabaseIntegrity:
    """Test database integrity and constraints"""
    
    @pytest.fixture(scope="function")
    def test_db(self):
        """Create a test database for each test"""
        Base.metadata.create_all(bind=engine)
        yield
        Base.metadata.drop_all(bind=engine)

    @pytest.fixture(scope="function")
    def db_session(self, test_db):
        """Create a database session for testing"""
        session = TestingSessionLocal()
        try:
            yield session
        finally:
            session.close()

    def test_participant_id_uniqueness(self, db_session):
        """Test that participant IDs are unique"""
        participant1 = Participant(
            name="User 1",
            email="user1@example.com",
            role="Guest"
        )
        
        participant2 = Participant(
            name="User 2",
            email="user2@example.com",
            role="Guest"
        )
        
        db_session.add(participant1)
        db_session.add(participant2)
        db_session.commit()
        db_session.refresh(participant1)
        db_session.refresh(participant2)
        
        assert participant1.id != participant2.id

    def test_participant_email_can_be_duplicate(self, db_session):
        """Test that email addresses can be duplicate (if not constrained)"""
        # Note: If email uniqueness is required, this test should be modified
        participant1 = Participant(
            name="User 1",
            email="same@example.com",
            role="Guest"
        )
        
        participant2 = Participant(
            name="User 2",
            email="same@example.com",
            role="Host"
        )
        
        db_session.add(participant1)
        db_session.add(participant2)
        db_session.commit()
        
        # Both should be created successfully
        participants = db_session.query(Participant).filter(
            Participant.email == "same@example.com"
        ).all()
        
        assert len(participants) == 2

    def test_database_rollback(self, db_session):
        """Test database transaction rollback"""
        participant = Participant(
            name="Rollback Test",
            email="rollback@example.com",
            role="Guest"
        )
        
        db_session.add(participant)
        # Don't commit
        
        # Rollback transaction
        db_session.rollback()
        
        # Verify participant was not saved
        participants = db_session.query(Participant).filter(
            Participant.email == "rollback@example.com"
        ).all()
        
        assert len(participants) == 0