import json
import os
import sys
import unittest
from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import patch

# Ensure backend root is importable regardless of working directory
BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

os.environ.setdefault("DATABASE_URL", "sqlite:///./test_audit.db")
os.environ.setdefault("SECRET_KEY", "test_secret_key_for_audit_verification")
os.environ.setdefault("ENVIRONMENT", "test")

from jose import jwt
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from core.config import settings
from core.versioning import SystemVersionController
from db.postgres import Base
import models  # noqa: F401 - register all SQLAlchemy tables
from models.event import EventLog
from models.mood import MoodLog
from models.proactive import ProactiveAlert
from models.user_state import UserState
from services.crisis_service import CrisisService
from services.deep_forecasting_engine import deep_forecasting_engine
from services.guardrails import run_ethical_guardrails
from services.llm_service import _generate_structured_fallback
from services.memory_engine import compute_similarity, extract_keywords
from services.privacy_vault import PrivacyVaultService
from services.proactive_monitor import ProactiveMonitor
from services.replay_engine import ForensicReplayEngine
from utils.security import create_token


class AuditRemediationTests(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
        Base.metadata.create_all(bind=self.engine)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        self.db = self.SessionLocal()

    def tearDown(self):
        self.db.close()
        self.engine.dispose()

    def test_jwt_includes_exp_and_iat(self):
        token = create_token({"sub": "audit@psychai.local"})
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        self.assertEqual(payload["sub"], "audit@psychai.local")
        self.assertIn("exp", payload)
        self.assertIn("iat", payload)
        self.assertGreater(payload["exp"], payload["iat"])

    def test_replay_detects_payload_tampering(self):
        payload = {
            "scenario": "Overbooked week",
            "decision": "Take a 15m recovery break",
            "reasoning": "Stress velocity exceeded threshold",
            "confidence": 0.85,
            "agents_involved": ["PredictionAgent", "StrategyAgent"],
            "weights": {"PredictionAgent": 0.5, "StrategyAgent": 0.5},
            "trust_tiers": {"PredictionAgent": "Trusted"},
            "conflicts_detected": [],
            "arguments": [{"agent": "StrategyAgent", "stance": "pace"}],
            "outcome": "pending",
        }
        decision_hash = SystemVersionController.generate_decision_hash(payload)

        valid_meta = dict(payload, decision_hash=decision_hash)
        self.db.add(
            EventLog(
                user_id="tenant-1",
                type="DECISION_MEMORY",
                metadata_col=json.dumps(valid_meta),
            )
        )
        self.db.commit()

        valid_replay = ForensicReplayEngine.verify_and_replay_decision(self.db, "tenant-1", decision_hash)
        self.assertIsNotNone(valid_replay)
        self.assertTrue(valid_replay["is_tamper_free"])

        # Tamper with stored decision text while leaving decision_hash untouched
        row = self.db.query(EventLog).filter_by(user_id="tenant-1", type="DECISION_MEMORY").first()
        tampered_meta = json.loads(row.metadata_col)
        tampered_meta["decision"] = "Push 16 hours nonstop"
        row.metadata_col = json.dumps(tampered_meta)
        self.db.commit()

        tampered_replay = ForensicReplayEngine.verify_and_replay_decision(self.db, "tenant-1", decision_hash)
        self.assertIsNotNone(tampered_replay)
        self.assertFalse(tampered_replay["is_tamper_free"])

    def test_guardrails_escalate_on_mood_key(self):
        for intensity in (0.85, 0.91):
            self.db.add(
                EventLog(
                    user_id="user-distress",
                    type="MOOD_LOGGED",
                    metadata_col=json.dumps({"mood": "stressed", "intensity": intensity}),
                )
            )
        self.db.commit()

        test_session = self.SessionLocal()
        with patch("services.guardrails.get_new_session", return_value=test_session):
            res = run_ethical_guardrails("user-distress", "Take a deep breath")

        self.assertTrue(res["blocked"])
        self.assertEqual(res["intervention_intensity"], "Critical")
        self.assertEqual(res["override_action"], "grounding_and_support_links")

    def test_llm_structured_fallback_handles_context_without_nameerror(self):
        res = _generate_structured_fallback(
            'Detect cognitive bias and return {"biases": ...}',
            context={
                "signals": {
                    "raw_candidates": [
                        {
                            "type": "Catastrophizing",
                            "quote": "Everything will ruin the launch",
                            "socratic_question": "What evidence supports a recoverable path?",
                            "reframe": "Setbacks are localized and solvable step by step.",
                        }
                    ]
                }
            },
        )
        parsed = json.loads(res["text"])
        self.assertEqual(len(parsed["biases"]), 1)
        self.assertEqual(parsed["biases"][0]["type"], "Catastrophizing")

    def test_crisis_normalization_and_india_helpline(self):
        obfuscated = "I am going to k1ll my\u200bself tonight"
        eval_obf = CrisisService.evaluate(obfuscated)
        self.assertTrue(eval_obf["is_crisis"])
        self.assertEqual(eval_obf["severity"], "critical")

        passive = "Honestly I don't want to wake up tomorrow"
        eval_passive = CrisisService.evaluate(passive)
        self.assertTrue(eval_passive["is_crisis"])

        helpline_contacts = [h["contact"] for h in eval_passive["response"]["helplines"]]
        helpline_names = [h["name"] for h in eval_passive["response"]["helplines"]]
        self.assertTrue(any("14416" in c for c in helpline_contacts))
        self.assertIn("988 Suicide & Crisis Lifeline", helpline_names)
        self.assertIn("The Trevor Project", helpline_names)
        self.assertIn("Veterans Crisis Line", helpline_names)

    def test_proactive_circadian_tz_offset_and_alert_dedup(self):
        # Verify timezone localization shifts hour cleanly from UTC midnight
        utc_midnight = datetime(2026, 5, 1, 0, 30, tzinfo=timezone.utc)
        with patch("services.proactive_monitor.datetime") as mock_dt:
            mock_dt.now.return_value = utc_midnight
            # UTC+9:00 => JS offset -540 -> local 09:30 (morning focus phase)
            phase_tokyo = ProactiveMonitor.get_circadian_phase(tz_offset_minutes=-540)
            self.assertEqual(phase_tokyo, "morning_focus")

        # Verify repeat scan does not duplicate active alerts
        for i in range(3):
            self.db.add(
                MoodLog(
                    user_id="scan-user",
                    mood_type="stressed",
                    intensity=0.85,
                    timestamp=datetime.now(timezone.utc).replace(tzinfo=None),
                )
            )
        self.db.commit()

        first = ProactiveMonitor.run_ambient_scan(self.db, "scan-user", tz_offset_minutes=0)
        count_after_first = self.db.query(ProactiveAlert).filter_by(user_id="scan-user").count()
        second = ProactiveMonitor.run_ambient_scan(self.db, "scan-user", tz_offset_minutes=0)
        count_after_second = self.db.query(ProactiveAlert).filter_by(user_id="scan-user").count()

        self.assertGreater(count_after_first, 0)
        self.assertEqual(count_after_first, count_after_second)
        self.assertEqual(len(first["active_alerts"]), len(second["active_alerts"]))

    def test_gdpr_erasure_removes_only_target_tenant(self):
        self.db.add(UserState(user_id="victim-1", current_emotion="anxious", intensity=0.8))
        self.db.add(MoodLog(user_id="victim-1", mood_type="anxious", intensity=0.8))
        self.db.add(UserState(user_id="other-2", current_emotion="calm", intensity=0.2))
        self.db.add(MoodLog(user_id="other-2", mood_type="calm", intensity=0.2))
        self.db.commit()

        counts = PrivacyVaultService.erase_all_user_data(self.db, "victim-1")
        self.assertGreaterEqual(counts.get("mood_logs", 0), 1)
        self.assertEqual(self.db.query(MoodLog).filter_by(user_id="victim-1").count(), 0)
        self.assertEqual(self.db.query(UserState).filter_by(user_id="victim-1").count(), 0)
        self.assertEqual(self.db.query(MoodLog).filter_by(user_id="other-2").count(), 1)

    def test_deep_forecasting_ci_and_memory_semantic_clusters(self):
        moods = [
            SimpleNamespace(mood_type="calm", intensity=0.3, timestamp=datetime(2026, 5, 1, 9, 0)),
            SimpleNamespace(mood_type="stressed", intensity=0.7, timestamp=datetime(2026, 5, 1, 14, 0)),
            SimpleNamespace(mood_type="anxious", intensity=0.82, timestamp=datetime(2026, 5, 1, 21, 0)),
        ]
        forecast = deep_forecasting_engine.forecast_trajectory(moods, horizon_steps=3)
        self.assertIs(forecast["weights_trained"], False)
        self.assertEqual(forecast["weight_source"], "deterministic_analytic_prior")
        self.assertIn("burnout_hazard_ci", forecast)
        low, high = forecast["burnout_hazard_ci"]
        self.assertLessEqual(low, forecast["burnout_hazard_rate"])
        self.assertGreaterEqual(high, forecast["burnout_hazard_rate"])
        self.assertEqual(len(forecast["multi_horizon_projections"]), 3)
        self.assertIn("burnout_hazard", forecast["multi_horizon_projections"][0])

        kw = extract_keywords("Late-night burnout from endless meetings")
        self.assertIn("burnout", kw)
        sim_clustered = compute_similarity({"burnout"}, {"exhausted"}, -0.6, -0.6)
        sim_unrelated = compute_similarity({"burnout"}, {"bicycle"}, -0.6, -0.6)
        self.assertGreater(sim_clustered, sim_unrelated)


if __name__ == "__main__":
    unittest.main()
