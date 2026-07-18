from __future__ import annotations

from app.config import get_settings
from core.state import ChatState
from public_tools.data_api_client import DataApiClient, DataApiError, get_data_api_client
from public_tools.matcher import page_items
from public_tools.tool_response import public_evidence, public_tool_patch, upstream_error_patch


TOOL_NAME = "get_departments"
ENDPOINT = "/departments"


async def get_departments(
    state: ChatState,
    client: DataApiClient | None = None,
) -> dict:
    data_api = client or get_data_api_client()
    settings = get_settings()
    try:
        payload = await data_api.get(
            ENDPOINT,
            params={"active": True, "page": 0, "size": settings.data_api_list_page_size},
        )
    except DataApiError as exc:
        return upstream_error_patch(
            state=state,
            tool=TOOL_NAME,
            error=exc,
            queried_endpoints=[ENDPOINT],
        )

    departments, truncated, total = page_items(payload)
    if not departments:
        return public_tool_patch(
            state=state,
            tool=TOOL_NAME,
            status="no_data",
            queried_endpoints=[ENDPOINT],
            message="Minh chua tim thay danh sach khoa/phong trong du lieu cong khai.",
            truncated=truncated,
            total=total,
        )

    return public_tool_patch(
        state=state,
        tool=TOOL_NAME,
        status="ok",
        evidence=[public_evidence("Danh sach khoa/phong", {"departments": departments})],
        queried_endpoints=[ENDPOINT],
        truncated=truncated,
        total=total,
    )
