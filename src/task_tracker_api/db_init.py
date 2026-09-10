import os
from pathlib import Path

import psycopg


DB_HOST = os.getenv("DB_HOST", "localhost")
DB_NAME = os.getenv("DB_NAME", "task_tracker_api")
DB_USER = os.getenv("DB_USER", "admin")
DB_PASSWORD = os.getenv("DB_PASSWORD", "password")

MIGRATION_PATH = (
    Path(__file__).resolve().parents[2]
    / "migrations"
    / "001_initial.sql"
)


def initialize_database() -> None:
    if not MIGRATION_PATH.exists():
        raise FileNotFoundError(f"Migration file not found: {MIGRATION_PATH}")

    migration_sql = MIGRATION_PATH.read_text(encoding="utf-8")

    with psycopg.connect(
        host=DB_HOST,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
    ) as connection:
        with connection.cursor() as cursor:
            cursor.execute(migration_sql)

    print("Database initialized successfully.")


if __name__ == "__main__":
    initialize_database()