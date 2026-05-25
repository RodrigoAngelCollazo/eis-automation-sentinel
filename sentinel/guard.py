import os
import json
from pydantic import BaseModel, Field, field_validator, model_validator, AliasChoices

class AdvancedGuardMetrics(BaseModel):
    drift: float = Field(..., ge=0.0, le=1.0)
    confidence: float = Field(..., ge=0.0, le=1.0)
    latency_ms: float = Field(..., validation_alias=AliasChoices('latency_ms', 'latency'), gt=0.0)
    tokens_per_second: float = Field(..., gt=0.0)
    context_utilization: float = Field(..., ge=0.0, le=1.0)

    @field_validator('tokens_per_second')
    @classmethod
    def verify_generation_efficiency(cls, v):
        if v < 5.0:
            raise ValueError("Degraded throughput: Generation speeds falling below 5 TPS token boundary.")
        return v

class EnvironmentalTelemetryGuard(BaseModel):
    scope1_fuel_liters: float = Field(..., ge=0.0, description="Direct stationary combustion fuel volume")
    scope2_kwh: float = Field(..., ge=0.0, description="Purchased electricity usage from local grid")

    @property
    def calculate_total_co2e(self) -> float:
        # 2.31 kg CO2 per liter of fuel and 0.35 kg CO2 per kWh
        return (self.scope1_fuel_liters * 2.31) + (self.scope2_kwh * 0.35)

    @model_validator(mode='after')
    def verify_carbon_intensity(self) -> 'EnvironmentalTelemetryGuard':
        if self.calculate_total_co2e > 500.0:
            raise ValueError("CRITICAL ENVIRONMENTAL BREACH: Total carbon intensity index exceeds 500.0 kg CO2e threshold")
        return self

class SentinelGuard:
    def __init__(self, config_path: str):
        with open(config_path, 'r') as f:
            self.config = json.load(f)

    def evaluate_payload(self, payload: dict) -> bool:
        if not isinstance(payload, dict):
            raise ValueError("Payload must be a dictionary")

        try:
            metrics = AdvancedGuardMetrics(**payload)
        except Exception as e:
            raise ValueError(f"Schema validation failed: {e}")

        # Check thresholds
        if metrics.drift > self.config.get("drift_limit", 1.0):
            return False
        if metrics.confidence < self.config.get("confidence_threshold", 0.0):
            return False
        if metrics.latency_ms > self.config.get("latency_limit_ms", float('inf')):
            return False

        return True

def evaluate_inference_payload(payload_dict):
    return AdvancedGuardMetrics(**payload_dict)
