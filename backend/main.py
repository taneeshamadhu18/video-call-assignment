from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from models import Participant
from database import SessionLocal


class MediaUpdate(BaseModel):
    mic_on: bool
    camera_on: bool

class MicrophoneUpdate(BaseModel):
    mic_on: bool

class CameraUpdate(BaseModel):
    camera_on: bool

class StatusUpdate(BaseModel):
    online: bool

app = FastAPI()
API_PREFIX = "/api"
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5174",
        "http://localhost:5175",
        "http://127.0.0.1:5175",
        "http://localhost:5176",
        "http://127.0.0.1:5176",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {"status": "Backend running"}


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/participants")
def get_participants(
    search: str = "",
    limit: int = 6,
    offset: int = 0,
    db: Session = Depends(get_db),
):
    query = db.query(Participant)

    if search:
        query = query.filter(Participant.name.ilike(f"%{search}%"))

    return query.order_by(Participant.id).offset(offset).limit(limit).all()


@app.get("/participants/{participant_id}")
def get_participant(
    participant_id: int,
    db: Session = Depends(get_db)
):
    participant = db.query(Participant).filter(
        Participant.id == participant_id
    ).first()

    if not participant:
        raise HTTPException(status_code=404, detail="Participant not found")

    return participant


@app.patch("/participants/{participant_id}/media")
def update_media(
    participant_id: int,
    payload: MediaUpdate,
    db: Session = Depends(get_db)
):
    participant = db.query(Participant).filter(
        Participant.id == participant_id
    ).first()

    if not participant:
        raise HTTPException(status_code=404, detail="Participant not found")

    participant.mic_on = payload.mic_on
    participant.camera_on = payload.camera_on

    db.commit()
    db.refresh(participant)

    return participant
@app.patch("/participants/{participant_id}/microphone")
def update_microphone(
    participant_id: int,
    payload: MicrophoneUpdate,
    db: Session = Depends(get_db),
):
    participant = db.query(Participant).filter(
        Participant.id == participant_id
    ).first()

    if not participant:
        raise HTTPException(status_code=404, detail="Participant not found")

    participant.mic_on = payload.mic_on
    db.commit()
    db.refresh(participant)

    return participant

@app.patch("/participants/{participant_id}/camera")
def update_camera(
    participant_id: int,
    payload: CameraUpdate,
    db: Session = Depends(get_db),
):
    participant = db.query(Participant).filter(
        Participant.id == participant_id
    ).first()

    if not participant:
        raise HTTPException(status_code=404, detail="Participant not found")

    participant.camera_on = payload.camera_on
    db.commit()
    db.refresh(participant)

    return participant

@app.patch("/participants/{participant_id}/status")
def update_status(
    participant_id: int,
    payload: StatusUpdate,
    db: Session = Depends(get_db),
):
    participant = db.query(Participant).filter(
        Participant.id == participant_id
    ).first()

    if not participant:
        raise HTTPException(status_code=404, detail="Participant not found")

    participant.online = payload.online
    db.commit()
    db.refresh(participant)

    return participant

