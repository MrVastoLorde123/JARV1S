import sqlite3
from pathlib import Path
from datetime import datetime

from memory_validator import validate_memory


DATABASE_PATH = Path("data/processed/jarvis.db")


def create_memory_table():
    connection = sqlite3.connect(DATABASE_PATH)
    cursor = connection.cursor()

    cursor.execute("""
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
        )
    """)

    connection.commit()
    connection.close()

    print("Memory table ready.")


def add_memory(
    content,
    category,
    memory_key,
    source_conversation_id=None,
    confidence=1.0,
    importance=0.5,
    status="ACTIVE"
):

    memory = {
        "content": content,
        "category": category,
        "memory_key": memory_key,
        "source_conversation_id": source_conversation_id,
        "confidence": confidence,
        "importance": importance,
        "status": status,
    }

    validation = validate_memory(memory)

    if not validation["valid"]:
        print("Memory rejected.")

        for error in validation["errors"]:
            print(f"  - {error}")

        return None

    category = category.upper()
    status = status.upper()

    connection = sqlite3.connect(DATABASE_PATH)
    cursor = connection.cursor()

    timestamp = datetime.now().isoformat()

    cursor.execute("""
        INSERT INTO memories (
            content,
            category,
            source_conversation_id,
            confidence,
            created_at,
            updated_at,
            memory_key,
            importance,
            status
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        content,
        category,
        source_conversation_id,
        confidence,
        timestamp,
        timestamp,
        memory_key,
        importance,
        status
    ))

    connection.commit()

    memory_id = cursor.lastrowid

    connection.close()

    return memory_id


def list_memories():
    connection = sqlite3.connect(DATABASE_PATH)
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            id,
            memory_key,
            content,
            category,
            confidence,
            importance,
            status,
            created_at
        FROM memories
        ORDER BY id
    """)

    memories = cursor.fetchall()

    connection.close()

    return memories


if __name__ == "__main__":

    create_memory_table()

    print()
    print("Testing valid memory...")

    memory_id = add_memory(
        content="User is actively learning PCVUE v17.",
        category="SKILL",
        memory_key="pcvue_skill",
        confidence=0.95,
        importance=0.90,
        status="ACTIVE"
    )

    if memory_id is not None:
        print(f"Created memory #{memory_id}")

    print()
    print("Current memories:")
    print("-" * 60)

    for memory in list_memories():
        print(memory)