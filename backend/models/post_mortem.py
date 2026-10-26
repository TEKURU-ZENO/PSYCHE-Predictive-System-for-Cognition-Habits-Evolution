from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Boolean, ForeignKey
from datetime import datetime
from db.postgres import Base

class PostMortemReport(Base):
    __tablename__ = "post_mortem_reports"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    decision_hash = Column(String(64), nullable=True, index=True)
    failed_action = Column(String(100), nullable=False)
    responsible_agent = Column(String(50), nullable=False)       # strategy, prediction, cognition, meta
    root_cause = Column(String(100), nullable=False)             # e.g., underestimated_burnout, aggressive_intervention
    penalty_applied = Column(Float, default=0.15)
    corrective_adaptation = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

class RedTeamAuditLog(Base):
    __tablename__ = "red_team_audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    decision_hash = Column(String(64), nullable=True, index=True)
    critique_score = Column(Float, default=0.0)                  # 0.0 (safe) to 1.0 (critically vulnerable)
    vulnerabilities_detected = Column(Text, nullable=True)       # Serialized JSON list
    veto_triggered = Column(Boolean, default=False)
    counter_critique = Column(Text, nullable=True)
    suggested_amendment = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
