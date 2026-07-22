from mcp_server.tools.content_tools import _clean_text, _truncate_at_references


def test_clean_text_collapses_excess_newlines():
    messy = "Line one\n\n\n\n\nLine two"
    result = _clean_text(messy)
    assert result == "Line one\n\nLine two"


def test_clean_text_collapses_excess_spaces():
    messy = "Too    many     spaces"
    result = _clean_text(messy)
    assert result == "Too many spaces"


def test_clean_text_fixes_hyphenation_at_linebreak():
    messy = "trans-\nformer"
    result = _clean_text(messy)
    assert result == "transformer"


def test_clean_text_strips_leading_trailing_whitespace():
    messy = "  \n  content here  \n  "
    result = _clean_text(messy)
    assert result == "content here"


def test_truncate_at_references_cuts_at_references_header():
    text = "Introduction text here.\n\nReferences\n\n[1] Some citation."
    result = _truncate_at_references(text)
    assert "citation" not in result
    assert "Introduction text here" in result


def test_truncate_at_references_is_case_insensitive():
    text = "Body content.\n\nREFERENCES\n\n[1] citation"
    result = _truncate_at_references(text)
    assert "citation" not in result


def test_truncate_at_references_handles_bibliography_variant():
    text = "Body content.\n\nBibliography\n\n[1] citation"
    result = _truncate_at_references(text)
    assert "citation" not in result


def test_truncate_at_references_returns_full_text_if_no_match():
    text = "Just body content, no references section at all."
    result = _truncate_at_references(text)
    assert result == text