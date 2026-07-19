from __future__ import annotations

from core.state import ChatState
from public_tools.data_api_client import DataApiClient, DataApiError, get_data_api_client
from public_tools.tool_response import public_evidence, public_tool_patch, upstream_error_patch


TOOL_NAME = "get_hospital_info"
ENDPOINT = "/hospital-info"


async def get_hospital_info(
    state: ChatState,
    client: DataApiClient | None = None,
) -> dict:
    data_api = client or get_data_api_client()
    try:
        info = await data_api.get(ENDPOINT)
    except DataApiError as exc:
        return upstream_error_patch(
            state=state,
            tool=TOOL_NAME,
            error=exc,
            queried_endpoints=[ENDPOINT],
        )

    if not isinstance(info, dict) or not info:
        return public_tool_patch(
            state=state,
            tool=TOOL_NAME,
            status="no_data",
            queried_endpoints=[ENDPOINT],
            message="Mình chưa tìm thấy thông tin bệnh viện trong dữ liệu công khai.",
        )

    return public_tool_patch(
        state=state,
        tool=TOOL_NAME,
        status="ok",
        evidence=[public_evidence("Thông tin bệnh viện", {"hospital_info": info})],
        queried_endpoints=[ENDPOINT],
        redirection=_contact_redirection(info),
    )


def _contact_redirection(info: dict) -> dict | None:
    if not info.get("hotline") and not info.get("website"):
        return None
    return {
        "type": "hospital_contact",
        "hotline": info.get("hotline"),
        "website": info.get("website"),
    }
