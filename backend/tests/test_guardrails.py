import unittest
from unittest.mock import MagicMock, patch
from services.guardrails import run_ethical_guardrails

class TestEthicalGuardrails(unittest.TestCase):
    @patch("services.guardrails.get_new_session")
    def test_standard_action_passes(self, mock_session_factory):
        mock_db = MagicMock()
        mock_db.query.return_value.filter.return_value.order_by.return_value.limit.return_value.all.return_value = []
        mock_session_factory.return_value = mock_db

        result = run_ethical_guardrails(user_id=1, proposed_action="take_break")
        self.assertFalse(result["blocked"])
        self.assertEqual(result["intervention_intensity"], "Moderate")

    @patch("services.guardrails.get_new_session")
    def test_escalation_protocol_triggers_on_high_distress(self, mock_session_factory):
        mock_db = MagicMock()
        
        # Mock distress logs
        mock_log1 = MagicMock()
        mock_log1.metadata_col = '{"intensity": 0.95, "emotion": "panicked"}'
        mock_log2 = MagicMock()
        mock_log2.metadata_col = '{"intensity": 0.90, "emotion": "anxious"}'

        def mock_query(model):
            q = MagicMock()
            q.filter.return_value.order_by.return_value.limit.return_value.all.return_value = [mock_log1, mock_log2]
            return q

        mock_db.query.side_effect = mock_query
        mock_session_factory.return_value = mock_db

        result = run_ethical_guardrails(user_id=1, proposed_action="push_through")
        self.assertTrue(result["blocked"])
        self.assertEqual(result["intervention_intensity"], "Critical")
        self.assertEqual(result["override_action"], "grounding_and_support_links")

if __name__ == "__main__":
    unittest.main()
