from agents.base_agent import BaseAgent

class PerceptionAgent(BaseAgent):
    name = "perception"

    async def _run(self, context: dict) -> dict:
        input_data = context.get("input", {})
        # Extracts raw state variables mapped from UI before deep DB pulls
        state = {
            "scenario": input_data.get("scenario", ""),
            "user_id": input_data.get("user_id", ""),
            "emotion": input_data.get("emotion", "neutral")
        }
        return {
            "output": state,
            "confidence": 1.0
        }
