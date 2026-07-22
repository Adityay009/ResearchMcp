import pytest
from mcp_server.storage import db


@pytest.fixture
def temp_db(tmp_path, monkeypatch):
    """Redirect DB_PATH to a temp file for the duration of this test,
    then initialize a fresh schema."""
    test_db_path = tmp_path / "test_research.db"
    monkeypatch.setattr(db, "DB_PATH", str(test_db_path))
    db.init_db()
    return test_db_path


def test_init_db_creates_tables(temp_db):
    conn = db._get_connection()
    tables = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table'"
    ).fetchall()
    table_names = {row["name"] for row in tables}
    conn.close()
    assert "papers" in table_names
    assert "notes" in table_names


def test_save_and_retrieve_paper(temp_db):
    db.save_paper_to_db(
        paper_id="1234.5678",
        title="Test Paper",
        authors=["Alice", "Bob"],
        abstract="An abstract about testing.",
        published="2026-01-01",
        pdf_url="https://arxiv.org/pdf/1234.5678"
    )

    saved = db.get_saved_paper("1234.5678")
    assert saved is not None
    assert saved["title"] == "Test Paper"
    assert saved["authors"] == "Alice, Bob"


def test_save_paper_is_idempotent_on_same_id(temp_db):
    """Saving the same paper_id twice should update, not duplicate."""
    db.save_paper_to_db("1234.5678", "Original Title", ["A"], "abstract", "2026-01-01", "url")
    db.save_paper_to_db("1234.5678", "Updated Title", ["A"], "abstract", "2026-01-01", "url")

    all_papers = db.list_saved_papers()
    matching = [p for p in all_papers if p["id"] == "1234.5678"]
    assert len(matching) == 1
    assert matching[0]["title"] == "Updated Title"


def test_get_saved_paper_returns_none_for_missing_id(temp_db):
    result = db.get_saved_paper("does-not-exist")
    assert result is None


def test_list_saved_papers_orders_by_most_recent_first(temp_db):
    db.save_paper_to_db("aaa", "First Saved", [], "", "2026-01-01", "url")
    db.save_paper_to_db("bbb", "Second Saved", [], "", "2026-01-01", "url")

    papers = db.list_saved_papers()
    assert papers[0]["id"] == "bbb"  # most recently saved comes first
    assert papers[1]["id"] == "aaa"


def test_save_note_linked_to_paper(temp_db):
    db.save_paper_to_db("1234.5678", "Test Paper", [], "", "2026-01-01", "url")
    note_id = db.save_note_to_db("1234.5678", "This is interesting")
    assert note_id == 1


def test_save_note_without_paper_link(temp_db):
    """General notes not tied to a specific paper should still save."""
    note_id = db.save_note_to_db(None, "A general research thought")
    assert note_id == 1
    
    
def test_save_paper_returns_success_status(temp_db):
    result = db.save_paper_to_db("1234.5678", "Test Paper", ["A"], "abstract", "2026-01-01", "url")
    assert result["status"] == "saved"
    assert result["paper_id"] == "1234.5678"


def test_save_paper_rejects_missing_required_fields(temp_db):
    result = db.save_paper_to_db("", "", [], "", "", "")
    assert result["status"] == "failed"
    assert "error" in result