import sqlite3
from pathlib import Path


DATABASE_PATH = Path("data/processed/jarvis.db")


def get_connection():
    """
    Create and configure a JARVIS database connection.
    """

    connection = sqlite3.connect(DATABASE_PATH)

    connection.execute("PRAGMA foreign_keys = ON")

    return connection


def set_database_path(database_path):
    """
    Change the database used by JARVIS.

    Primarily used by tests and future deployment configuration.
    """

    global DATABASE_PATH

    DATABASE_PATH = Path(database_path)


if __name__ == "__main__":

    print("=" * 60)
    print("JARVIS DATABASE CONNECTION TEST")
    print("=" * 60)

    connection = get_connection()

    print()
    print(f"Database: {DATABASE_PATH}")
    print("Connection: OK")

    foreign_keys = connection.execute(
        "PRAGMA foreign_keys"
    ).fetchone()[0]

    print(
        f"Foreign keys: "
        f"{'ON' if foreign_keys else 'OFF'}"
    )

    connection.close()

    print()
    print("Database connection test complete.")