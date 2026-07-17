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

    # Embedding (OpenAI-compatible endpoint)
    embed_base_url: str = "https://api.openai.com/v1"
    embed_model: str = "text-embedding-3-small"
    # Falls back to the project-wide OPENAI_API_KEY; set RAG_EMBED_API_KEY (+
    # RAG_EMBED_BASE_URL/RAG_EMBED_MODEL/RAG_EMBED_DIM) to switch to FPT Cloud.
    embed_api_key: str = Field(
        "", validation_alias=AliasChoices("RAG_EMBED_API_KEY", "OPENAI_API_KEY")
    )
    # Dense vector size must match embed_model output:
    # text-embedding-3-small=1536, multilingual-e5-large=1024, Vietnamese_Embedding=1024
    embed_dim: int = 1536

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

    # Ingest source directory, relative to the chatbot-service working dir
    data_dir: str = "../data"


@lru_cache
def get_settings() -> RagSettings:
    return RagSettings()
