from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from api.auth import get_db, get_current_user
from models.user import User
from services.meta_engine import generate_meta_profile

router = APIRouter(prefix="/api/v1/meta", tags=["meta"])

@router.get("/profile")
def get_profile(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    profile = generate_meta_profile(db, user.id)
    return profile

@router.get("/telemetry")
def get_telemetry(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    from services.health_engine import HealthEngine
    from services.self_eval_engine import get_system_effectiveness
    from services.calibration_service import CalibrationService
    from core.versioning import SystemVersionController

    health_status = HealthEngine.check_learning_health(db, user.id)
    effectiveness = get_system_effectiveness(user.id)

    agents = ["prediction", "strategy", "meta", "cognition"]
    calibrated = {agent: CalibrationService.get_calibrated_weight(user.id, agent, 0.75) for agent in agents}

    weights = {agent: data["dynamic_weight"] for agent, data in calibrated.items()}
    total = sum(weights.values()) or 1.0
    weights = {k: round(v / total, 3) for k, v in weights.items()}

    trust_tiers = {agent: data["trust_tier"] for agent, data in calibrated.items()}
    effective_accuracies = {agent: data["effective_accuracy"] for agent, data in calibrated.items()}

    return {
        "learning_health": {
            "status": health_status,
            "effectiveness": effectiveness
        },
        "weights": weights,
        "trust_tiers": trust_tiers,
        "effective_accuracies": effective_accuracies,
        "dominant_agent": max(weights, key=weights.get) if weights else "strategy",
        "version_matrix": SystemVersionController.VERSION_REGISTRY
    }
