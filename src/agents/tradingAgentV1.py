

from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent



client = MultiServerMCPClient(
    {
        "tool_name": {
            "command": "python",
            "args": ["/path to file"],
            "transport": "stdio"
        }
    }
)

tools = client.get_tools()
agent = create_react_agent(
    llm = "",
    tools=tools
)