from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from datetime import datetime
import uuid
from db.postgres import Base

class EventType:
    MOOD_LOGGED = "mood_logged"
    NUDGE_SHOWN = "nudge_shown"
    NUDGE_ACCEPTED = "nudge_accepted"

class EventLog(Base):
    __tablename__ = "event_logs"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), index=True)
    session_id = Column(String, index=True, nullable=True) # Temporal bucket connecting events
    type = Column(String, index=True)
    metadata_col = Column(String) # stringified JSON
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
