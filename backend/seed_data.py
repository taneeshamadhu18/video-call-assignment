from database import SessionLocal
from models import Participant

db = SessionLocal()

participants = [
    Participant(
        name="Alice",
        email="alice@test.com",
        role="Host",
        online=True,
        mic_on=True,
        camera_on=True
    ),
    Participant(
        name="Bob",
        email="bob@test.com",
        role="Guest",
        online=False,
        mic_on=False,
        camera_on=True
    )
]

db.add_all(participants)
db.commit()
db.close()

print("Dummy data inserted")
