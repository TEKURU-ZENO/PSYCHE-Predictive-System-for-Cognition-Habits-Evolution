from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from db.postgres import Base, engine
from api.auth import router as auth_router
from api.mood import router as mood_router
from api.state import router as state_router
from api.behavior import router as behavior_router
from api.cognition import router as cognition_router
from api.prediction import router as prediction_router
from api.intervention import router as intervention_router
from api.meta import router as meta_router
from api.evolution import router as evolution_router
from api.goals import router as goals_router
from api.agent import router as agent_router
from api.memory import router as memory_router
from api.proactive import router as proactive_router, cf_router
from api.post_mortem import router as post_mortem_router
from api.replay import router as replay_router
from api.vault import router as vault_router
from api.metrics import router as metrics_router
from models.event import EventLog
from models.user_state import UserState
from models.behavior import BehaviorLog
from models.pattern import Trigger
from models.personalization import UserPolicy, PendingReward
from models.evolution import EvolutionSnapshot
from models.goals import Goal
from models.system_state import SystemState
from models.agent_metrics import AgentMetrics
from models.memory import EpisodicMemory, AssociativeLink, SchemaConsolidation
from models.proactive import ProactiveAlert, CounterfactualBranch
from models.post_mortem import PostMortemReport, RedTeamAuditLog

app = FastAPI()

# Make sure tables are created (gracefully handled if DB container is spinning up)
try:
    Base.metadata.create_all(bind=engine)
    print("PostgreSQL tables verified and synced.")
except Exception as e:
    print(f"Warning: Database connection deferred during initialization ({e}). Retrying on first request.")

app.include_router(auth_router)
app.include_router(mood_router)
app.include_router(state_router)
app.include_router(behavior_router)
app.include_router(cognition_router)
app.include_router(prediction_router)
app.include_router(intervention_router)
app.include_router(meta_router)
app.include_router(evolution_router)
app.include_router(goals_router)
app.include_router(agent_router)
app.include_router(memory_router)
app.include_router(proactive_router)
app.include_router(cf_router)
app.include_router(post_mortem_router)
app.include_router(replay_router)
app.include_router(vault_router)
app.include_router(metrics_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"msg": "Psych-AI running"}

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/metrics")
def root_metrics():
    from api.metrics import prometheus_metrics
    from db.postgres import SessionLocal
    db = SessionLocal()
    try:
        return prometheus_metrics(db)
    finally:
        db.close()
