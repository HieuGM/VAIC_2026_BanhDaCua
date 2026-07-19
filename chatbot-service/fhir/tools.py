from __future__ import annotations

from typing import Any

from core.contracts import Evidence
from core.state import ChatState
from fhir.access_control import resolve_allowed_patient_id
from fhir.client import FhirClient, get_fhir_client
from fhir.normalizer import normalize_bundle, normalize_fhir_resource
from fhir.planner import plan_fhir_tool
from fhir.schemas import FhirPlannerDecision
from fhir.tool_registry import is_allowed_fhir_tool


DEFAULT_LIMIT = 10
MAX_LIMIT = 20
FHIR_PLANNER_METADATA_KEY = "fhir_planner"


async def get_patient_profile(state: ChatState, client: FhirClient | None = None) -> list[Evidence]:
    _ensure_allowed_tool("get_patient_profile")
    patient_id = resolve_allowed_patient_id(state)
    resource = await _client(client).get_patient(patient_id)
    return [normalize_fhir_resource(resource)]


async def get_patient_appointments(state: ChatState, client: FhirClient | None = None) -> list[Evidence]:
    _ensure_allowed_tool("get_patient_appointments")
    return await _search_patient_resource(
        state,
        resource_type="Appointment",
        client=client,
        sort="-date",
    )


async def get_patient_encounters(state: ChatState, client: FhirClient | None = None) -> list[Evidence]:
    _ensure_allowed_tool("get_patient_encounters")
    return await _search_patient_resource(
        state,
        resource_type="Encounter",
        client=client,
        sort="-date",
    )


async def get_lab_results(state: ChatState, client: FhirClient | None = None) -> list[Evidence]:
    _ensure_allowed_tool("get_lab_results")
    observations = await _search_patient_resource(
        state,
        resource_type="Observation",
        client=client,
        sort="-date",
    )
    diagnostic_reports = await _search_patient_resource(
        state,
        resource_type="DiagnosticReport",
        client=client,
        sort="-date",
    )
    return [*observations, *diagnostic_reports]


async def get_medications(state: ChatState, client: FhirClient | None = None) -> list[Evidence]:
    _ensure_allowed_tool("get_medications")
    return await _search_patient_resource(
        state,
        resource_type="MedicationRequest",
        client=client,
        sort="-authoredon",
    )


async def retrieve_fhir_evidence(state: ChatState, client: FhirClient | None = None) -> list[Evidence]:
    decision = await plan_fhir_tool(state)
    _store_planner_metadata(state, decision)

    if decision.tool_name is None:
        return []

    executor = _FHIR_TOOL_EXECUTORS.get(decision.tool_name)
    if executor is None:
        return []
    return await executor(state, client=client)


async def _search_patient_resource(
    state: ChatState,
    *,
    resource_type: str,
    client: FhirClient | None,
    sort: str | None = None,
) -> list[Evidence]:
    patient_id = resolve_allowed_patient_id(state)
    bundle = await _client(client).search_patient_resources(
        resource_type,
        patient_id,
        count=_limit_from_state(state),
        sort=sort,
    )
    return normalize_bundle(bundle, resource_type)


def _client(client: FhirClient | None) -> FhirClient:
    return client or get_fhir_client()


_FHIR_TOOL_EXECUTORS = {
    "get_patient_profile": get_patient_profile,
    "get_patient_encounters": get_patient_encounters,
    "get_lab_results": get_lab_results,
    "get_medications": get_medications,
}


def _ensure_allowed_tool(tool_name: str) -> None:
    if not is_allowed_fhir_tool(tool_name):
        raise ValueError(f"FHIR tool is not allowlisted: {tool_name}")


def _limit_from_state(state: ChatState) -> int:
    context = state.get("context")
    raw_limit: Any = context.get("limit") if isinstance(context, dict) else None
    try:
        limit = int(raw_limit)
    except (TypeError, ValueError):
        limit = DEFAULT_LIMIT
    return max(1, min(limit, MAX_LIMIT))


def _store_planner_metadata(state: ChatState, decision: FhirPlannerDecision) -> None:
    metadata = dict(state.get("metadata") or {})
    metadata[FHIR_PLANNER_METADATA_KEY] = {
        "source": decision.source,
        "selected_tool": decision.tool_name,
        "confidence": decision.confidence,
        "reason": decision.reason,
    }
    state["metadata"] = metadata
