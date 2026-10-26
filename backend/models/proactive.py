from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Boolean, ForeignKey
from datetime import datetime
from db.postgres import Base

class ProactiveAlert(Base):
    __tablename__ = "proactive_alerts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    alert_type = Column(String(50), nullable=False, index=True)  # circadian_friction, burnout_velocity, fatigue_trap, preemptive_nudge
    severity = Column(String(20), default="moderate")           # low, moderate, critical
    title = Column(String(150), nullable=False)
    message = Column(Text, nullable=False)
    preemptive_action = Column(String(100), nullable=True)
    circadian_phase = Column(String(50), nullable=True)         # morning_focus, midday_surge, afternoon_dip, evening_wind_down, late_night_vulnerability
    is_acknowledged = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

class CounterfactualBranch(Base):
    __tablename__ = "counterfactual_branches"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    scenario = Column(Text, nullable=False)
    decision_hash = Column(String(64), nullable=True, index=True)
    branch_name = Column(String(100), nullable=False)           # e.g., "Push Through", "Take Break", "Cognitive Reframe"
    projected_stress_48h = Column(Float, default=0.5)           # 0.0 to 1.0
    projected_burnout_risk = Column(Float, default=0.3)         # 0.0 to 1.0
    projected_dissonance = Column(Float, default=0.4)           # 0.0 to 1.0
    cognitive_energy_delta = Column(Float, default=0.0)         # -1.0 to +1.0
    expected_q_value = Column(Float, default=0.5)
    recommendation_rank = Column(Integer, default=1)
    tradeoff_analysis = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
