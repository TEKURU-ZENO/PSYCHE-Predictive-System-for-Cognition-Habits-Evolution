import unittest
import json
from unittest.mock import MagicMock
from services.replay_engine import ForensicReplayEngine
from core.versioning import SystemVersionController

class TestForensicReplay(unittest.TestCase):
    def test_decision_hash_integrity_verification(self):
        payload = {
            "scenario": "High deadline friction with fatigue",
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

        generated_hash = SystemVersionController.generate_decision_hash(payload)
        self.assertIsInstance(generated_hash, str)
        self.assertEqual(len(generated_hash), 64)

        # Mock EventLog in DB
        mock_db = MagicMock()
        mock_log = MagicMock()
        mock_log.timestamp = None
        mock_log.metadata_col = json.dumps({
            **payload,
            "decision_hash": generated_hash,
            "system_versions": SystemVersionController.VERSION_REGISTRY
        })
        mock_db.query.return_value.filter.return_value.order_by.return_value.all.return_value = [mock_log]
        mock_db.query.return_value.filter_by.return_value.first.return_value = None
        mock_db.query.return_value.filter_by.return_value.all.return_value = []

        replay = ForensicReplayEngine.verify_and_replay_decision(mock_db, user_id=1, decision_hash=generated_hash)
        self.assertIsNotNone(replay)
        self.assertTrue(replay["is_tamper_free"])
        self.assertEqual(replay["final_decision"], "take_break")
        self.assertEqual(replay["decision_hash"], generated_hash)

if __name__ == "__main__":
    unittest.main()
