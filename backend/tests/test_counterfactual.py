import unittest
from unittest.mock import MagicMock
from services.counterfactual_engine import CounterfactualEngine

class TestCounterfactualEngine(unittest.TestCase):
    def test_branching_generation_and_ranking(self):
        mock_db = MagicMock()
        mock_db.query.return_value.filter_by.return_value.all.return_value = []
        mock_db.query.return_value.filter_by.return_value.order_by.return_value.limit.return_value.all.return_value = []

        branches = CounterfactualEngine.simulate_branches(
            db=mock_db,
            user_id=1,
            scenario="Facing tight deadline with high cognitive exhaustion",
            current_emotion="stressed",
            current_intensity=0.85
        )

        self.assertEqual(len(branches), 4)
        
        # Check that branches are ranked by payoff
        payoffs = [b["expected_payoff"] for b in branches]
        self.assertEqual(payoffs, sorted(payoffs, reverse=True))

        # Branch 1 should be rank 1
        self.assertEqual(branches[0]["recommendation_rank"], 1)

        # Direct push through should show high burnout risk
        push_branch = next(b for b in branches if b["action_key"] == "push_through")
        self.assertGreaterEqual(push_branch["projected_burnout_risk"], 0.7)
        self.assertLess(push_branch["cognitive_energy_delta"], 0)

if __name__ == "__main__":
    unittest.main()
