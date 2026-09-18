import os
import sqlite3
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from src import database


class DatabaseTests(unittest.TestCase):

    def test_connection_can_be_created(self):

        connection = database.get_connection()

        self.assertIsInstance(
            connection,
            sqlite3.Connection
        )

        connection.close()

    def test_configured_data_directory_controls_default_database_path(self):
        original_database_path = database.DATABASE_PATH
        temp_directory = tempfile.TemporaryDirectory()
        try:
            database.set_database_path(database.DEFAULT_DATABASE_PATH)
            with patch.dict(
                os.environ,
                {"JARVIS_DATA_DIR": temp_directory.name},
                clear=False,
            ):
                expected = (
                    Path(temp_directory.name)
                    / "processed"
                    / "jarvis.db"
                )
                self.assertEqual(database.get_database_path(), expected)
                connection = database.get_connection()
                connection.execute("SELECT 1")
                connection.close()
                self.assertTrue(expected.exists())
        finally:
            database.set_database_path(original_database_path)
            temp_directory.cleanup()

    def test_foreign_keys_are_enabled(self):

        connection = database.get_connection()

        foreign_keys = connection.execute(
            "PRAGMA foreign_keys"
        ).fetchone()[0]

        connection.close()

        self.assertEqual(
            foreign_keys,
            1
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)