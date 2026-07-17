from core.errors import PermissionDenied
from core.state import ChatState


def resolve_allowed_patient_id(state: ChatState) -> str:
    allowed = state.get("allowed_patient_ids") or []
    if state.get("user_role") != "USER":
        raise PermissionDenied("FHIR access for non-USER roles must be implemented explicitly.")
    if not allowed:
        raise PermissionDenied("USER has no linked FHIR patient scope.")
    return allowed[0]
