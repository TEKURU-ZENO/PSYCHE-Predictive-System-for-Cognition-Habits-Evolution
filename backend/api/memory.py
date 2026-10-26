from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List, Dict, Any

from api.auth import get_db, get_current_user
from models.user import User
from models.memory import EpisodicMemory, SchemaConsolidation
from services.memory_engine import CognitiveMemoryEngine

router = APIRouter(prefix="/api/v1/memory", tags=["memory"])

class EpisodeCreateInput(BaseModel):
    scenario_text: str
    episode_type: str = "decision_outcome"
    trigger_context: Optional[str] = None
    cognitive_distortion: Optional[str] = None
    emotional_valence: float = 0.0
    intensity: float = 0.5
    intervention_applied: Optional[str] = None
    outcome_delta: float = 0.0
    key_learnings: Optional[str] = None

class RetrospectiveInput(BaseModel):
    question: str

@router.get("/episodes")
def list_episodes(limit: int = 20, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    episodes = db.query(EpisodicMemory).filter_by(user_id=user.id).order_by(EpisodicMemory.created_at.desc()).limit(limit).all()
    return [
        {
            "id": ep.id,
            "episode_type": ep.episode_type,
            "scenario": ep.scenario_text,
            "trigger_context": ep.trigger_context,
            "cognitive_distortion": ep.cognitive_distortion,
            "emotional_valence": ep.emotional_valence,
            "intensity": ep.intensity,
            "intervention_applied": ep.intervention_applied,
            "outcome_delta": ep.outcome_delta,
            "key_learnings": ep.key_learnings,
            "importance_score": ep.importance_score,
            "access_count": ep.access_count,
            "created_at": ep.created_at.isoformat() if ep.created_at else None
        }
        for ep in episodes
    ]

@router.post("/episode")
def create_episode(data: EpisodeCreateInput, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    ep = CognitiveMemoryEngine.store_episode(
        db=db,
        user_id=user.id,
        scenario_text=data.scenario_text,
        episode_type=data.episode_type,
        trigger_context=data.trigger_context,
        cognitive_distortion=data.cognitive_distortion,
        emotional_valence=data.emotional_valence,
        intensity=data.intensity,
        intervention_applied=data.intervention_applied,
        outcome_delta=data.outcome_delta,
        key_learnings=data.key_learnings
    )
    return {"status": "stored", "episode_id": ep.id, "importance_score": ep.importance_score}

@router.get("/graph")
def get_graph(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return CognitiveMemoryEngine.get_associative_graph(db, user.id)

@router.get("/schemas")
def get_schemas(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    schemas = db.query(SchemaConsolidation).filter_by(user_id=user.id).order_by(SchemaConsolidation.updated_at.desc()).all()
    if not schemas:
        # Trigger lazy consolidation to generate baseline schema
        CognitiveMemoryEngine.consolidate_memories(db, user.id)
        schemas = db.query(SchemaConsolidation).filter_by(user_id=user.id).order_by(SchemaConsolidation.updated_at.desc()).all()
    return [
        {
            "id": s.id,
            "theme": s.theme,
            "consolidated_insight": s.consolidated_insight,
            "evidence_count": s.evidence_count,
            "confidence": s.confidence,
            "updated_at": s.updated_at.isoformat() if s.updated_at else None
        }
        for s in schemas
    ]

@router.post("/retrospective")
def query_retrospective(data: RetrospectiveInput, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return CognitiveMemoryEngine.retrospective_query(db, user.id, data.question)

@router.post("/consolidate")
def trigger_consolidation(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    consolidated = CognitiveMemoryEngine.consolidate_memories(db, user.id)
    return {"status": "consolidated", "schemas_updated": len(consolidated), "schemas": consolidated}
