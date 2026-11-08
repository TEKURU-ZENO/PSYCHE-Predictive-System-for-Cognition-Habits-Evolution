import unittest
from services.cognition_engine import cognition_engine
from services.prediction_engine import (
    predict_next_mood,
    detect_early_warnings,
    project_long_term_risk,
    _holt_linear_trend_forecast,
    _compute_markov_transition_probabilities
)

class MockMood:
    def __init__(self, mood_type, intensity):
        self.mood_type = mood_type
        self.intensity = intensity

class TestCBTCognitionAndPrediction(unittest.TestCase):
    def test_cbt_all_or_nothing_distortion(self):
        text = "I completely ruined the presentation, it was a total failure."
        res = cognition_engine.analyze(text)
        self.assertFalse(res["is_crisis"])
        bias_types = [b["type"] for b in res["biases"]]
        self.assertTrue(any("All-or-Nothing" in b for b in bias_types), f"Expected All-or-Nothing, got: {bias_types}")
        first_bias = res["biases"][0]
        self.assertIn("socratic_question", first_bias)
        self.assertIn("reframe", first_bias)

    def test_cbt_overgeneralization_distortion(self):
        text = "Nobody ever listens to me, it never works out for me."
        res = cognition_engine.analyze(text)
        self.assertFalse(res["is_crisis"])
        bias_types = [b["type"] for b in res["biases"]]
        self.assertTrue(any("Overgeneralization" in b for b in bias_types), f"Expected Overgeneralization, got: {bias_types}")

    def test_cbt_catastrophizing_distortion(self):
        text = "This mistake means my career is ruined and my life is over."
        res = cognition_engine.analyze(text)
        bias_types = [b["type"] for b in res["biases"]]
        self.assertTrue(any("Catastrophizing" in b for b in bias_types), f"Expected Catastrophizing, got: {bias_types}")

    def test_cbt_should_statement_distortion(self):
        text = "I should have known better, I must never make mistakes."
        res = cognition_engine.analyze(text)
        bias_types = [b["type"] for b in res["biases"]]
        self.assertTrue(any("Should" in b for b in bias_types), f"Expected Should statement, got: {bias_types}")

    def test_cbt_labeling_distortion(self):
        text = "I am a total loser and an imposter."
        res = cognition_engine.analyze(text)
        bias_types = [b["type"] for b in res["biases"]]
        self.assertTrue(any("Labeling" in b for b in bias_types), f"Expected Labeling, got: {bias_types}")

    def test_holt_linear_trend_forecasting(self):
        intensities = [0.4, 0.5, 0.6, 0.7, 0.8]
        forecast = _holt_linear_trend_forecast(intensities, h=1)
        self.assertGreater(forecast["projected"], 0.7)
        self.assertGreater(forecast["velocity"], 0.0)
        self.assertIn("volatility", forecast)

    def test_markov_state_probabilities(self):
        moods = [
            MockMood("stressed", 0.8),
            MockMood("stressed", 0.85),
            MockMood("fatigued", 0.7),
            MockMood("stressed", 0.9)
        ]
        probs = _compute_markov_transition_probabilities(moods, current_state="stressed")
        self.assertIn("stressed", probs)
        self.assertIn("fatigued", probs)
        self.assertGreater(probs["stressed"], 0.0)

    def test_predict_next_mood_multivariate(self):
        moods = [
            MockMood("calm", 0.3),
            MockMood("calm", 0.35),
            MockMood("focused", 0.5),
            MockMood("focused", 0.6),
            MockMood("stressed", 0.8)
        ]
        pred = predict_next_mood(moods)
        self.assertIn("predicted_state", pred)
        self.assertIn("predicted_intensity", pred)
        self.assertIn("state_probabilities", pred)
        self.assertIn("trend", pred)
        self.assertIn("velocity", pred)
        self.assertIn("volatility", pred)
        self.assertIn("circadian_phase", pred)

    def test_detect_early_warnings_burnout(self):
        moods = [
            MockMood("stressed", 0.85),
            MockMood("stressed", 0.90),
            MockMood("fatigued", 0.80),
            MockMood("stressed", 0.95)
        ]
        warning = detect_early_warnings(moods, triggers=[])
        self.assertIsNotNone(warning)
        self.assertIn(warning["type"], ["burnout_risk", "critical_slowing_down"])

if __name__ == '__main__':
    unittest.main()
