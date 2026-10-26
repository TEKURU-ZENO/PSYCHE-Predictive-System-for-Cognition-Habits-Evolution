import asyncio

async def run_blocking(fn, *args):
    return await asyncio.to_thread(fn, *args)

class BaseAgent:
    name = "base"
    timeout = 1.5  # seconds

    async def run(self, context: dict) -> dict:
        try:
            result = await asyncio.wait_for(self._run(context), timeout=self.timeout)
            
            # 1.1 Agent Confidence Normalization
            result["confidence"] = min(1.0, max(0.0, result.get("confidence", 0.0)))
            return result
        except asyncio.TimeoutError:
            return self.fallback("timeout", timeout_penalty=True)
        except Exception as e:
            return self.fallback(str(e))

    async def _run(self, context: dict) -> dict:
        raise NotImplementedError

    def fallback(self, reason, timeout_penalty=False):
        # 1.4 Timeout Weight Penalization
        conf = 0.5 if timeout_penalty else 0.0 
        return {
            "output": None,
            "confidence": conf,
            "error": reason,
            "agent": self.name
        }
