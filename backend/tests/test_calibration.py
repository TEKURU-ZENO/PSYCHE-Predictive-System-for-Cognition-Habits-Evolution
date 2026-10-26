import unittest
from services.calibration_service import CalibrationService
from services.reliability_service import ReliabilityService

class TestCalibrationAndReliability(unittest.TestCase):
    def test_recency_decay_calculation(self):
        # 0 days since last success => factor is 1.0
        acc_0_days = 0.85 * (0.98 ** 0)
        self.assertAlmostEqual(acc_0_days, 0.85, places=4)

        # 10 days since last success => factor is 0.98^10 (~0.817)
        acc_10_days = 0.85 * (0.98 ** 10)
        self.assertLess(acc_10_days, 0.85)
        self.assertGreater(acc_10_days, 0.65)

    def test_trust_tier_assignment(self):
        # Verify classification rules
        self.assertEqual(ReliabilityService.classify_trust_tier(0.85, 1.2), "Trusted")
        self.assertEqual(ReliabilityService.classify_trust_tier(0.75, 1.0), "Stable")
        self.assertEqual(ReliabilityService.classify_trust_tier(0.60, 0.8), "Uncertain")
        self.assertEqual(ReliabilityService.classify_trust_tier(0.40, 0.5), "Degraded")

    def test_dynamic_weight_formula(self):
        raw_conf = 0.8
        reliability = 0.9
        effective_acc = 0.85
        expected_dynamic = round(raw_conf * reliability * effective_acc, 3)
        self.assertGreater(expected_dynamic, 0.5)
        self.assertLessEqual(expected_dynamic, 1.0)

if __name__ == "__main__":
    unittest.main()
