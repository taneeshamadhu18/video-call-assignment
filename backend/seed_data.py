from database import SessionLocal
from models import Participant

db = SessionLocal()

participants = [
    Participant(
        name="Alice Johnson",
        email="alice@test.com",
        role="Host",
        online=True,
        mic_on=True,
        camera_on=True,
        about_me="Frontend engineer with 4 years of experience",
        resume_url="https://example.com/alice.pdf"
    ),
    Participant(
        name="Bob Smith",
        email="bob@test.com",
        role="Guest",
        online=False,
        mic_on=False,
        camera_on=True,
        about_me="Backend developer specialising in APIs",
        resume_url="https://example.com/bob.pdf"
    ),
    Participant(
        name="Carol White",
        email="carol@test.com",
        role="Guest",
        online=True,
        mic_on=True,
        camera_on=False,
        about_me="UI/UX designer passionate about accessibility",
        resume_url=None
    ),
    Participant(
        name="David Brown",
        email="david@test.com",
        role="Guest",
        online=False,
        mic_on=False,
        camera_on=False,
        about_me="Computer science student and intern",
        resume_url=None
    ),
    Participant(
        name="Eva Green",
        email="eva@test.com",
        role="Guest",
        online=True,
        mic_on=True,
        camera_on=True,
        about_me="Product manager with a focus on user experience",
        resume_url="https://example.com/eva.pdf"
    ),
    Participant(
        name="Frank Miller",
        email="frank@test.com",
        role="Guest",
        online=True,
        mic_on=False,
        camera_on=True,
        about_me="DevOps engineer working on cloud infrastructure",
        resume_url=None
    ),
    Participant(
        name="Grace Lee",
        email="grace@test.com",
        role="Guest",
        online=False,
        mic_on=True,
        camera_on=False,
        about_me="Data analyst interested in ML and analytics",
        resume_url="https://example.com/grace.pdf"
    ),
    Participant(
        name="Henry Adams",
        email="henry@test.com",
        role="Guest",
        online=True,
        mic_on=True,
        camera_on=True,
        about_me="Full-stack developer and open-source contributor",
        resume_url="https://example.com/henry.pdf"
    ),
]

db.add_all(participants)
db.commit()
db.close()

print("✅ 8 dummy participants inserted successfully")
