import unittest
from types import SimpleNamespace
from unittest.mock import patch

from core.enums import Intent
from fhir.plan_validator import FhirPlannerValidationError, validate_fhir_planner_decision
from fhir.planner import FhirPlannerError, parse_fhir_planner_response, plan_fhir_tool
from fhir.schemas import FhirPlannerDecision


class FhirPlannerTest(unittest.IsolatedAsyncioTestCase):
    def test_parse_valid_json(self) -> None:
        decision = parse_fhir_planner_response(
            '{"tool_name": "get_patient_profile", "confidence": 0.86, "reason": "profile"}'
        )

        self.assertEqual(decision.tool_name, "get_patient_profile")
        self.assertEqual(decision.source, "llm")
        self.assertEqual(decision.confidence, 0.86)

    def test_parse_rejects_tool_outside_allowlist(self) -> None:
        with self.assertRaises(FhirPlannerError):
            parse_fhir_planner_response(
                '{"tool_name": "get_patient_appointments", "confidence": 0.9, "reason": "appointment"}'
            )

    def test_parse_rejects_patient_id_from_llm(self) -> None:
        with self.assertRaises(FhirPlannerError):
            parse_fhir_planner_response(
                '{"tool_name": "get_patient_profile", "patient_id": "vn-patient-999", "confidence": 0.9}'
            )

    def test_validate_rejects_low_confidence(self) -> None:
        decision = FhirPlannerDecision(
            tool_name="get_patient_profile",
            confidence=0.2,
            reason="low",
            source="llm",
        )

        with self.assertRaises(FhirPlannerValidationError):
            validate_fhir_planner_decision(
                decision,
                {"intent": Intent.PATIENT_PROFILE.value},
                min_confidence=0.65,
            )

    def test_validate_rejects_intent_tool_mismatch(self) -> None:
        decision = FhirPlannerDecision(
            tool_name="get_medications",
            confidence=0.9,
            reason="wrong tool",
            source="llm",
        )

        with self.assertRaises(FhirPlannerValidationError):
            validate_fhir_planner_decision(
                decision,
                {"intent": Intent.PATIENT_PROFILE.value},
                min_confidence=0.65,
            )

    async def test_missing_openai_key_falls_back_by_intent(self) -> None:
        settings = SimpleNamespace(use_llm_fhir_planner=True, openai_api_key=None)

        with patch("fhir.planner.get_settings", return_value=settings):
            decision = await plan_fhir_tool({"intent": Intent.PATIENT_PROFILE.value})

        self.assertEqual(decision.tool_name, "get_patient_profile")
        self.assertEqual(decision.source, "fallback")

    async def test_invalid_llm_response_falls_back_by_intent(self) -> None:
        settings = SimpleNamespace(
            use_llm_fhir_planner=True,
            openai_api_key="test-key",
            openai_base_url=None,
            fhir_planner_timeout_seconds=1,
            model_fhir_planner=None,
            model_route=None,
            model_simple="gpt-4o-mini",
            fhir_planner_min_confidence=0.65,
        )

        async def fake_llm(state, settings):
            return '{"tool_name": "get_medications", "confidence": 0.95, "reason": "wrong"}'

        with (
            patch("fhir.planner.get_settings", return_value=settings),
            patch("fhir.planner._call_llm_fhir_planner", side_effect=fake_llm),
        ):
            decision = await plan_fhir_tool({"intent": Intent.PATIENT_PROFILE.value})

        self.assertEqual(decision.tool_name, "get_patient_profile")
        self.assertEqual(decision.source, "fallback")


if __name__ == "__main__":
    unittest.main()
