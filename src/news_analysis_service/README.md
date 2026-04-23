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
The News Analysis Service contains two execution modes:
- `FastAPI` server for synchronous API requests
- RabbitMQ worker for asynchronous queued processing

Both entrypoints share the same AI analysis pipeline:
- request -> `AIContentAnalyzer` -> `OllamaService` -> external Ollama API

### FastAPI workflow
- `src/scripts/run_fastapi.py` loads application and FastAPI settings.
- `src/fastapi/app.py` creates the FastAPI application and mounts `/api/ollama`.
- `src/fastapi/ollama.py` defines `/generate` and `/tags` endpoints.
- `src/interfaces/__init__.py` creates `AIContentAnalyzer` with the selected AI service.
- `src/interfaces/content_analyzer.py` forwards requests to `src/services/ollama.py`.
- `src/services/ollama.py` calls the configured Ollama API and returns the parsed response.

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
- `src/scripts/run_mq_worker.py` loads RabbitMQ settings and connects to the broker.
- It declares the exchange and bind queues from `mq_worker_settings.toml`.
- Incoming messages are deserialized to `AnalyzeContentRequest`.
- `content_analyzer.analyze_content()` uses the same AI pipeline and `OllamaService`.
- The worker publishes the `AnalyzeContentResponse` to configured send queue(s).

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
- `src/settings/settings.toml` contains the general service and AI model configuration.
- `src/settings/fastapi_settings.toml` defines FastAPI host/port settings.
- `src/settings/mq_worker_settings.toml` defines RabbitMQ connection and queue settings.

This service design keeps synchronous HTTP analysis and asynchronous RabbitMQ processing consistent through the same AI service abstraction.
