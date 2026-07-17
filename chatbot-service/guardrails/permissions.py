from core.enums import Route
from core.state import ChatState


def can_access_route(state: ChatState, route: Route) -> bool:
    if route != Route.AUTHENTICATED_FHIR:
        return True
    return state.get("user_role") == "USER" and bool(state.get("allowed_patient_ids"))
