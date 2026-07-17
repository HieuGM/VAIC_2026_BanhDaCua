from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


class ChatRequest(BaseModel):
    session_id: str | None = Field(default=None, alias="sessionId")
    text: str = Field(min_length=1)
    lang: Literal["vi"] = "vi"
    user_id: str | None = Field(default=None, alias="userId")
    user_role: Literal["ANONYMOUS", "USER", "DOCTOR", "ADMIN"] = Field(
        default="ANONYMOUS",
        alias="userRole",
    )
    allowed_patient_ids: list[str] = Field(default_factory=list, alias="allowedPatientIds")
    context: dict[str, Any] = Field(default_factory=dict)

    model_config = ConfigDict(populate_by_name=True)


class ChatResponse(BaseModel):
    answer: str
    citations: list[dict[str, Any]] = Field(default_factory=list)
    confidence: float = 0.0
    guardrail_flags: list[str] = Field(default_factory=list, alias="guardrailFlags")
    intent: str = "UNKNOWN"
    route: str = "UNSUPPORTED"
    redirection: dict[str, Any] | None = None
    needs_handoff: bool = Field(default=False, alias="needsHandoff")
    metadata: dict[str, Any] = Field(default_factory=dict)

    model_config = ConfigDict(populate_by_name=True)
