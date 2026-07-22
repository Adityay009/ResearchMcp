from mcp_server.tools.arxiv_tools import search_papers, get_paper_details

results = search_papers("retrieval augmented generation", max_results=3)
for r in results:
    print(r["id"], "-", r["title"])

print("\n--- Full details for first result ---")
details = get_paper_details(results[0]["id"])
print(details["title"])
print(details["abstract"][:200], "...")