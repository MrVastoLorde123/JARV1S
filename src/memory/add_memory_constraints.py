import sqlite3
from pathlib import Path


DATABASE_PATH = Path("data/processed/jarvis.db")


def add_memory_constraints():
    connection = sqlite3.connect(DATABASE_PATH)
    cursor = connection.cursor()

    print("=" * 60)
    print("JARVIS MEMORY CONSTRAINT SETUP")
    print("=" * 60)

    cursor.execute("""
        CREATE UNIQUE INDEX IF NOT EXISTS
        idx_unique_active_memory_key
        ON memories(memory_key)
        WHERE status = 'ACTIVE'
          AND memory_key IS NOT NULL
    """)

    connection.commit()

    print()
    print("Created/verified:")
    print("  UNIQUE ACTIVE memory_key constraint")

    connection.close()

    print()
    print("Constraint setup complete.")


if __name__ == "__main__":
    add_memory_constraints()