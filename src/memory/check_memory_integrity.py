import sqlite3
from pathlib import Path


DATABASE_PATH = Path("data/processed/jarvis.db")


def check_memory_integrity():
    connection = sqlite3.connect(DATABASE_PATH)
    cursor = connection.cursor()

    print("=" * 60)
    print("JARVIS MEMORY INTEGRITY CHECK")
    print("=" * 60)

    # Check for duplicate ACTIVE memory keys
    cursor.execute("""
        SELECT
            memory_key,
            COUNT(*)
        FROM memories
        WHERE status = 'ACTIVE'
          AND memory_key IS NOT NULL
        GROUP BY memory_key
        HAVING COUNT(*) > 1
    """)

    duplicates = cursor.fetchall()

    print()
    print("Duplicate ACTIVE memory keys:")

    if duplicates:
        for memory_key, count in duplicates:
            print(
                f"  - {memory_key}: {count} records"
            )
    else:
        print("  None")

    # Check for invalid categories
    valid_categories = {
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

    cursor.execute("""
        SELECT id, category
        FROM memories
    """)

    invalid_categories = []

    for memory_id, category in cursor.fetchall():

        if category not in valid_categories:
            invalid_categories.append(
                (memory_id, category)
            )

    print()
    print("Invalid categories:")

    if invalid_categories:
        for memory_id, category in invalid_categories:
            print(
                f"  - Memory {memory_id}: {category}"
            )
    else:
        print("  None")

    # Check confidence and importance ranges
    cursor.execute("""
        SELECT id, confidence, importance
        FROM memories
        WHERE confidence < 0
           OR confidence > 1
           OR importance < 0
           OR importance > 1
    """)

    invalid_scores = cursor.fetchall()

    print()
    print("Invalid confidence/importance values:")

    if invalid_scores:
        for memory in invalid_scores:
            print(f"  - {memory}")
    else:
        print("  None")

    connection.close()

    print()
    print("Integrity check complete.")


if __name__ == "__main__":
    check_memory_integrity()