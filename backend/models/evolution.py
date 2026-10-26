from sqlalchemy import Column, String, Float, DateTime, ForeignKey
from datetime import datetime
import uuid
from db.postgres import Base

class EvolutionSnapshot(Base):
    __tablename__ = "evolution_snapshots"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), index=True)
    week = Column(String)

    archetype = Column(String)
    stress_avg = Column(Float)
    dissonance = Column(Float)
    top_strategy = Column(String)

    created_at = Column(DateTime, default=datetime.utcnow)
