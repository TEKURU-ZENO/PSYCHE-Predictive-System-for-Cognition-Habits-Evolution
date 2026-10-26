from sqlalchemy import Column, String, Float, DateTime, ForeignKey
from datetime import datetime
import uuid
from db.postgres import Base

class UserState(Base):
    __tablename__ = "user_states"

    user_id = Column(String, ForeignKey("users.id"), primary_key=True)
    current_emotion = Column(String)
    intensity = Column(Float)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
