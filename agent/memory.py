import sqlite3
import uuid
from datetime import datetime, timezone
import os

MEMORY_DB_PATH = "data/conversations.db"


def _get_connection():
    os.makedirs(os.path.dirname(MEMORY_DB_PATH), exist_ok=True)
    conn = sqlite3.connect(MEMORY_DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_memory_db():
    conn = _get_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            id TEXT PRIMARY KEY,
            title TEXT,
            created_at TEXT NOT NULL
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY (session_id) REFERENCES sessions(id)
        )
    """)
    conn.commit()
    conn.close()


def create_session(title: str = "") -> str:
    session_id = str(uuid.uuid4())[:8]
    conn = _get_connection()
    conn.execute(
        "INSERT INTO sessions (id, title, created_at) VALUES (?, ?, ?)",
        (session_id, title, datetime.now(timezone.utc).isoformat())
    )
    conn.commit()
    conn.close()
    return session_id


def save_message(session_id: str, role: str, content: str) -> None:
    conn = _get_connection()
    conn.execute(
        "INSERT INTO messages (session_id, role, content, created_at) VALUES (?, ?, ?, ?)",
        (session_id, role, content, datetime.now(timezone.utc).isoformat())
    )
    conn.commit()
    conn.close()


def load_session_messages(session_id: str) -> list[dict]:
    conn = _get_connection()
    rows = conn.execute(
        "SELECT role, content FROM messages WHERE session_id = ? ORDER BY id ASC",
        (session_id,)
    ).fetchall()
    conn.close()
    return [{"role": r["role"], "content": r["content"]} for r in rows]


def get_latest_session_id() -> str | None:
    conn = _get_connection()
    row = conn.execute("SELECT id FROM sessions ORDER BY created_at DESC LIMIT 1").fetchone()
    conn.close()
    return row["id"] if row else None


def list_sessions() -> list[dict]:
    conn = _get_connection()
    rows = conn.execute("""
        SELECT s.id, s.title, s.created_at, COUNT(m.id) as message_count
        FROM sessions s
        LEFT JOIN messages m ON m.session_id = s.id
        GROUP BY s.id
        ORDER BY s.created_at DESC
    """).fetchall()
    conn.close()
    return [dict(r) for r in rows]