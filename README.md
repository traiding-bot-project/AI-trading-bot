# How to start working on the project
- Install uv
- Install Python 3.12 for uv (`uv python install 3.12`)
- Sync Python version with the .venv (`uv sync`)
- Activate .venv (for linux `source ./.venv/bin/activate`)
- Change code and save files
- Run server using uvicorn (`uv run uvicorn main:app --host 127.0.0.1 --port 8000`)
- Check endpoint:
    - By sending requests to it
    - By checking docs at `127.0.0.1:8000/docs`
 
https://github.com/kweinmeister/agentic-trading
