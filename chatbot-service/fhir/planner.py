from __future__ import annotations

import json
import re
import unicodedata
from typing import Any

from pydantic import ValidationError

from app.config import get_settings
from core.state import ChatState
from fhir.plan_validator import FHIR_TOOL_BY_INTENT, FhirPlannerValidationError, validate_fhir_planner_decision
from fhir.schemas import FhirPlannerDecision


JSON_BLOCK_RE = re.compile(r"```(?:json)?\s*(.*?)\s*```", re.IGNORECASE | re.DOTALL)
FORBIDDEN_PAYLOAD_KEYS = {
    "args",
    "arguments",
    "parameters",
    "patient_id",
    "patientId",
    "allowed_patient_ids",
    "allowedPatientIds",
    "resource_id",
    "resourceId",
    "resource_type",
    "resourceType",
}


class FhirPlannerError(Exception):
    pass


async def plan_fhir_tool(state: ChatState) -> FhirPlannerDecision:
    settings = get_settings()
    fallback_source = "rule" if not settings.use_llm_fhir_planner else "fallback"

    if not settings.use_llm_fhir_planner:
        return rule_fhir_plan(state, source="rule", reason="LLM FHIR planner is disabled.")
    if not settings.openai_api_key:
        return rule_fhir_plan(state, source="fallback", reason="OPENAI_API_KEY is not configured.")

    try:
        content = await _call_llm_fhir_planner(state, settings)
        decision = parse_fhir_planner_response(content)
        return validate_fhir_planner_decision(
            decision,
            state,
            min_confidence=settings.fhir_planner_min_confidence,
        )
    except (FhirPlannerError, FhirPlannerValidationError) as exc:
        return rule_fhir_plan(state, source=fallback_source, reason=str(exc))


def parse_fhir_planner_response(text: str) -> FhirPlannerDecision:
    payload = _parse_json_payload(text)
    forbidden = sorted(FORBIDDEN_PAYLOAD_KEYS.intersection(payload))
    if forbidden:
        raise FhirPlannerError(f"FHIR planner returned forbidden fields: {', '.join(forbidden)}")

    try:
        return FhirPlannerDecision(
            tool_name=payload.get("tool_name") or payload.get("selected_tool"),
            confidence=float(payload.get("confidence", 0.0)),
            reason=str(payload.get("reason")).strip() if payload.get("reason") else None,
            source="llm",
        )
    except (TypeError, ValueError, ValidationError) as exc:
        raise FhirPlannerError(f"FHIR planner response is invalid: {exc}") from exc


def rule_fhir_plan(
    state: ChatState,
    *,
    source: str = "rule",
    reason: str | None = None,
) -> FhirPlannerDecision:
    intent_tool = FHIR_TOOL_BY_INTENT.get(str(state.get("intent") or ""))
    if intent_tool:
        return FhirPlannerDecision(
            tool_name=intent_tool,
            confidence=0.9,
            reason=reason or f"Rule matched FHIR intent {state.get('intent')}.",
            source=source,  # type: ignore[arg-type]
        )

    text = _normalized_query(state)
    keyword_tool = _tool_from_keywords(text)
    if keyword_tool:
        return FhirPlannerDecision(
            tool_name=keyword_tool,
            confidence=0.74,
            reason=reason or "Rule matched FHIR message keywords.",
            source=source,  # type: ignore[arg-type]
        )

    return FhirPlannerDecision(
        tool_name=None,
        confidence=0.0,
        reason=reason or "No supported FHIR planner tool matched.",
        source=source,  # type: ignore[arg-type]
    )


async def _call_llm_fhir_planner(state: ChatState, settings: Any) -> str:
    try:
        from openai import AsyncOpenAI

        client = AsyncOpenAI(
            api_key=settings.openai_api_key,
            base_url=settings.openai_base_url,
            timeout=settings.fhir_planner_timeout_seconds,
        )
        response = await client.chat.completions.create(
            model=settings.model_fhir_planner or settings.model_route or settings.model_simple,
            temperature=0,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": fhir_planner_system_prompt()},
                {"role": "user", "content": _fhir_planner_user_prompt(state)},
            ],
        )
        return response.choices[0].message.content or ""
    except Exception as exc:
        raise FhirPlannerError(f"FHIR planner call failed: {exc}") from exc


