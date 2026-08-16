import sqlite3
import sys
from pathlib import Path


DATABASE_PATH = Path("data/processed/jarvis.db")


def search_memory(query, limit=10):
    connection = sqlite3.connect(DATABASE_PATH)
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            messages.id,
            messages.conversation_id,
            messages.role,
            messages.content,
            conversations.title
        FROM message_search
        JOIN messages
            ON messages.rowid = message_search.rowid
        JOIN conversations
            ON conversations.id = messages.conversation_id
        WHERE message_search MATCH ?
        LIMIT ?
    """, (query, limit))

    results = cursor.fetchall()

    connection.close()

    return results


def display_results(query, results):
    print()
    print("=" * 60)
    print("JARVIS MEMORY SEARCH")
    print("=" * 60)
    print(f"Query: {query}")
    print(f"Results: {len(results)}")
    print()

    if not results:
        print("No memories found.")
        return

    for number, result in enumerate(results, start=1):

        message_id, conversation_id, role, content, title = result

        print(f"[{number}] {title}")
        print(f"Role: {role}")
        print("-" * 60)

        if len(content) > 500:
            content = content[:500] + "..."

        print(content)
        print()


def main():

    if len(sys.argv) < 2:
        print("Usage:")
        print('python src\\memory\\search.py "your search"')
        return

    query = " ".join(sys.argv[1:])

    results = search_memory(query)

    display_results(query, results)


if __name__ == "__main__":
    main()