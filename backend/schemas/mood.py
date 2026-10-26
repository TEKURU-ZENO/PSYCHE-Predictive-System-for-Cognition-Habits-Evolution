from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class LogMoodRequest(BaseModel):
    mood_type: str
    intensity: float
    note: Optional[str] = None

class MoodResponse(BaseModel):
    mood_type: str
    intensity: float
    timestamp: datetime
