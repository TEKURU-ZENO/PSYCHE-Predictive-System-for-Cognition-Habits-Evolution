from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session
import json
from api.auth import get_db, get_current_user
from models.user import User
from services.privacy_vault import PrivacyVaultService

router = APIRouter(prefix="/api/v1/vault", tags=["vault"])

@router.get("/export")
def export_vault(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    data = PrivacyVaultService.export_full_vault(db, user.id)
    json_bytes = json.dumps(data, indent=2).encode('utf-8')
    return Response(
        content=json_bytes,
        media_type="application/json",
        headers={
            "Content-Disposition": f"attachment; filename=psychai_cognitive_twin_vault_{user.id}.json"
        }
    )

@router.delete("/memory/{episode_id}")
def purge_memory(episode_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    success = PrivacyVaultService.prune_episode(db, user.id, episode_id)
    if not success:
        raise HTTPException(status_code=404, detail="Episodic memory record not found")
    return {"status": "purged", "episode_id": episode_id}
