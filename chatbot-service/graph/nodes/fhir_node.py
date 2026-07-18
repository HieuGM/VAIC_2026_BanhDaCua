from core.enums import SafetyFlag
from core.errors import PermissionDenied
from core.state import ChatState
from fhir.client import FhirClientError
from fhir.planner import FhirPlannerError
from fhir.tools import FHIR_PLANNER_METADATA_KEY, retrieve_fhir_evidence


async def fhir_node(state: ChatState) -> dict:
    try:
        evidence = await retrieve_fhir_evidence(state)
    except PermissionDenied as exc:
        flags = list(state.get("safety_flags") or [])
        if SafetyFlag.UNAUTHORIZED_PATIENT_ACCESS.value not in flags:
            flags.append(SafetyFlag.UNAUTHORIZED_PATIENT_ACCESS.value)
        return {
            "evidence": [],
            "safety_flags": flags,
            "error": {"code": exc.error_code, "message": str(exc)},
            "needs_handoff": True,
            "metadata": _with_fhir_metadata(
                state,
                status="permission_denied",
                evidence=[],
            ),
        }
    except FhirClientError as exc:
        return {
            "evidence": [],
            "error": {"code": "FHIR_ERROR", "message": exc.user_message},
            "needs_handoff": True,
            "metadata": _with_fhir_metadata(
                state,
                status="upstream_error",
                evidence=[],
            ),
        }
    except FhirPlannerError as exc:
        return {
            "evidence": [],
            "metadata": _with_fhir_metadata(
                state,
                status="planner_error",
                evidence=[],
                planner_override={
                    "source": "fallback",
                    "selected_tool": None,
                    "confidence": 0.0,
                    "reason": str(exc),
                },
            ),
        }
    payload = [item.model_dump(mode="json") for item in evidence]
    status = "ok" if payload else "no_data"
    return {
        "evidence": payload,
        "metadata": _with_fhir_metadata(state, status=status, evidence=payload),
    }


def _with_fhir_metadata(
    state: ChatState,
    *,
    status: str,
    evidence: list[dict],
    planner_override: dict | None = None,
) -> dict:
    metadata = dict(state.get("metadata") or {})
    planner = planner_override or metadata.pop(FHIR_PLANNER_METADATA_KEY, None)
    metadata["fhir"] = {
        "queried": True,
        "status": status,
        "evidence_count": len(evidence),
        "resource_types": _resource_types(evidence),
    }
    if isinstance(planner, dict):
        metadata["fhir"]["planner"] = planner
    return metadata


def _resource_types(evidence: list[dict]) -> list[str]:
    resource_types: list[str] = []
    for item in evidence:
        data = item.get("data") if isinstance(item, dict) else None
        resource_type = data.get("resource_type") if isinstance(data, dict) else None
        if isinstance(resource_type, str) and resource_type not in resource_types:
            resource_types.append(resource_type)
    return resource_types
