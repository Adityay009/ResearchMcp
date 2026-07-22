from unittest.mock import MagicMock, patch
from mcp_server.tools.arxiv_tools import search_papers


def _make_fake_paper(short_id="1234.5678", title="Fake Paper"):
    """Build a mock object that looks like arxiv.Result."""
    fake = MagicMock()
    fake.get_short_id.return_value = short_id
    fake.title = title
    fake.authors = [MagicMock(name="Author One")]
    fake.authors[0].name = "Author One"
    fake.summary = "This is a fake abstract."
    fake.published.strftime.return_value = "2026-01-01"
    fake.pdf_url = f"https://arxiv.org/pdf/{short_id}"
    return fake


@patch("mcp_server.tools.arxiv_tools.arxiv.Client")
def test_search_papers_returns_correct_shape(mock_client_class):
    fake_paper = _make_fake_paper()
    mock_client_instance = MagicMock()
    mock_client_instance.results.return_value = [fake_paper]
    mock_client_class.return_value = mock_client_instance

    results = search_papers("test query", max_results=1)

    assert len(results) == 1
    assert results[0]["id"] == "1234.5678"
    assert results[0]["title"] == "Fake Paper"
    assert results[0]["authors"] == ["Author One"]
    assert results[0]["abstract"] == "This is a fake abstract."
    assert results[0]["published"] == "2026-01-01"


@patch("mcp_server.tools.arxiv_tools.arxiv.Client")
def test_search_papers_handles_multiple_results(mock_client_class):
    fake_papers = [_make_fake_paper(short_id=f"id-{i}") for i in range(3)]
    mock_client_instance = MagicMock()
    mock_client_instance.results.return_value = fake_papers
    mock_client_class.return_value = mock_client_instance

    results = search_papers("test query", max_results=3)

    assert len(results) == 3
    assert results[0]["id"] == "id-0"
    assert results[2]["id"] == "id-2"


@patch("mcp_server.tools.arxiv_tools.arxiv.Client")
def test_search_papers_returns_empty_list_for_no_results(mock_client_class):
    mock_client_instance = MagicMock()
    mock_client_instance.results.return_value = []
    mock_client_class.return_value = mock_client_instance

    results = search_papers("query with no matches", max_results=5)

    assert results == []