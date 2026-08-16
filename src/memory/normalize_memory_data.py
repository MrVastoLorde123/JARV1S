import sqlite3
from pathlib import Path


DATABASE_PATH = Path("data/processed/jarvis.db")


VALID_CATEGORIES = {
    "PERSONAL",
    "SKILL",
    "PREFERENCE",
    "PROJECT",
    "GOAL",
    "FACT",
    "WORKFLOW",
    "RELATIONSHIP",
    "EXPERIENCE",
    "OTHER",
}


def normalize_memory_data():
    connection = sqlite3.connect(DATABASE_PATH)
    cursor = connection.cursor()

    print("=" * 60)
    print("JARVIS MEMORY DATA NORMALIZATION")
    print("=" * 60)

    cursor.execute("""
        SELECT id, category
        FROM memories
    """)

    memories = cursor.fetchall()

    for memory_id, category in memories:

        normalized_category = category.strip().upper()

        if normalized_category not in VALID_CATEGORIES:
            print(
                f"WARNING: Memory {memory_id} has "
                f"unknown category: {category}"
            )
            continue

        if category != normalized_category:
            cursor.execute("""
                UPDATE memories
                SET category = ?
                WHERE id = ?
            """, (
                normalized_category,
                memory_id
            ))

            print(
                f"Memory {memory_id}: "
                f"{category} -> {normalized_category}"
            )

    connection.commit()

    print()
    print("Normalization complete.")

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

    print()
    print("Current memories:")
    print("-" * 60)

    for memory in cursor.fetchall():
        print(memory)

    connection.close()


if __name__ == "__main__":
    normalize_memory_data()