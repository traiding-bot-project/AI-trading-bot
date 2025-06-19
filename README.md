# AI Trading Bot

## How to setup venv for this project

- Install uv
- Install Python 3.12 for uv (`uv python install 3.12`)
- Sync Python version with the .venv (`uv sync`)
- Activate .venv (for linux `source ./.venv/bin/activate`)

## How to manually test changes

### To check FastAPI endpoints you should run a server and manually check links.

- Run server `python main.py`
- Check endpoint:
  - By sending requests to it
  - By checking docs at `http://127.0.0.1:8000/docs` or `http://localhost:8000/docs`

### To check anything from MCP server you should run a server and use Inspector

There are 2 ways how to check if your MCP server works correctly:

- `Streamable HTTP` - Use route requests through FastAPI server
(test if routing and components work)
- `stdio` - Creates MCP server without FastAPI using CLI command
(test if components work)

Common part for both of these ways:

- Run server `python main.py`
- Run Inspector `PYTHONPATH=./ mcp dev ./src/server/server.py`
- Open `http://127.0.0.1:6274` or `http://localhost:6274` or click
on the link with set `MCP_PROXY_AUTH_TOKEN`
(`http://localhost:6274/?MCP_PROXY_AUTH_TOKEN=...`)
- In case you opened Inspector without `MCP_PROXY_AUTH_TOKEN` set
`Proxy Session Token` in the `Configuration` section on the
left (copy session token from cli)

For the `Streamable HTTP`:

- On the left in the URL field write a route to the Streamable HTTP endpoint for
the MCP server (right now `http://localhost:8000/mcp`)
- On the left click `Connect`

For the `stdio`:
- On the left click `Connect`

For testing:

- Use top menu to switch between resources, prompts, tools and other components
- Get latest components by clicking `List <items>` where `items`
represent the type of component you want to get
- Click on the component and try to run it

Example of an AI trading bot - <https://github.com/kweinmeister/agentic-trading>
