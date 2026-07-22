from mcp_server.tools.arxiv_tools import get_paper_details
from mcp_server.tools.content_tools import extract_paper_content


def prepare_paper_for_summary(paper_id: str) -> dict:
    """Fetch a paper's details and content, formatted for an LLM to summarize.
    This tool does NOT generate the summary itself — it returns the material
    for the calling LLM client to reason over."""
    details = get_paper_details(paper_id)
    content = extract_paper_content(paper_id, details["pdf_url"])

    return {
        "paper_id": paper_id,
        "title": details["title"],
        "authors": details["authors"],
        "abstract": details["abstract"],
        # Truncate to keep tool responses reasonably sized — first ~8000 chars
        # covers intro + methodology for most papers, which is enough for a summary
        "content_excerpt": content["content"][:8000],
        "full_content_char_count": content["char_count"],
    }


def prepare_papers_for_comparison(paper_ids: list[str]) -> dict:
    """Fetch details and content for multiple papers, formatted for an LLM to compare.
    This tool does NOT generate the comparison itself — it returns the material
    for the calling LLM client to reason over."""
    papers = []
    for pid in paper_ids:
        details = get_paper_details(pid)
        content = extract_paper_content(pid, details["pdf_url"])
        papers.append({
            "paper_id": pid,
            "title": details["title"],
            "abstract": details["abstract"],
            "content_excerpt": content["content"][:5000],  # smaller excerpt per paper since we're fetching multiple
        })

    return {"papers": papers, "count": len(papers)}