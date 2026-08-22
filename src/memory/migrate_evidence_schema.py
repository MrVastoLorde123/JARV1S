import sqlite3
from pathlib import Path


DATABASE_PATH = Path("data/processed/jarvis.db")


def migrate():

    connection = sqlite3.connect(DATABASE_PATH)

    connection.execute("PRAGMA foreign_keys = ON")

    cursor = connection.cursor()

    print("=" * 60)
    print("JARVIS EVIDENCE SCHEMA MIGRATION")
    print("=" * 60)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS memory_evidence (
            id INTEGER PRIMARY KEY AUTOINCREMENT,

            memory_id INTEGER NOT NULL,

            conversation_id TEXT,
            message_id TEXT,

            evidence_text TEXT NOT NULL,

            evidence_type TEXT NOT NULL,

            confidence REAL NOT NULL,

            source_created_at TEXT,

            created_at TEXT NOT NULL,

            FOREIGN KEY (memory_id)
                REFERENCES memories(id),

            FOREIGN KEY (conversation_id)
                REFERENCES conversations(id)
        )
    """)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS
        idx_memory_evidence_memory_id
        ON memory_evidence(memory_id)
    """)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS
        idx_memory_evidence_conversation_id
        ON memory_evidence(conversation_id)
    """)

    connection.commit()

    print()
    print("Evidence table ready.")

    print()
    print("Indexes created:")
    print("  - idx_memory_evidence_memory_id")
    print("  - idx_memory_evidence_conversation_id")

    connection.close()

    print()
    print("Migration complete.")


if __name__ == "__main__":
    migrate()