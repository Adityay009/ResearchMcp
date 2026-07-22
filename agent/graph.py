import asyncio
from dotenv import load_dotenv

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent

load_dotenv()


async def build_agent():
    """Connect to the ResearchMCP server and build a LangGraph ReAct agent
    that can call all its tools."""

    client = MultiServerMCPClient({
        "researchmcp": {
            "command": "python",
            "args": ["-m", "mcp_server.server"],
            "transport": "stdio",
        }
    })

    tools = await client.get_tools()
    print(f"Loaded {len(tools)} tools from ResearchMCP:")
    for t in tools:
        print(f"  - {t.name}")

    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0)

    agent = create_react_agent(llm, tools)
    return agent


async def run_query(query: str):
    agent = await build_agent()
    result = await agent.ainvoke({"messages": [{"role": "user", "content": query}]})

    # Print the final message from the agent
    final_message = result["messages"][-1]
    content = final_message.content

    # Gemini sometimes returns content as a list of blocks instead of a plain string
    if isinstance(content, list):
        text_parts = [block.get("text", "") for block in content if isinstance(block, dict) and "text" in block]
        content = "\n".join(text_parts)

    print("\n--- Agent's final answer ---")
    print(content)

    return result


if __name__ == "__main__":
    test_query = (
    "Search for papers about neighborhood attention transformers. "
    "Get the full details of the top result and save it to my research library. "
    "Then search my library for anything related to vision transformers."
)
    asyncio.run(run_query(test_query))