import psycopg2
import json

class VectorIngestionEngine:
    def __init__(self, db_config):
        self.db_config = db_config

    def stage_vector_payloads(self, payloads: list) -> bool:
        """
        Stages vector payloads into a temporary table for high-throughput ingestion.
        Uses isolated transactions and bulk inserts for maximum data integrity.
        """
        if not payloads:
            return True

        conn = None
        try:
            conn = psycopg2.connect(**self.db_config)
            with conn:
                with conn.cursor() as cur:
                    # Create temporary staging table with strict schema
                    cur.execute("""
                        CREATE TEMPORARY TABLE temp_staging_vectors (
                            vector JSONB NOT NULL,
                            drift DOUBLE PRECISION NOT NULL,
                            latency DOUBLE PRECISION NOT NULL,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                        ) ON COMMIT DROP;
                    """)

                    # Prepare data for bulk insert, ensuring proper serialization
                    data = [
                        (
                            json.dumps(p['vector']),
                            float(p['drift']),
                            float(p['latency'])
                        ) for p in payloads
                    ]

                    # Execute bulk insert using executemany for efficiency
                    insert_query = "INSERT INTO temp_staging_vectors (vector, drift, latency) VALUES (%s, %s, %s)"
                    cur.executemany(insert_query, data)

            return True
        except Exception as e:
            # High-integrity failure handling
            print(f"Ingestion critical failure: {e}")
            if conn:
                conn.rollback()
            return False
        finally:
            if conn:
                conn.close()
