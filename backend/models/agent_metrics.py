from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey
from datetime import datetime
from db.postgres import Base
import enum
from sqlalchemy import Enum as SQLEnum

class TrustTier(str, enum.Enum):
    TRUSTED = "Trusted"
    STABLE = "Stable"
    UNCERTAIN = "Uncertain"
    DEGRADED = "Degraded"

class AgentMetrics(Base):
    __tablename__ = "agent_metrics"

    user_id = Column(String, ForeignKey("users.id"), primary_key=True)
    agent_id = Column(String, primary_key=True)

    total_invocations = Column(Integer, default=0)
    timeouts = Column(Integer, default=0)
    overrides = Column(Integer, default=0)
    successful_contributions = Column(Integer, default=0)
    
    historical_accuracy = Column(Float, default=1.0)
    contribution_impact_score = Column(Float, default=1.0)
    
    last_success_timestamp = Column(DateTime, default=datetime.utcnow)
    
    trust_tier = Column(SQLEnum(TrustTier), default=TrustTier.STABLE)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
