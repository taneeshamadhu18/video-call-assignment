from sqlalchemy import Column, Integer, String, Boolean, Text
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Participant(Base):
    __tablename__ = "participants"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    role = Column(String)
    email = Column(String)

    about_me = Column(Text, nullable=True)
    resume_url = Column(String, nullable=True)

    mic_on = Column(Boolean, default=False)
    camera_on = Column(Boolean, default=False)
    online = Column(Boolean, default=False)
