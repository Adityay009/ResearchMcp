import arxiv


def search_papers(query: str, max_results: int = 5) -> list[dict]:
    """Search arXiv for papers matching a query.

    Returns a list of paper summaries with id, title, authors, and abstract.
    """
    if not query or not query.strip():
        return {"error": "Query cannot be empty", "status": "failed"}

    try:
        client = arxiv.Client()
        search = arxiv.Search(
            query=query,
            max_results=max_results,
            sort_by=arxiv.SortCriterion.Relevance,
        )

        results = []
        for paper in client.results(search):
            results.append({
                "id": paper.get_short_id(),
                "title": paper.title,
                "authors": [a.name for a in paper.authors],
                "abstract": paper.summary,
                "published": paper.published.strftime("%Y-%m-%d"),
                "pdf_url": paper.pdf_url,
            })
        return results

    except Exception as e:
        return {"error": f"arXiv search failed: {str(e)}", "status": "failed"}


def get_paper_details(paper_id: str) -> dict:
    """Fetch full metadata for a single paper by its arXiv id (e.g. '2310.06825')."""
    if not paper_id or not paper_id.strip():
        return {"error": "paper_id cannot be empty", "status": "failed"}

    try:
        client = arxiv.Client()
        search = arxiv.Search(id_list=[paper_id])
        paper = next(client.results(search), None)

        if paper is None:
            return {"error": f"No paper found with id '{paper_id}'", "status": "failed"}

        return {
            "id": paper.get_short_id(),
            "title": paper.title,
            "authors": [a.name for a in paper.authors],
            "abstract": paper.summary,
            "published": paper.published.strftime("%Y-%m-%d"),
            "categories": paper.categories,
            "pdf_url": paper.pdf_url,
            "doi": paper.doi,
        }

    except Exception as e:
        return {"error": f"Failed to fetch paper '{paper_id}': {str(e)}", "status": "failed"}