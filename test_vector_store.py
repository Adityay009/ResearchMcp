from mcp_server.storage.vector_store import add_paper_to_index, search_similar_papers

add_paper_to_index(
    "2506.06962",
    "AR-RAG: Autoregressive Retrieval Augmentation for Image Generation",
    "We introduce Autoregressive Retrieval Augmentation, a novel paradigm for image generation using patch-level retrieval."
)
add_paper_to_index(
    "2209.15001",
    "Dilated Neighborhood Attention Transformer",
    "We introduce Dilated Neighborhood Attention, an extension to neighborhood attention for vision transformers."
)

print("Searching for 'retrieval augmented image generation':")
results = search_similar_papers("retrieval augmented image generation", top_k=2)
for r in results:
    print(f"- {r['title']} (distance: {r['distance']:.3f})")