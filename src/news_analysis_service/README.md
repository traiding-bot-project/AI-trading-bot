# News service

## How to run AI model in docker

- docker model pull ai/llama3.2:1B-Q8_0
- docker model run ai/llama3.2:1B-Q8_0

## How to run RabbitMQ in docker

- docker run --name my-rabbit -p 5672:5672 rabbitmq:4.2.4-management

## Good source materials

- [litellm](https://github.com/BerriAI/litellm/tree/main)
- [Docker DMR](https://docs.docker.com/ai/model-runner/api-reference)

## Fix to the problem with code running on WSL2 and models hosted on Windowses localhost

```bash
echo [wsl2] > %USERPROFILE%\.wslconfig
echo networkingMode=mirrored >> %USERPROFILE%\.wslconfig
wsl --shutdown
```

## Architecture and workflow

### Overview
The News Analysis Service is built around two runtime modes:
- `FastAPI` web server for live API requests
- `RabbitMQ` worker for queued content analysis tasks

Both modes share the same core AI analysis pipeline:
- request input -> `AIContentAnalyzer` -> `OllamaService` -> external Ollama API

### FastAPI workflow
- `src/scripts/run_fastapi.py` loads settings and starts the FastAPI server.
- `src/fastapi/app.py` exposes `/health` and `/api/ollama` routes.
- `/api/ollama/generate` and `/api/ollama/tags` call `src.interfaces.content_analyzer`.
- `src/interfaces/content_analyzer.py` wraps the `OllamaService` implementation.
- `src/services/ollama.py` sends requests to the Ollama API and returns results.

```mermaid
flowchart LR
    A[run_fastapi.py] --> B[FastAPI app]
    B --> C[/health]
    B --> D[/api/ollama/generate]
    B --> E[/api/ollama/tags]
    D --> F[AIContentAnalyzer]
    E --> F
    F --> G[OllamaService]
    G --> H[Ollama API]
    A --> I[FastAPI settings TOML]
    I --> B
```

### RabbitMQ worker workflow
- `src/scripts/run_mq_worker.py` loads RabbitMQ settings and starts a consuming worker.
- Messages arrive on the configured input queue(s).
- The worker deserializes a `AnalyzeContentRequest`.
- It uses the same `AIContentAnalyzer` pipeline to generate a response.
- The result is published back to the configured send queue(s).

```mermaid
flowchart LR
    A[run_mq_worker.py] --> B[RabbitMQ exchange]
    B --> C[Receive queue(s)]
    C --> D[Worker on_message]
    D --> E[AIContentAnalyzer]
    E --> F[OllamaService]
    F --> G[Ollama API]
    D --> H[Send queue(s)]
    A --> I[MQ worker settings TOML]
```

### Configuration
- `src/settings/settings.toml` holds general service settings and AI model connection details.
- `src/settings/fastapi_settings.toml` holds FastAPI host/port configuration.
- `src/settings/mq_worker_settings.toml` holds RabbitMQ connection and queue settings.

This architecture makes the service easy to use for both synchronous HTTP requests and asynchronous queued tasks.
