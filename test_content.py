from mcp_server.tools.arxiv_tools import get_paper_details
from mcp_server.tools.content_tools import extract_paper_content

details = get_paper_details("2506.06962")
result = extract_paper_content(details["id"], details["pdf_url"])

print("Paper:", details["title"])
print("Extracted chars:", result["char_count"])
print("\n--- First 500 chars ---")
print(result["content"][:500])
