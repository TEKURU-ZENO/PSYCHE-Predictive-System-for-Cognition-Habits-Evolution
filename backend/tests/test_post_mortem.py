import unittest
from unittest.mock import MagicMock
from services.post_mortem_engine import PostMortemEngine

class TestPostMortemEngine(unittest.TestCase):
    def test_aggressive_push_attributes_to_strategy(self):
        mock_db = MagicMock()
        mock_metric = MagicMock()
        mock_metric.overrides = 0
        mock_metric.historical_accuracy = 0.85
        mock_db.query.return_value.filter_by.return_value.first.return_value = mock_metric

        report = PostMortemEngine.conduct_post_mortem(
            db=mock_db,
            user_id=1,
            failed_action="push_through_harder",
            decision_hash="test_hash_123"
        )

        self.assertEqual(report["responsible_agent"], "strategy")
        self.assertEqual(report["secondary_agent"], "prediction")
        self.assertIn("Over-aggressive", report["root_cause"])
        self.assertGreater(report["penalty_applied"], 0.05)

    def test_avoidance_attributes_to_cognition(self):
        mock_db = MagicMock()
        mock_metric = MagicMock()
        mock_metric.overrides = 0
        mock_metric.historical_accuracy = 0.85
        mock_db.query.return_value.filter_by.return_value.first.return_value = mock_metric

        report = PostMortemEngine.conduct_post_mortem(
            db=mock_db,
            user_id=1,
            failed_action="isolate_and_avoid_conflict",
            decision_hash="test_hash_456"
        )

        self.assertEqual(report["responsible_agent"], "cognition")
        self.assertIn("avoidance", report["root_cause"].lower())

if __name__ == "__main__":
    unittest.main()
