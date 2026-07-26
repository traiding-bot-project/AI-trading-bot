# syntax=docker/dockerfile:1
#
# The build context MUST be ./src so the local path dependency `market_intel_lib`
# (pinned by every service as `market-intel-lib = { path = "../market_intel_lib" }`)
# is available inside the build.

FROM ghcr.io/astral-sh/uv:python3.14-bookworm-slim

ARG SERVICE
ENV SERVICE=${SERVICE}

ENV UV_PYTHON_DOWNLOADS=0 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Shared library first — mirrors the src/ layout so `../market_intel_lib` resolves
# from the service directory exactly as it does locally.
COPY market_intel_lib/ ./market_intel_lib/

COPY ${SERVICE}/ ./${SERVICE}/

# Promote the docker-variant configs over the local-dev defaults, so the image is
# self-contained (no host bind-mounts needed). Hosts become compose service DNS
# names, uvicorn binds 0.0.0.0, and the LLM points at host.docker.internal.
# Done BEFORE `uv sync` so the baked lib settings land in the installed package.
#
# `set -eux` + explicit mv: fail loudly if an expected variant goes missing.
RUN set -eux; \
    mv market_intel_lib/market_intel_lib/settings/settings.docker.toml \
       market_intel_lib/market_intel_lib/settings/settings.toml; \
    for f in "${SERVICE}"/src/settings/*.docker.toml; do \
        [ -e "$f" ] || continue; \
        mv "$f" "${f%.docker.toml}.toml"; \
    done; \
    if [ -e "${SERVICE}/alembic.docker.ini" ]; then \
        mv "${SERVICE}/alembic.docker.ini" "${SERVICE}/alembic.ini"; \
    fi

WORKDIR /app/${SERVICE}

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --all-extras --frozen

ENV PATH="/app/${SERVICE}/.venv/bin:${PATH}"

CMD ["uv", "run", "run-fastapi"]
