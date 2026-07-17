from core.contracts import Evidence
from core.state import ChatState
from fhir.access_control import resolve_allowed_patient_id


async def retrieve_fhir_evidence(state: ChatState) -> list[Evidence]:
    # TODO(FHIR owner): map intent to allowlisted FHIR/HIS tools.
    # This intentionally resolves patient scope from backend context, not user text.
    resolve_allowed_patient_id(state)
    return []
