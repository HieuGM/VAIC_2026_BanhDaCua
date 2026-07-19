from __future__ import annotations

from core.state import ChatState
from public_tools.data_api_client import DataApiClient, DataApiError, get_data_api_client
from public_tools.param_extractor import extract_bhyt_category
from public_tools.tool_response import public_evidence, public_tool_patch, upstream_error_patch


TOOL_NAME = "get_bhyt_policies"
ENDPOINT = "/bhyt-policies"


async def get_bhyt_policies(
    state: ChatState,
    client: DataApiClient | None = None,
) -> dict:
    text = state.get("message") or state.get("normalized_message") or ""
    category = extract_bhyt_category(text)
    data_api = client or get_data_api_client()
    try:
        payload = await data_api.get(ENDPOINT, params={"category": category})
    except DataApiError as exc:
        return upstream_error_patch(
            state=state,
            tool=TOOL_NAME,
            error=exc,
            queried_endpoints=[ENDPOINT],
        )

    policies = [item for item in payload if isinstance(item, dict)] if isinstance(payload, list) else []
    if not policies:
        return public_tool_patch(
            state=state,
            tool=TOOL_NAME,
            status="no_data",
            queried_endpoints=[ENDPOINT],
            message="Mình chưa tìm thấy thông tin BHYT phù hợp trong dữ liệu công khai.",
            extra={"category": category},
        )

    return public_tool_patch(
        state=state,
        tool=TOOL_NAME,
        status="ok",
        evidence=[public_evidence("Thông tin BHYT", {"policies": policies})],
        queried_endpoints=[ENDPOINT],
        extra={"category": category},
    )
