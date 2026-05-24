from sentinel.guard import SentinelGuard
from sentinel.ingestion import VectorIngestionEngine
import os

def main():
    # Configuration and Initialization
    guard = SentinelGuard('config.json')

    # Mock DB Config (In production, these would come from env vars)
    db_config = {
        "host": os.getenv("DB_HOST", "localhost"),
        "database": os.getenv("DB_NAME", "sentinel_db"),
        "user": os.getenv("DB_USER", "postgres"),
        "password": os.getenv("DB_PASS", "postgres")
    }

    engine = VectorIngestionEngine(db_config)

    # Example payloads
    payloads = [
        {"vector": [0.1, 0.2, 0.3], "drift": 0.02, "latency": 150},
        {"vector": [0.4, 0.5, 0.6], "drift": 0.01, "latency": 200}
    ]

    # 1. Guard Evaluation
    if guard.evaluate_batch_telemetry(payloads):
        print("Telemetry check passed. Proceeding with ingestion.")

        # 2. Vector Ingestion
        if engine.stage_vector_payloads(payloads):
            print("Batch successfully staged in temporary table.")
        else:
            print("Ingestion failed.")
    else:
        print("Telemetry check failed. Batch rejected.")

if __name__ == "__main__":
    main()
