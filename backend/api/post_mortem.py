from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from api.auth import get_db, get_current_user
from models.user import User
from models.post_mortem import PostMortemReport, RedTeamAuditLog

router = APIRouter(prefix="/api/v1/post_mortem", tags=["post_mortem"])

@router.get("/reports")
def list_post_mortem_reports(limit: int = 10, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    reports = db.query(PostMortemReport).filter_by(user_id=user.id).order_by(PostMortemReport.created_at.desc()).limit(limit).all()
    return [
        {
            "id": r.id,
            "decision_hash": r.decision_hash,
            "failed_action": r.failed_action,
            "responsible_agent": r.responsible_agent,
            "root_cause": r.root_cause,
            "penalty_applied": r.penalty_applied,
            "corrective_adaptation": r.corrective_adaptation,
            "created_at": r.created_at.isoformat() if r.created_at else None
        }
        for r in reports
    ]

@router.get("/red_team_audits")
def list_red_team_audits(limit: int = 10, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    audits = db.query(RedTeamAuditLog).filter_by(user_id=user.id).order_by(RedTeamAuditLog.created_at.desc()).limit(limit).all()
    return [
        {
            "id": a.id,
            "decision_hash": a.decision_hash,
            "critique_score": a.critique_score,
            "veto_triggered": a.veto_triggered,
            "vulnerabilities": a.vulnerabilities_detected,
            "counter_critique": a.counter_critique,
            "suggested_amendment": a.suggested_amendment,
            "created_at": a.created_at.isoformat() if a.created_at else None
        }
        for a in audits
    ]
