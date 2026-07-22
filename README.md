# ResearchMCP

An agentic research assistant that lets an LLM autonomously search arXiv, extract and analyze paper content, and build a personal semantically-searchable research library — built as a custom [MCP](https://modelcontextprotocol.io) server paired with a LangGraph agent.

## What it does

Ask it something like:
> "Search for papers about neighborhood attention transformers, save the top result to my library, then find related papers I've already saved."

The agent autonomously decides which tools to call, in what order, chaining multiple steps together without being told the exact sequence.

## Architecture

```
User query
    ↓
LangGraph ReAct Agent (Gemini 2.5 Flash)
    ↓ (decides which tool to call, loops until done)
ResearchMCP Server (9 tools over MCP protocol)
    ↓
┌─────────────┬──────────────┬─────────────────┐
│  arXiv API  │ PDF extract  │ SQLite + FAISS  │
│  (search)   │ (pymupdf)    │ (personal library)│
└─────────────┴──────────────┴─────────────────┘
    ↓
Synthesized answer, grounded in real tool results
```

The MCP server and the agent are fully decoupled — the server is a standalone, protocol-compliant MCP server that works with **any** MCP client (Claude Desktop, other agents), not just the LangGraph agent built here.

## Tools

| Tool | What it does |
|---|---|
| `search_arxiv` | Search arXiv by keyword, returns titles/authors/abstracts |
| `get_paper` | Full metadata for one paper by arXiv ID |
| `extract_content` | Downloads a paper's PDF, extracts and cleans the text (strips references) |
| `save_to_library` | Saves a paper to a personal SQLite + FAISS-indexed library |
| `search_library` | Semantic search over your saved papers — finds conceptually related work, not just keyword matches |
| `save_note` | Save a research note, optionally linked to a paper |
| `list_saved_papers` | List everything in your library |
| `summarize_paper` | Fetches a paper's content, formatted for the calling LLM to summarize |
| `compare_papers` | Fetches multiple papers' content side by side, formatted for the calling LLM to compare |

**Design note**: `summarize_paper` and `compare_papers` intentionally do **not** call an LLM internally — they return raw, structured data for the client (the LLM asking the question) to reason over. This keeps the server's responsibility scoped to *retrieval*, not *reasoning*, which is the correct separation of concerns for MCP tools and keeps the server reusable across any client.

## Tech stack

- **MCP server**: Python, official `mcp` SDK (FastMCP)
- **Paper search**: `arxiv` package (arXiv API wrapper)
- **PDF extraction**: `pymupdf`
- **Personal library**: SQLite (metadata) + FAISS (semantic search) + `sentence-transformers` (`all-MiniLM-L6-v2` embeddings)
- **Agent**: LangGraph (`create_react_agent`) + `langchain-mcp-adapters` + Gemini 2.5 Flash

## Setup

```bash
# Clone and enter the repo
git clone <your-repo-url>
cd researchmcp

# Create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate

# Install MCP server dependencies
pip install -r requirements.txt

# Install agent dependencies
pip install -r agent/requirements.txt

# Add your Gemini API key
echo "GOOGLE_API_KEY=your_key_here" > .env
```

### Running the MCP server standalone (with the official Inspector)

```bash
PYTHONPATH=. mcp dev mcp_server/server.py
```

Opens a local web UI to test each of the 9 tools individually.

### Running the full agent

```bash
python agent/graph.py
```

Edit the `test_query` variable in `agent/graph.py` to try your own queries.

## Known limitations

- PDF text extraction is imperfect on figure-heavy papers — captions, author affiliations, and diagram labels can bleed into the extracted body text (a known limitation of plain-text PDF extraction, not something specific to this project)
- Reference-section stripping uses a simple regex match on "References"/"Bibliography" headers — doesn't catch every paper's formatting (e.g. "Works Cited")
- `compare_papers` truncates each paper's content to keep tool responses within a reasonable context size, so very long papers are compared on excerpts (intro + methodology) rather than full text
- FAISS (`IndexFlatL2`) does exact brute-force search — fine at personal-library scale (hundreds of papers), would need a different index type (e.g. HNSW) at much larger scale

## Environment notes

Built and tested on macOS (Apple Silicon/M1). If `mcp dev` fails with `spawn uv ENOENT`, it's because the Inspector shells out to [`uv`](https://github.com/astral-sh/uv) regardless of your project setup — install it with `curl -LsSf https://astral.sh/uv/install.sh | sh` and make sure `~/.local/bin` is on your `PATH`.