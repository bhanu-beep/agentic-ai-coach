"""Tiny SQLite helper. SQLite is a database stored in a single file - no server needed."""
import os
import sqlite3
from pathlib import Path

DB_PATH = Path(os.getenv("COACH_DB", "data/coach.db"))

SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS assessments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL REFERENCES users(id),
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    openness REAL NOT NULL,
    conscientiousness REAL NOT NULL,
    extraversion REAL NOT NULL,
    agreeableness REAL NOT NULL,
    emotional_stability REAL NOT NULL
);
"""


def get_conn() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH, timeout=10)
    conn.row_factory = sqlite3.Row  # lets us read columns by name: row["openness"]
    return conn


def init_db() -> None:
    with get_conn() as conn:
        conn.executescript(SCHEMA)


def seed_db() -> None:
    """Insert 3 sample users with a little history, only if the table is empty."""
    init_db()
    with get_conn() as conn:
        if conn.execute("SELECT COUNT(*) FROM users").fetchone()[0] > 0:
            return
        conn.executemany(
            "INSERT INTO users (id, name) VALUES (?, ?)",
            [(1, "Asha"), (2, "Ravi"), (3, "Meera")],
        )
        rows = [
            # user_id, created_at, O, C, E, A, ES
            (1, "2026-09-01 10:00:00", 45, 35, 60, 70, 40),
            (1, "2026-10-01 10:00:00", 50, 48, 62, 72, 46),
            (1, "2026-10-20 10:00:00", 58, 60, 65, 75, 55),
            (2, "2026-09-15 09:30:00", 70, 40, 30, 55, 65),
            (2, "2026-10-15 09:30:00", 72, 45, 38, 58, 66),
            (3, "2026-10-10 18:00:00", 55, 80, 75, 85, 70),
        ]
        conn.executemany(
            "INSERT INTO assessments (user_id, created_at, openness, conscientiousness,"
            " extraversion, agreeableness, emotional_stability) VALUES (?,?,?,?,?,?,?)",
            rows,
        )