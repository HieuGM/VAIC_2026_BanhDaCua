from __future__ import annotations

from typing import Any

from core.contracts import Evidence
from core.enums import SourceType


def normalize_fhir_resource(resource: dict[str, Any]) -> Evidence:
    normalized = normalize_resource_data(resource)
    resource_type = normalized.get("resource_type") or resource.get("resourceType") or "FHIR"
    resource_id = normalized.get("id") or resource.get("id") or "unknown"
    return Evidence(
        source_type=SourceType.FHIR,
        title=f"{resource_type}/{resource_id}",
        data=normalized,
        confidence=1.0,
        updated_at=_updated_at(normalized),
    )


def normalize_bundle(bundle: dict[str, Any], resource_type: str) -> list[Evidence]:
    return [
        normalize_fhir_resource(entry["resource"])
        for entry in bundle.get("entry", [])
        if isinstance(entry, dict)
        and isinstance(entry.get("resource"), dict)
        and entry["resource"].get("resourceType") == resource_type
    ]


def normalize_resource_data(resource: dict[str, Any]) -> dict[str, Any]:
    resource_type = resource.get("resourceType")
    if resource_type == "Patient":
        return normalize_patient(resource)
    if resource_type == "Appointment":
        return normalize_appointment(resource)
    if resource_type == "Encounter":
        return normalize_encounter(resource)
    if resource_type == "Observation":
        return normalize_observation(resource)
    if resource_type == "DiagnosticReport":
        return normalize_diagnostic_report(resource)
    if resource_type == "MedicationRequest":
        return normalize_medication_request(resource)
    return {
        "resource_type": resource_type or "FHIR",
        "id": resource.get("id"),
    }


def normalize_patient(resource: dict[str, Any]) -> dict[str, Any]:
    return _compact(
        {
            "resource_type": "Patient",
            "id": resource.get("id"),
            "active": resource.get("active"),
            "name": _human_name(_first(resource.get("name"))),
            "gender": resource.get("gender"),
            "birth_date": resource.get("birthDate"),
            "identifier": _identifiers(resource.get("identifier", [])),
            "telecom": _telecom(resource.get("telecom", [])),
        }
    )


def normalize_appointment(resource: dict[str, Any]) -> dict[str, Any]:
    return _compact(
        {
            "resource_type": "Appointment",
            "id": resource.get("id"),
            "status": resource.get("status"),
            "service_type": [_codeable_concept(item) for item in resource.get("serviceType", []) if isinstance(item, dict)],
            "appointment_type": _codeable_concept(resource.get("appointmentType", {})),
            "description": resource.get("description"),
            "start": resource.get("start"),
            "end": resource.get("end"),
            "created": resource.get("created"),
            "participant": [_appointment_participant(item) for item in resource.get("participant", []) if isinstance(item, dict)],
            "reason_code": [_codeable_concept(item) for item in resource.get("reasonCode", []) if isinstance(item, dict)],
        }
    )


def normalize_encounter(resource: dict[str, Any]) -> dict[str, Any]:
    return _compact(
        {
            "resource_type": "Encounter",
            "id": resource.get("id"),
            "status": resource.get("status"),
            "class": _coding(resource.get("class", {})),
            "type": [_codeable_concept(item) for item in resource.get("type", []) if isinstance(item, dict)],
            "service_type": _codeable_concept(resource.get("serviceType", {})),
            "subject": _reference(resource.get("subject", {})),
            "period": resource.get("period"),
            "participant": [_encounter_participant(item) for item in resource.get("participant", []) if isinstance(item, dict)],
            "location": [_encounter_location(item) for item in resource.get("location", []) if isinstance(item, dict)],
        }
    )


def normalize_observation(resource: dict[str, Any]) -> dict[str, Any]:
    return _compact(
        {
            "resource_type": "Observation",
            "id": resource.get("id"),
            "status": resource.get("status"),
            "category": [_codeable_concept(item) for item in resource.get("category", []) if isinstance(item, dict)],
            "code": _code_text(resource.get("code", {})),
            "code_detail": _codeable_concept(resource.get("code", {})),
            "effective_time": resource.get("effectiveDateTime") or resource.get("effectivePeriod"),
            "issued": resource.get("issued"),
            "subject": _reference(resource.get("subject", {})),
            "value": _value(resource),
            "interpretation": [_codeable_concept(item) for item in resource.get("interpretation", []) if isinstance(item, dict)],
            "reference_range": [_reference_range(item) for item in resource.get("referenceRange", []) if isinstance(item, dict)],
            "components": [_observation_component(item) for item in resource.get("component", []) if isinstance(item, dict)],
            "note": _notes(resource.get("note", [])),
        }
    )


def normalize_diagnostic_report(resource: dict[str, Any]) -> dict[str, Any]:
    return _compact(
        {
            "resource_type": "DiagnosticReport",
            "id": resource.get("id"),
            "status": resource.get("status"),
            "category": [_codeable_concept(item) for item in resource.get("category", []) if isinstance(item, dict)],
            "code": _code_text(resource.get("code", {})),
            "code_detail": _codeable_concept(resource.get("code", {})),
            "subject": _reference(resource.get("subject", {})),
            "effective_time": resource.get("effectiveDateTime") or resource.get("effectivePeriod"),
            "issued": resource.get("issued"),
            "conclusion": resource.get("conclusion"),
            "result": [_reference(item) for item in resource.get("result", []) if isinstance(item, dict)],
        }
    )


