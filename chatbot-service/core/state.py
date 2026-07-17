from typing import Any, TypedDict


class ChatState(TypedDict, total=False):
    session_id: str | None
    user_id: str | None
    user_role: str
    message: str
    normalized_message: str
    lang: str
    allowed_patient_ids: list[str]
    context: dict[str, Any]

    intent: str
    route: str
    entities: dict[str, Any]
    safety_flags: list[str]

    evidence: list[dict[str, Any]]
    citations: list[dict[str, Any]]
    confidence: float
    answer: str
    redirection: dict[str, Any] | None
    needs_handoff: bool

    error: dict[str, Any] | None
    metadata: dict[str, Any]
