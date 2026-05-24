import unittest
from unittest.mock import patch, MagicMock, call
from sentinel.ingestion import VectorIngestionEngine
import json

class TestVectorIngestionEngine(unittest.TestCase):
    def setUp(self):
        self.db_config = {"host": "test_host"}
        self.engine = VectorIngestionEngine(self.db_config)

    @patch('psycopg2.connect')
    def test_stage_vector_payloads_success(self, mock_connect):
        # Setup mock
        mock_conn = MagicMock()
        mock_connect.return_value = mock_conn
        mock_cur = MagicMock()
        mock_conn.cursor.return_value.__enter__.return_value = mock_cur

        payloads = [
            {"vector": [0.1, 0.2], "drift": 0.02, "latency": 100.0}
        ]

        result = self.engine.stage_vector_payloads(payloads)

        self.assertTrue(result)

        # Verify temporary table creation logic
        mock_cur.execute.assert_called_once()
        sql_call = mock_cur.execute.call_args[0][0]
        self.assertIn("CREATE TEMPORARY TABLE temp_staging_vectors", sql_call)
        self.assertIn("ON COMMIT DROP", sql_call)

        # Verify bulk insert integrity
        mock_cur.executemany.assert_called_once()
        query, data = mock_cur.executemany.call_args[0]
        self.assertIn("INSERT INTO temp_staging_vectors", query)
        self.assertEqual(data[0][0], json.dumps([0.1, 0.2]))
        self.assertEqual(data[0][1], 0.02)
        self.assertEqual(data[0][2], 100.0)

    @patch('psycopg2.connect')
    def test_stage_vector_payloads_failure(self, mock_connect):
        mock_connect.side_effect = Exception("DB Connection Error")
        payloads = [{"vector": [0.1], "drift": 0.0, "latency": 0.0}]
        result = self.engine.stage_vector_payloads(payloads)
        self.assertFalse(result)

if __name__ == '__main__':
    unittest.main()
