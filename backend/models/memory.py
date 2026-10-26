from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey
from datetime import datetime
from db.postgres import Base

class EpisodicMemory(Base):
    __tablename__ = "episodic_memories"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    episode_type = Column(String(50), nullable=False, index=True)  # breakthrough, friction_episode, decision_outcome, reframe_success
    scenario_text = Column(Text, nullable=False)
    trigger_context = Column(String(255), nullable=True)
    cognitive_distortion = Column(String(100), nullable=True)
    emotional_valence = Column(Float, default=0.0)  # -1.0 (very negative) to +1.0 (very positive)
    intensity = Column(Float, default=0.5)           # 0.0 to 1.0
    intervention_applied = Column(String(100), nullable=True)
    outcome_delta = Column(Float, default=0.0)      # Improvement rating (-1.0 to +1.0)
    key_learnings = Column(Text, nullable=True)
    embedding_json = Column(Text, nullable=True)     # Serialized vector representation
    importance_score = Column(Float, default=0.5)   # Salience / memory retention priority
    access_count = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    last_accessed_at = Column(DateTime, default=datetime.utcnow)

class AssociativeLink(Base):
    __tablename__ = "associative_links"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    source_node = Column(String(150), nullable=False, index=True)  # e.g., trigger:tight_deadline
    target_node = Column(String(150), nullable=False, index=True)  # e.g., distortion:catastrophizing
    relation_type = Column(String(50), nullable=False)            # triggers, mitigated_by, escalates_to
    weight = Column(Float, default=0.5)                           # Strength of association
    occurrences = Column(Integer, default=1)
    updated_at = Column(DateTime, default=datetime.utcnow)

class SchemaConsolidation(Base):
    __tablename__ = "schema_consolidations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    theme = Column(String(100), nullable=False)                   # e.g., "Imposter Dissonance", "Work Burnout Loop"
    consolidated_insight = Column(Text, nullable=False)
    evidence_count = Column(Integer, default=1)
    confidence = Column(Float, default=0.8)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)
