import asyncio
from dotenv import load_dotenv
from rich.console import Console
from rich.markdown import Markdown

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent

from agent.memory import (
    init_memory_db, create_session, save_message,
    load_session_messages, get_latest_session_id, list_sessions
)

load_dotenv()
console = Console()


def extract_text(content) -> str:
    """Handle Gemini's occasional list-of-blocks content format."""
    if isinstance(content, list):
        return "\n".join(b.get("text", "") for b in content if isinstance(b, dict) and "text" in b)
    return content


async def build_agent():
    client = MultiServerMCPClient({
        "researchmcp": {
            "command": "python",
            "args": ["-m", "mcp_server.server"],
            "transport": "stdio",
        }
    })
    tools = await client.get_tools()
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0)

    system_prompt = (
        "You are a research assistant with access to tools for searching arXiv, "
        "extracting paper content, and managing a personal research library. "
        "You have access to the full conversation history. "
        "If the answer to the user's question is already present in earlier messages "
        "in this conversation, answer directly from that context — do NOT call a tool "
        "just to re-fetch information you already stated. Only call tools when you "
        "need new information that isn't already in the conversation."
    )

    return create_react_agent(llm, tools, prompt=system_prompt)


def print_tool_calls(new_messages):
    """Print any tool calls that happened during this turn, before the final answer."""
    for msg in new_messages:
        tool_calls = getattr(msg, "tool_calls", None)
        if tool_calls:
            for tc in tool_calls:
                console.print(f"  🔧 [dim]calling {tc['name']}({tc['args']})[/dim]")


async def main():
    console.print("[bold cyan]ResearchMCP — Interactive Agent[/bold cyan]")
    console.print("[dim]Commands: /new (new session), /sessions (list past sessions), /exit[/dim]\n")

    init_memory_db()
    console.print("[dim]Connecting to MCP server...[/dim]")
    agent = await build_agent()

    # Resume last session if one exists, else start fresh
    session_id = get_latest_session_id()
    history = []
    if session_id:
        history = load_session_messages(session_id)
        console.print(f"[green]Resumed session {session_id} ({len(history)} prior messages)[/green]\n")
    else:
        session_id = create_session()
        console.print(f"[green]Started new session {session_id}[/green]\n")

    while True:
        user_input = console.input("[bold yellow]You:[/bold yellow] ").strip()

        if not user_input:
            continue
        if user_input.lower() in ("/exit", "exit", "quit"):
            console.print("[dim]Goodbye![/dim]")
            break
        if user_input == "/new":
            session_id = create_session()
            history = []
            console.print(f"[green]Started new session {session_id}[/green]\n")
            continue
        if user_input == "/sessions":
            for s in list_sessions():
                console.print(f"  {s['id']} — {s['message_count']} messages — {s['created_at']}")
            continue

        history.append({"role": "user", "content": user_input})
        save_message(session_id, "user", user_input)

        pre_call_len = len(history)
        result = await agent.ainvoke({"messages": history})
        all_messages = result["messages"]

        # Show which tools were called this turn
        print_tool_calls(all_messages[pre_call_len:])

        final_content = extract_text(all_messages[-1].content)
        console.print("[bold cyan]Agent:[/bold cyan]", Markdown(final_content))
        console.print()

        history.append({"role": "assistant", "content": final_content})
        save_message(session_id, "assistant", final_content)


if __name__ == "__main__":
    asyncio.run(main())