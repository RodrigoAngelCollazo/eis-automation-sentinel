import json
from pydantic import BaseModel, Field, ValidationError
from typing import List

class TelemetryPayload(BaseModel):
    vector: List[float]
    drift: float
    latency: float

class SentinelGuard:
    def __init__(self, config_path='config.json'):
        try:
            with open(config_path, 'r') as f:
                self.config = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            self.config = {}

        self.max_allowed_drift = self.config.get('max_allowed_drift', 0.05)
        self.latency_sla_ms = self.config.get('latency_sla_ms', 450)

    def evaluate_batch_telemetry(self, payloads: list) -> bool:
        """
        Evaluates a batch of telemetry payloads using Pydantic for high-integrity validation.
        Enforces drift and latency thresholds.
        """
        if not payloads:
            return True

        for payload_dict in payloads:
            try:
                # High-integrity schema validation
                payload = TelemetryPayload(**payload_dict)

                # Threshold enforcement
                if payload.drift > self.max_allowed_drift:
                    return False

                if payload.latency > self.latency_sla_ms:
                    return False

            except (ValidationError, TypeError, KeyError):
                # Intercept and fail if schema is violated or keys are missing
                return False

        return True
