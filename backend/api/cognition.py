from fastapi import APIRouter
from schemas.cognition import TextInput
from services.cognition_engine import cognition_engine

router = APIRouter(prefix="/api/v1/cognition", tags=["cognition"])

@router.post("/analyze")
def analyze(data: TextInput):
    result = cognition_engine.analyze(data.text)
    return result
