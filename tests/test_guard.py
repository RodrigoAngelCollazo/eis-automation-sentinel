import unittest
import os
from sentinel.guard import SentinelGuard

class TestSentinelGuard(unittest.TestCase):
    def setUp(self):
        # Resolve path to the default config.json
        dir_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.config_path = os.path.join(dir_path, "config.json")
        self.guard = SentinelGuard(self.config_path)

    def test_payload_within_bounds_passes(self):
        """
        Validates that a telemetry payload where all metrics are within bounds
        (drift <= 0.25, confidence >= 0.80, latency <= 100.0) successfully evaluates to True.
        """
        payload = {
            "drift": 0.15,
            "confidence": 0.90,
            "latency": 45.0
        }
        self.assertTrue(self.guard.evaluate_payload(payload))

    def test_drift_violation_raises_error_or_returns_false(self):
        """
        Validates that a telemetry payload where drift exceeds drift_limit returns False.
        """
        payload = {
            "drift": 0.30,  # config limit: 0.25
            "confidence": 0.90,
            "latency": 45.0
        }
        self.assertFalse(self.guard.evaluate_payload(payload))

    def test_latency_violation_fails_sla(self):
        """
        Validates that a telemetry payload where latency violates latency_limit_ms returns False.
        """
        payload = {
            "drift": 0.15,
            "confidence": 0.90,
            "latency": 120.0  # config limit: 100.0 ms
        }
        self.assertFalse(self.guard.evaluate_payload(payload))

    def test_malformed_payload_schema_interception(self):
        """
        Validates that malformed telemetry payloads trigger schema validation exceptions (ValueError).
        Checks the 4 core schema constraints:
        1. Non-dictionary input payload.
        2. Missing required keys.
        3. Non-numeric value types.
        4. Values violating fundamental physical range requirements (e.g. confidence outside [0, 1]).
        """
        # Constraint 1: Non-dictionary payload
        with self.assertRaises(ValueError):
            self.guard.evaluate_payload("not-a-dict")

        # Constraint 2: Missing key 'confidence'
        with self.assertRaises(ValueError):
            self.guard.evaluate_payload({
                "drift": 0.15,
                "latency": 45.0
            })

        # Constraint 3: Non-numeric value type for 'latency' (string instead of float/int)
        with self.assertRaises(ValueError):
            self.guard.evaluate_payload({
                "drift": 0.15,
                "confidence": 0.90,
                "latency": "fast"
            })

        # Constraint 4: Out of range confidence value (e.g. 1.5)
        with self.assertRaises(ValueError):
            self.guard.evaluate_payload({
                "drift": 0.15,
                "confidence": 1.5,
                "latency": 45.0
            })
