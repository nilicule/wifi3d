FROM python:3.13-slim

# uv is only needed at build time to install dependencies
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends fonts-dejavu-core && rm -rf /var/lib/apt/lists/*

# Install dependencies first (cached unless lockfile changes)
COPY pyproject.toml uv.lock ./
RUN uv sync --no-dev --frozen

# Application code
COPY backend/ backend/
COPY frontend/ frontend/

# ROOT_PATH: set to the subpath the app is served from, e.g. /wifi3d
# Leave empty (default) when serving from the domain root.
ENV ROOT_PATH=""
ENV PATH="/app/.venv/bin:$PATH"

EXPOSE 8000

CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
