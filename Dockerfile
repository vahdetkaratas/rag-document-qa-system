# Production-oriented image: full project root copied; artifacts must exist under artifacts/ (bake after local indexing).
# Build from repo root after: run_extraction → run_chunking → indexing_pipeline
FROM python:3.11-slim-bookworm

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Ensure `import src` works regardless of process cwd (e.g. some process managers).
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

EXPOSE 8000

# Bind all interfaces so reverse proxy / Docker port publish can reach the API.
CMD ["uvicorn", "src.api.app:app", "--host", "0.0.0.0", "--port", "8000"]
