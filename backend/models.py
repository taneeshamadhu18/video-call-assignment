from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class Participant(Base):
    __tablename__ = "participants"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String, index=True)
    email = Column(String)
    role = Column(String)
    avatar = Column(String, nullable=True)

    online = Column(Boolean, default=False)
    mic_on = Column(Boolean, default=True)
    camera_on = Column(Boolean, default=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)
