from collections import defaultdict, deque
import time
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from core.config import settings
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

app = FastAPI(title="Psych-AI Cognitive Twin Platform", version="2.0.0")

# Only auto-create schema in non-production environments; production uses Alembic migrations
if settings.ENVIRONMENT != "production":
    try:
        Base.metadata.create_all(bind=engine)
        print("PostgreSQL tables verified and synced.")
    except Exception as e:
        print(f"Warning: Database connection deferred during initialization ({e}). Retrying on first request.")

# Sliding-window in-process rate limiter (with health probe exemptions)
_RATE_BUCKETS: dict[str, deque] = defaultdict(deque)
_EXEMPT_PATHS = {"/", "/health", "/api/v1/metrics/healthz"}


@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    if request.url.path in _EXEMPT_PATHS:
        return await call_next(request)

    client_ip = request.client.host if request.client else "unknown"
    now = time.monotonic()
    window = 60.0
    limit = max(10, settings.RATE_LIMIT_PER_MINUTE)
    bucket = _RATE_BUCKETS[client_ip]

    while bucket and (now - bucket[0]) > window:
        bucket.popleft()

    if len(bucket) >= limit:
        return JSONResponse(
            status_code=429,
            content={"detail": "Rate limit exceeded. Please wait before sending additional requests."},
            headers={"Retry-After": "60"}
        )

    bucket.append(now)
    response = await call_next(request)
    response.headers["X-RateLimit-Limit"] = str(limit)
    response.headers["X-RateLimit-Remaining"] = str(max(0, limit - len(bucket)))
    return response


app.include_router(auth_router)
app.include_router(mood_router)
app.include_router(state_router)
app.include_router(behavior_router)
from api.cognition import router as _cognition_router  # noqa: E402
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

allowed_origins = [o.strip() for o in settings.CORS_ORIGINS.split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "X-Timezone-Offset"],
)


@app.get("/")
def root():
    return {"msg": "Psych-AI running"}


@app.get("/health")
def health():
    return {"status": "ok"}
