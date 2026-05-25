import unittest
import os
from pydantic import ValidationError
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
            "latency": 45.0,
            "tokens_per_second": 25.0,
            "context_utilization": 0.4
        }
        self.assertTrue(self.guard.evaluate_payload(payload))

    def test_drift_violation_raises_error_or_returns_false(self):
        """
        Validates that a telemetry payload where drift exceeds drift_limit returns False.
        """
        payload = {
            "drift": 0.30,  # config limit: 0.25
            "confidence": 0.90,
            "latency": 45.0,
            "tokens_per_second": 25.0,
            "context_utilization": 0.4
        }
        self.assertFalse(self.guard.evaluate_payload(payload))

    def test_latency_violation_fails_sla(self):
        """
        Validates that a telemetry payload where latency violates latency_limit_ms returns False.
        """
        payload = {
            "drift": 0.15,
            "confidence": 0.90,
            "latency": 120.0,  # config limit: 100.0 ms
            "tokens_per_second": 25.0,
            "context_utilization": 0.4
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
                "latency": 45.0,
                "tokens_per_second": 25.0,
                "context_utilization": 0.4
            })

        # Constraint 3: Non-numeric value type for 'latency' (string instead of float/int)
        with self.assertRaises(ValueError):
            self.guard.evaluate_payload({
                "drift": 0.15,
                "confidence": 0.90,
                "latency": "fast",
                "tokens_per_second": 25.0,
                "context_utilization": 0.4
            })

        # Constraint 4: Out of range confidence value (e.g. 1.5)
        with self.assertRaises(ValueError):
            self.guard.evaluate_payload({
                "drift": 0.15,
                "confidence": 1.5,
                "latency": 45.0,
                "tokens_per_second": 25.0,
                "context_utilization": 0.4
            })

    def test_carbon_footprint_calculation(self):
        """
        Verifies that the math processing functions scale correctly for GHG metrics.
        100L fuel (2.31 kg/L) + 100kWh (0.35 kg/kWh) = 231 + 35 = 266.0 kg CO2e.
        """
        from sentinel.guard import EnvironmentalTelemetryGuard
        metrics = EnvironmentalTelemetryGuard(scope1_fuel_liters=100.0, scope2_kwh=100.0)
        self.assertAlmostEqual(metrics.calculate_total_co2e, 266.0)

    def test_carbon_footprint_overage_breach(self):
        """
        Asserts that greenhouse gas emission overages (> 500.0 kg CO2e) break the Pydantic guard gate.
        200L fuel (462 kg) + 200kWh (70 kg) = 532 kg CO2e.
        """
        from sentinel.guard import EnvironmentalTelemetryGuard
        with self.assertRaises(ValidationError) as cm:
            EnvironmentalTelemetryGuard(scope1_fuel_liters=200.0, scope2_kwh=200.0)
        self.assertIn("CRITICAL ENVIRONMENTAL BREACH", str(cm.exception))
