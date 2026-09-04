import sqlite3
import tempfile
import unittest
from pathlib import Path

from src import database
from src.database_bootstrap import bootstrap_database


class DatabaseBootstrapTests(unittest.TestCase):

    def setUp(self):
        self.original_database_path = database.DATABASE_PATH
        self.temp_directory = tempfile.TemporaryDirectory()
        self.database_path = Path(self.temp_directory.name) / "bootstrap.db"
        database.set_database_path(self.database_path)

    def tearDown(self):
        database.set_database_path(self.original_database_path)
        self.temp_directory.cleanup()

    def test_fresh_database_gets_runtime_tables(self):
        bootstrap_database()

        connection = sqlite3.connect(self.database_path)
        try:
            rows = connection.execute(
                """
                SELECT name
                FROM sqlite_master
                WHERE type = 'table'
                  AND name IN (
                      'conversations',
                      'messages',
                      'conversation_state',
                      'memories',
                      'memory_evidence'
                  )
                ORDER BY name
                """
            ).fetchall()
        finally:
            connection.close()

        self.assertEqual(
            [row[0] for row in rows],
            [
                "conversation_state",
                "conversations",
                "memories",
                "memory_evidence",
                "messages",
            ],
        )

    def test_bootstrap_is_idempotent(self):
        bootstrap_database()
        bootstrap_database()

        connection = sqlite3.connect(self.database_path)
        try:
            for table_name in (
                "conversations",
                "messages",
                "conversation_state",
                "memories",
                "memory_evidence",
            ):
                row = connection.execute(
                    """
                    SELECT name
                    FROM sqlite_master
                    WHERE type = 'table'
                      AND name = ?
                    """,
                    (table_name,),
                ).fetchone()
                self.assertIsNotNone(row)
        finally:
            connection.close()


if __name__ == "__main__":
    unittest.main(verbosity=2)
