import sqlite3
from datetime import datetime, timezone

from mcp_server.config import DB_PATH
import os


def _get_connection():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Create tables if they don't exist. Safe to call every time the server starts."""
    conn = _get_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS papers (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            authors TEXT,
            abstract TEXT,
            published TEXT,
            pdf_url TEXT,
            saved_at TEXT NOT NULL
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            paper_id TEXT,
            note TEXT NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY (paper_id) REFERENCES papers(id)
        )
    """)
    conn.commit()
    conn.close()


def save_paper_to_db(paper_id: str, title: str, authors: list[str], abstract: str, published: str, pdf_url: str) -> dict:
    if not paper_id or not title:
        return {"error": "paper_id and title are required", "status": "failed"}

    try:
        conn = _get_connection()
        conn.execute(
            """INSERT OR REPLACE INTO papers (id, title, authors, abstract, published, pdf_url, saved_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (paper_id, title, ", ".join(authors), abstract, published, pdf_url,
                datetime.now(timezone.utc).isoformat())
        )
        conn.commit()
        conn.close()
        return {"status": "saved", "paper_id": paper_id}
    except Exception as e:
        return {"error": f"Failed to save paper: {str(e)}", "status": "failed"}


def get_saved_paper(paper_id: str) -> dict | None:
    conn = _get_connection()
    row = conn.execute("SELECT * FROM papers WHERE id = ?", (paper_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


def list_saved_papers() -> list[dict]:
    conn = _get_connection()
    rows = conn.execute("SELECT * FROM papers ORDER BY saved_at DESC").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def save_note_to_db(paper_id: str | None, note: str) -> int:
    conn = _get_connection()
    cursor = conn.execute(
        "INSERT INTO notes (paper_id, note, created_at) VALUES (?, ?, ?)",
        (paper_id, note, datetime.now(timezone.utc).isoformat())
    )
    conn.commit()
    note_id = cursor.lastrowid
    conn.close()
    return note_id