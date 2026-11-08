import asyncio
from agents.perception import PerceptionAgent
from agents.cognition import CognitionAgent
from agents.prediction import PredictionAgent
from agents.strategy import StrategyAgent
from agents.meta import MetaAgent
from services.crisis_service import CrisisService

class Orchestrator:
    def __init__(self):
        self.perception_agent = PerceptionAgent()
        self.parallel_agents = [
            CognitionAgent(),
            PredictionAgent(),
            StrategyAgent(),
            MetaAgent()
        ]

    async def run(self, input_data):
        scenario = input_data.get("scenario") or ""
        crisis_check = CrisisService.evaluate(scenario)
        if crisis_check["is_crisis"]:
            return {
                "state": {"scenario": scenario, "is_crisis": True},
                "cognition": {"output": [], "confidence": 1.0, "is_crisis": True},
                "prediction": {"output": {"risk": "Critical Safety Escalation"}, "confidence": 1.0},
                "strategy": {"output": {"action": "crisis_helpline_intervention", "crisis_response": crisis_check["response"]}, "confidence": 1.0},
                "meta": {"output": {"approved": False, "guardrail_blocked": True, "reason": "Crisis Circuit Breaker"}, "confidence": 1.0}
            }

        # 1. Perception Layer (Sequential)
        context = {"input": input_data, "db": input_data.get("db")}
        perception_res = await self.perception_agent.run(context)
        context["state"] = perception_res.get("output", {})
        
        # Base input state mapped into explicit DB-reliant parallel workflows
        tasks = [agent.run(context) for agent in self.parallel_agents]

        # 2. Asynchronous Execution
        results = await asyncio.gather(*tasks, return_exceptions=True)

        output = { "state": context["state"] }
        for agent, res in zip(self.parallel_agents, results):
            if isinstance(res, Exception):
                output[agent.name] = agent.fallback(str(res) or "exception")
            else:
                output[agent.name] = res

        return output

orchestrator = Orchestrator()
