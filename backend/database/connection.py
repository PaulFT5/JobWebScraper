import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "jobs" /"JobsDatabase.sqlite"

def database_connect():
    if not DB_PATH.exists():
        raise FileNotFoundError("Database not found at the given path")
    try:
        conn = sqlite3.connect(DB_PATH)
    except sqlite3.Error as e:
        raise RuntimeError(f"Could not open database at {DB_PATH}: {e}") from e
    return conn.cursor(), conn