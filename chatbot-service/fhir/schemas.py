from typing import Literal

from pydantic import BaseModel, Field


FhirToolName = Literal[
    "get_patient_profile",
    "get_patient_appointments",
    "get_patient_encounters",
    "get_lab_results",
    "get_medications",
]


class FhirToolCall(BaseModel):
    tool_name: FhirToolName
    patient_id: str | None = None
    limit: int = Field(default=10, ge=1, le=20)


FhirPlannerToolName = Literal[
    "get_patient_profile",
    "get_patient_encounters",
    "get_lab_results",
    "get_medications",
]
FhirPlannerSource = Literal["llm", "rule", "fallback"]


class FhirPlannerDecision(BaseModel):
    tool_name: FhirPlannerToolName | None = None
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    reason: str | None = None
    source: FhirPlannerSource = "fallback"
