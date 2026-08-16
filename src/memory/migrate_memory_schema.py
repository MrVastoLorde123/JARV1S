import sqlite3
from pathlib import Path


DATABASE_PATH = Path("data/processed/jarvis.db")


def migrate_memory_schema():
    connection = sqlite3.connect(DATABASE_PATH)
    cursor = connection.cursor()

    print("=" * 60)
    print("JARVIS MEMORY SCHEMA MIGRATION")
    print("=" * 60)

    # Check which columns already exist
    cursor.execute("PRAGMA table_info(memories)")
    columns = cursor.fetchall()

    existing_columns = {column[1] for column in columns}

    print()
    print("Existing columns:")
    for column in existing_columns:
        print(f"  - {column}")

    # Add memory_key
    if "memory_key" not in existing_columns:
        cursor.execute("""
            ALTER TABLE memories
            ADD COLUMN memory_key TEXT
        """)
        print("Added: memory_key")
    else:
        print("Already exists: memory_key")

    # Add importance
    if "importance" not in existing_columns:
        cursor.execute("""
            ALTER TABLE memories
            ADD COLUMN importance REAL NOT NULL DEFAULT 0.5
        """)
        print("Added: importance")
    else:
        print("Already exists: importance")

    # Add status
    if "status" not in existing_columns:
        cursor.execute("""
            ALTER TABLE memories
            ADD COLUMN status TEXT NOT NULL DEFAULT 'ACTIVE'
        """)
        print("Added: status")
    else:
        print("Already exists: status")

    # Give our existing memory a proper key
    cursor.execute("""
        UPDATE memories
        SET memory_key = 'pcvue_skill'
        WHERE id = 1
          AND memory_key IS NULL
    """)

    # Give our existing memory an importance value
    cursor.execute("""
        UPDATE memories
        SET importance = 0.90
        WHERE id = 1
    """)

    # Make sure the existing memory is active
    cursor.execute("""
        UPDATE memories
        SET status = 'ACTIVE'
        WHERE id = 1
    """)

    connection.commit()

    print()
    print("Migration complete.")

    # Verify the resulting schema
    cursor.execute("PRAGMA table_info(memories)")
    columns = cursor.fetchall()

    print()
    print("Final schema:")
    print("-" * 60)

    for column in columns:
        column_id = column[0]
        name = column[1]
        data_type = column[2]
        not_null = column[3]
        default = column[4]

        print(
            f"{column_id}: {name} "
            f"({data_type}) "
            f"NOT NULL={not_null} "
            f"DEFAULT={default}"
        )

    # Verify existing memory
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
        ORDER BY id
    """)

    memories = cursor.fetchall()

    print()
    print("Current memories:")
    print("-" * 60)

    for memory in memories:
        print(memory)

    connection.close()


if __name__ == "__main__":
    migrate_memory_schema()