import sqlite3
import unittest

from src import database


class DatabaseTests(unittest.TestCase):

    def test_connection_can_be_created(self):

        connection = database.get_connection()

        self.assertIsInstance(
            connection,
            sqlite3.Connection
        )

        connection.close()

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