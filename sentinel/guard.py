import os
import json
from pydantic import BaseModel, Field, field_validator

class AdvancedGuardMetrics(BaseModel):
    drift: float = Field(..., ge=0.0, le=1.0)
    confidence: float = Field(..., ge=0.0, le=1.0)
    latency_ms: float = Field(..., gt=0.0)
    tokens_per_second: float = Field(..., gt=0.0)
    context_utilization: float = Field(..., ge=0.0, le=1.0)

    @field_validator('tokens_per_second')
    @classmethod
    def verify_generation_efficiency(cls, v):
        if v < 5.0:
            raise ValueError("Degraded throughput: Generation speeds falling below 5 TPS token boundary.")
        return v

def evaluate_inference_payload(payload_dict):
    return AdvancedGuardMetrics(**payload_dict)
