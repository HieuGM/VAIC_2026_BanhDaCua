from __future__ import annotations

from typing import Any

from core.contracts import Evidence
from core.enums import SourceType
from core.state import ChatState
from public_tools.data_api_client import DataApiError


def public_evidence(title: str, data: dict[str, Any], *, confidence: float = 0.9) -> dict[str, Any]:
    return Evidence(
        source_type=SourceType.PUBLIC_API,
        title=title,
        data=data,
        confidence=confidence,
    ).model_dump(mode="json")


def public_tool_patch(
    *,
    state: ChatState | None = None,
    tool: str,
    status: str,
    evidence: list[dict[str, Any]] | None = None,
    options: list[dict[str, Any]] | None = None,
    queried_endpoints: list[str] | None = None,
    redirection: dict[str, Any] | None = None,
    message: str | None = None,
    truncated: bool = False,
    total: int | None = None,
    extra: dict[str, Any] | None = None,
) -> dict[str, Any]:
    metadata = dict((state or {}).get("metadata") or {})
    metadata["public_tool"] = {
        "tool": tool,
        "status": status,
        "options": options or [],
        "queried_endpoints": queried_endpoints or [],
        "message": message,
        "truncated": truncated,
        "total": total,
        **(extra or {}),
    }
    patch: dict[str, Any] = {
        "evidence": evidence or [],
        "metadata": metadata,
    }
    if redirection is not None:
        patch["redirection"] = redirection
    return patch


def upstream_error_patch(
    *,
    state: ChatState | None = None,
    tool: str,
    error: DataApiError,
    queried_endpoints: list[str] | None = None,
) -> dict[str, Any]:
    return public_tool_patch(
        state=state,
        tool=tool,
        status="upstream_error",
        queried_endpoints=queried_endpoints or [],
        message=error.user_message,
        extra={"error_detail": error.detail, "status_code": error.status_code},
    )
