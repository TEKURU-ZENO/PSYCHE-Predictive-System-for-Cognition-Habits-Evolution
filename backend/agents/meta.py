from agents.base_agent import BaseAgent, run_blocking
from db.postgres import get_new_session
from services.meta_engine import generate_meta_profile


class MetaAgent(BaseAgent):
    name = "meta"

    async def _run(self, context: dict) -> dict:
        user_id = context.get("state", {}).get("user_id")
        if not user_id:
            return {"output": None, "confidence": 0.0}

        uid_str = str(user_id)

        def build_meta():
            db = get_new_session()
            try:
                return generate_meta_profile(db, uid_str)
            finally:
                db.close()

        profile = await run_blocking(build_meta)
        return {
            "output": profile,
            "confidence": 0.9
        }
