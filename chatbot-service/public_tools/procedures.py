from __future__ import annotations

from core.state import ChatState
from public_tools.data_api_client import DataApiClient, DataApiError, get_data_api_client
from public_tools.param_extractor import extract_procedure_code
from public_tools.tool_response import public_evidence, public_tool_patch, upstream_error_patch


TOOL_NAME = "get_procedures"
ENDPOINT = "/procedures"
DEFAULT_PROCEDURE_CODE = "QT.25.01"


async def get_procedures(
    state: ChatState,
    client: DataApiClient | None = None,
) -> dict:
    text = state.get("message") or state.get("normalized_message") or ""
    code = extract_procedure_code(text) or DEFAULT_PROCEDURE_CODE
    data_api = client or get_data_api_client()
    try:
        payload = await data_api.get(ENDPOINT, params={"code": code})
    except DataApiError as exc:
        return upstream_error_patch(
            state=state,
            tool=TOOL_NAME,
            error=exc,
            queried_endpoints=[ENDPOINT],
        )

    procedures = [item for item in payload if isinstance(item, dict)] if isinstance(payload, list) else []
    if not procedures:
        return public_tool_patch(
            state=state,
            tool=TOOL_NAME,
            status="no_data",
            queried_endpoints=[ENDPOINT],
            message="Mình chưa tìm thấy quy trình phù hợp trong dữ liệu công khai.",
            extra={"procedure_code": code},
        )

    return public_tool_patch(
        state=state,
        tool=TOOL_NAME,
        status="ok",
        evidence=[public_evidence("Quy trình khám", {"procedures": procedures})],
        queried_endpoints=[ENDPOINT],
        extra={"procedure_code": code},
    )
