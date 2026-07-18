from app.config import get_settings
from core.state import ChatState
from public_tools.data_api_client import DataApiClient, DataApiError, get_data_api_client
from public_tools.matcher import page_items, select_best_match
from public_tools.param_extractor import extract_service_category, extract_service_query
from public_tools.tool_response import public_evidence, public_tool_patch, upstream_error_patch


TOOL_NAME = "get_service_prices"
SERVICES_ENDPOINT = "/services"


async def get_service_prices(
    state: ChatState,
    client: DataApiClient | None = None,
) -> dict:
    text = state.get("message") or state.get("normalized_message") or ""
    query = extract_service_query(text)
    if not query:
        return public_tool_patch(
            state=state,
            tool=TOOL_NAME,
            status="needs_clarification",
            message="Ban vui long cho minh biet ten dich vu can tra cuu gia.",
        )

    data_api = client or get_data_api_client()
    settings = get_settings()
    category = _api_category(extract_service_category(text))
    queried_endpoints = [SERVICES_ENDPOINT]
    try:
        services_payload = await data_api.get(
            SERVICES_ENDPOINT,
            params={
                "category": category,
                "page": 0,
                "size": settings.data_api_list_page_size,
            },
        )
    except DataApiError as exc:
        return upstream_error_patch(
            state=state,
            tool=TOOL_NAME,
            error=exc,
            queried_endpoints=queried_endpoints,
        )

    services, truncated, total = page_items(services_payload)
    match = select_best_match(
        query,
        services,
        fields=["name", "code", "category", "description"],
        label_field="name",
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
            extra={"query": query, "category": category},
        )

    prices_endpoint = f"/services/{match.selected['id']}/prices"
    queried_endpoints.append(prices_endpoint)
    try:
        prices_payload = await data_api.get(prices_endpoint)
    except DataApiError as exc:
        return upstream_error_patch(
            state=state,
            tool=TOOL_NAME,
            error=exc,
            queried_endpoints=queried_endpoints,
        )

    prices = [item for item in prices_payload if isinstance(item, dict)] if isinstance(prices_payload, list) else []
    return public_tool_patch(
        state=state,
        tool=TOOL_NAME,
        status="ok" if prices else "no_data",
        evidence=[
            public_evidence(
                f"Gia dich vu {match.selected.get('name') or match.selected.get('id')}",
                {"service": match.selected, "prices": prices},
            )
        ]
        if prices
        else [],
        options=match.options,
        queried_endpoints=queried_endpoints,
        message=None if prices else "Minh chua tim thay bang gia cong khai cho dich vu nay.",
        truncated=truncated,
        total=total,
        extra={"query": query, "category": category},
    )


def _api_category(category: str | None) -> str | None:
    if category == "imaging":
        return "ct"
    return category


def _status_message(status: str) -> str:
    if status == "needs_selection":
        return "Minh tim thay nhieu dich vu gan dung. Ban muon tra cuu dich vu nao?"
    if status == "no_data":
        return "Minh chua tim thay dich vu phu hop trong du lieu cong khai."
    return "Ban vui long bo sung ten dich vu can tra cuu gia."
