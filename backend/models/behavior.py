from sqlalchemy import Column, String, Float, DateTime, ForeignKey
from datetime import datetime
import uuid
from db.postgres import Base

class BehaviorLog(Base):
    __tablename__ = "behavior_logs"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"))
    type = Column(String)       # e.g., "task", "study", "social"
    value = Column(Float)       # e.g., completion score
    context = Column(String)    # e.g., "coding", "meeting"
    timestamp = Column(DateTime, default=datetime.utcnow)
