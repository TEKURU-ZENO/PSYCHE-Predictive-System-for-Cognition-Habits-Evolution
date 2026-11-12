from fastapi import APIRouter
from fastapi import Depends
from schemas.cognition import TextInput
from services.cognition_engine import cognition_engine
from api.auth import get_current_user
from models.user import User

router = APIRouter(prefix="/api/v1/cognition", tags=["cognition"])


@router.post("/analyze")
def analyze(data: TextInput, user: User = Depends(get_current_user)):
    result = cognition_engine.analyze(data.text)
    return result
