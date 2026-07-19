from __future__ import annotations

import json
import re
from typing import Any

from app.config import get_settings
from core.contracts import RouteDecision
from core.enums import Intent, Route
from core.state import ChatState


JSON_BLOCK_RE = re.compile(r"```(?:json)?\s*(.*?)\s*```", re.IGNORECASE | re.DOTALL)

VALID_ROUTE_BY_INTENT: dict[Intent, Route] = {
    Intent.EMERGENCY: Route.EMERGENCY,
    Intent.PATIENT_PROFILE: Route.AUTHENTICATED_FHIR,
    Intent.PATIENT_ENCOUNTER: Route.AUTHENTICATED_FHIR,
    Intent.LAB_RESULT: Route.AUTHENTICATED_FHIR,
    Intent.MEDICATION_INFORMATION: Route.AUTHENTICATED_FHIR,
    Intent.PATIENT_APPOINTMENT: Route.HUMAN_HANDOFF,
    Intent.APPOINTMENT_STATUS: Route.HUMAN_HANDOFF,
    Intent.SERVICE_PRICE: Route.PUBLIC_TOOL,
    Intent.DOCTOR_SCHEDULE: Route.PUBLIC_TOOL,
    Intent.APPOINTMENT_BOOKING: Route.PUBLIC_TOOL,
    Intent.BHYT_INFORMATION: Route.PUBLIC_TOOL,
    Intent.EXAMINATION_PROCEDURE: Route.PUBLIC_TOOL,
    Intent.WORKING_HOURS: Route.PUBLIC_TOOL,
    Intent.DEPARTMENT_INFORMATION: Route.PUBLIC_TOOL,
    Intent.DOCTOR_INFORMATION: Route.PUBLIC_RAG,
    Intent.HOSPITAL_INFORMATION: Route.PUBLIC_TOOL,
    Intent.HOSPITAL_CONTACT: Route.PUBLIC_TOOL,
    Intent.SERVICE_INFORMATION: Route.PUBLIC_RAG,
    Intent.APPOINTMENT_GUIDANCE: Route.PUBLIC_TOOL,
    Intent.SYMPTOM_QUESTION: Route.PUBLIC_RAG,
    Intent.GREETING: Route.PUBLIC_RAG,
    Intent.HUMAN_SUPPORT: Route.HUMAN_HANDOFF,
    Intent.COMPLAINT: Route.HUMAN_HANDOFF,
    Intent.OUT_OF_SCOPE: Route.UNSUPPORTED,
    Intent.UNKNOWN: Route.PUBLIC_RAG,
}


class LlmRouterError(Exception):
    pass


async def route_with_llm(state: ChatState) -> RouteDecision:
    settings = get_settings()
    if not settings.use_llm_router:
        raise LlmRouterError("LLM router is disabled.")
    if not settings.openai_api_key:
        raise LlmRouterError("OPENAI_API_KEY is not configured.")

    try:
        from openai import AsyncOpenAI

        client = AsyncOpenAI(
            api_key=settings.openai_api_key,
            base_url=settings.openai_base_url,
            timeout=settings.llm_router_timeout_seconds,
        )
        response = await client.chat.completions.create(
            model=settings.model_route or settings.model_simple,
            temperature=0,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": router_system_prompt()},
                {"role": "user", "content": _router_user_prompt(state)},
            ],
        )
        content = response.choices[0].message.content or ""
    except LlmRouterError:
        raise
    except Exception as exc:
        raise LlmRouterError(f"LLM router call failed: {exc}") from exc

    decision = parse_router_response(content)
    return validate_route_decision(
        decision,
        min_confidence=settings.llm_router_min_confidence,
    )


def parse_router_response(text: str) -> RouteDecision:
    payload = _parse_json_payload(text)
    try:
        route = Route(str(payload.get("route") or "").strip())
        intent = Intent(str(payload.get("intent") or "").strip())
    except ValueError as exc:
        raise LlmRouterError(f"Router returned unsupported enum: {exc}") from exc

    try:
        confidence = float(payload.get("confidence", 0.0))
    except (TypeError, ValueError) as exc:
        raise LlmRouterError("Router confidence must be numeric.") from exc

    entities = payload.get("entities") if isinstance(payload.get("entities"), dict) else {}
    reason = payload.get("reason")
    return RouteDecision(
        route=route,
        intent=intent,
        entities=entities,
        reason=str(reason).strip() if reason else None,
        confidence=confidence,
    )


def validate_route_decision(
    decision: RouteDecision,
    *,
    min_confidence: float = 0.65,
) -> RouteDecision:
    expected_route = VALID_ROUTE_BY_INTENT.get(decision.intent)
    if expected_route is None:
        raise LlmRouterError(f"Unsupported intent: {decision.intent.value}")
    if decision.route != expected_route:
        raise LlmRouterError(
            f"Invalid route-intent pair: {decision.intent.value} -> {decision.route.value}"
        )
    if decision.confidence < min_confidence:
        raise LlmRouterError(
            f"Router confidence too low: {decision.confidence}"
        )
    return decision


