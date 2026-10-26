from sqlalchemy import Column, String, Float, DateTime, ForeignKey
from datetime import datetime
import uuid
from db.postgres import Base
from enum import Enum

class MoodType(str, Enum):
    stressed = "stressed"
    calm = "calm"
    motivated = "motivated"
    fatigued = "fatigued"

class MoodLog(Base):
    __tablename__ = "mood_logs"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"))
    mood_type = Column(String)
    intensity = Column(Float)
    timestamp = Column(DateTime, default=datetime.utcnow)
