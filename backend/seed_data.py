from database import SessionLocal
from models import Participant
from datetime import datetime, timedelta
import random

db = SessionLocal()

# Create realistic timestamps
base_time = datetime.utcnow() - timedelta(days=30)  # 30 days ago

participants = [
    Participant(
        name="Alice Johnson",
        email="alice@test.com",
        role="Host",
        online=True,
        mic_on=False,
        camera_on=False,
        about_me="Frontend engineer with 4 years of experience",
        resume_url="https://example.com/alice.pdf",
        created_at=base_time + timedelta(days=1),
        updated_at=datetime.utcnow() - timedelta(minutes=5)
    ),
    Participant(
        name="Bob Smith",
        email="bob@test.com",
        role="Guest",
        online=False,
        mic_on=False,
        camera_on=False,
        about_me="Backend developer specialising in APIs",
        resume_url="https://example.com/bob.pdf",
        created_at=base_time + timedelta(days=2),
        updated_at=datetime.utcnow() - timedelta(hours=2)
    ),
    Participant(
        name="Carol White",
        email="carol@test.com",
        role="Guest",
        online=True,
        mic_on=False,
        camera_on=False,
        about_me="UI/UX designer passionate about accessibility",
        resume_url=None,
        created_at=base_time + timedelta(days=3),
        updated_at=datetime.utcnow() - timedelta(minutes=30)
    ),
    Participant(
        name="David Brown",
        email="david@test.com",
        role="Guest",
        online=False,
        mic_on=False,
        camera_on=False,
        about_me="Computer science student and intern",
        resume_url=None,
        created_at=base_time + timedelta(days=5),
        updated_at=datetime.utcnow() - timedelta(days=1)
    ),
    Participant(
        name="Eva Green",
        email="eva@test.com",
        role="Guest",
        online=True,
        mic_on=False,
        camera_on=False,
        about_me="Product manager with a focus on user experience",
        resume_url="https://example.com/eva.pdf",
        created_at=base_time + timedelta(days=7),
        updated_at=datetime.utcnow() - timedelta(minutes=15)
    ),
    Participant(
        name="Frank Miller",
        email="frank@test.com",
        role="Guest",
        online=True,
        mic_on=False,
        camera_on=False,
        about_me="DevOps engineer working on cloud infrastructure",
        resume_url=None,
        created_at=base_time + timedelta(days=10),
        updated_at=datetime.utcnow() - timedelta(hours=6)
    ),
    Participant(
        name="Grace Lee",
        email="grace@test.com",
        role="Guest",
        online=False,
        mic_on=False,
        camera_on=False,
        about_me="Data analyst interested in ML and analytics",
        resume_url="https://example.com/grace.pdf",
        created_at=base_time + timedelta(days=12),
        updated_at=datetime.utcnow() - timedelta(hours=12)
    ),
    Participant(
        name="Henry Adams",
        email="henry@test.com",
        role="Guest",
        online=True,
        mic_on=False,
        camera_on=False,
        about_me="Full-stack developer and open-source contributor",
        resume_url="https://example.com/henry.pdf",
        created_at=base_time + timedelta(days=15),
        updated_at=datetime.utcnow() - timedelta(minutes=45)
    ),
]

db.add_all(participants)
db.commit()
db.close()

print("✅ 8 dummy participants inserted successfully")
