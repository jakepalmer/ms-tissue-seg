# syntax=docker/dockerfile:1
# Keep this syntax directive! It's used to enable Docker BuildKit
FROM python:3.11

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Python
ENV PYTHONUNBUFFERED=1 \
    # Compile bytecode
    # Ref: https://docs.astral.sh/uv/guides/integration/docker/#compiling-bytecode
    UV_COMPILE_BYTECODE=1 \
    # Cache
    # Ref: https://docs.astral.sh/uv/guides/integration/docker/#caching
    UV_LINK_MODE=hardlink \
    # Skip updating environment in the container
    # Ref: https://docs.astral.sh/uv/reference/environment/#uv_no_sync
    UV_NO_SYNC=1

# Install uv
# Ref: https://docs.astral.sh/uv/guides/integration/docker/#installing-uv
COPY --from=ghcr.io/astral-sh/uv:0.8.11 /uv /uvx /bin/

WORKDIR /home

COPY uv.lock pyproject.toml ./
RUN uv sync --frozen
