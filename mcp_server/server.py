from mcp.server.fastmcp import FastMCP
from mcp_server.tools.arxiv_tools import search_papers, get_paper_details
from mcp_server.tools.content_tools import extract_paper_content
from mcp_server.tools.library_tools import save_paper, search_knowledge_base, save_research_note, list_library
from mcp_server.storage.db import init_db
from mcp_server.tools.notes_tools import prepare_paper_for_summary, prepare_papers_for_comparison

# Ensure tables exist before the server starts handling requests
init_db()

mcp = FastMCP("ResearchMCP")


@mcp.tool()
def search_arxiv(query: str, max_results: int = 5) -> list[dict]:
    """Search arXiv for research papers matching a query.

    Args:
        query: Search terms, e.g. 'retrieval augmented generation'
        max_results: Number of results to return (default 5)
    """
    return search_papers(query, max_results)


@mcp.tool()
def get_paper(paper_id: str) -> dict:
    """Get full metadata for a specific arXiv paper.

    Args:
        paper_id: The arXiv id, e.g. '2506.06962'
    """
    return get_paper_details(paper_id)


@mcp.tool()
def extract_content(paper_id: str, pdf_url: str) -> dict:
    """Download a paper's PDF and extract its clean text content (excluding references).

    Args:
        paper_id: The arXiv id, used for caching the downloaded PDF
        pdf_url: Direct PDF URL, obtained from get_paper
    """
    return extract_paper_content(paper_id, pdf_url)


@mcp.tool()
def save_to_library(paper_id: str, title: str, authors: list[str], abstract: str, published: str, pdf_url: str) -> dict:
    """Save a paper to your personal research library for later semantic search.

    Args:
        paper_id: The arXiv id
        title: Paper title
        authors: List of author names
        abstract: Paper abstract
        published: Publication date
        pdf_url: Direct PDF URL
    """
    return save_paper(paper_id, title, authors, abstract, published, pdf_url)


@mcp.tool()
def search_library(query: str, top_k: int = 5) -> list[dict]:
    """Semantically search your saved papers library — finds conceptually related papers, not just keyword matches.

    Args:
        query: What you're looking for, e.g. 'papers about attention mechanisms'
        top_k: Number of results to return (default 5)
    """
    return search_knowledge_base(query, top_k)


@mcp.tool()
def save_note(note: str, paper_id: str | None = None) -> dict:
    """Save a research note, optionally linked to a specific paper.

    Args:
        note: The note content
        paper_id: Optional arXiv id to link this note to a specific paper
    """
    return save_research_note(note, paper_id)


@mcp.tool()
def list_saved_papers() -> list[dict]:
    """List all papers currently saved in your personal research library."""
    return list_library()


@mcp.tool()
def summarize_paper(paper_id: str) -> dict:
    """Prepare a paper's content for summarization. Returns title, abstract, and
    a content excerpt for the calling LLM to synthesize into a summary.

    Args:
        paper_id: The arXiv id of the paper to summarize
    """
    return prepare_paper_for_summary(paper_id)


@mcp.tool()
def compare_papers(paper_ids: list[str]) -> dict:
    """Prepare multiple papers' content for comparison. Returns each paper's
    details and content excerpt for the calling LLM to compare and contrast.

    Args:
        paper_ids: List of arXiv ids to compare, e.g. ['2506.06962', '2209.15001']
    """
    return prepare_papers_for_comparison(paper_ids)


if __name__ == "__main__":
    mcp.run()