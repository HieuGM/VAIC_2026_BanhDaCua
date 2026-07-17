from core.enums import Intent, Route
from core.state import ChatState


async def intent_router_node(state: ChatState) -> dict:
    text = (state.get("normalized_message") or "").lower()

    if any(keyword in text for keyword in ["nhan vien", "tong dai", "hotline", "khieu nai"]):
        return {
            "intent": Intent.HUMAN_SUPPORT.value,
            "route": Route.HUMAN_HANDOFF.value,
            "needs_handoff": True,
            "confidence": 0.8,
        }

    if any(keyword in text for keyword in ["lich bac si", "bac si nao", "gia", "bang gia", "slot"]):
        return {
            "intent": Intent.DOCTOR_SCHEDULE.value if "bac si" in text else Intent.SERVICE_PRICE.value,
            "route": Route.PUBLIC_TOOL.value,
            "confidence": 0.7,
        }

    if any(keyword in text for keyword in ["lich hen cua toi", "ket qua xet nghiem", "don thuoc", "ho so cua toi"]):
        return {
            "intent": Intent.PATIENT_APPOINTMENT.value,
            "route": Route.AUTHENTICATED_FHIR.value,
            "confidence": 0.7,
        }

    if any(keyword in text for keyword in ["dat lich", "dat kham", "hen kham"]):
        return {
            "intent": Intent.APPOINTMENT_BOOKING.value,
            "route": Route.PUBLIC_TOOL.value,
            "confidence": 0.75,
        }

    if any(keyword in text for keyword in ["bhyt", "bao hiem", "quy trinh", "giay to", "gio lam viec"]):
        return {
            "intent": Intent.BHYT_INFORMATION.value if "bhyt" in text or "bao hiem" in text else Intent.EXAMINATION_PROCEDURE.value,
            "route": Route.PUBLIC_RAG.value,
            "confidence": 0.65,
        }

    return {
        "intent": Intent.HOSPITAL_INFORMATION.value,
        "route": Route.PUBLIC_RAG.value,
        "confidence": 0.5,
    }