def router_system_prompt() -> str:
    return (
        "You are the intent router for Hanoi Heart Hospital chatbot.\n"
        "Your only job is to choose route and intent. Do not answer the user. "
        "Do not call tools. Do not decide permissions. Do not reveal patient data.\n"
        "Emergency rule detection already runs before you, but you may still return EMERGENCY when the text suggests emergency.\n"
        "Return exactly one JSON object. No markdown.\n\n"
        "Valid route-intent pairs:\n"
        "- EMERGENCY -> EMERGENCY\n"
        "- PATIENT_PROFILE, PATIENT_ENCOUNTER, LAB_RESULT, MEDICATION_INFORMATION -> AUTHENTICATED_FHIR\n"
        "- PATIENT_APPOINTMENT, APPOINTMENT_STATUS -> HUMAN_HANDOFF because appointment status will be owned by backend-service later\n"
        "- SERVICE_PRICE, DOCTOR_SCHEDULE, APPOINTMENT_BOOKING, BHYT_INFORMATION, EXAMINATION_PROCEDURE, "
        "WORKING_HOURS, DEPARTMENT_INFORMATION, HOSPITAL_INFORMATION, HOSPITAL_CONTACT, APPOINTMENT_GUIDANCE -> PUBLIC_TOOL\n"
        "- DOCTOR_INFORMATION, SERVICE_INFORMATION, SYMPTOM_QUESTION, GREETING, UNKNOWN -> PUBLIC_RAG\n"
        "- HUMAN_SUPPORT, COMPLAINT -> HUMAN_HANDOFF\n"
        "- OUT_OF_SCOPE -> UNSUPPORTED\n\n"
        "FHIR personal data examples:\n"
        "- 'ho so cua toi', 'thong tin cua toi' -> PATIENT_PROFILE / AUTHENTICATED_FHIR\n"
        "- 'ket qua xet nghiem cua toi', 'can lam sang cua toi' -> LAB_RESULT / AUTHENTICATED_FHIR\n"
        "- 'don thuoc cua toi', 'thuoc cua toi' -> MEDICATION_INFORMATION / AUTHENTICATED_FHIR\n"
        "- 'lan kham cua toi', 'luot kham cua toi' -> PATIENT_ENCOUNTER / AUTHENTICATED_FHIR\n"
        "Appointment distinction:\n"
        "- Public doctor schedule such as 'bac si Vo Thi Ngoc Anh co lich kham ngay nao', "
        "'lich bac si tim mach ngay 16/7' -> DOCTOR_SCHEDULE / PUBLIC_TOOL\n"
        "- Personal appointment status such as 'lich hen cua toi', 'kiem tra lich tai kham cua toi' "
        "-> APPOINTMENT_STATUS / HUMAN_HANDOFF\n"
        "- Appointment booking channels or guidance such as 'dat lich kham nhu the nao' "
        "-> APPOINTMENT_BOOKING or APPOINTMENT_GUIDANCE / PUBLIC_TOOL\n"
        "Public tool examples: price, doctor schedule, appointment booking channels, BHYT, procedure, paperwork, working hours, department, hospital info.\n"
        "Public RAG is for general explanatory knowledge that is not a structured data lookup. "
        "Use PUBLIC_TOOL for structured public lookups such as prices, schedules, channels, procedures, BHYT policy, departments, contact and working hours.\n"
        "Public RAG examples: general service descriptions, general doctor information, non-emergency symptoms.\n"
        "Human handoff examples: hotline, call center, complaint, staff support.\n\n"
        "Schema:\n"
        "{\n"
        '  "route": "AUTHENTICATED_FHIR|PUBLIC_RAG|PUBLIC_TOOL|HUMAN_HANDOFF|EMERGENCY|UNSUPPORTED",\n'
        '  "intent": "LAB_RESULT|MEDICATION_INFORMATION|PATIENT_PROFILE|PATIENT_ENCOUNTER|PATIENT_APPOINTMENT|APPOINTMENT_STATUS|SERVICE_PRICE|DOCTOR_SCHEDULE|APPOINTMENT_BOOKING|BHYT_INFORMATION|EXAMINATION_PROCEDURE|WORKING_HOURS|DEPARTMENT_INFORMATION|DOCTOR_INFORMATION|HOSPITAL_INFORMATION|HOSPITAL_CONTACT|SERVICE_INFORMATION|APPOINTMENT_GUIDANCE|SYMPTOM_QUESTION|GREETING|HUMAN_SUPPORT|COMPLAINT|EMERGENCY|OUT_OF_SCOPE|UNKNOWN",\n'
        '  "confidence": 0.0,\n'
        '  "reason": "short reason",\n'
        '  "entities": {}\n'
        "}\n"
    )


def _router_user_prompt(state: ChatState) -> str:
    payload = {
        "message": state.get("message") or "",
        "normalized_message": state.get("normalized_message") or "",
        "user_role": state.get("user_role") or "",
        "has_allowed_patient_ids": bool(state.get("allowed_patient_ids")),
        "lang": state.get("lang") or "vi",
        "context": _compact_context(state.get("context")),
    }
    return json.dumps(payload, ensure_ascii=False)


def _compact_context(value: Any) -> dict[str, Any]:
    if not isinstance(value, dict):
        return {}
    allowed_keys = {
        "active_patient_id",
        "last_intent",
        "last_resource_type",
        "last_resource_id",
    }
    return {key: value.get(key) for key in allowed_keys if value.get(key)}


def _parse_json_payload(text: str) -> dict[str, Any]:
    content = (text or "").strip()
    match = JSON_BLOCK_RE.search(content)
    if match:
        content = match.group(1).strip()
    try:
        payload = json.loads(content)
    except json.JSONDecodeError as exc:
        raise LlmRouterError("Router response is not valid JSON.") from exc
    if not isinstance(payload, dict):
        raise LlmRouterError("Router response must be a JSON object.")
    return payload
