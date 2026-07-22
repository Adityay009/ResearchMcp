from mcp_server.storage.db import save_paper_to_db, list_saved_papers, save_note_to_db, get_saved_paper
from mcp_server.storage.vector_store import add_paper_to_index, search_similar_papers


def save_paper(paper_id: str, title: str, authors: list[str], abstract: str, published: str, pdf_url: str) -> dict:
    """Save a paper to the personal research library (SQLite) and index it for semantic search (FAISS)."""
    result = save_paper_to_db(paper_id, title, authors, abstract, published, pdf_url)
    if result.get("status") == "failed":
        return result  # propagate the error, don't try to index a paper that failed to save

    add_paper_to_index(paper_id, title, abstract)
    return {"status": "saved", "paper_id": paper_id, "title": title}


def search_knowledge_base(query: str, top_k: int = 5) -> list[dict]:
    """Semantic search over your saved papers library."""
    return search_similar_papers(query, top_k)


def save_research_note(note: str, paper_id: str | None = None) -> dict:
    """Save a research note, optionally linked to a specific paper."""
    note_id = save_note_to_db(paper_id, note)
    return {"status": "saved", "note_id": note_id}


def list_library() -> list[dict]:
    """List all papers currently saved in the personal library."""
    return list_saved_papers()