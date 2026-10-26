from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel
import json

from api.auth import get_current_user, get_db
from models.user import User
from models.event import EventLog
from db.postgres import get_new_session

from services.orchestrator import orchestrator
from services.aggregator import aggregate
from services.llm_service import generate_grounded_text
from services.debate_engine import run_debate, synthesize_debate
from services.self_eval_engine import get_system_effectiveness
from services.outcome_engine import push_real_outcome
from services.guardrails import run_ethical_guardrails
from services.memory_engine import CognitiveMemoryEngine
from services.streaming_engine import DeliberationStreamingEngine
from core.versioning import SystemVersionController

router = APIRouter(prefix="/api/v1/agent", tags=["agent"])

RATE_LIMITS = {}
MAX_REQUESTS_PER_MINUTE = 10

class AgentInput(BaseModel):
    scenario: str

class OutcomeInput(BaseModel):
    success: bool
    delta: float = 0.0
    scenario: Optional[str] = None
    decision: Optional[str] = None

@router.get("/stream")
async def stream_deliberation(scenario: str, user: User = Depends(get_current_user)):
    return StreamingResponse(
        DeliberationStreamingEngine.stream_deliberation(user.id, scenario),
        media_type="text/event-stream"
    )

@router.post("/respond")
async def respond(data: AgentInput, user: User = Depends(get_current_user)):
    db = get_new_session()
    try:
        # Phase 11: Long-term episodic memory retrieval
        past_memories = CognitiveMemoryEngine.retrieve_relevant_episodes(db, user.id, data.scenario, top_k=3)
    finally:
        db.close()

    # 1. Orchestrator Parallel Async Pipe
    # For Phase 9 & 11, emotion defaults to neutral if not supplied directly
    input_dict = {
        "user_id": user.id,
        "emotion": "neutral",
        "scenario": data.scenario,
        "memories": past_memories
    }
    agent_outputs = await orchestrator.run(input_dict)
    
    # 2. Aggregator Conflict Resolution Pipe
    final = aggregate(user.id, agent_outputs)
    
    # Safety Check: Confidence Floor Degrade
    if final["confidence"] < 0.4:
        final["degraded_safe_mode"] = True
        
    # 3. Agent Event Memory Logging + Compression
    db = get_new_session()
    try:
        log_event = EventLog(
            user_id=user.id, 
            type="AGENT_OUTPUT",
            metadata_col=json.dumps({
                "confidence": final["confidence"],
                "weights": final["weights"],
                "timestamp": "now"
            })
        )
        db.add(log_event)
        
        # 1.5 Memory Compression Stub
        logs_count = db.query(EventLog).filter(EventLog.user_id == user.id, EventLog.type == "AGENT_OUTPUT").count()
        if logs_count > 1000:
            pass
            
        db.commit()
    finally:
        db.close()
        
    # Phase 9: LLM Debate & Synthesis Fusion
    arguments = run_debate(agent_outputs)
    synthesis = synthesize_debate(arguments)
    
    # 2.6 MEMORY OF DECISIONS Logging (Enhanced Forensic Stamping for Phase 14)
    db_mem = get_new_session()
    try:
        decision_payload = {
            "scenario": data.scenario,
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
        
        decision_log = EventLog(
            user_id=user.id,
            type="DECISION_MEMORY",
            metadata_col=json.dumps({
                **decision_payload,
                "decision_hash": decision_hash,
                "compatibility_mode": SystemVersionController.get_compatibility_flags({}),
                "system_versions": SystemVersionController.VERSION_REGISTRY
            })
        )
        db_mem.add(decision_log)
        db_mem.commit()
    finally:
        db_mem.close()
    
    # 2.7 SAFETY FILTER: Protect hard overrides & Confidence Calibration
    llm_conf = synthesis.get("confidence", 0.0)
    aggregator_conf = final["confidence"]
    synthesis["confidence"] = (llm_conf * 0.5) + (aggregator_conf * 0.5)
    
    strategy_action = final["strategy"].get("output", "rest") if isinstance(final["strategy"], dict) else "rest"
    
    if final["mode"] in ["safe", "conservative"]:
        if "push" in synthesis.get("final_decision", "").lower() and "push" not in str(strategy_action).lower():
            synthesis["final_decision"] = strategy_action
            synthesis["reasoning"] += " [System Overrode Synthesis: Unsafe LLM prediction forced into bounds]."
            synthesis["conflicts_detected"].append("HARD LLM Drift Override Applied")
            synthesis["confidence"] = aggregator_conf
            
    # 2.8 ETHICAL GUARDRAILS (Phase 10.3)
    guard_check = run_ethical_guardrails(user.id, synthesis.get("final_decision", ""))
    synthesis["intervention_intensity"] = guard_check.get("intervention_intensity", "Moderate")
    
    if guard_check["blocked"] == True:
        synthesis["final_decision"] = guard_check.get("override_action", "take_break")
        synthesis["reasoning"] = guard_check["reason"]
        synthesis["conflicts_detected"].append("Ethical Guardrail Block Triggered.")
    elif guard_check.get("override_action"):
        synthesis["final_decision"] = guard_check["override_action"]
        synthesis["reasoning"] = guard_check["reason"]
        synthesis["conflicts_detected"].append("Ethical Guardrail Soft Override.")
    
    from services.health_engine import HealthEngine
    from services.counterfactual_engine import CounterfactualEngine
    from services.red_team_engine import RedTeamEngine
    from db.postgres import get_new_session
    db_health = get_new_session()
    try:
        learning_health_status = HealthEngine.check_learning_health(db_health, user.id)
        # Phase 12: Generate counterfactual shadow simulation branches
        cf_branches = CounterfactualEngine.simulate_branches(
            db=db_health,
            user_id=user.id,
            scenario=data.scenario,
            current_emotion=input_dict.get("emotion", "neutral"),
            current_intensity=final["confidence"],
            decision_hash=synthesis.get("decision_hash")
        )
        # Phase 13: Adversarial Red-Team Audit
        red_team_audit = RedTeamEngine.audit_synthesis(
            db=db_health,
            user_id=user.id,
            scenario=data.scenario,
            synthesis=synthesis,
            weights=final["weights"],
            decision_hash=synthesis.get("decision_hash")
        )
        if red_team_audit["veto_triggered"] and red_team_audit.get("suggested_amendment"):
            synthesis["final_decision"] = red_team_audit["suggested_amendment"]
            synthesis["reasoning"] += f" [Adversarial Red-Team VETO: {red_team_audit['counter_critique']}]."
            synthesis["conflicts_detected"].append("Adversarial Red-Team VETO Applied")
            synthesis["red_team_veto_applied"] = True
    finally:
        db_health.close()

    return {
        "agents": {
            "prediction": final["prediction"],
            "strategy": final["strategy"],
            "meta": final["meta"],
            "cognition": final["cognition"]
        },
        "weights": final["weights"],
        "trust_tiers": final["trust_tiers"],
        "effective_accuracies": final["effective_accuracies"],
        "learning_health": {
            "status": learning_health_status,
            "effectiveness": get_system_effectiveness(user.id)
        },
        "confidence_trace": final["reasoning_traces"],
        "conflicts": [final["strategy"].get("conflict_reason")] if final["strategy"].get("conflict_reason") else [],
        "synthesized_payload": synthesis,
        "autobiographical_memories": past_memories,
        "counterfactual_branches": cf_branches,
        "red_team_audit": red_team_audit,
        "version_matrix": SystemVersionController.VERSION_REGISTRY
    }

@router.post("/outcome")
async def log_outcome(data: OutcomeInput, user: User = Depends(get_current_user)):
    from services.reliability_service import ReliabilityService
    from services.post_mortem_engine import PostMortemEngine
    # Applies real-feedback loop to the RL engine implicitly
    push_real_outcome("latest", data.success, data.delta)
    # Process the outcome to update Agent Reliability metrics
    ReliabilityService.process_outcome(user.id, data.success)

    post_mortem_report = None
    # Phase 11: Store episode in long-term episodic memory and reinforce graph
    db = get_new_session()
    try:
        scenario_text = data.scenario or "Target scenario intervention"
        CognitiveMemoryEngine.store_episode(
            db=db,
            user_id=user.id,
            scenario_text=scenario_text,
            episode_type="breakthrough" if data.success else "friction_episode",
            intervention_applied=data.decision or "adaptive_nudge",
            outcome_delta=data.delta if data.delta != 0.0 else (0.4 if data.success else -0.4),
            key_learnings=f"Decision '{data.decision or 'action'}' was evaluated as {'effective' if data.success else 'ineffective'}."
        )

        # Phase 13: If outcome failed, conduct automated forensic post-mortem
        if not data.success:
            post_mortem_report = PostMortemEngine.conduct_post_mortem(
                db=db,
                user_id=user.id,
                failed_action=data.decision or "unspecified_intervention"
            )
    finally:
        db.close()

    return {"status": "tracked", "post_mortem": post_mortem_report}