def fhir_planner_system_prompt() -> str:
    return (
        "You are the FHIR planner for Hanoi Heart Hospital chatbot.\n"
        "The request has already been routed to AUTHENTICATED_FHIR. Your only job is to select one FHIR tool.\n"
        "Do not answer the user. Do not explain medical meaning. Do not diagnose. Do not prescribe or change medicine.\n"
        "Do not decide permissions. Do not choose or output patient_id. Patient scope is enforced by backend access control.\n"
        "Only choose one tool from this allowlist:\n"
        "- get_patient_profile: personal patient profile, identity, demographics, linked record information\n"
        "- get_lab_results: observations, lab results, diagnostic reports, clinical measurements\n"
        "- get_medications: medication requests, prescriptions, current or past prescribed medicines\n"
        "- get_patient_encounters: personal visits, encounters, visit history\n\n"
        "Do not choose appointment tools. Personal appointments are owned by backend-service, not FHIR v1.\n"
        "Return exactly one JSON object. No markdown. No extra fields.\n"
        "{\n"
        '  "tool_name": "get_patient_profile|get_lab_results|get_medications|get_patient_encounters",\n'
        '  "confidence": 0.0,\n'
        '  "reason": "short reason"\n'
        "}\n"
    )


def _fhir_planner_user_prompt(state: ChatState) -> str:
    payload = {
        "message": state.get("message") or "",
        "normalized_message": state.get("normalized_message") or "",
        "intent": state.get("intent") or "",
        "route": state.get("route") or "",
        "user_role": state.get("user_role") or "",
        "has_allowed_patient_ids": bool(state.get("allowed_patient_ids")),
        "lang": state.get("lang") or "vi",
        "context": _compact_context(state.get("context")),
    }
    return json.dumps(payload, ensure_ascii=False)


def _parse_json_payload(text: str) -> dict[str, Any]:
    content = (text or "").strip()
    match = JSON_BLOCK_RE.search(content)
    if match:
        content = match.group(1).strip()
    try:
        payload = json.loads(content)
    except json.JSONDecodeError as exc:
        raise FhirPlannerError("FHIR planner response is not valid JSON.") from exc
    if not isinstance(payload, dict):
        raise FhirPlannerError("FHIR planner response must be a JSON object.")
    return payload


def _compact_context(value: Any) -> dict[str, Any]:
    if not isinstance(value, dict):
        return {}
    allowed_keys = {"last_intent", "last_resource_type", "last_resource_id", "limit"}
    return {key: value.get(key) for key in allowed_keys if value.get(key)}


def _normalized_query(state: ChatState) -> str:
    value = state.get("normalized_message") or state.get("message") or ""
    text = str(value).lower().replace("\u0111", "d")
    text = unicodedata.normalize("NFD", text)
    return " ".join("".join(char for char in text if unicodedata.category(char) != "Mn").split())


def _tool_from_keywords(text: str) -> str | None:
    if _contains_any(text, ["xet nghiem", "ket qua", "lab", "cls", "can lam sang", "chi so"]):
        return "get_lab_results"
    if _contains_any(text, ["don thuoc", "thuoc", "medication", "toa thuoc", "y lenh thuoc"]):
        return "get_medications"
    if _contains_any(text, ["lan kham", "luot kham", "lich su kham", "encounter"]):
        return "get_patient_encounters"
    if _contains_any(
        text,
        [
            "ho so",
            "thong tin cua toi",
            "thong tin cua minh",
            "thong tin suc khoe",
            "suc khoe cua minh",
            "kiem tra thong tin",
        ],
    ):
        return "get_patient_profile"
    return None


def _contains_any(text: str, keywords: list[str]) -> bool:
    return any(keyword in text for keyword in keywords)
