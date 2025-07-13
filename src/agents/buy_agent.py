"""Agent to analyze market data and buy stocks."""

from langchain_core.runnables import RunnableLambda
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.graph import END, StateGraph
from langgraph.prebuilt import create_react_agent
from tradingLogic.trading_logic import trading_logic, update_memory

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


class TradingState(dict):
    """Custom dictionary."""

    pass


builder = StateGraph(TradingState)
builder.add_node("fetch_data", RunnableLambda())
builder.add_node("decide", RunnableLambda(trading_logic))
builder.add_node("log", RunnableLambda(update_memory))

builder.set_entry_point("fetch_data")
builder.add_edge("fetch", "decide")
builder.add_edge("decide", "log")
builder.add_edge("log", END)

graph = builder.compile()


agent = create_react_agent(llm="", tools=tools)
