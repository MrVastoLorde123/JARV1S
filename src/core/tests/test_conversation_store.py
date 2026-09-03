import sqlite3
import tempfile
import unittest
from pathlib import Path

from src import database

from src.core.conversation import (
    ConversationState,
)

from src.core.conversation_models import (
    ASSISTANT,
    USER,
)

from src.core.conversation_store import (
    ConversationStore,
)


def create_test_schema(
    database_path,
):
    connection = sqlite3.connect(
        database_path
    )

    connection.execute(
        "PRAGMA foreign_keys = ON"
    )

    cursor = connection.cursor()

    cursor.execute(
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

    cursor.execute(
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
            ON DELETE CASCADE
        )
        """
    )

    connection.commit()
    connection.close()


class ConversationStoreTests(
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
            / "test_conversation.db"
        )

        database.set_database_path(
            self.database_path
        )

        create_test_schema(
            self.database_path
        )

        self.store = (
            ConversationStore()
        )

    def tearDown(
        self,
    ):

        database.set_database_path(
            self.original_database_path
        )

        self.temp_directory.cleanup()

    def test_conversation_can_be_created(
        self,
    ):

        record = (
            self.store
            .create_conversation(
                title="Test Conversation"
            )
        )

        self.assertTrue(
            record.conversation_id
        )

        self.assertEqual(
            record.title,
            "Test Conversation"
        )

    def test_created_conversation_exists(
        self,
    ):

        record = (
            self.store
            .create_conversation()
        )

        self.assertTrue(
            self.store
            .conversation_exists(
                record.conversation_id
            )
        )

    def test_conversation_can_be_retrieved(
        self,
    ):

        record = (
            self.store
            .create_conversation(
                title="Persistent Test"
            )
        )

        loaded = (
            self.store
            .get_conversation(
                record.conversation_id
            )
        )

        self.assertIsNotNone(
            loaded
        )

        self.assertEqual(
            loaded.title,
            "Persistent Test"
        )

    def test_message_can_be_persisted(
        self,
    ):

        record = (
            self.store
            .create_conversation()
        )

        message = (
            self.store
            .append_message(
                conversation_id=(
                    record.conversation_id
                ),
                role=USER,
                content="Hello JARVIS.",
            )
        )

        self.assertTrue(
            message["message_id"]
        )

    def test_messages_preserve_order(
        self,
    ):

        record = (
            self.store
            .create_conversation()
        )

        first = (
            self.store
            .append_message(
                record.conversation_id,
                USER,
                "Hello.",
            )
        )

        second = (
            self.store
            .append_message(
                record.conversation_id,
                ASSISTANT,
                "Hello.",
                parent_id=(
                    first["message_id"]
                ),
            )
        )

        rows = (
            self.store
            .get_messages(
                record.conversation_id
            )
        )

        self.assertEqual(
            len(rows),
            2,
        )

        self.assertEqual(
            rows[0][0],
            first["message_id"],
        )

        self.assertEqual(
            rows[1][0],
            second["message_id"],
        )

        self.assertEqual(
            rows[1][5],
            first["message_id"],
        )

    def test_state_can_be_saved(
            self,
    ):
        record = (
            self.store
            .create_conversation()
        )

        state = ConversationState(
            conversation_id=(
                record.conversation_id
            )
        )

        state.set_topic(
            "JARVIS development"
        )

        state.set_task(
            "Build persistent conversations"
        )

        stored_message = (
            self.store
            .append_message(
                conversation_id=(
                    record.conversation_id
                ),
                role=USER,
                content="Let's persist this.",
            )
        )

        state.add_turn(
            USER,
            "Let's persist this.",
        )

        self.store.save_state(
            state.snapshot()
        )

        restored = (
            self.store
            .load_state(
                record.conversation_id
            )
        )

        self.assertIsNotNone(
            restored
        )

        self.assertEqual(
            restored.active_topic,
            "JARVIS development"
        )

        self.assertEqual(
            restored.active_task,
            "Build persistent conversations"
        )

        turns = (
            restored
            .get_recent_turns()
        )

        self.assertEqual(
            len(turns),
            1
        )

        self.assertEqual(
            turns[0].content,
            "Let's persist this."
        )

        self.assertEqual(
            turns[0].role,
            USER
        )

        persisted_rows = (
            self.store
            .get_messages(
                record.conversation_id
            )
        )

        self.assertEqual(
            len(persisted_rows),
            1
        )

        self.assertEqual(
            persisted_rows[0][0],
            stored_message["message_id"]
        )

    def test_conversation_can_be_rehydrated(
        self,
    ):

        record = (
            self.store
            .create_conversation()
        )

        self.store.append_message(
            record.conversation_id,
            USER,
            "First turn.",
        )

        self.store.append_message(
            record.conversation_id,
            ASSISTANT,
            "First response.",
        )

        self.store.append_message(
            record.conversation_id,
            USER,
            "Second turn.",
        )

        restored = (
            self.store
            .load_state(
                record.conversation_id
            )
        )

        turns = (
            restored
            .get_recent_turns()
        )

        self.assertEqual(
            len(turns),
            3,
        )

        self.assertEqual(
            turns[0].role,
            USER,
        )

        self.assertEqual(
            turns[1].role,
            ASSISTANT,
        )

        self.assertEqual(
            turns[2].role,
            USER,
        )

    def test_nonexistent_conversation_returns_none(
        self,
    ):

        state = (
            self.store
            .load_state(
                "does-not-exist"
            )
        )

        self.assertIsNone(
            state
        )

    def test_invalid_role_is_rejected(
        self,
    ):

        record = (
            self.store
            .create_conversation()
        )

        with self.assertRaises(
            ValueError
        ):

            self.store.append_message(
                record.conversation_id,
                "tool",
                "Not supported yet.",
            )

    def test_empty_message_is_rejected(
        self,
    ):

        record = (
            self.store
            .create_conversation()
        )

        with self.assertRaises(
            ValueError
        ):

            self.store.append_message(
                record.conversation_id,
                USER,
                "   ",
            )

    def test_missing_conversation_is_rejected(
        self,
    ):

        with self.assertRaises(
            ValueError
        ):

            self.store.append_message(
                "missing",
                USER,
                "Hello.",
            )


if __name__ == "__main__":
    unittest.main(
        verbosity=2
    )
