from typing import Optional
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel
import json

from api.auth import get_current_user, get_db
from models.user import User
from models.event import EventLog

from services.orchestrator import orchestrator
from services.aggregator import aggregate
from services.llm_service import generate_grounded_text
from services.debate_engine import run_debate, synthesize_debate
from services.self_eval_engine import get_system_effectiveness
from services.outcome_engine import push_real_outcome
from services.guardrails import run_ethical_guardrails
from services.memory_engine import CognitiveMemoryEngine
from services.streaming_engine import DeliberationStreamingEngine
from services.health_engine import HealthEngine
from services.counterfactual_engine import CounterfactualEngine
from services.red_team_engine import RedTeamEngine
from services.reliability_service import ReliabilityService
from services.post_mortem_engine import PostMortemEngine
from services.crisis_service import CrisisService
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
async def respond(
    data: AgentInput, 
    user: User = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    # Mandatory Safety Gate: Crisis Circuit Breaker
    crisis_check = CrisisService.evaluate(data.scenario, user_id=user.id, db=db)
    if crisis_check["is_crisis"]:
        log_event = EventLog(
            user_id=user.id,
            type="CRISIS_INTERCEPTION",
            metadata_col=json.dumps({
                "severity": crisis_check["severity"],
                "triggers": crisis_check["triggers"],
                "timestamp": "now"
            })
        )
        db.add(log_event)
        db.commit()

        return {
            "is_crisis": True,
            "severity": crisis_check["severity"],
            "crisis_response": crisis_check["response"],
            "synthesized_payload": {
                "final_decision": "EMERGENCY SAFETY INTERVENTION: Please contact 988 or a crisis helpline immediately.",
                "reasoning": crisis_check["response"]["message"],
                "confidence": 1.0,
                "strategy_selected": "Crisis De-escalation & Helpline Connect",
                "decision_hash": "crisis_circuit_breaker_triggered",
                "is_crisis": True,
                "intervention_intensity": "Critical",
                "helplines": crisis_check["response"]["helplines"]
            },
            "agent_contributions": {},
            "trust_tiers": {},
            "learning_health": {"status": "suspended", "reason": "crisis_circuit_breaker"}
        }

    # Phase 11: Long-term episodic memory retrieval reusing request db session
    past_memories = CognitiveMemoryEngine.retrieve_relevant_episodes(db, user.id, data.scenario, top_k=3)

    # 1. Orchestrator Parallel Async Pipe reusing request db session
    input_dict = {
        "user_id": user.id,
        "emotion": "neutral",
        "scenario": data.scenario,
        "memories": past_memories,
        "db": db
    }
    agent_outputs = await orchestrator.run(input_dict)
    
    # 2. Aggregator Conflict Resolution Pipe
    final = aggregate(user.id, agent_outputs)
    
    # Safety Check: Confidence Floor Degrade
    if final["confidence"] < 0.4:
        final["degraded_safe_mode"] = True
        
    # 3. Agent Event Memory Logging
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
    db.commit()
        
    # Phase 9: LLM Debate & Synthesis Fusion
    arguments = run_debate(agent_outputs)
    synthesis = synthesize_debate(arguments)
    
    # 2.6 MEMORY OF DECISIONS Logging (Forensic Cryptographic Stamping)
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
    db.add(decision_log)
    db.commit()
    
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
    
    learning_health_status = HealthEngine.check_learning_health(db, user.id)
    
    # Phase 12: Generate counterfactual shadow simulation branches
    cf_branches = CounterfactualEngine.simulate_branches(
        db=db,
        user_id=user.id,
        scenario=data.scenario,
        current_emotion=input_dict.get("emotion", "neutral"),
        current_intensity=final["confidence"],
        decision_hash=synthesis.get("decision_hash")
    )
    
    # Phase 13: Adversarial Red-Team Audit
    red_team_audit = RedTeamEngine.audit_synthesis(
        db=db,
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
async def log_outcome(
    data: OutcomeInput, 
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Strict tenant-isolated outcome credit assignment
    push_real_outcome(user.id, "latest", data.success, data.delta, db=db)
    # Process the outcome to update Agent Reliability metrics
    ReliabilityService.process_outcome(user.id, data.success, db=db)

    post_mortem_report = None
    scenario_text = data.scenario or "Target scenario intervention"
    
    # Phase 11: Store episode in long-term episodic memory and reinforce graph
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

    return {"status": "tracked", "post_mortem": post_mortem_report}
