from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import logging
from datetime import datetime
from sqlalchemy import func

from models import Participant
from database import SessionLocal

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


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
        "http://localhost:5177",
        "http://127.0.0.1:5177",
        "http://localhost:5178",
        "http://127.0.0.1:5178",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
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
    logger.info(f"Fetching participants with search='{search}', limit={limit}, offset={offset}")
    query = db.query(Participant)

    if search:
        query = query.filter(Participant.name.ilike(f"%{search}%"))

    return query.order_by(Participant.id).offset(offset).limit(limit).all()


@app.get("/participants/count")
def get_participants_count(
    search: str = "",
    db: Session = Depends(get_db),
):
    """Get total count of participants (optionally filtered by search)"""
    logger.info(f"Getting participant count with search='{search}'")
    query = db.query(func.count(Participant.id))
    
    if search:
        query = query.filter(Participant.name.ilike(f"%{search}%"))
    
    total = query.scalar()
    return {"total": total}


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
    logger.info(f"Updating media for participant {participant_id}: mic={payload.mic_on}, camera={payload.camera_on}")
    participant = db.query(Participant).filter(
        Participant.id == participant_id
    ).first()

    if not participant:
        logger.warning(f"Participant {participant_id} not found")
        raise HTTPException(status_code=404, detail="Participant not found")

    participant.mic_on = payload.mic_on
    participant.camera_on = payload.camera_on
    participant.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(participant)

    logger.info(f"Successfully updated media for participant {participant_id}")
    return participant
@app.patch("/participants/{participant_id}/microphone")
def update_microphone(
    participant_id: int,
    payload: MicrophoneUpdate,
    db: Session = Depends(get_db),
):
    logger.info(f"Updating microphone for participant {participant_id}: {payload.mic_on}")
    participant = db.query(Participant).filter(
        Participant.id == participant_id
    ).first()

    if not participant:
        logger.warning(f"Participant {participant_id} not found")
        raise HTTPException(status_code=404, detail="Participant not found")

    participant.mic_on = payload.mic_on
    participant.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(participant)

    logger.info(f"Successfully updated microphone for participant {participant_id}")
    return participant

@app.patch("/participants/{participant_id}/camera")
def update_camera(
    participant_id: int,
    payload: CameraUpdate,
    db: Session = Depends(get_db),
):
    logger.info(f"Updating camera for participant {participant_id}: {payload.camera_on}")
    participant = db.query(Participant).filter(
        Participant.id == participant_id
    ).first()

    if not participant:
        logger.warning(f"Participant {participant_id} not found")
        raise HTTPException(status_code=404, detail="Participant not found")

    participant.camera_on = payload.camera_on
    participant.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(participant)

    logger.info(f"Successfully updated camera for participant {participant_id}")
    return participant

@app.patch("/participants/{participant_id}/status")
def update_status(
    participant_id: int,
    payload: StatusUpdate,
    db: Session = Depends(get_db),
):
    logger.info(f"Updating status for participant {participant_id}: online={payload.online}")
    participant = db.query(Participant).filter(
        Participant.id == participant_id
    ).first()

    if not participant:
        logger.warning(f"Participant {participant_id} not found")
        raise HTTPException(status_code=404, detail="Participant not found")

    participant.online = payload.online
    participant.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(participant)

    logger.info(f"Successfully updated status for participant {participant_id}")
    return participant


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)

