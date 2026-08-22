from datetime import datetime
from src.database import get_connection
from memory_validator import validate_memory


def create_memory_table():
    connection = get_connection()
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


def find_active_memory(memory_key):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            id,
            memory_key,
            content,
            category,
            confidence,
            importance,
            status
        FROM memories
        WHERE memory_key = ?
          AND status = 'ACTIVE'
        LIMIT 1
    """, (memory_key,))

    memory = cursor.fetchone()

    connection.close()

    return memory


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

    # ---------------------------------------------------------
    # STEP 1 — Validate
    # ---------------------------------------------------------

    validation = validate_memory(memory)

    if not validation["valid"]:

        print("Memory rejected.")

        for error in validation["errors"]:
            print(f"  - {error}")

        return None

    # ---------------------------------------------------------
    # STEP 2 — Normalize
    # ---------------------------------------------------------

    category = category.upper()
    status = status.upper()

    # ---------------------------------------------------------
    # STEP 3 — Check for existing ACTIVE memory
    # ---------------------------------------------------------

    existing_memory = find_active_memory(memory_key)

    if existing_memory is not None:

        print("Memory already exists.")

        print()
        print("Existing memory:")
        print("-" * 60)
        print(existing_memory)

        return existing_memory[0]

    # ---------------------------------------------------------
    # STEP 4 — Insert new memory
    # ---------------------------------------------------------

    connection = get_connection()
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
    connection = get_connection()
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