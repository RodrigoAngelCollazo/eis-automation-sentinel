import os
import json

class SentinelGuard:
    """
    SentinelGuard enforces high-integrity data governance on incoming
    inference pipeline telemetry by checking parameters against configurable bounds.
    """
    def __init__(self, config_path=None):
        if config_path is None:
            # Attempt to resolve configuration file path relative to current working directory,
            # or fallback to package root directory relative to this file.
            if os.path.exists("config.json"):
                config_path = "config.json"
            else:
                dir_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                potential_path = os.path.join(dir_path, "config.json")
                if os.path.exists(potential_path):
                    config_path = potential_path
                else:
                    raise FileNotFoundError("Could not locate config.json default path.")
        
        with open(config_path, 'r') as f:
            self.config = json.load(f)
            
        self.drift_limit = self.config.get("drift_limit")
        self.confidence_threshold = self.config.get("confidence_threshold")
        self.latency_limit_ms = self.config.get("latency_limit_ms")
        
        # Verify the loaded config contains correct fields
        required_keys = ["drift_limit", "confidence_threshold", "latency_limit_ms"]
        for key in required_keys:
            if key not in self.config:
                raise ValueError(f"Missing required configuration key: {key}")
                
    def evaluate_payload(self, telemetry: dict) -> bool:
        """
        Evaluates a telemetry payload against the loaded configuration limits.
        
        Args:
            telemetry (dict): Telemetry data containing 'drift', 'confidence', and 'latency'.
            
        Returns:
            bool: True if payload is within limits, False otherwise.
            
        Raises:
            ValueError: If payload is malformed or violates fundamental schema constraints.
        """
        # Constraint 1: Payload type check (must be a dictionary)
        if not isinstance(telemetry, dict):
            raise ValueError("Telemetry payload must be a dictionary.")
            
        # Constraint 2: Key presence check (must contain all required keys)
        required_keys = ["drift", "confidence", "latency"]
        for key in required_keys:
            if key not in telemetry:
                raise ValueError(f"Missing required telemetry key: '{key}'")
                
        # Constraint 3: Value type check (must be numeric, and not bool which is a subclass of int)
        for key in required_keys:
            val = telemetry[key]
            if not isinstance(val, (int, float)) or isinstance(val, bool):
                raise ValueError(f"Telemetry key '{key}' must be numeric, got {type(val).__name__}.")
                
        # Constraint 4: Schema-level value range constraints
        confidence = telemetry["confidence"]
        if not (0.0 <= confidence <= 1.0):
            raise ValueError(f"Telemetry key 'confidence' must be between 0.0 and 1.0, got {confidence}.")
            
        drift = telemetry["drift"]
        latency = telemetry["latency"]
        
        if latency < 0:
            raise ValueError(f"Telemetry key 'latency' must be non-negative, got {latency}.")
            
        # Validate against configuration limits
        if drift > self.drift_limit:
            return False
            
        if confidence < self.confidence_threshold:
            return False
            
        if latency > self.latency_limit_ms:
            return False
            
        return True
