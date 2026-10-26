import unittest
from unittest.mock import MagicMock
from api.metrics import prometheus_metrics, healthz, telemetry

class TestMetricsAndObservability(unittest.TestCase):
    def setUp(self):
        self.mock_db = MagicMock()

    def test_healthz_healthy_db(self):
        response = healthz(self.mock_db)
        self.assertEqual(response["status"], "healthy")
        self.assertEqual(response["database"], "connected")
        self.assertIn("uptime_seconds", response)
        self.assertIn("versions", response)
        self.assertIn("core", response["versions"])

    def test_prometheus_metrics_format(self):
        response = prometheus_metrics(self.mock_db)
        content = response.body.decode("utf-8")
        self.assertIn("psychai_system_uptime_seconds", content)
        self.assertIn("psychai_agent_invocations_total", content)
        self.assertIn("psychai_agent_reliability_score", content)

    def test_telemetry_structure(self):
        response = telemetry(self.mock_db)
        self.assertEqual(response["system_status"], "operational")
        self.assertIn("version_matrix", response)
        self.assertIn("agents", response)
        self.assertIn("learning_health", response)

if __name__ == '__main__':
    unittest.main()
