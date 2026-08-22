import sqlite3
from pathlib import Path


DATABASE_PATH = Path("data/processed/jarvis.db")


def cleanup_test_memory():
    connection = sqlite3.connect(DATABASE_PATH)
    cursor = connection.cursor()

    cursor.execute("""
        DELETE FROM memories
        WHERE id = 2
    """)

    deleted = cursor.rowcount

    connection.commit()
    connection.close()

    print("=" * 60)
    print("JARVIS TEST MEMORY CLEANUP")
    print("=" * 60)
    print(f"Deleted memories: {deleted}")


if __name__ == "__main__":
    cleanup_test_memory()