import unittest
import json
import asyncio
from unittest.mock import MagicMock, patch, AsyncMock, patch as mock_patch
from services.crisis_service import CrisisService
from services.streaming_engine import DeliberationStreamingEngine
from services.memory_engine import CognitiveMemoryEngine
from services.deep_forecasting_engine import deep_forecasting_engine, DeepGRUCell, TemporalSelfAttention
from models.user import User

class MockMoodItem:
    def __init__(self, mood_type: str, intensity: float):
        self.mood_type = mood_type
        self.intensity = intensity

class TestLiveChatFlowCrisisConfirmation(unittest.TestCase):
    """
    Confirms end-to-end that the crisis protocol is not just a passive helper module,
    but an active runtime circuit breaker embedded in live interactive chat and deliberation pipelines.
    """

    def test_live_stream_deliberation_triggers_crisis_circuit_breaker(self):
        """
        Verify that DeliberationStreamingEngine halts immediately when a crisis scenario
        is passed, yielding an emergency event frame and closing the stream at Step 0.
        """
        async def run_stream():
            scenario = "I can't take this anymore, I want to kill myself tonight"
            events = []
            async for chunk in DeliberationStreamingEngine.stream_deliberation(user_id=1, scenario=scenario):
                events.append(chunk)
            return events

        events = asyncio.run(run_stream())
        self.assertGreater(len(events), 0, "Stream produced no events")
        
        # Parse first event frame
        first_event_str = events[0].strip()
        if first_event_str.startswith("data: "):
            first_event_str = first_event_str[6:].strip()
            
        first_frame = json.loads(first_event_str)
        
        # Verify circuit breaker triggered
        self.assertEqual(first_frame["stage"], "crisis_circuit_breaker")
        self.assertEqual(first_frame["step"], 0)
        self.assertTrue(first_frame["is_crisis"])
        self.assertIn("EMERGENCY SAFETY INTERVENTION", first_frame["message"])
        
        # Verify 988 lifeline provided in crisis response
        crisis_data = first_frame["data"]["crisis_response"]
        self.assertIn("helplines", crisis_data)
        has_988 = any("988" in str(h["contact"]) for h in crisis_data["helplines"])
        self.assertTrue(has_988, "988 Helpline was not yielded in the live streaming frame")
        
        # Verify stream terminated at Step 0 (did NOT execute parallel agents / stages 1-6)
        self.assertEqual(len(events), 1, f"Expected exactly 1 event (immediate termination), got {len(events)}")

    @patch("services.streaming_engine.get_new_session")
    def test_benign_stream_does_not_trigger_crisis_gate(self, mock_session_factory):
        """
        Verify that non-crisis scenarios are NOT blocked by the streaming safety gate.
        Uses patch.object on CognitiveMemoryEngine (staticmethod-safe) and patches all
        orchestration paths to prevent live DB calls.
        Only the first yielded frame is consumed — confirms the crisis gate is NOT triggered.
        """
        mock_db = MagicMock()
        mock_session_factory.return_value = mock_db

        async def consume_first_frame():
            scenario = "I have a tight deadline tomorrow morning for my project"
            async for chunk in DeliberationStreamingEngine.stream_deliberation(user_id=1, scenario=scenario):
                raw = chunk.strip()
                if raw.startswith("data: "):
                    raw = raw[6:].strip()
                return json.loads(raw)
            return None

        # patch.object is required for staticmethods; @patch string path doesn't work for them.
        with patch.object(CognitiveMemoryEngine, "retrieve_relevant_episodes", return_value=[]), \
             patch("services.streaming_engine.orchestrator.run", new_callable=AsyncMock, return_value={}) as mock_orch, \
             patch("services.streaming_engine.aggregate", return_value={"final_decision": "take_break", "confidence": 0.7, "weights": {}, "trust_tiers": {}, "dominant_agent": "strategy", "conflicts": [], "effective_accuracies": {}, "reasoning_traces": [], "strategy": {}, "prediction": {}, "meta": {}, "cognition": {}}) as mock_agg, \
             patch("services.streaming_engine.run_debate", return_value=[]), \
             patch("services.streaming_engine.synthesize_debate", return_value={"final_decision": "take_break", "confidence": 0.7, "reasoning": "rest", "conflicts_detected": []}), \
             patch("services.streaming_engine.RedTeamEngine.audit_synthesis", return_value={"veto_triggered": False, "vulnerabilities": [], "critique_score": 0.1, "suggested_amendment": None, "counter_critique": ""}), \
             patch("services.streaming_engine.CounterfactualEngine.simulate_branches", return_value=[]):

            first_frame = asyncio.run(consume_first_frame())

        self.assertIsNotNone(first_frame, "Stream yielded no frames for benign scenario")
        self.assertNotEqual(
            first_frame.get("stage"), "crisis_circuit_breaker",
            "Crisis circuit breaker triggered on a benign scenario — false positive"
        )
        # First stage should be perception (crisis short-circuit did not fire)
        self.assertEqual(first_frame["stage"], "perception")
        self.assertEqual(first_frame["step"], 1)

    def test_crisis_service_evaluate_benign_returns_false(self):
        """
        Unit test: CrisisService returns is_crisis=False for clearly benign workplace stress text.
        Confirms the false-positive suppression layer works independently of the streaming engine.
        """
        result = CrisisService.evaluate(
            "I have a really stressful presentation tomorrow and I'm worried about it",
            user_id="test_user"
        )
        self.assertFalse(result["is_crisis"], 
            "False positive: benign workplace stress should NOT trigger crisis gate")

    def test_crisis_service_evaluate_explicit_ideation_returns_true(self):
        """
        Unit test: CrisisService.evaluate returns is_crisis=True for explicit suicidal ideation.
        """
        result = CrisisService.evaluate(
            "I want to end my life, I have a plan to kill myself",
            user_id="test_user"
        )
        self.assertTrue(result["is_crisis"])
        self.assertEqual(result["severity"], "critical")

    def test_deep_neural_sequence_forecaster(self):
        """
        Verifies the DeepForecastingEngine executes continuous GRU forward passes,
        temporal self-attention, and deep non-linear burnout hazard projection.
        """
        mood_seq = [
            MockMoodItem("calm", 0.3),
            MockMoodItem("focused", 0.6),
            MockMoodItem("stressed", 0.8),
            MockMoodItem("stressed", 0.85),
            MockMoodItem("fatigued", 0.75),
            MockMoodItem("stressed", 0.90)
        ]

        result = deep_forecasting_engine.forecast_trajectory(mood_seq, horizon_steps=3)
        self.assertEqual(result["model_type"], "deep_neural_sequence")
        self.assertEqual(result["architecture"], "GRU_Latent_Transitions_with_Temporal_Self_Attention")
        self.assertIn("state_distribution", result)
        self.assertIn("dominant_forecast", result)
        self.assertIn("burnout_hazard_rate", result)
        self.assertIn("temporal_attention_weights", result)
        self.assertIn("multi_horizon_projections", result)
        self.assertIn("latent_representation", result)

        # Validate non-linear burnout hazard bounded in (0, 1)
        self.assertGreaterEqual(result["burnout_hazard_rate"], 0.0)
        self.assertLessEqual(result["burnout_hazard_rate"], 1.0)
        self.assertEqual(len(result["multi_horizon_projections"]), 3)

    def test_gru_cell_mathematical_properties(self):
        """
        Verifies GRU cell reset and update gating operations on continuous psychological vectors.
        """
        cell = DeepGRUCell()
        x = [0.5, 0.8, 0.2, 0.1, 0.6, 0.4]
        h_prev = [0.0] * 8
        h_next = cell.forward(x, h_prev)
        self.assertEqual(len(h_next), 8)
        # All hidden values must be bounded in (-1, 1) due to tanh activation
        for val in h_next:
            self.assertGreaterEqual(val, -1.0)
            self.assertLessEqual(val, 1.0)

    def test_temporal_self_attention_normalization(self):
        """
        Verifies self-attention weights sum to 1.0 across historical psychological states.
        """
        attn = TemporalSelfAttention(hidden_dim=8)
        h_seq = [[0.1 * i] * 8 for i in range(1, 6)]
        context, weights = attn.compute(h_seq)
        self.assertEqual(len(context), 8)
        self.assertAlmostEqual(sum(weights), 1.0, places=4)

if __name__ == '__main__':
    unittest.main()
