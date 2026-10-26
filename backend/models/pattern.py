from sqlalchemy import Column, String, Float, ForeignKey
import uuid
from db.postgres import Base

class Trigger(Base):
    __tablename__ = "triggers"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"))
    event = Column(String)      # e.g., "coding"
    emotion = Column(String)    # e.g., "stressed"
    frequency = Column(Float)
    confidence = Column(Float)
    stability = Column(Float)
