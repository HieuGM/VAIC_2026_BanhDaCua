# syntax=docker/dockerfile:1
#
# chatbot-service (FastAPI + LangGraph RAG).
# Multi-stage: build a venv in `builder`, copy only the venv + app into a slim runtime.
#
# Build context = repo ROOT (.) so this Dockerfile can COPY both the service code
# (chatbot-service/) and the knowledge base (data/, ~828K — baked in so the image is
# self-contained for one-shot ingest). docker-compose uses:
#     build: { context: ., dockerfile: chatbot-service/Dockerfile }
#
# RAG runs hosted embedding (NVIDIA NIM bge-m3) + hosted rerank (FPT Cloud), so the
# heavy local models (torch/sentence-transformers ~2GB RAM) are installed but never
# loaded at runtime → low RAM. fastembed (BM25 sparse) is imported unconditionally
# and is therefore required.

# ---- Builder: install deps into a reusable venv (cached layer) ----
FROM python:3.11-slim AS builder
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1
WORKDIR /app

COPY chatbot-service/requirements.txt ./requirements.txt
RUN python -m venv /opt/venv \
 && /opt/venv/bin/pip install --upgrade pip \
 && /opt/venv/bin/pip install -r requirements.txt

# ---- Runtime: slim, non-root, code + KB baked in ----
FROM python:3.11-slim AS runtime
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/opt/venv/bin:${PATH}" \
    # KB source lives inside the image (baked); override the default ../data.
    RAG_DATA_DIR=/app/data
WORKDIR /app

# Non-root user for the running process.
RUN useradd -r -u 1001 -m -d /home/chatbot chatbot

# Reusable venv from builder (read-only system install).
COPY --from=builder /opt/venv /opt/venv

# App code + baked knowledge base.
COPY chatbot-service/ /app/
COPY data/ /app/data/

# Qdrant embedded storage on a named volume (compose mounts /app/.qdrant_data).
# Pre-create + own it so the named-volume copy-up preserves chatbot ownership.
RUN mkdir -p /app/.qdrant_data && chown -R chatbot:chatbot /app

USER chatbot
EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
  CMD python -c "import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://127.0.0.1:8000/health',timeout=3).status==200 else 1)"

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
