"""Agent to analyze portfolio and sell assets."""

from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent

# "args": "http://localhost:8000/mcp",
client = MultiServerMCPClient(
    {
        "echo_tool": {
            "command": "python",
            "args": [
                "C:/Users/Andrzej T (Standard)/Desktop/Projects/AI-trading-bot/src/router/mcp/mcp.py"
            ],
            "transport": "stdio",  # streamable_http
        }
    }
)

tools = client.get_tools()
agent = create_react_agent(llm="", tools=tools)
