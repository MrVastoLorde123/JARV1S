import sqlite3
from pathlib import Path


DATABASE_PATH = Path("data/processed/jarvis.db")


def inspect_database():
    connection = sqlite3.connect(DATABASE_PATH)
    cursor = connection.cursor()

    print("=" * 50)
    print("JARVIS DATABASE INSPECTION")
    print("=" * 50)

    # Count conversations
    cursor.execute("SELECT COUNT(*) FROM conversations")
    conversation_count = cursor.fetchone()[0]

    # Count messages
    cursor.execute("SELECT COUNT(*) FROM messages")
    message_count = cursor.fetchone()[0]

    # Count messages by role
    cursor.execute("""
        SELECT role, COUNT(*)
        FROM messages
        GROUP BY role
    """)

    role_counts = cursor.fetchall()

    print()
    print(f"Conversations: {conversation_count}")
    print(f"Messages:      {message_count}")

    print()
    print("Messages by role:")

    for role, count in role_counts:
        print(f"  {role}: {count}")

    # Count archived conversations
    cursor.execute("""
        SELECT COUNT(*)
        FROM conversations
        WHERE is_archived = 1
    """)

    archived_count = cursor.fetchone()[0]

    # Count starred conversations
    cursor.execute("""
        SELECT COUNT(*)
        FROM conversations
        WHERE is_starred = 1
    """)

    starred_count = cursor.fetchone()[0]

    print()
    print(f"Archived: {archived_count}")
    print(f"Starred:  {starred_count}")

    # Show sample conversations
    print()
    print("Sample conversations:")
    print("-" * 50)

    cursor.execute("""
        SELECT id, title
        FROM conversations
        ORDER BY created_at
        LIMIT 10
    """)

    for conversation_id, title in cursor.fetchall():
        print(f"{title}")
        print(f"  ID: {conversation_id}")

    connection.close()


if __name__ == "__main__":
    inspect_database()