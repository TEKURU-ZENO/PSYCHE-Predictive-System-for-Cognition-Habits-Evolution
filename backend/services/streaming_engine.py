import asyncio
import json
from typing import AsyncGenerator, Dict, Any
from db.postgres import get_new_session
from services.orchestrator import orchestrator
from services.aggregator import aggregate
from services.debate_engine import run_debate, synthesize_debate
from services.red_team_engine import RedTeamEngine
from services.memory_engine import CognitiveMemoryEngine
from services.counterfactual_engine import CounterfactualEngine
from core.versioning import SystemVersionController

class DeliberationStreamingEngine:
    @staticmethod
    async def stream_deliberation(user_id: int, scenario: str) -> AsyncGenerator[str, None]:
        """
        Progressively streams multi-agent deliberation frames as SSE / JSON events.
        """
        # --- Stage 1: Perception & Autobiographical Retrieval ---
        db = get_new_session()
        try:
            past_memories = CognitiveMemoryEngine.retrieve_relevant_episodes(db, user_id, scenario, top_k=3)
        finally:
            db.close()

        yield json.dumps({
            "stage": "perception",
            "step": 1,
            "message": "PerceptionAgent active: normalising scenario and retrieving autobiographical memories...",
            "data": {
                "scenario": scenario,
                "memories_count": len(past_memories),
                "memories_sample": past_memories[:2]
            }
        }) + "\n\n"
        await asyncio.sleep(0.3)

        # --- Stage 2: Parallel Agent Deliberation ---
        input_dict = {
            "user_id": user_id,
            "emotion": "neutral",
            "scenario": scenario,
            "memories": past_memories
        }
        agent_outputs = await orchestrator.run(input_dict)

        yield json.dumps({
            "stage": "agents_deliberating",
            "step": 2,
            "message": "Parallel cognitive agents completed role-lens positions.",
            "data": {
                "prediction": agent_outputs.get("prediction"),
                "strategy": agent_outputs.get("strategy"),
                "meta": agent_outputs.get("meta"),
                "cognition": agent_outputs.get("cognition")
            }
        }) + "\n\n"
        await asyncio.sleep(0.3)

        # --- Stage 3: Dynamic Calibration & Aggregation ---
        final = aggregate(user_id, agent_outputs)

        yield json.dumps({
            "stage": "calibration",
            "step": 3,
            "message": "Dynamic Calibration applied: recency decay, historical accuracy, and trust tiers computed.",
            "data": {
                "weights": final["weights"],
                "trust_tiers": final["trust_tiers"],
                "dominant_agent": final["dominant_agent"],
                "conflicts": final["conflicts"]
            }
        }) + "\n\n"
        await asyncio.sleep(0.3)

        # --- Stage 4: Synthesis & Debate Fusion ---
        arguments = run_debate(agent_outputs)
        synthesis = synthesize_debate(arguments)

        decision_payload = {
            "scenario": scenario,
            "decision": synthesis.get("final_decision", "unknown"),
            "reasoning": synthesis.get("reasoning", ""),
            "confidence": synthesis.get("confidence", 0.5),
            "agents_involved": list(final["weights"].keys()),
            "weights": final["weights"],
            "trust_tiers": final["trust_tiers"],
            "conflicts_detected": synthesis.get("conflicts_detected", []),
            "arguments": arguments,
            "outcome": "pending"
        }
        decision_hash = SystemVersionController.generate_decision_hash(decision_payload)
        synthesis["decision_hash"] = decision_hash

        yield json.dumps({
            "stage": "synthesis",
            "step": 4,
            "message": "Synthesizer reconciled multi-agent debate into consensus.",
            "data": {
                "decision": synthesis.get("final_decision"),
                "confidence": synthesis.get("confidence"),
                "decision_hash": decision_hash
            }
        }) + "\n\n"
        await asyncio.sleep(0.3)

        # --- Stage 5: Adversarial Red-Team Audit ---
        db_audit = get_new_session()
        try:
            red_team_audit = RedTeamEngine.audit_synthesis(
                db=db_audit,
                user_id=user_id,
                scenario=scenario,
                synthesis=synthesis,
                weights=final["weights"],
                decision_hash=decision_hash
            )
            if red_team_audit["veto_triggered"] and red_team_audit.get("suggested_amendment"):
                synthesis["final_decision"] = red_team_audit["suggested_amendment"]
                synthesis["red_team_veto_applied"] = True
        finally:
            db_audit.close()

        yield json.dumps({
            "stage": "red_team_audit",
            "step": 5,
            "message": "Adversarial Red-Team audit completed.",
            "data": red_team_audit
        }) + "\n\n"
        await asyncio.sleep(0.3)

        # --- Stage 6: Final Lock & Shadow Projections ---
        db_cf = get_new_session()
        try:
            cf_branches = CounterfactualEngine.simulate_branches(
                db=db_cf,
                user_id=user_id,
                scenario=scenario,
                current_emotion="neutral",
                current_intensity=final["confidence"],
                decision_hash=decision_hash
            )
        finally:
            db_cf.close()

        yield json.dumps({
            "stage": "completed",
            "step": 6,
            "message": "Deliberation finalized and hashed with forensic integrity.",
            "data": {
                "synthesized_payload": synthesis,
                "weights": final["weights"],
                "trust_tiers": final["trust_tiers"],
                "effective_accuracies": final["effective_accuracies"],
                "confidence_trace": final["reasoning_traces"],
                "conflicts": final["conflicts"],
                "autobiographical_memories": past_memories,
                "counterfactual_branches": cf_branches,
                "red_team_audit": red_team_audit,
                "version_matrix": SystemVersionController.VERSION_REGISTRY
            }
        }) + "\n\n"