def normalize_medication_request(resource: dict[str, Any]) -> dict[str, Any]:
    medication = resource.get("medicationCodeableConcept") or {}
    return _compact(
        {
            "resource_type": "MedicationRequest",
            "id": resource.get("id"),
            "status": resource.get("status"),
            "intent": resource.get("intent"),
            "medication": _code_text(medication),
            "medication_detail": _codeable_concept(medication),
            "subject": _reference(resource.get("subject", {})),
            "authored_on": resource.get("authoredOn"),
            "requester": _reference(resource.get("requester", {})),
            "dosage": [
                item.get("text")
                for item in resource.get("dosageInstruction", [])
                if isinstance(item, dict) and item.get("text")
            ],
            "dosage_instruction": [
                _dosage_instruction(item)
                for item in resource.get("dosageInstruction", [])
                if isinstance(item, dict)
            ],
            "note": _notes(resource.get("note", [])),
        }
    )


def _updated_at(data: dict[str, Any]) -> str | None:
    for key in ("issued", "effective_time", "authored_on", "start", "created"):
        value = data.get(key)
        if isinstance(value, str):
            return value
    period = data.get("period")
    if isinstance(period, dict) and isinstance(period.get("start"), str):
        return period["start"]
    return None


def _compact(value: dict[str, Any]) -> dict[str, Any]:
    return {
        key: item
        for key, item in value.items()
        if item not in (None, "", [], {})
    }


def _first(items: Any) -> dict[str, Any]:
    if isinstance(items, list) and items and isinstance(items[0], dict):
        return items[0]
    return {}


def _human_name(name: dict[str, Any]) -> str | None:
    text = name.get("text")
    if text:
        return text
    given = name.get("given") or []
    family = name.get("family")
    parts = [str(part) for part in [family, *given] if part]
    return " ".join(parts) or None


def _identifiers(items: list[dict[str, Any]]) -> list[dict[str, str | None]]:
    return [
        {"system": item.get("system"), "value": item.get("value")}
        for item in items
        if isinstance(item, dict) and item.get("value")
    ]


def _telecom(items: list[dict[str, Any]]) -> list[dict[str, str | None]]:
    return [
        {"system": item.get("system"), "value": item.get("value"), "use": item.get("use")}
        for item in items
        if isinstance(item, dict) and item.get("value")
    ]


def _coding(item: dict[str, Any]) -> dict[str, Any]:
    return _compact(
        {
            "system": item.get("system"),
            "code": item.get("code"),
            "display": item.get("display"),
        }
    )


def _codeable_concept(item: dict[str, Any]) -> dict[str, Any]:
    codings = [_coding(coding) for coding in item.get("coding", []) if isinstance(coding, dict)]
    return _compact(
        {
            "text": item.get("text") or _first_display(codings),
            "coding": [coding for coding in codings if coding],
        }
    )


def _code_text(item: dict[str, Any]) -> str | None:
    concept = _codeable_concept(item)
    return concept.get("text") if isinstance(concept.get("text"), str) else None


def _first_display(codings: list[dict[str, Any]]) -> str | None:
    for coding in codings:
        if coding.get("display"):
            return coding["display"]
        if coding.get("code"):
            return coding["code"]
    return None


def _reference(item: dict[str, Any]) -> dict[str, Any]:
    return _compact(
        {
            "reference": item.get("reference"),
            "display": item.get("display"),
        }
    )


def _value(resource: dict[str, Any]) -> Any:
    quantity = resource.get("valueQuantity")
    if isinstance(quantity, dict):
        return _quantity(quantity)
    for key in ("valueString", "valueBoolean", "valueInteger", "valueCodeableConcept"):
        if key in resource:
            value = resource[key]
            if key == "valueCodeableConcept" and isinstance(value, dict):
                return _codeable_concept(value)
            return value
    return None


def _quantity(item: dict[str, Any]) -> dict[str, Any]:
    return _compact(
        {
            "value": item.get("value"),
            "unit": item.get("unit"),
            "system": item.get("system"),
            "code": item.get("code"),
        }
    )


def _reference_range(item: dict[str, Any]) -> dict[str, Any]:
    return _compact(
        {
            "low": _quantity(item.get("low", {})),
            "high": _quantity(item.get("high", {})),
            "text": item.get("text"),
        }
    )


def _observation_component(item: dict[str, Any]) -> dict[str, Any]:
    return _compact(
        {
            "code": _code_text(item.get("code", {})),
            "code_detail": _codeable_concept(item.get("code", {})),
            "value": _value(item),
            "reference_range": [_reference_range(value) for value in item.get("referenceRange", []) if isinstance(value, dict)],
        }
    )


def _dosage_instruction(item: dict[str, Any]) -> dict[str, Any]:
    return _compact(
        {
            "text": item.get("text"),
            "patient_instruction": item.get("patientInstruction"),
        }
    )


def _appointment_participant(item: dict[str, Any]) -> dict[str, Any]:
    return _compact(
        {
            "actor": _reference(item.get("actor", {})),
            "status": item.get("status"),
            "required": item.get("required"),
        }
    )


def _encounter_participant(item: dict[str, Any]) -> dict[str, Any]:
    return _compact(
        {
            "individual": _reference(item.get("individual", {})),
            "period": item.get("period"),
        }
    )


def _encounter_location(item: dict[str, Any]) -> dict[str, Any]:
    return _compact(
        {
            "location": _reference(item.get("location", {})),
            "status": item.get("status"),
            "period": item.get("period"),
        }
    )


def _notes(items: list[dict[str, Any]]) -> list[str]:
    return [
        item["text"]
        for item in items
        if isinstance(item, dict) and isinstance(item.get("text"), str) and item["text"].strip()
    ]
