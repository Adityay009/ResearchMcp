import os
import pickle
import faiss
import numpy as np
import os
os.environ["HF_HUB_OFFLINE"] = "0"  # keep online for first download; flip to "1" once cached if you want faster runs
from sentence_transformers import SentenceTransformer

VECTOR_DIR = "data/vector_store"
INDEX_PATH = os.path.join(VECTOR_DIR, "papers.index")
METADATA_PATH = os.path.join(VECTOR_DIR, "papers_meta.pkl")

_model = None


def _get_model():
    """Lazy-load the embedding model so it's only loaded once, on first use."""
    global _model
    if _model is None:
        _model = SentenceTransformer("all-MiniLM-L6-v2")
    return _model


def _load_index(dim: int = 384):
    os.makedirs(VECTOR_DIR, exist_ok=True)
    if os.path.exists(INDEX_PATH):
        index = faiss.read_index(INDEX_PATH)
        with open(METADATA_PATH, "rb") as f:
            metadata = pickle.load(f)
    else:
        index = faiss.IndexFlatL2(dim)
        metadata = []  # parallel list: metadata[i] corresponds to vector i in index
    return index, metadata


def _save_index(index, metadata):
    faiss.write_index(index, INDEX_PATH)
    with open(METADATA_PATH, "wb") as f:
        pickle.dump(metadata, f)


def add_paper_to_index(paper_id: str, title: str, abstract: str) -> None:
    """Embed a paper's title+abstract and add it to the FAISS index.
    If the paper is already indexed, skip to avoid duplicates."""
    model = _get_model()
    text = f"{title}. {abstract}"
    embedding = model.encode([text])[0].astype("float32")

    index, metadata = _load_index(dim=len(embedding))

    # Skip if this paper_id is already indexed
    if any(m["paper_id"] == paper_id for m in metadata):
        return

    index.add(np.array([embedding]))
    metadata.append({"paper_id": paper_id, "title": title})
    _save_index(index, metadata)


def search_similar_papers(query: str, top_k: int = 5) -> list[dict]:
    """Semantic search over saved papers. Returns closest matches with distance scores."""
    if not query or not query.strip():
        return []

    try:
        model = _get_model()
        index, metadata = _load_index()

        if index.ntotal == 0:
            return []

        query_vec = model.encode([query])[0].astype("float32")
        distances, indices = index.search(np.array([query_vec]), min(top_k, index.ntotal))

        results = []
        for dist, idx in zip(distances[0], indices[0]):
            if idx == -1:
                continue
            results.append({
                "paper_id": metadata[idx]["paper_id"],
                "title": metadata[idx]["title"],
                "distance": float(dist),
            })
        return results

    except Exception as e:
        return [{"error": f"Semantic search failed: {str(e)}"}]