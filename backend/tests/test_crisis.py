import unittest
from unittest.mock import MagicMock
from services.crisis_service import CrisisService
from services.cognition_engine import cognition_engine
from services.guardrails import run_ethical_guardrails

class TestCrisisIntervention(unittest.TestCase):
    def test_explicit_suicidal_ideation_triggers_critical_crisis(self):
        phrases = [
            "I want to kill myself",
            "I'm going to end my life tonight",
            "There's no point in living, I wish I was dead",
            "I wrote a goodbye note to everyone",
            "I can't go on living anymore"
        ]
        for phrase in phrases:
            res = CrisisService.evaluate(phrase)
            self.assertTrue(res["is_crisis"], f"Failed to detect crisis for: {phrase}")
            self.assertEqual(res["severity"], "critical")
            self.assertIsNotNone(res["response"])
            self.assertIn("helplines", res["response"])
            
            # Verify 988 is present
            helplines = res["response"]["helplines"]
            has_988 = any(h["contact"] == "988" for h in helplines)
            self.assertTrue(has_988, "988 lifeline missing from crisis response")

    def test_self_harm_triggers_crisis(self):
        phrases = [
            "I feel like cutting myself again",
            "I want to burn myself",
            "I need to punish my body",
            "I've been thinking about self harm"
        ]
        for phrase in phrases:
            res = CrisisService.evaluate(phrase)
            self.assertTrue(res["is_crisis"], f"Failed to detect self-harm for: {phrase}")
            self.assertIn("self_harm", res["triggers"])

    def test_benign_expressions_do_not_trigger_false_positives(self):
        phrases = [
            "This deadline is killing me, so much work",
            "I am dying of laughter from that joke",
            "I would kill for a cup of coffee right now",
            "I don't want to die, I want to live a long healthy life",
            "I have a killer presentation prepared"
        ]
        for phrase in phrases:
            res = CrisisService.evaluate(phrase)
            self.assertFalse(res["is_crisis"], f"False positive triggered for benign phrase: {phrase}")

    def test_cognition_engine_circuit_breaker(self):
        result = cognition_engine.analyze("I want to end my life")
        self.assertTrue(result["is_crisis"])
        self.assertEqual(len(result["biases"]), 0)
        self.assertIn("crisis_response", result)
        self.assertEqual(result["crisis_response"]["action"], "crisis_helpline_intervention")

    def test_guardrails_blocks_crisis_action(self):
        result = run_ethical_guardrails(user_id="test_user", proposed_action="I want to hurt myself")
        self.assertTrue(result["blocked"])
        self.assertEqual(result["intervention_intensity"], "Critical")
        self.assertEqual(result["override_action"], "crisis_helpline_intervention")

if __name__ == '__main__':
    unittest.main()
