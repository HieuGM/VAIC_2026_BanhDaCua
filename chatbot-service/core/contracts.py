from typing import Any

from pydantic import BaseModel, Field

from core.enums import Intent, Route, SourceType


class Citation(BaseModel):
    source: str
    title: str
    chunk_id: str | None = None
    url: str | None = None
    snippet: str | None = None
    updated_at: str | None = None


class Evidence(BaseModel):
    source_type: SourceType
    title: str
    content: str | None = None
    data: dict[str, Any] | None = None
    citation: Citation | None = None
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    updated_at: str | None = None


class RouteDecision(BaseModel):
    route: Route
    intent: Intent = Intent.UNKNOWN
    entities: dict[str, Any] = Field(default_factory=dict)
    reason: str | None = None
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)


class ToolResult(BaseModel):
    ok: bool
    evidence: list[Evidence] = Field(default_factory=list)
    error_code: str | None = None
    message: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
