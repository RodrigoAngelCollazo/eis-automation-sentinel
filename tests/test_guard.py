import unittest
from sentinel.guard import SentinelGuard

class TestSentinelGuard(unittest.TestCase):
    def setUp(self):
        self.guard = SentinelGuard('config.json')

    def test_nominal_path(self):
        payloads = [
            {"vector": [0.1, 0.2], "drift": 0.02, "latency": 100}
        ]
        self.assertTrue(self.guard.evaluate_batch_telemetry(payloads))

    def test_threshold_breach_drift(self):
        payloads = [
            {"vector": [0.1, 0.2], "drift": 0.06, "latency": 100}
        ]
        self.assertFalse(self.guard.evaluate_batch_telemetry(payloads))

    def test_threshold_breach_latency(self):
        payloads = [
            {"vector": [0.1, 0.2], "drift": 0.01, "latency": 500}
        ]
        self.assertFalse(self.guard.evaluate_batch_telemetry(payloads))

    def test_missing_keys(self):
        payloads = [
            {"vector": [0.1, 0.2], "drift": 0.01}
        ]
        self.assertFalse(self.guard.evaluate_batch_telemetry(payloads))

    def test_empty_batch(self):
        self.assertTrue(self.guard.evaluate_batch_telemetry([]))

if __name__ == '__main__':
    unittest.main()
