from sqlalchemy import Column, String, Float, Integer, Boolean, DateTime, ForeignKey
from datetime import datetime
import uuid
from db.postgres import Base

class UserPolicy(Base):
    __tablename__ = "user_policies"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), index=True)
    state = Column(String)    # e.g., coding_stressed_high
    action = Column(String)   # e.g., take_break
    q_score = Column(Float, default=0.0)
    stable_q_score = Column(Float, default=0.0) # Phase 10.2 Rollback baseline
    visits = Column(Integer, default=0)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class PendingReward(Base):
    __tablename__ = "pending_rewards"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), index=True)
    state = Column(String)
    action = Column(String)
    intensity_before = Column(Float)
    timestamp = Column(DateTime, default=datetime.utcnow)
    resolved = Column(Boolean, default=False)
