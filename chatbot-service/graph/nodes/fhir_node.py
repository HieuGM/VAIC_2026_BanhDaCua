from core.enums import SafetyFlag
from core.errors import PermissionDenied
from core.state import ChatState
from fhir.client import FhirClientError
from fhir.tools import retrieve_fhir_evidence


async def fhir_node(state: ChatState) -> dict:
    try:
        evidence = await retrieve_fhir_evidence(state)
    except PermissionDenied as exc:
        return {
            "evidence": [],
            "safety_flags": [SafetyFlag.UNAUTHORIZED_PATIENT_ACCESS.value],
            "error": {"code": exc.error_code, "message": str(exc)},
            "needs_handoff": True,
        }
    except FhirClientError as exc:
        return {
            "evidence": [],
            "error": {"code": "FHIR_ERROR", "message": exc.user_message},
            "needs_handoff": True,
        }
    return {"evidence": [item.model_dump(mode="json") for item in evidence]}
