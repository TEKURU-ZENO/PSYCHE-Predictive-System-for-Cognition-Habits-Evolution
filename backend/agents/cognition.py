from agents.base_agent import BaseAgent, run_blocking
from services.cognition_engine import cognition_engine

class CognitionAgent(BaseAgent):
    name = "cognition"

    async def _run(self, context: dict) -> dict:
        state = context.get("state", {})
        text = state.get("scenario", "")
        
        result = await run_blocking(cognition_engine.analyze, text)
        biases = result.get("biases", [])
        
        return {
            "output": biases,
            "confidence": result.get("confidence", 0.8)
        }
