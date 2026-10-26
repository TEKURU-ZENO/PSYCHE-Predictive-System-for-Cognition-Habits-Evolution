from pydantic import BaseModel

class LogBehaviorRequest(BaseModel):
    type: str
    value: float
    context: str
