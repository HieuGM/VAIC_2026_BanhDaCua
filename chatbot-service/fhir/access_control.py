from core.errors import PermissionDenied
from core.state import ChatState


def resolve_allowed_patient_id(state: ChatState) -> str:
    if state.get("user_role") != "USER":
        raise PermissionDenied("FHIR access is only enabled for linked USER patient scope in v1.")

    patient_ids = [
        patient_id
        for patient_id in (_normalize_patient_id(value) for value in (state.get("allowed_patient_ids") or []))
        if patient_id
    ]
    if not patient_ids:
        raise PermissionDenied("USER has no linked FHIR patient scope.")
    return patient_ids[0]


def _normalize_patient_id(value: object) -> str | None:
    if not isinstance(value, str):
        return None
    patient_id = value.strip()
    if not patient_id:
        return None
    if patient_id.lower().startswith("patient/"):
        patient_id = patient_id.split("/", 1)[1].strip()
    return patient_id or None
