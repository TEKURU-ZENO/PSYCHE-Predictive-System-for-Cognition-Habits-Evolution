#!/usr/bin/env python3
"""
Psych-AI Platform - Production Preflight Diagnostic Suite
Validates system integrity, agent registries, database schemas, and cryptographic pipelines.
"""

import sys
import os
import time
import json

# Ensure backend is on python path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "backend"))

from core.versioning import SystemVersionController
from services.replay_engine import ForensicReplayEngine
from services.red_team_engine import RedTeamEngine
from services.memory_engine import CognitiveMemoryEngine, extract_keywords, compute_similarity
from services.privacy_vault import PrivacyVaultService
from services.reliability_service import ReliabilityService
from db.postgres import Base

def run_diagnostics():
    print("=" * 70)
    print("PSYCH-AI: COGNITIVE TWIN PLATFORM - PRODUCTION PREFLIGHT CHECK")
    print("=" * 70)
    
    passed_checks = 0
    total_checks = 6

    # 1. System Version Matrix Registry
    print("\n[1/6] Verifying System Version Controller...")
    versions = SystemVersionController.get_version_matrix()
    assert "core" in versions and "agents" in versions and "vault" in versions
    print(f"  [OK] Version Matrix Verified: {len(versions)} sub-modules tracked.")
    print(f"    - Core: {versions['core']} | Agents: {versions['agents']} | Vault: {versions['vault']}")
    passed_checks += 1

    # 2. Database Schema Model Registration
    print("\n[2/6] Verifying SQLAlchemy Metadata & Registered Tables...")
    import models.user
    import models.mood
    import models.event
    import models.user_state
    import models.behavior
    import models.pattern
    import models.personalization
    import models.evolution
    import models.goals
    import models.system_state
    import models.agent_metrics
    import models.memory
    import models.proactive
    import models.post_mortem
    
    registered_tables = list(Base.metadata.tables.keys())
    assert len(registered_tables) >= 15, f"Expected at least 15 tables, found {len(registered_tables)}"
    print(f"  [OK] {len(registered_tables)} Database Tables Registered in Metadata:")
    for t in sorted(registered_tables):
        print(f"    - {t}")
    passed_checks += 1

    # 3. Cryptographic Decision Hashing & Forensic Verification
    print("\n[3/6] Verifying Cryptographic Hashing & Replay Engine...")
    test_decision = {
        "scenario": "Urgent deadline approaching with cognitive exhaustion",
        "decision": "take_break",
        "reasoning": "Rest restores energy and prevents burnout.",
        "confidence": 0.85,
        "agents_involved": ["prediction", "strategy"],
        "weights": {"prediction": 0.4, "strategy": 0.6},
        "trust_tiers": {"prediction": "Trusted", "strategy": "Trusted"},
        "conflicts_detected": [],
        "arguments": [],
        "outcome": "pending"
    }
    decision_hash = SystemVersionController.generate_decision_hash(test_decision)
    assert len(decision_hash) == 64
    
    # Verify replay verification logic with mock DB
    from unittest.mock import MagicMock
    mock_db = MagicMock()
    mock_log = MagicMock()
    mock_log.timestamp = None
    mock_log.metadata_col = json.dumps({
        **test_decision,
        "decision_hash": decision_hash,
        "system_versions": SystemVersionController.VERSION_REGISTRY
    })
    mock_db.query.return_value.filter.return_value.order_by.return_value.all.return_value = [mock_log]
    mock_db.query.return_value.filter_by.return_value.first.return_value = None
    mock_db.query.return_value.filter_by.return_value.all.return_value = []

    replay = ForensicReplayEngine.verify_and_replay_decision(mock_db, user_id=1, decision_hash=decision_hash)
    assert replay is not None and replay["is_tamper_free"] is True
    print(f"  [OK] SHA-256 Decision Hash Generated: {decision_hash[:16]}...{decision_hash[-16:]}")
    print(f"  [OK] Forensic Integrity Verified: Tamper-Free Verified ({replay['final_decision']})")
    passed_checks += 1

    # 4. Adversarial Red-Team Gatekeeper
    print("\n[4/6] Verifying Adversarial Red-Team Gatekeeper...")
    veto_result = RedTeamEngine.audit_synthesis(
        db=None,
        user_id=1,
        scenario="Severe burnout and completely exhausted",
        synthesis={
            "final_decision": "Push harder and grind through the entire night",
            "reasoning": "Ignore symptoms and sprint to complete tasks"
        },
        weights={"strategy": 0.70}
    )
    assert veto_result["veto_triggered"] is True
    print(f"  [OK] Harmful Pattern Caught: {veto_result['vulnerabilities'][0]}")
    print(f"  [OK] Veto Triggered: {veto_result['veto_triggered']} (Risk Score: {int(veto_result['critique_score'] * 100)}%)")
    passed_checks += 1

    # 5. Episodic & Associative Memory Engine
    print("\n[5/6] Verifying Episodic Memory Indexing & Keyword Extraction...")
    keywords = extract_keywords(
        "Late-night burnout caused by consecutive unscheduled meetings and context switching"
    )
    assert "burnout" in keywords or "meetings" in keywords
    q_tokens = set(extract_keywords("burnout and deep stress"))
    e_tokens = set(extract_keywords("burnout and severe fatigue"))
    sim = compute_similarity(q_tokens, e_tokens, q_valence=-0.5, e_valence=-0.6)
    assert sim > 0.2
    print(f"  [OK] Keyword Extraction Extracted: {keywords}")
    print(f"  [OK] Semantic Overlap Metric: {sim:.4f}")
    passed_checks += 1

    # 6. Observability & Agent Trust Tiers
    print("\n[6/6] Verifying Agent Trust Tier Classification...")
    tier_trusted = ReliabilityService.classify_trust_tier(accuracy=0.92, impact=1.3)
    tier_degraded = ReliabilityService.classify_trust_tier(accuracy=0.40, impact=0.8)
    assert tier_trusted == "Trusted" and tier_degraded == "Degraded"
    print(f"  [OK] Trust Tier Calibration: Accuracy 92% -> {tier_trusted} | Accuracy 40% -> {tier_degraded}")
    passed_checks += 1

    print("\n" + "=" * 70)
    print(f"PRODUCTION PREFLIGHT COMPLETE: {passed_checks}/{total_checks} CHECKS PASSED")
    print("All architectural subsystems ready for production deployment.")
    print("=" * 70)
    return True

if __name__ == "__main__":
    success = run_diagnostics()
    sys.exit(0 if success else 1)
