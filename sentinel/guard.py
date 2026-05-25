import os
import json
from functools import lru_cache
from pydantic import BaseModel, Field, field_validator, model_validator, AliasChoices

@lru_cache(maxsize=1)
def load_config():
    config_path = os.path.join(os.path.dirname(__file__), '..', 'config.json')
    try:
        with open(config_path, 'r') as f:
            return json.load(f)
    except Exception:
        return {}

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

class ProductCarbonFootprintISO14067(BaseModel):
    model_config = {"frozen": True}

    raw_material_kg: float = Field(..., ge=0.0)
    production_processing_kwh: float = Field(..., ge=0.0)
    distribution_transport_km: float = Field(..., ge=0.0)
    end_of_life_disposal_kg: float = Field(..., ge=0.0)

    @model_validator(mode='before')
    @classmethod
    def check_missing_fields(cls, data):
        required_fields = ['raw_material_kg', 'production_processing_kwh', 'distribution_transport_km', 'end_of_life_disposal_kg']
        for field in required_fields:
            if field not in data:
                raise ValueError(f"AUDIT COMPLIANCE BREACH: Missing mandatory field '{field}'")
        return data

    def get_total_pcf_co2e(self) -> float:
        config = load_config()
        factors = config.get("emission_factors", {})

        total = (
            self.raw_material_kg * factors.get("raw_material_kg_co2e_per_kg", 0.0) +
            self.production_processing_kwh * factors.get("electricity_kg_co2e_per_kwh", 0.0) +
            self.distribution_transport_km * factors.get("transport_kg_co2e_per_km", 0.0) +
            self.end_of_life_disposal_kg * factors.get("disposal_kg_co2e_per_kg", 0.0)
        )
        return total

class OrganizationalGHGISO14064(BaseModel):
    model_config = {"frozen": True}

    scope1_direct_combustion_liters: float = Field(..., ge=0.0)
    scope2_indirect_electricity_kwh: float = Field(..., ge=0.0)
    scope3_value_chain_emissions_co2e: float = Field(..., ge=0.0)

    @model_validator(mode='before')
    @classmethod
    def check_missing_fields(cls, data):
        required_fields = ['scope1_direct_combustion_liters', 'scope2_indirect_electricity_kwh', 'scope3_value_chain_emissions_co2e']
        for field in required_fields:
            if field not in data:
                raise ValueError(f"AUDIT COMPLIANCE BREACH: Missing mandatory field '{field}'")
        return data

    @model_validator(mode='after')
    def verify_organizational_ceiling(self) -> 'OrganizationalGHGISO14064':
        config = load_config()
        factors = config.get("emission_factors", {})
        ceiling = config.get("org_carbon_ceiling_kg_co2e", float('inf'))

        total_emissions = (
            self.scope1_direct_combustion_liters * factors.get("diesel_fuel_kg_co2e_per_liter", 0.0) +
            self.scope2_indirect_electricity_kwh * factors.get("electricity_kg_co2e_per_kwh", 0.0) +
            self.scope3_value_chain_emissions_co2e
        )

        if total_emissions > ceiling:
            raise ValueError(f"AUDIT COMPLIANCE BREACH: Total organizational emissions ({total_emissions:.2f}) exceed the environmental carbon ceiling of {ceiling} kg CO2e")

        return self

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
