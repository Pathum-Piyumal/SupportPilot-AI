FROM ghcr.io/astral-sh/uv:0.11.19 AS uv
FROM python:3.12.13-slim
COPY --from=uv /uv /usr/local/bin/uv
WORKDIR /workspace
COPY pyproject.toml uv.lock ./
COPY apps/api ./apps/api
COPY ml ./ml
RUN uv sync --locked --all-packages --no-dev
RUN useradd --create-home appuser
USER appuser
EXPOSE 8000
CMD [".venv/bin/uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
