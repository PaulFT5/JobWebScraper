import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "jobs" /"JobsDatabase.sqlite"

def database_connect():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    return cursor, conn