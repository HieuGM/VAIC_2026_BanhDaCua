from __future__ import annotations

from core.enums import Intent
from core.state import ChatState
from fhir.schemas import FhirPlannerDecision
from fhir.tool_registry import is_allowed_fhir_planner_tool


FHIR_TOOL_BY_INTENT = {
    Intent.PATIENT_PROFILE.value: "get_patient_profile",
    Intent.PATIENT_ENCOUNTER.value: "get_patient_encounters",
    Intent.LAB_RESULT.value: "get_lab_results",
    Intent.MEDICATION_INFORMATION.value: "get_medications",
}


class FhirPlannerValidationError(Exception):
    pass


def validate_fhir_planner_decision(
    decision: FhirPlannerDecision,
    state: ChatState,
    *,
    min_confidence: float,
) -> FhirPlannerDecision:
    if decision.tool_name is None:
        return decision

    if not is_allowed_fhir_planner_tool(decision.tool_name):
        raise FhirPlannerValidationError(f"FHIR planner tool is not allowlisted: {decision.tool_name}")

    if decision.confidence < min_confidence:
        raise FhirPlannerValidationError(f"FHIR planner confidence too low: {decision.confidence}")

    expected_tool = FHIR_TOOL_BY_INTENT.get(str(state.get("intent") or ""))
    if expected_tool and decision.tool_name != expected_tool:
        raise FhirPlannerValidationError(
            f"Invalid FHIR intent-tool pair: {state.get('intent')} -> {decision.tool_name}"
        )

    return decision
