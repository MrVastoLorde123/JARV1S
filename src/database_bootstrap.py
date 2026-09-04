import sqlite3

from src.database import get_connection


def bootstrap_database():
    """
    Ensure the local JARVIS database has the base persistence schema.

    This is intentionally idempotent so local startup can safely run it
    against both a fresh database and an already-initialized database.
    """

    connection = get_connection()

    try:
        cursor = connection.cursor()

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS conversations (
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
            CREATE TABLE IF NOT EXISTS messages (
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

        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS
            idx_messages_conversation_created
            ON messages(
                conversation_id,
                created_at
            )
            """
        )

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

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS memories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content TEXT NOT NULL,
                category TEXT NOT NULL,
                source_conversation_id TEXT,
                confidence REAL NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                memory_key TEXT,
                importance REAL NOT NULL DEFAULT 0.5,
                status TEXT NOT NULL DEFAULT 'ACTIVE',

                FOREIGN KEY (source_conversation_id)
                    REFERENCES conversations(id)
                    ON DELETE SET NULL
            )
            """
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS memory_evidence (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                memory_id INTEGER NOT NULL,
                conversation_id TEXT,
                message_id TEXT,
                evidence_text TEXT NOT NULL,
                evidence_type TEXT,
                confidence REAL,
                source_created_at TEXT,
                created_at TEXT NOT NULL,

                FOREIGN KEY (memory_id)
                    REFERENCES memories(id)
                    ON DELETE CASCADE,
                FOREIGN KEY (conversation_id)
                    REFERENCES conversations(id)
                    ON DELETE SET NULL,
                FOREIGN KEY (message_id)
                    REFERENCES messages(id)
                    ON DELETE SET NULL
            )
            """
        )

        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS
            idx_memory_evidence_memory_created
            ON memory_evidence(
                memory_id,
                created_at
            )
            """
        )

        connection.commit()

    except sqlite3.Error:
        connection.rollback()
        raise

    finally:
        connection.close()


if __name__ == "__main__":
    bootstrap_database()
    print("JARVIS database bootstrap complete.")
