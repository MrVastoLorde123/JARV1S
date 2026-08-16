import sqlite3
from pathlib import Path


DATABASE_PATH = Path("data/processed/jarvis.db")


def build_search_index():
    connection = sqlite3.connect(DATABASE_PATH)
    cursor = connection.cursor()

    print("Building JARVIS full-text search index...")

    cursor.execute("""
        DROP TABLE IF EXISTS message_search
    """)

    cursor.execute("""
        CREATE VIRTUAL TABLE message_search
        USING fts5(
            content,
            content='messages',
            content_rowid='rowid'
        )
    """)

    cursor.execute("""
        INSERT INTO message_search(message_search)
        VALUES ('rebuild')
    """)

    connection.commit()
    connection.close()

    print("Search index rebuilt successfully.")


if __name__ == "__main__":
    build_search_index()