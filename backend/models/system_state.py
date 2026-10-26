from sqlalchemy import Column, String, Float, DateTime, ForeignKey, Boolean
from datetime import datetime
from db.postgres import Base

class SystemState(Base):
    __tablename__ = "system_state"

    user_id = Column(String, ForeignKey("users.id"), primary_key=True)

    alpha = Column(Float, default=0.3)
    epsilon = Column(Float, default=0.2)
    
    # Phase 10.2: Learning Health & Recovery
    epsilon_history = Column(String, default="[]") # JSON list
    recovery_mode_active = Column(Boolean, default=False)
    policy_entropy = Column(Float, default=0.0)

    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
