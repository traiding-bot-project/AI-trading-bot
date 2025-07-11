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
agent = create_react_agent(
    llm = "",
    tools=tools
)