from agents.base_agent import BaseAgent, run_blocking
from db.postgres import get_new_session
from models.mood import MoodLog
from models.pattern import Trigger
from services.prediction_engine import project_long_term_risk
from services.deep_forecasting_engine import deep_forecasting_engine


class PredictionAgent(BaseAgent):
    name = "prediction"

    async def _run(self, context: dict) -> dict:
        user_id = context.get("state", {}).get("user_id")
        if not user_id:
            return {"output": None, "confidence": 0.0}

        uid_str = str(user_id)

        def fetch_risk():
            # Create thread-local session inside worker thread for thread safety
            db = get_new_session()
            try:
                moods = db.query(MoodLog).filter(MoodLog.user_id == uid_str).order_by(MoodLog.timestamp.asc()).limit(15).all()
                triggers = db.query(Trigger).filter(Trigger.user_id == uid_str).all()
                classical = project_long_term_risk(moods, triggers, [])

                deep = {}
                try:
                    deep = deep_forecasting_engine.forecast_trajectory(moods, horizon_steps=2)
                except Exception:
                    pass

                return classical, deep
            finally:
                db.close()

        result, deep_result = await run_blocking(fetch_risk)

        if not result:
            return {"output": {"risk": "unknown"}, "confidence": 0.1}

        output = {**result}
        if deep_result:
            output["deep_forecast"] = {
                "burnout_hazard_rate": deep_result.get("burnout_hazard_rate"),
                "burnout_hazard_level": deep_result.get("burnout_hazard_level"),
                "dominant_forecast": deep_result.get("dominant_forecast"),
                "architecture": deep_result.get("architecture"),
            }

        return {
            "output": output,
            "confidence": result.get("confidence", 0.5)
        }
