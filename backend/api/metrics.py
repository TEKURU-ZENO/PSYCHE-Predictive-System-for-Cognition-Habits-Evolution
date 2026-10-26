import time
from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session
from sqlalchemy import text
from db.postgres import SessionLocal
from core.versioning import SystemVersionController
from services.health_engine import HealthEngine
from services.reliability_service import ReliabilityService

router = APIRouter(prefix="/api/v1/metrics", tags=["Metrics & Observability"])

START_TIME = time.time()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/healthz")
def healthz(db: Session = Depends(get_db)):
    """Kubernetes/Container readiness & liveness probe."""
    db_status = "connected"
    try:
        db.execute(text("SELECT 1"))
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"
        return Response(content='{"status": "degraded", "db": "disconnected"}', status_code=503, media_type="application/json")
    
    return {
        "status": "healthy",
        "database": db_status,
        "uptime_seconds": round(time.time() - START_TIME, 2),
        "versions": SystemVersionController.get_version_matrix()
    }

@router.get("/telemetry")
def telemetry(db: Session = Depends(get_db)):
    """Comprehensive production telemetry for system dashboard & ops."""
    all_metrics = ReliabilityService.get_all_metrics(db)
    
    agent_summary = {}
    for name, m in all_metrics.items():
        agent_summary[name] = {
            "invocations": m["total_invocations"],
            "reliability": m["reliability_score"],
            "trust_tier": m["trust_tier"],
            "impact": m["contribution_impact_score"]
        }
        
    return {
        "system_status": "operational",
        "uptime_seconds": round(time.time() - START_TIME, 2),
        "version_matrix": SystemVersionController.get_version_matrix(),
        "agents": agent_summary,
        "agents_count": len(agent_summary),
        "learning_health": {
            "status": "active",
            "decay_factor": 0.98
        }
    }

@router.get("/prometheus")
def prometheus_metrics(db: Session = Depends(get_db)):
    """Standard Prometheus exposition format for metrics scraping."""
    uptime = time.time() - START_TIME
    all_metrics = ReliabilityService.get_all_metrics(db)
    
    lines = [
        "# HELP psychai_system_uptime_seconds Total runtime of the Psych-AI engine.",
        "# TYPE psychai_system_uptime_seconds gauge",
        f"psychai_system_uptime_seconds {uptime:.2f}",
        "",
        "# HELP psychai_agent_invocations_total Total times an agent was dispatched.",
        "# TYPE psychai_agent_invocations_total counter"
    ]
    
    for name, m in all_metrics.items():
        lines.append(f'psychai_agent_invocations_total{{agent="{name}"}} {m["total_invocations"]}')
        
    lines.append("")
    lines.append("# HELP psychai_agent_reliability_score Dynamic reliability score of agent.")
    lines.append("# TYPE psychai_agent_reliability_score gauge")
    for name, m in all_metrics.items():
        lines.append(f'psychai_agent_reliability_score{{agent="{name}"}} {m["reliability_score"]:.4f}')

    lines.append("")
    output = "\n".join(lines) + "\n"
    return Response(content=output, media_type="text/plain; version=0.0.4; charset=utf-8")
