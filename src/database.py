import os
import sqlite3
from pathlib import Path


DEFAULT_DATABASE_PATH = Path("data/processed/jarvis.db")
DATABASE_PATH = DEFAULT_DATABASE_PATH


def get_database_path():
    """Return the canonical runtime database path, honoring JARVIS_DATA_DIR."""

    if DATABASE_PATH != DEFAULT_DATABASE_PATH:
        return DATABASE_PATH

    configured_data_dir = os.environ.get("JARVIS_DATA_DIR")
    if configured_data_dir:
        return Path(configured_data_dir) / "processed" / "jarvis.db"

    return DATABASE_PATH


def get_connection():
    """
    Create and configure a JARVIS database connection.

    The configured database path may live below a directory that does not yet
    exist in a fresh checkout or isolated test environment. Directory setup is
    part of the connection contract, not a caller responsibility.
    """

    database_path = get_database_path()
    database_path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(database_path)

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
    print(f"Database: {get_database_path()}")
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