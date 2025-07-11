import asyncio

from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_core.runnables import RunnableLambda
from langgraph.prebuilt import create_react_agent
from langgraph.graph import StateGraph, END

from tradingLogic.trading_logic import update_memory, trading_logic


client = MultiServerMCPClient(
    {
        "echo_tool": {
            "command": "python",
            "args": ["C:\Users\Andrzej T (Standard)\Desktop\Projects\AI-trading-bot\src\router\mcp\mcp.py"],
            #"args": "http://localhost:8000/mcp",
            "transport": "stdio" #streamable_http
        }
    }
)

tools = client.get_tools()

class TradingState(dict):
    """Custom dictionary"""
    pass

def get_market_data():
    return search_all_assets() # avaliable classes: us_option, us_equity, crypto




builder = StateGraph(TradingState)
builder.add_node("fetch_data", RunnableLambda(get_market_data))
builder.add_node("decide", RunnableLambda(trading_logic))
builder.add_node("log", RunnableLambda(update_memory))

builder.set_entry_point("fetch_data")
builder.add_edge("fetch", "decide")
builder.add_edge("decide", "log")
builder.add_edge("log", END)

graph = builder.compile()



agent = create_react_agent(
    llm = "",
    tools=tools
)