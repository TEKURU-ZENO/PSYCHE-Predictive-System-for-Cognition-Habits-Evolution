import asyncio
from agents.perception import PerceptionAgent
from agents.cognition import CognitionAgent
from agents.prediction import PredictionAgent
from agents.strategy import StrategyAgent
from agents.meta import MetaAgent

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
        # 1. Perception Layer (Sequential)
        context = {"input": input_data}
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
