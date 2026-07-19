from core.state import ChatState
from public_tools.data_api_client import DataApiClient, DataApiError, get_data_api_client
from public_tools.tool_response import public_evidence, public_tool_patch, upstream_error_patch


TOOL_NAME = "get_booking_channels"
ENDPOINT = "/channels"


async def get_booking_channels(
    state: ChatState,
    client: DataApiClient | None = None,
) -> dict:
    data_api = client or get_data_api_client()
    try:
        payload = await data_api.get(ENDPOINT)
    except DataApiError as exc:
        return upstream_error_patch(
            state=state,
            tool=TOOL_NAME,
            error=exc,
            queried_endpoints=[ENDPOINT],
        )

    channels = [item for item in payload if isinstance(item, dict)] if isinstance(payload, list) else []
    if not channels:
        return public_tool_patch(
            state=state,
            tool=TOOL_NAME,
            status="no_data",
            queried_endpoints=[ENDPOINT],
            message="Mình chưa tìm thấy kênh đặt lịch/hỗ trợ trong dữ liệu công khai.",
        )

    return public_tool_patch(
        state=state,
        tool=TOOL_NAME,
        status="ok",
        evidence=[
            public_evidence(
                "Kênh đặt lịch/hỗ trợ",
                {"channels": channels},
            )
        ],
        queried_endpoints=[ENDPOINT],
        redirection=_first_redirection(channels),
    )


def _first_redirection(channels: list[dict]) -> dict | None:
    for channel in channels:
        if channel.get("url") or channel.get("phone"):
            return {
                "type": "booking_channel",
                "label": channel.get("label") or channel.get("channelType"),
                "url": channel.get("url"),
                "phone": channel.get("phone"),
            }
    return None
