import sqlite3
from datetime import datetime
from src.database import get_connection
from src.memory.memory_validator import validate_memory


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

def get_memory(memory_id):
    """
    Retrieve one memory by ID.
    """

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
        WHERE id = ?
        LIMIT 1
    """, (memory_id,))

    memory = cursor.fetchone()

    connection.close()

    return memory


def update_memory(
    memory_id,
    content=None,
    confidence=None,
    importance=None,
):
    """
    Update mutable fields of an existing memory.

    The memory identity/category are intentionally not changed
    by this operation.
    """

    existing = get_memory(
        memory_id
    )

    if existing is None:
        return False

    current_content = existing[2]
    current_confidence = existing[4]
    current_importance = existing[5]

    if content is None:
        content = current_content

    if confidence is None:
        confidence = current_confidence

    if importance is None:
        importance = current_importance

    validation = validate_memory({
        "content": content,
        "category": existing[3],
        "memory_key": existing[1],
        "confidence": confidence,
        "importance": importance,
        "status": existing[6],
    })

    if not validation["valid"]:
        return False

    timestamp = datetime.now().isoformat()

    connection = get_connection()

    try:

        connection.execute("""
            UPDATE memories
            SET
                content = ?,
                confidence = ?,
                importance = ?,
                updated_at = ?
            WHERE id = ?
        """, (
            content,
            confidence,
            importance,
            timestamp,
            memory_id,
        ))

        connection.commit()

    except sqlite3.Error:

        connection.rollback()

        return False

    finally:

        connection.close()

    return True


def update_memory_status(
    memory_id,
    status,
):
    """
    Update the status of an existing memory.
    """

    existing = get_memory(
        memory_id
    )

    if existing is None:
        return False

    status = status.upper()

    validation = validate_memory({
        "content": existing[2],
        "category": existing[3],
        "memory_key": existing[1],
        "confidence": existing[4],
        "importance": existing[5],
        "status": status,
    })

    if not validation["valid"]:
        return False

    timestamp = datetime.now().isoformat()

    connection = get_connection()

    try:

        connection.execute("""
            UPDATE memories
            SET
                status = ?,
                updated_at = ?
            WHERE id = ?
        """, (
            status,
            timestamp,
            memory_id,
        ))

        connection.commit()

    except sqlite3.Error:

        connection.rollback()

        return False

    finally:

        connection.close()

    return True