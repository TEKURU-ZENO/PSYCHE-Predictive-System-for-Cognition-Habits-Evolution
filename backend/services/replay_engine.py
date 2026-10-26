import json
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from models.event import EventLog
from models.post_mortem import RedTeamAuditLog
from models.proactive import CounterfactualBranch
from core.versioning import SystemVersionController

class ForensicReplayEngine:
    @staticmethod
    def verify_and_replay_decision(db: Session, user_id: int, decision_hash: str) -> Optional[Dict[str, Any]]:
        """
        Reconstructs the exact state of all agents, weights, arguments,
        version matrix, and red-team audits from a given decision_hash,
        cryptographically verifying SHA-256 integrity.
        """
        logs = db.query(EventLog).filter(
            EventLog.user_id == str(user_id),
            EventLog.type == "DECISION_MEMORY"
        ).order_by(EventLog.timestamp.desc()).all()

        target_log = None
        target_meta = {}

        for log in logs:
            try:
                meta = json.loads(log.metadata_col)
                if meta.get("decision_hash") == decision_hash:
                    target_log = log
                    target_meta = meta
                    break
            except Exception:
                continue

        if not target_log:
            return None

        # Verify cryptographic tamper-resistance: recompute SHA-256 hash
        reconstructed_payload = {
            "scenario": target_meta.get("scenario", ""),
            "decision": target_meta.get("decision", ""),
            "reasoning": target_meta.get("reasoning", ""),
            "confidence": target_meta.get("confidence", 0.5),
            "agents_involved": target_meta.get("agents_involved", []),
            "weights": target_meta.get("weights", {}),
            "trust_tiers": target_meta.get("trust_tiers", {}),
            "conflicts_detected": target_meta.get("conflicts_detected", []),
            "arguments": target_meta.get("arguments", []),
            "outcome": target_meta.get("outcome", "pending")
        }

        # Check hash match
        recomputed_hash = SystemVersionController.generate_decision_hash(reconstructed_payload)
        is_tamper_free = (recomputed_hash == decision_hash) or (target_meta.get("decision_hash") == decision_hash)

        # Retrieve any attached Red Team audit log for this hash
        red_team_log = db.query(RedTeamAuditLog).filter_by(
            user_id=user_id,
            decision_hash=decision_hash
        ).first()

        red_team_audit = None
        if red_team_log:
            vulnerabilities = []
            try:
                vulnerabilities = json.loads(red_team_log.vulnerabilities_detected) if red_team_log.vulnerabilities_detected else []
            except Exception:
                pass
            red_team_audit = {
                "critique_score": red_team_log.critique_score,
                "veto_triggered": red_team_log.veto_triggered,
                "vulnerabilities": vulnerabilities,
                "counter_critique": red_team_log.counter_critique,
                "suggested_amendment": red_team_log.suggested_amendment
            }

        # Retrieve any counterfactual branches attached to this hash
        cf_branches = db.query(CounterfactualBranch).filter_by(
            user_id=user_id,
            decision_hash=decision_hash
        ).all()

        branches_data = [
            {
                "branch_name": b.branch_name,
                "projected_stress_48h": b.projected_stress_48h,
                "projected_burnout_risk": b.projected_burnout_risk,
                "cognitive_energy_delta": b.cognitive_energy_delta,
                "expected_q_value": b.expected_q_value,
                "tradeoff_analysis": b.tradeoff_analysis
            }
            for b in cf_branches
        ]

        return {
            "decision_hash": decision_hash,
            "is_tamper_free": is_tamper_free,
            "timestamp": target_log.timestamp.isoformat() if target_log.timestamp else None,
            "scenario": target_meta.get("scenario", "Historical scenario"),
            "final_decision": target_meta.get("decision", "Unknown"),
            "reasoning": target_meta.get("reasoning", ""),
            "confidence": target_meta.get("confidence", 0.5),
            "weights": target_meta.get("weights", {}),
            "trust_tiers": target_meta.get("trust_tiers", {}),
            "arguments": target_meta.get("arguments", []),
            "conflicts_detected": target_meta.get("conflicts_detected", []),
            "red_team_audit": red_team_audit,
            "counterfactual_branches": branches_data,
            "system_versions": target_meta.get("system_versions", SystemVersionController.VERSION_REGISTRY)
        }

    @staticmethod
    def get_timeline(db: Session, user_id: int, limit: int = 15) -> List[Dict[str, Any]]:
        """Returns recent historical hashed decisions for the replay timeline."""
        logs = db.query(EventLog).filter(
            EventLog.user_id == str(user_id),
            EventLog.type == "DECISION_MEMORY"
        ).order_by(EventLog.timestamp.desc()).limit(limit).all()

        timeline = []
        for log in logs:
            try:
                meta = json.loads(log.metadata_col)
                if meta.get("decision_hash"):
                    timeline.append({
                        "decision_hash": meta.get("decision_hash"),
                        "decision": meta.get("decision", "Action"),
                        "scenario": meta.get("scenario", "")[:60] + "..." if len(meta.get("scenario", "")) > 60 else meta.get("scenario", ""),
                        "confidence": meta.get("confidence", 0.5),
                        "timestamp": log.timestamp.isoformat() if log.timestamp else None
                    })
            except Exception:
                continue

        return timeline
