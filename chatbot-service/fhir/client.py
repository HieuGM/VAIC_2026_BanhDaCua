from typing import Any

import httpx

from app.config import get_settings


class FhirClient:
    def __init__(self, base_url: str | None = None, timeout_seconds: float | None = None) -> None:
        settings = get_settings()
        self.base_url = (base_url or settings.fhir_base_url).rstrip("/")
        self.timeout_seconds = timeout_seconds or settings.fhir_request_timeout_seconds

    async def get_resource(self, resource_type: str, resource_id: str) -> dict[str, Any]:
        async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
            response = await client.get(f"{self.base_url}/{resource_type}/{resource_id}")
            response.raise_for_status()
            return response.json()
