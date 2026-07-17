"""RAG-scoped settings.

Separate from app/config.py on purpose: the RAG owner only touches rag/**,
so all knobs live here under the RAG_ env prefix (e.g. RAG_EMBED_API_KEY).

Embedding + rerank endpoints are OpenAI-compatible so the same client works
with OpenAI or FPT Cloud (multilingual-e5-large / Vietnamese_Embedding).
"""

from functools import lru_cache

from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class RagSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="RAG_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Embedding provider: "sentence_transformers" (local, e.g. bge-m3) or
    # "openai" (OpenAI-compatible HTTP API: OpenAI / FPT Cloud).
    embed_provider: str = "sentence_transformers"
    embed_model: str = "BAAI/bge-m3"
    # Dense vector size must match embed_model output:
    # bge-m3=1024, text-embedding-3-small=1536, multilingual-e5-large=1024
    embed_dim: int = 1024

    # Local (sentence_transformers) knobs
    embed_device: str = "auto"  # auto -> cuda if available else cpu
    embed_max_seq_length: int = 512  # chunks are short; caps memory
    embed_batch_size: int = 32

    # OpenAI-compatible API knobs (used when embed_provider == "openai")
    embed_base_url: str = "https://api.openai.com/v1"
    # Falls back to the project-wide OPENAI_API_KEY; set RAG_EMBED_API_KEY (+
    # RAG_EMBED_BASE_URL/RAG_EMBED_MODEL/RAG_EMBED_DIM) for FPT Cloud.
    embed_api_key: str = Field(
        "", validation_alias=AliasChoices("RAG_EMBED_API_KEY", "OPENAI_API_KEY")
    )

    # Rerank (chat-completion endpoint, cheap model; may differ from embedding provider)
    rerank_base_url: str = "https://api.openai.com/v1"
    rerank_model: str = "gpt-4o-mini"
    rerank_api_key: str = Field(
        "", validation_alias=AliasChoices("RAG_RERANK_API_KEY", "OPENAI_API_KEY")
    )
    rerank_enabled: bool = True
    rerank_min_score: float = 0.3

    # Qdrant embedded local storage (no Docker). See kb_store.py for the
    # single-process lock caveat.
    qdrant_path: str = "./.qdrant_data"
    collection: str = "hospital_kb"
    sparse_model: str = "Qdrant/bm25"

    # Retrieval tuning
    prefetch_limit: int = 20  # candidates per branch (dense/sparse) before RRF fusion
    rerank_top_k: int = 5  # final number of evidence chunks returned
    # Return [] when the top dense cosine is below this — measured on the eval
    # set: in-domain top-1 cosine min 0.575, off-topic max 0.502.
    dense_min_score: float = 0.5

    # Ingest source directory, relative to the chatbot-service working dir
    data_dir: str = "../data"


@lru_cache
def get_settings() -> RagSettings:
    return RagSettings()
