# ResearchMCP

An agentic research assistant that lets an LLM autonomously search arXiv, extract and analyze paper content, and build a personal semantically-searchable research library — built as a custom [MCP](https://modelcontextprotocol.io) server paired with a LangGraph agent.

## What it does

Ask it something like:
> "Search for papers about neighborhood attention transformers, save the top result to my library, then find related papers I've already saved."

The agent autonomously decides which tools to call, in what order, chaining multiple steps together without being told the exact sequence.

An interactive CLI (`agent/cli.py`) lets you have a real multi-turn conversation with the agent — it remembers context within a session, and persists conversation history to SQLite so sessions survive restarts.

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

## Memory

The agent has two layers of memory, both backed by SQLite (separate from the research library database):

- **Short-term (in-session)**: the full conversation history is passed to the agent on every turn, so follow-up questions ("what was the title of the paper you just saved?") can be answered directly from context without a redundant tool call.
- **Long-term (persistent)**: every message is saved to `data/conversations.db`. Closing and reopening the CLI resumes the most recent session automatically, with full prior context intact.

The agent is prompted to distinguish between two different kinds of questions: recalling what was *discussed* in the conversation (answered from memory) versus querying the actual state of the saved paper *library* (answered by calling `list_saved_papers`) — these pull from different sources of truth, and the agent correctly picks the right one.

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
- **CLI**: `rich` for formatted terminal output, SQLite for persistent conversation memory

## Setup

```bash
# Clone and enter the repo
git clone <https://github.com/Adityay009/ResearchMcp>
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


### Running the interactive CLI (recommended)

```bash
python -m agent.cli
```

Commands available inside the CLI:
- `/new` — start a fresh conversation session
- `/sessions` — list all past sessions with message counts
- `/exit` — quit

Tool calls are printed live as the agent makes them, so you can see its reasoning step by step.

### Running a single scripted query

```bash
python agent/graph.py
```

Edit the `test_query` variable in `agent/graph.py` to try your own one-off queries.

## Known limitations

- PDF text extraction is imperfect on figure-heavy papers — captions, author affiliations, and diagram labels can bleed into the extracted body text (a known limitation of plain-text PDF extraction, not something specific to this project)
- Reference-section stripping uses a simple regex match on "References"/"Bibliography" headers — doesn't catch every paper's formatting (e.g. "Works Cited")
- `compare_papers` truncates each paper's content to keep tool responses within a reasonable context size, so very long papers are compared on excerpts (intro + methodology) rather than full text
- FAISS (`IndexFlatL2`) does exact brute-force search — fine at personal-library scale (hundreds of papers), would need a different index type (e.g. HNSW) at much larger scale

## Environment notes

Built and tested on macOS (Apple Silicon/M1). If `mcp dev` fails with `spawn uv ENOENT`, it's because the Inspector shells out to [`uv`](https://github.com/astral-sh/uv) regardless of your project setup — install it with `curl -LsSf https://astral.sh/uv/install.sh | sh` and make sure `~/.local/bin` is on your `PATH`.

If you hit a RESOURCE_EXHAUSTED / limit: 0 error from Gemini even on a fresh API key, try a different model (e.g. gemini-2.5-flash instead of gemini-2.0-flash) — free-tier quota allocation varies by model.