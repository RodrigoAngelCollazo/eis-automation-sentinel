# Sentinel Framework Requirements

1. config.json:
   - max_allowed_drift: 0.05
   - latency_sla_ms: 450

2. sentinel/guard.py:
   - Class: SentinelGuard
   - Method: evaluate_batch_telemetry(payloads)
   - Validation: {"vector", "drift", "latency"}
   - Thresholds: drift > 0.05 or latency > 450ms -> Fail

3. sentinel/ingestion.py & main.py:
   - Class: VectorIngestionEngine
   - Method: stage_vector_payloads(payloads)
   - DB: psycopg2
   - Pattern: CREATE TEMPORARY TABLE temp_staging_vectors (...) ON COMMIT DROP;
   - Bulk Insert: cursor.executemany

4. tests/:
   - tests/test_guard.py
   - tests/test_ingestion.py
   - Use unittest.mock.patch for psycopg2

5. .github/workflows/ci-cd.yml:
   - Name: Sentinel CI Automation Loop
   - Env: Python 3.11 (Note: local is 3.12, but user requested 3.11 for CI)
   - Steps: Setup, Install (pytest, pytest-cov, pydantic, psycopg2-binary), JSON Validate, Pytest
