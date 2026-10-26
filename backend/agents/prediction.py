from agents.base_agent import BaseAgent, run_blocking
from db.postgres import get_new_session
from models.mood import MoodLog
from models.pattern import Trigger
from services.prediction_engine import project_long_term_risk

class PredictionAgent(BaseAgent):
    name = "prediction"

    async def _run(self, context: dict) -> dict:
        user_id = context.get("state", {}).get("user_id")
        if not user_id:
            return {"output": None, "confidence": 0.0}
            
        db = get_new_session()
        try:
            def fetch_risk():
                moods = db.query(MoodLog).filter(MoodLog.user_id == user_id).order_by(MoodLog.timestamp.asc()).limit(10).all()
                triggers = db.query(Trigger).filter(Trigger.user_id == user_id).all()
                return project_long_term_risk(moods, triggers, [])
                
            result = await run_blocking(fetch_risk)
            
            if not result:
                return {"output": {"risk": "unknown"}, "confidence": 0.1}
                
            return {
                "output": result,
                "confidence": result.get("confidence", 0.5)
            }
        finally:
            db.close()
