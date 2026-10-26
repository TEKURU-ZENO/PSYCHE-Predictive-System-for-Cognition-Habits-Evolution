import unittest
from services.red_team_engine import RedTeamEngine

class TestRedTeamEngine(unittest.TestCase):
    def test_benign_consensus_passes(self):
        scenario = "I have a big presentation on Friday and need to prepare my slides."
        synthesis = {
            "final_decision": "Break preparation into 3 focused 30-minute intervals",
            "reasoning": "Pacing slides creation prevents late-night rush."
        }
        weights = {"strategy": 0.3, "prediction": 0.3, "meta": 0.2, "cognition": 0.2}

        audit = RedTeamEngine.audit_synthesis(None, user_id=1, scenario=scenario, synthesis=synthesis, weights=weights)
        self.assertFalse(audit["veto_triggered"])
        self.assertIn(audit["safety_tier"], ["Safe", "Guarded"])

    def test_sycophancy_and_avoidance_triggers_high_critique(self):
        scenario = "My manager gave me tough feedback and I think everyone hates me."
        synthesis = {
            "final_decision": "You can never change anything, so just isolate yourself from them.",
            "reasoning": "Avoid contact to prevent hurt."
        }
        weights = {"strategy": 0.3, "prediction": 0.3, "meta": 0.2, "cognition": 0.2}

        audit = RedTeamEngine.audit_synthesis(None, user_id=1, scenario=scenario, synthesis=synthesis, weights=weights)
        self.assertGreaterEqual(audit["critique_score"], 0.5)
        self.assertTrue(any("Sycophantic" in v for v in audit["vulnerabilities"]))

    def test_over_optimistic_grind_under_exhaustion_triggers_veto(self):
        scenario = "I am in complete burnout, completely exhausted and failing my exams."
        synthesis = {
            "final_decision": "Push through and execute harder with 8 hours of deep work.",
            "reasoning": "Maximum grind will fix the grades."
        }
        weights = {"strategy": 0.70, "prediction": 0.10, "meta": 0.10, "cognition": 0.10}

        audit = RedTeamEngine.audit_synthesis(None, user_id=1, scenario=scenario, synthesis=synthesis, weights=weights)
        self.assertTrue(audit["veto_triggered"])
        self.assertEqual(audit["safety_tier"], "Vetoed")
        self.assertIsNotNone(audit["suggested_amendment"])

if __name__ == "__main__":
    unittest.main()
