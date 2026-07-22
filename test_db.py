from mcp_server.storage.db import init_db, save_paper_to_db, list_saved_papers, save_note_to_db

init_db()

save_paper_to_db(
    paper_id="2506.06962",
    title="AR-RAG: Autoregressive Retrieval Augmentation for Image Generation",
    authors=["Jingyuan Qi", "Zhiyang Xu"],
    abstract="We introduce Autoregressive Retrieval Augmentation...",
    published="2025-06-14",
    pdf_url="https://arxiv.org/pdf/2506.06962"
)

note_id = save_note_to_db("2506.06962", "Interesting patch-level retrieval approach, worth comparing to CLIP-based methods")
print("Saved note with id:", note_id)

print("\nAll saved papers:")
for p in list_saved_papers():
    print("-", p["title"])