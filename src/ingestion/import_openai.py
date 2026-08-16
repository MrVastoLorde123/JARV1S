import json
import sqlite3
from pathlib import Path


# ---------------------------------------------------------
# CONFIGURATION
# ---------------------------------------------------------

EXPORT_DIR = Path("data/raw/openai_export")
DATABASE_PATH = Path("data/processed/jarvis.db")


# ---------------------------------------------------------
# DATABASE
# ---------------------------------------------------------

def create_database(connection):
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS conversations (
            id TEXT PRIMARY KEY,
            title TEXT,
            created_at REAL,
            updated_at REAL,
            is_archived INTEGER,
            is_starred INTEGER
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id TEXT PRIMARY KEY,
            conversation_id TEXT,
            role TEXT,
            content TEXT,
            created_at REAL,
            parent_id TEXT,
            FOREIGN KEY (conversation_id)
                REFERENCES conversations(id)
        )
    """)

    connection.commit()


# ---------------------------------------------------------
# CONVERSATION IMPORT
# ---------------------------------------------------------

def import_conversation(connection, conversation):
    cursor = connection.cursor()

    conversation_id = conversation.get("conversation_id") or conversation.get("id")

    cursor.execute("""
        INSERT OR IGNORE INTO conversations
        (id, title, created_at, updated_at, is_archived, is_starred)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        conversation_id,
        conversation.get("title"),
        conversation.get("create_time"),
        conversation.get("update_time"),
        int(bool(conversation.get("is_starred"))),
        int(bool(conversation.get("is_starred")))
    ))

    for node_id, node in conversation.get("mapping", {}).items():

        message = node.get("message")

        if not message:
            continue

        content = message.get("content", {})
        parts = content.get("parts", [])

        text_parts = []

        for part in parts:
            if isinstance(part, str):
                text_parts.append(part)

        text = "\n".join(text_parts).strip()

        if not text:
            continue

        cursor.execute("""
            INSERT OR IGNORE INTO messages
            (id, conversation_id, role, content, created_at, parent_id)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            message.get("id") or node_id,
            conversation_id,
            message.get("author", {}).get("role"),
            text,
            message.get("create_time"),
            node.get("parent")
        ))

    connection.commit()


# ---------------------------------------------------------
# IMPORT ALL CONVERSATIONS
# ---------------------------------------------------------

def import_export():
    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(DATABASE_PATH)

    create_database(connection)

    conversation_files = sorted(
        EXPORT_DIR.glob("conversations-*.json")
    )

    print(f"Found {len(conversation_files)} conversation files.")

    total = 0

    for file in conversation_files:

        print(f"Importing {file.name}...")

        with file.open("r", encoding="utf-8") as f:
            conversations = json.load(f)

        for conversation in conversations:
            import_conversation(connection, conversation)
            total += 1

    connection.close()

    print()
    print("===================================")
    print("JARVIS IMPORT COMPLETE")
    print("===================================")
    print(f"Conversations processed: {total}")
    print(f"Database: {DATABASE_PATH}")


# ---------------------------------------------------------
# PROGRAM ENTRY POINT
# ---------------------------------------------------------

if __name__ == "__main__":
    import_export()