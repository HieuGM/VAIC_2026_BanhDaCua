from __future__ import annotations

from typing import Any

import httpx

from app.config import get_settings


class DataApiError(Exception):
    def __init__(
        self,
        user_message: str,
        detail: str | None = None,
        *,
        status_code: int | None = None,
    ) -> None:
        super().__init__(detail or user_message)
        self.user_message = user_message
        self.detail = detail or user_message
        self.status_code = status_code


class DataApiClient:
    def __init__(
        self,
        *,
        base_url: str,
        api_key: str | None = None,
        timeout_seconds: float = 10,
        transport: httpx.AsyncBaseTransport | None = None,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.timeout_seconds = timeout_seconds
        self.transport = transport

    async def get(self, path: str, params: dict[str, Any] | None = None) -> Any:
        url = self._url(path)
        headers = {"Accept": "application/json"}
        if self.api_key:
            headers["X-API-Key"] = self.api_key

        try:
            async with httpx.AsyncClient(
                timeout=self.timeout_seconds,
                transport=self.transport,
            ) as client:
                response = await client.get(url, params=_compact_params(params), headers=headers)
                response.raise_for_status()
                return response.json()
        except httpx.HTTPStatusError as exc:
            raise DataApiError(
                "Không thể lấy dữ liệu công khai từ hệ thống.",
                f"Data API returned HTTP {exc.response.status_code}.",
                status_code=exc.response.status_code,
            ) from exc
        except httpx.RequestError as exc:
            raise DataApiError(
                "Hệ thống dữ liệu công khai hiện không khả dụng.",
                str(exc),
            ) from exc
        except ValueError as exc:
            raise DataApiError(
                "Hệ thống dữ liệu công khai trả về dữ liệu không hợp lệ.",
                str(exc),
            ) from exc

    def _url(self, path: str) -> str:
        return f"{self.base_url}/{path.lstrip('/')}"


def get_data_api_client() -> DataApiClient:
    settings = get_settings()
    return DataApiClient(
        base_url=settings.data_api_base_url,
        api_key=settings.data_api_key,
        timeout_seconds=settings.data_api_timeout_seconds,
    )


def _compact_params(params: dict[str, Any] | None) -> dict[str, Any] | None:
    if not params:
        return None
    return {
        key: value
        for key, value in params.items()
        if value not in (None, "", [], {})
    }
