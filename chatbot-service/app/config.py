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
    use_llm_router: bool = True
    llm_router_min_confidence: float = 0.65
    llm_router_timeout_seconds: float = 10
    model_route: str | None = None
    use_llm_fhir_planner: bool = True
    fhir_planner_min_confidence: float = 0.65
    fhir_planner_timeout_seconds: float = 8
    model_fhir_planner: str | None = None

    fhir_base_url: str = "http://localhost:8080/fhir"
    fhir_request_timeout_seconds: float = 20

    data_api_base_url: str = "http://localhost:8081/data/v1"
    data_api_key: str | None = None
    data_api_timeout_seconds: float = 10
    data_api_list_page_size: int = 100

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
