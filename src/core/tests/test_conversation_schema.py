import sqlite3
import tempfile
import unittest
from pathlib import Path

from src import database

from src.core.conversation_store import (
    ConversationStore,
)


class ConversationSchemaTests(
    unittest.TestCase
):

    def setUp(
        self,
    ):

        self.original_database_path = (
            database.DATABASE_PATH
        )

        self.temp_directory = (
            tempfile.TemporaryDirectory()
        )

        self.database_path = (
            Path(
                self.temp_directory.name
            )
            / "test_schema.db"
        )

        database.set_database_path(
            self.database_path
        )

        connection = sqlite3.connect(
            self.database_path
        )

        connection.execute(
            "PRAGMA foreign_keys = ON"
        )

        connection.execute(
            """
            CREATE TABLE conversations (
                id TEXT PRIMARY KEY,
                title TEXT,
                created_at REAL,
                updated_at REAL,
                is_archived INTEGER,
                is_starred INTEGER
            )
            """
        )

        connection.execute(
            """
            CREATE TABLE messages (
                id TEXT PRIMARY KEY,
                conversation_id TEXT NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                created_at REAL,
                parent_id TEXT,

                FOREIGN KEY (
                    conversation_id
                )
                REFERENCES conversations(id)
            )
            """
        )

        connection.commit()
        connection.close()

    def tearDown(
        self,
    ):

        database.set_database_path(
            self.original_database_path
        )

        self.temp_directory.cleanup()

    def test_conversation_state_table_is_created(
        self,
    ):

        ConversationStore()

        connection = sqlite3.connect(
            self.database_path
        )

        row = connection.execute(
            """
            SELECT name
            FROM sqlite_master
            WHERE type = 'table'
              AND name = 'conversation_state'
            """
        ).fetchone()

        connection.close()

        self.assertIsNotNone(
            row
        )

    def test_initialization_tolerates_missing_messages_table(self):
        connection = sqlite3.connect(
            self.database_path
        )

        connection.execute(
            "DROP TABLE messages"
        )
        connection.commit()
        connection.close()

        ConversationStore()

        connection = sqlite3.connect(
            self.database_path
        )

        state_row = connection.execute(
            """
            SELECT name
            FROM sqlite_master
            WHERE type = 'table'
              AND name = 'conversation_state'
            """
        ).fetchone()

        index_row = connection.execute(
            """
            SELECT name
            FROM sqlite_master
            WHERE type = 'index'
              AND name = 'idx_messages_conversation_created'
            """
        ).fetchone()

        connection.close()

        self.assertIsNotNone(
            state_row
        )
        self.assertIsNone(
            index_row
        )


if __name__ == "__main__":
    unittest.main(
        verbosity=2
    )
