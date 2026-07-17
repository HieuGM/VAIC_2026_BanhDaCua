from __future__ import annotations

import unicodedata

from app.config import get_settings
from core.contracts import RouteDecision
from core.enums import Intent, Route, SafetyFlag
from core.state import ChatState
from graph.nodes.emergency_node import emergency_answer_text
from llm.router import LlmRouterError, route_with_llm, validate_route_decision


async def intent_router_node(state: ChatState) -> dict:
    text = _normalize(state.get("normalized_message") or state.get("message") or "")

    rule_decision = _rule_shortcut(text)
    if rule_decision is not None:
        return _decision_patch(state, rule_decision, source="rule")

    try:
        llm_decision = await route_with_llm({**state, "normalized_message": text})
        decision = validate_route_decision(
            llm_decision,
            min_confidence=get_settings().llm_router_min_confidence,
        )
        return _decision_patch(state, decision, source="llm")
    except LlmRouterError as exc:
        fallback = _fallback_decision(text)
        return _decision_patch(
            state,
            fallback,
            source="fallback",
            fallback_reason=str(exc),
        )


def _rule_shortcut(text: str) -> RouteDecision | None:
    if _contains_any(text, ["nhan vien", "tong dai", "hotline", "cskh", "ho tro nguoi", "khieu nai", "phan anh"]):
        intent = Intent.COMPLAINT if _contains_any(text, ["khieu nai", "phan anh"]) else Intent.HUMAN_SUPPORT
        return _decision(Route.HUMAN_HANDOFF, intent, 0.9, "Rule matched human support.")

    if _contains_any(text, ["lich hen cua toi", "lich tai kham cua toi", "kiem tra lich hen", "trang thai lich hen"]):
        return _decision(Route.HUMAN_HANDOFF, Intent.APPOINTMENT_STATUS, 0.86, "Appointment status is owned by backend-service later.")

    if _contains_any(text, ["ket qua xet nghiem", "xet nghiem cua toi", "can lam sang cua toi", "ket qua cls"]):
        return _decision(Route.AUTHENTICATED_FHIR, Intent.LAB_RESULT, 0.9, "Rule matched personal lab result.")

    if _contains_any(text, ["don thuoc cua toi", "thuoc cua toi", "y lenh thuoc cua toi"]):
        return _decision(Route.AUTHENTICATED_FHIR, Intent.MEDICATION_INFORMATION, 0.9, "Rule matched personal medication.")

    if _contains_any(text, ["ho so cua toi", "thong tin cua toi", "ho so benh nhan cua toi"]):
        return _decision(Route.AUTHENTICATED_FHIR, Intent.PATIENT_PROFILE, 0.9, "Rule matched patient profile.")

    if _contains_any(text, ["lan kham cua toi", "luot kham cua toi", "lich su kham cua toi"]):
        return _decision(Route.AUTHENTICATED_FHIR, Intent.PATIENT_ENCOUNTER, 0.9, "Rule matched patient encounter.")

    if _contains_any(text, ["dat lich", "dat kham", "dang ky kham", "hen kham"]):
        return _decision(Route.PUBLIC_TOOL, Intent.APPOINTMENT_BOOKING, 0.85, "Rule matched appointment booking.")

    if _contains_any(text, ["lich bac si", "bac si nao", "ca kham bac si", "bac si lam viec"]):
        return _decision(Route.PUBLIC_TOOL, Intent.DOCTOR_SCHEDULE, 0.85, "Rule matched doctor schedule.")

    if _contains_any(text, ["bang gia", "chi phi", "phi kham", "gia dich vu", "gia kham"]):
        return _decision(Route.PUBLIC_TOOL, Intent.SERVICE_PRICE, 0.85, "Rule matched service price.")

    if _contains_any(text, ["bhyt", "bao hiem y te", "bao hiem"]):
        return _decision(Route.PUBLIC_RAG, Intent.BHYT_INFORMATION, 0.8, "Rule matched insurance information.")

    if _contains_any(text, ["quy trinh", "thu tuc", "giay to", "can chuan bi"]):
        return _decision(Route.PUBLIC_RAG, Intent.EXAMINATION_PROCEDURE, 0.8, "Rule matched examination procedure.")

    if _contains_any(text, ["gio lam viec", "thoi gian lam viec", "may gio mo cua"]):
        return _decision(Route.PUBLIC_RAG, Intent.WORKING_HOURS, 0.8, "Rule matched working hours.")

    if _contains_any(text, ["khoa", "phong kham", "chuyen khoa"]):
        return _decision(Route.PUBLIC_RAG, Intent.DEPARTMENT_INFORMATION, 0.72, "Rule matched department information.")

    if _contains_any(text, ["dia chi", "lien he", "benh vien o dau", "thong tin benh vien"]):
        return _decision(Route.PUBLIC_RAG, Intent.HOSPITAL_CONTACT, 0.72, "Rule matched hospital contact.")

    return None


def _fallback_decision(text: str) -> RouteDecision:
    if _contains_any(text, ["xin chao", "chao ban", "cam on", "tam biet"]):
        return _decision(Route.PUBLIC_RAG, Intent.GREETING, 0.5, "Fallback greeting route.")
    if _contains_any(text, ["dau", "trieu chung", "met", "sot"]):
        return _decision(Route.PUBLIC_RAG, Intent.SYMPTOM_QUESTION, 0.5, "Fallback symptom information route.")
    return _decision(Route.PUBLIC_RAG, Intent.HOSPITAL_INFORMATION, 0.5, "Fallback hospital information route.")


def _decision_patch(
    state: ChatState,
    decision: RouteDecision,
    *,
    source: str,
    fallback_reason: str | None = None,
) -> dict:
    patch = {
        "intent": decision.intent.value,
        "route": decision.route.value,
        "entities": decision.entities,
        "confidence": decision.confidence,
        "metadata": _router_metadata(state, decision, source, fallback_reason),
    }

    if decision.route == Route.HUMAN_HANDOFF:
        patch["needs_handoff"] = True

    if decision.route == Route.EMERGENCY:
        flags = list(state.get("safety_flags") or [])
        if SafetyFlag.EMERGENCY.value not in flags:
            flags.append(SafetyFlag.EMERGENCY.value)
        patch.update(
            {
                "answer": emergency_answer_text(),
                "needs_handoff": True,
                "safety_flags": flags,
            }
        )

    return patch


def _router_metadata(
    state: ChatState,
    decision: RouteDecision,
    source: str,
    fallback_reason: str | None,
) -> dict:
    metadata = dict(state.get("metadata") or {})
    metadata["router"] = {
        "source": source,
        "status": "fallback" if fallback_reason else "ok",
        "confidence": decision.confidence,
        "reason": decision.reason,
        "fallback_reason": fallback_reason,
    }
    return metadata


def _decision(route: Route, intent: Intent, confidence: float, reason: str) -> RouteDecision:
    return RouteDecision(
        route=route,
        intent=intent,
        confidence=confidence,
        reason=reason,
    )


def _normalize(value: str) -> str:
    text = (value or "").lower().replace("đ", "d")
    text = unicodedata.normalize("NFD", text)
    text = "".join(char for char in text if unicodedata.category(char) != "Mn")
    return " ".join(text.split())


def _contains_any(text: str, keywords: list[str]) -> bool:
    return any(keyword in text for keyword in keywords)
