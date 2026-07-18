from app.config import get_settings
from core.state import ChatState
from public_tools.data_api_client import DataApiClient, DataApiError, get_data_api_client
from public_tools.matcher import page_items, select_best_match
from public_tools.param_extractor import extract_date_range, extract_doctor_query
from public_tools.tool_response import public_evidence, public_tool_patch, upstream_error_patch


TOOL_NAME = "get_doctor_schedule"
DOCTORS_ENDPOINT = "/doctors"


async def get_doctor_schedule(
    state: ChatState,
    client: DataApiClient | None = None,
) -> dict:
    text = state.get("message") or state.get("normalized_message") or ""
    query = extract_doctor_query(text)
    if not query:
        return public_tool_patch(
            state=state,
            tool=TOOL_NAME,
            status="needs_clarification",
            message="Ban vui long cho minh biet ten bac si hoac chuyen khoa can xem lich.",
        )

    data_api = client or get_data_api_client()
    settings = get_settings()
    queried_endpoints = [DOCTORS_ENDPOINT]
    try:
        doctors_payload = await data_api.get(
            DOCTORS_ENDPOINT,
            params={"page": 0, "size": settings.data_api_list_page_size},
        )
    except DataApiError as exc:
        return upstream_error_patch(
            state=state,
            tool=TOOL_NAME,
            error=exc,
            queried_endpoints=queried_endpoints,
        )

    doctors, truncated, total = page_items(doctors_payload)
    match = select_best_match(
        query,
        doctors,
        fields=["fullName", "specialty", "departmentName", "title", "degree", "bio"],
        label_field="fullName",
    )
    if match.status != "ok" or not match.selected:
        return public_tool_patch(
            state=state,
            tool=TOOL_NAME,
            status=match.status,
            options=match.options,
            queried_endpoints=queried_endpoints,
            message=_status_message(match.status),
            truncated=truncated,
            total=total,
            extra={"query": query},
        )

    from_date, to_date = extract_date_range(text)
    schedule_endpoint = f"/doctors/{match.selected['id']}/schedules"
    queried_endpoints.append(schedule_endpoint)
    try:
        schedules = await data_api.get(
            schedule_endpoint,
            params={"from": from_date, "to": to_date},
        )
    except DataApiError as exc:
        return upstream_error_patch(
            state=state,
            tool=TOOL_NAME,
            error=exc,
            queried_endpoints=queried_endpoints,
        )

    rows = [item for item in schedules if isinstance(item, dict)] if isinstance(schedules, list) else []
    return public_tool_patch(
        state=state,
        tool=TOOL_NAME,
        status="ok" if rows else "no_data",
        evidence=[
            public_evidence(
                f"Lich bac si {match.selected.get('fullName') or match.selected.get('id')}",
                {"doctor": match.selected, "schedules": rows},
            )
        ]
        if rows
        else [],
        options=match.options,
        queried_endpoints=queried_endpoints,
        message=None if rows else "Minh chua tim thay lich lam viec phu hop cua bac si nay.",
        truncated=truncated,
        total=total,
        extra={"query": query},
    )


def _status_message(status: str) -> str:
    if status == "needs_selection":
        return "Minh tim thay nhieu bac si/chuyen khoa gan dung. Ban muon xem lich cua ai?"
    if status == "no_data":
        return "Minh chua tim thay bac si/chuyen khoa phu hop trong du lieu cong khai."
    return "Ban vui long bo sung ten bac si hoac chuyen khoa can xem lich."
