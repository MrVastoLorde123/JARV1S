import sqlite3

from src.database import get_connection


def migrate():
    """
    Create the persistent conversation-state table.

    This migration is intentionally idempotent.
    """

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS conversation_state (
            conversation_id TEXT PRIMARY KEY,

            active_topic TEXT,
            active_task TEXT,

            metadata TEXT NOT NULL
                DEFAULT '{}',

            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,

            FOREIGN KEY (
                conversation_id
            )
            REFERENCES conversations(id)
            ON DELETE CASCADE
        )
        """
    )

    cursor.execute(
        """
        CREATE INDEX IF NOT EXISTS
        idx_conversation_state_updated_at
        ON conversation_state(updated_at)
        """
    )

    connection.commit()
    connection.close()

    print("Conversation state table ready.")


if __name__ == "__main__":

    print("=" * 60)
    print("JARVIS CONVERSATION STATE MIGRATION")
    print("=" * 60)

    migrate()

    print()
    print("Migration complete.")