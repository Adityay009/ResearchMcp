import os
import re
import urllib.request
import fitz  # pymupdf

from mcp_server.config import PDF_CACHE_DIR


def _download_pdf(paper_id: str, pdf_url: str) -> str:
    """Download a paper's PDF if not already cached. Returns local file path."""
    os.makedirs(PDF_CACHE_DIR, exist_ok=True)
    local_path = os.path.join(PDF_CACHE_DIR, f"{paper_id}.pdf")

    if not os.path.exists(local_path):
        urllib.request.urlretrieve(pdf_url, local_path)

    return local_path


def _clean_text(text: str) -> str:
    """Strip common PDF extraction noise: excess whitespace, page numbers, hyphenation."""
    # Collapse multiple newlines/spaces
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"[ \t]{2,}", " ", text)
    # Remove hyphenation at line breaks (e.g. "trans-\nformer" -> "transformer")
    text = re.sub(r"(\w)-\n(\w)", r"\1\2", text)
    return text.strip()


def _truncate_at_references(text: str) -> str:
    """Cut off the text at the References/Bibliography section, if found."""
    match = re.search(r"\n\s*(references|bibliography)\s*\n", text, re.IGNORECASE)
    if match:
        return text[:match.start()]
    return text


def extract_paper_content(paper_id: str, pdf_url: str) -> dict:
    """Download a paper's PDF and extract clean text content (excluding references).

    Args:
        paper_id: The arXiv id, used for caching
        pdf_url: Direct PDF URL, from get_paper_details
    """
    local_path = _download_pdf(paper_id, pdf_url)

    doc = fitz.open(local_path)
    full_text = ""
    for page in doc:
        full_text += page.get_text()
    doc.close()

    cleaned = _clean_text(full_text)
    body_only = _truncate_at_references(cleaned)

    return {
        "paper_id": paper_id,
        "char_count": len(body_only),
        "content": body_only,
    }