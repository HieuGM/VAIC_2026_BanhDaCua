import unittest

from core.enums import Intent, Route
from llm.router import LlmRouterError, parse_router_response, router_system_prompt, validate_route_decision


class LlmRouterTest(unittest.TestCase):
    def test_parse_valid_router_json(self) -> None:
        decision = parse_router_response(
            """
            {
              "route": "AUTHENTICATED_FHIR",
              "intent": "LAB_RESULT",
              "confidence": 0.86,
              "reason": "Personal lab result",
              "entities": {"resource": "Observation"}
            }
            """
        )

        self.assertEqual(decision.route, Route.AUTHENTICATED_FHIR)
        self.assertEqual(decision.intent, Intent.LAB_RESULT)
        self.assertEqual(decision.entities["resource"], "Observation")

    def test_parse_json_from_markdown_block(self) -> None:
        decision = parse_router_response(
            """
            ```json
            {"route": "PUBLIC_TOOL", "intent": "SERVICE_PRICE", "confidence": 0.8}
            ```
            """
        )

        self.assertEqual(decision.route, Route.PUBLIC_TOOL)
        self.assertEqual(decision.intent, Intent.SERVICE_PRICE)

    def test_invalid_json_is_rejected(self) -> None:
        with self.assertRaises(LlmRouterError):
            parse_router_response("route: fhir")

    def test_invalid_enum_is_rejected(self) -> None:
        with self.assertRaises(LlmRouterError):
            parse_router_response(
                '{"route": "FHIR", "intent": "LAB_RESULT", "confidence": 0.9}'
            )

    def test_invalid_route_intent_pair_is_rejected(self) -> None:
        decision = parse_router_response(
            '{"route": "PUBLIC_RAG", "intent": "LAB_RESULT", "confidence": 0.9}'
        )

        with self.assertRaises(LlmRouterError):
            validate_route_decision(decision)

    def test_public_tool_data_api_intents_are_accepted(self) -> None:
        for intent in [
            "DOCTOR_SCHEDULE",
            "BHYT_INFORMATION",
            "EXAMINATION_PROCEDURE",
            "WORKING_HOURS",
            "DEPARTMENT_INFORMATION",
            "HOSPITAL_INFORMATION",
            "HOSPITAL_CONTACT",
            "APPOINTMENT_GUIDANCE",
        ]:
            with self.subTest(intent=intent):
                decision = parse_router_response(
                    f'{{"route": "PUBLIC_TOOL", "intent": "{intent}", "confidence": 0.9}}'
                )
                self.assertEqual(validate_route_decision(decision).route, Route.PUBLIC_TOOL)

    def test_low_confidence_is_rejected(self) -> None:
        decision = parse_router_response(
            '{"route": "AUTHENTICATED_FHIR", "intent": "LAB_RESULT", "confidence": 0.2}'
        )

        with self.assertRaises(LlmRouterError):
            validate_route_decision(decision, min_confidence=0.65)

    def test_prompt_distinguishes_doctor_schedule_and_personal_appointment(self) -> None:
        prompt = router_system_prompt()

        self.assertIn("DOCTOR_SCHEDULE / PUBLIC_TOOL", prompt)
        self.assertIn("APPOINTMENT_STATUS / HUMAN_HANDOFF", prompt)
        self.assertIn("AUTHENTICATED_FHIR", prompt)


if __name__ == "__main__":
    unittest.main()
