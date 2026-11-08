from agents.base_agent import BaseAgent, run_blocking
from db.postgres import get_new_session
from services.meta_engine import generate_meta_profile

class MetaAgent(BaseAgent):
    name = "meta"

    async def _run(self, context: dict) -> dict:
        user_id = context.get("state", {}).get("user_id")
        if not user_id:
             return {"output": None, "confidence": 0.0}

        db = context.get("db")
        should_close = False
        if db is None:
            db = get_new_session()
            should_close = True

        try:
            def build_meta():
                return generate_meta_profile(db, user_id)
                
            profile = await run_blocking(build_meta)
            return {
                "output": profile,
                "confidence": 0.9 
            }
        finally:
            if should_close:
                db.close()
