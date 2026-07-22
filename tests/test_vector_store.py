import pytest
from mcp_server.storage import vector_store


@pytest.fixture
def temp_vector_store(tmp_path, monkeypatch):
    """Redirect FAISS index + metadata paths to a temp directory."""
    monkeypatch.setattr(vector_store, "VECTOR_DIR", str(tmp_path))
    monkeypatch.setattr(vector_store, "INDEX_PATH", str(tmp_path / "test.index"))
    monkeypatch.setattr(vector_store, "METADATA_PATH", str(tmp_path / "test_meta.pkl"))
    # Reset the lazily-loaded model between tests to avoid cross-test state
    vector_store._model = None
    return tmp_path


def test_add_paper_to_index_then_search_finds_it(temp_vector_store):
    vector_store.add_paper_to_index(
        "1234.5678", "Attention Is All You Need", "A paper about transformers and self-attention."
    )

    results = vector_store.search_similar_papers("transformer attention mechanisms", top_k=5)

    assert len(results) == 1
    assert results[0]["paper_id"] == "1234.5678"


def test_add_same_paper_twice_does_not_duplicate(temp_vector_store):
    """Regression test for the FAISS duplicate-entry bug found during manual testing."""
    vector_store.add_paper_to_index("1234.5678", "Title", "Abstract text.")
    vector_store.add_paper_to_index("1234.5678", "Title", "Abstract text.")  # duplicate save

    results = vector_store.search_similar_papers("Title", top_k=10)
    matching = [r for r in results if r["paper_id"] == "1234.5678"]
    assert len(matching) == 1


def test_search_on_empty_index_returns_empty_list(temp_vector_store):
    results = vector_store.search_similar_papers("anything", top_k=5)
    assert results == []


def test_multiple_different_papers_all_indexed(temp_vector_store):
    vector_store.add_paper_to_index("aaa", "Paper A", "About topic A.")
    vector_store.add_paper_to_index("bbb", "Paper B", "About topic B.")

    results = vector_store.search_similar_papers("topic", top_k=10)
    result_ids = {r["paper_id"] for r in results}
    assert result_ids == {"aaa", "bbb"}