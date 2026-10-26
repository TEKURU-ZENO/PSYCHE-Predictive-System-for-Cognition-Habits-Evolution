from agents.base_agent import BaseAgent, run_blocking
from db.postgres import get_new_session
from services.intervention_engine import select_nudge

class StrategyAgent(BaseAgent):
    name = "strategy"

    async def _run(self, context: dict) -> dict:
        state = context.get("state", {})
        user_id = state.get("user_id")
        emotion = state.get("emotion", "neutral")
        
        if not user_id:
             return {"output": None, "confidence": 0.0}

        db = get_new_session()
        try:
            def fetch_strategy():
                return select_nudge(db, user_id, emotion, 0.8, "general")
                
            action = await run_blocking(fetch_strategy)
            
            chosen_action = action.get("action", "rest") if action else "rest"
            base_conf = action.get("confidence", 0.4) if action else 0.4
            
            # Phase 11: Autobiographical Precedent Grounding
            memories = context.get("input", {}).get("memories", [])
            precedent_note = None
            if memories:
                effective = [m for m in memories if m.get("outcome_delta", 0) > 0]
                if effective:
                    best_match = effective[0]
                    if best_match.get("intervention_applied"):
                        chosen_action = best_match["intervention_applied"]
                        base_conf = min(0.95, base_conf + 0.2)
                        precedent_note = f"Grounding in past episode: '{best_match.get('trigger_context')}' successfully resolved by '{chosen_action}'."

            return {
                "output": chosen_action,
                "confidence": round(base_conf, 2),
                "precedent_note": precedent_note,
                "adjusted": False
            }
        finally:
            db.close()
