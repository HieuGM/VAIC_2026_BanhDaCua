from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Hanoi Heart Hospital Chatbot Service"
    api_prefix: str = "/api/v1"
    max_input_chars: int = 2000

    llm_provider: str = "openai"
    model_simple: str = "gpt-4o-mini"
    model_complex: str = "gpt-4.1-mini"
    openai_api_key: str | None = None
    openai_base_url: str | None = None
    llm_request_timeout_seconds: float = 20

    fhir_base_url: str = "http://localhost:8080/fhir"
    fhir_request_timeout_seconds: float = 20

    qdrant_url: str = "http://localhost:6333"
    rag_collection_name: str = "hanoi_heart_hospital_kb"

    booking_website_url: str | None = None
    booking_zalo_url: str | None = None
    hotline: str | None = None
    emergency_number: str = "115"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
