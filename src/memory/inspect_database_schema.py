import sqlite3
from pathlib import Path


DATABASE_PATH = Path("data/processed/jarvis.db")


def inspect_database():

    connection = sqlite3.connect(DATABASE_PATH)
    cursor = connection.cursor()

    print("=" * 60)
    print("JARVIS DATABASE SCHEMA")
    print("=" * 60)

    cursor.execute("""
        SELECT name
        FROM sqlite_master
        WHERE type = 'table'
        ORDER BY name
    """)

    tables = cursor.fetchall()

    for table in tables:

        table_name = table[0]

        print()
        print(f"TABLE: {table_name}")
        print("-" * 60)

        cursor.execute(
            f"PRAGMA table_info({table_name})"
        )

        columns = cursor.fetchall()

        for column in columns:

            column_id = column[0]
            name = column[1]
            data_type = column[2]
            not_null = column[3]
            default = column[4]
            primary_key = column[5]

            print(
                f"{column_id}: "
                f"{name} "
                f"({data_type}) "
                f"NOT NULL={not_null} "
                f"PK={primary_key} "
                f"DEFAULT={default}"
            )

    connection.close()


if __name__ == "__main__":
    inspect_database()