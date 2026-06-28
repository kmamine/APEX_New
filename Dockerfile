# API image — runs the FastAPI service. Defaults to the GPU-free `fake` backend
# so the full stack is demoable anywhere. For real local inference, run on a GPU
# host with the `local-gpu` extra and an external vLLM server (see README).
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

WORKDIR /app

COPY pyproject.toml uv.lock README.md ./
COPY src ./src
RUN uv sync --no-dev --frozen

ENV APEX_HOST=0.0.0.0 \
    APEX_PORT=8000 \
    APEX_BACKEND_MODE=fake \
    APEX_RUNS_DIR=/data/runs \
    APEX_PROFILES_DIR=/data/profiles

EXPOSE 8000
CMD ["uv", "run", "uvicorn", "apex.api.app:app", "--host", "0.0.0.0", "--port", "8000"]
