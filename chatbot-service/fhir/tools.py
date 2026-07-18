from __future__ import annotations

import unicodedata
from typing import Any

from core.contracts import Evidence
from core.enums import Intent
from core.state import ChatState
from fhir.access_control import resolve_allowed_patient_id
from fhir.client import FhirClient, get_fhir_client
from fhir.normalizer import normalize_bundle, normalize_fhir_resource
from fhir.tool_registry import is_allowed_fhir_tool


DEFAULT_LIMIT = 10
MAX_LIMIT = 20


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
    text = _normalized_query(state)
    intent = state.get("intent")

    if _contains_any(text, ["xet nghiem", "ket qua", "lab", "cls"]):
        return await get_lab_results(state, client=client)
    if _contains_any(text, ["don thuoc", "thuoc", "medication"]):
        return await get_medications(state, client=client)
    if _contains_any(text, ["lich hen", "tai kham", "appointment"]):
        return await get_patient_appointments(state, client=client)
    if _contains_any(text, ["lan kham", "luot kham", "encounter"]):
        return await get_patient_encounters(state, client=client)
    if _contains_any(text, ["ho so", "thong tin cua toi"]):
        return await get_patient_profile(state, client=client)

    if intent == Intent.LAB_RESULT.value:
        return await get_lab_results(state, client=client)
    if intent == Intent.MEDICATION_INFORMATION.value:
        return await get_medications(state, client=client)
    if intent == Intent.PATIENT_APPOINTMENT.value:
        return await get_patient_appointments(state, client=client)

    return []


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


def _normalized_query(state: ChatState) -> str:
    value = state.get("normalized_message") or state.get("message") or ""
    text = str(value).lower()
    text = unicodedata.normalize("NFD", text)
    return "".join(char for char in text if unicodedata.category(char) != "Mn")


def _contains_any(text: str, keywords: list[str]) -> bool:
    return any(keyword in text for keyword in keywords)
