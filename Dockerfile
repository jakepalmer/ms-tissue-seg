# syntax=docker/dockerfile:1
FROM python:3.11-slim AS builder

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

ENV PYTHONUNBUFFERED=1 \
    UV_LINK_MODE=copy \
    UV_VENV_PATH=/opt/.venv

COPY --from=ghcr.io/astral-sh/uv:0.8.11 /uv /uvx /bin/

WORKDIR /opt

COPY uv.lock pyproject.toml ./

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen

# Final stage - smaller image
FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

ENV PYTHONUNBUFFERED=1 \
    UV_VENV_PATH=/opt/.venv

# Copy only the venv, not build tools
COPY --from=builder /opt/.venv /opt/.venv
COPY --from=ghcr.io/astral-sh/uv:0.8.11 /uv /uvx /bin/

ENV PATH="/opt/.venv/bin:$PATH"

WORKDIR /home

CMD ["bash"]