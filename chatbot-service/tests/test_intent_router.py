import unittest
from unittest.mock import patch

from core.contracts import RouteDecision
from core.enums import Intent, Route
from graph.nodes.intent_router_node import intent_router_node
from llm.router import LlmRouterError


def _decision(route: Route, intent: Intent, confidence: float = 0.9) -> RouteDecision:
    return RouteDecision(
        route=route,
        intent=intent,
        confidence=confidence,
        reason="mocked router decision",
    )


class IntentRouterTest(unittest.IsolatedAsyncioTestCase):
<<<<<<< HEAD
    async def test_prefers_llm_over_fallback_keyword(self) -> None:
=======
    async def test_routes_fhir_lab_result_with_accents(self) -> None:
        result = await intent_router_node({"message": "Ket qua xet nghiem cua toi"})

        self.assertEqual(result["route"], "AUTHENTICATED_FHIR")
        self.assertEqual(result["intent"], "LAB_RESULT")
        self.assertEqual(result["metadata"]["router"]["source"], "rule")

    async def test_routes_fhir_medications_profile_and_encounters(self) -> None:
        cases = [
            ("don thuoc cua toi", "MEDICATION_INFORMATION"),
            ("ho so cua toi", "PATIENT_PROFILE"),
            ("lan kham cua toi", "PATIENT_ENCOUNTER"),
        ]

        for message, expected_intent in cases:
            with self.subTest(message=message):
                result = await intent_router_node({"message": message})
                self.assertEqual(result["route"], "AUTHENTICATED_FHIR")
                self.assertEqual(result["intent"], expected_intent)

    async def test_personal_appointment_status_does_not_route_fhir(self) -> None:
        result = await intent_router_node({"message": "lich hen cua toi"})

        self.assertEqual(result["route"], "HUMAN_HANDOFF")
        self.assertEqual(result["intent"], "APPOINTMENT_STATUS")
        self.assertTrue(result["needs_handoff"])

    async def test_routes_public_tool_cases(self) -> None:
        cases = [
            ("dat lich kham", "APPOINTMENT_BOOKING"),
            ("bang gia kham", "SERVICE_PRICE"),
            ("lich bac si tim mach", "DOCTOR_SCHEDULE"),
        ]

        for message, expected_intent in cases:
            with self.subTest(message=message):
                result = await intent_router_node({"message": message})
                self.assertEqual(result["route"], "PUBLIC_TOOL")
                self.assertEqual(result["intent"], expected_intent)

    async def test_routes_doctor_schedule_natural_vietnamese_with_accents(self) -> None:
        cases = [
            "Bác sĩ Võ Thị Ngọc Anh có lịch khám ngày nào?",
            "Bác sĩ Nguyễn Văn A có khám hôm nay không?",
            "Lịch bác sĩ tim mạch ngày 16/7",
        ]

        for message in cases:
            with self.subTest(message=message):
                result = await intent_router_node({"message": message})
                self.assertEqual(result["route"], "PUBLIC_TOOL")
                self.assertEqual(result["intent"], "DOCTOR_SCHEDULE")
                self.assertEqual(result["metadata"]["router"]["source"], "rule")

    async def test_routes_public_tool_data_api_cases(self) -> None:
        cases = [
            ("bhyt can giay to gi", "BHYT_INFORMATION"),
            ("quy trinh kham", "EXAMINATION_PROCEDURE"),
            ("gio lam viec cua benh vien", "WORKING_HOURS"),
            ("dia chi benh vien", "HOSPITAL_CONTACT"),
            ("khoa tim mach", "DEPARTMENT_INFORMATION"),
        ]

        for message, expected_intent in cases:
            with self.subTest(message=message):
                result = await intent_router_node({"message": message})
                self.assertEqual(result["route"], "PUBLIC_TOOL")
                self.assertEqual(result["intent"], expected_intent)

    async def test_routes_human_support(self) -> None:
        result = await intent_router_node({"message": "toi muon gap nhan vien"})

        self.assertEqual(result["route"], "HUMAN_HANDOFF")
        self.assertEqual(result["intent"], "HUMAN_SUPPORT")
        self.assertTrue(result["needs_handoff"])

    async def test_uses_llm_for_ambiguous_question(self) -> None:
>>>>>>> c19675f045ecdd71794cc4932b096a16e2cda411
        async def fake_route(state):
            return _decision(Route.PUBLIC_RAG, Intent.GREETING)

        with patch("graph.nodes.intent_router_node.route_with_llm", side_effect=fake_route) as mocked:
            result = await intent_router_node({"message": "ket qua xet nghiem cua toi"})

        self.assertTrue(mocked.called)
        self.assertEqual(result["route"], "PUBLIC_RAG")
        self.assertEqual(result["intent"], "GREETING")
        self.assertEqual(result["metadata"]["router"]["source"], "llm")

    async def test_llm_routes_public_tool_cases(self) -> None:
        cases = [
            ("Bác sĩ Võ Thị Ngọc Anh có lịch khám ngày nào?", Intent.DOCTOR_SCHEDULE),
            ("Giá siêu âm Doppler tim bao nhiêu?", Intent.SERVICE_PRICE),
            ("BHYT cần giấy tờ gì?", Intent.BHYT_INFORMATION),
        ]

        for message, expected_intent in cases:
            async def fake_route(state, intent=expected_intent):
                return _decision(Route.PUBLIC_TOOL, intent)

            with self.subTest(message=message):
                with patch("graph.nodes.intent_router_node.route_with_llm", side_effect=fake_route):
                    result = await intent_router_node({"message": message})

                self.assertEqual(result["route"], "PUBLIC_TOOL")
                self.assertEqual(result["intent"], expected_intent.value)
                self.assertEqual(result["metadata"]["router"]["source"], "llm")

    async def test_llm_routes_fhir_and_handoff_cases(self) -> None:
        cases = [
            ("toi muon kiem tra thong tin cua minh", Route.AUTHENTICATED_FHIR, Intent.PATIENT_PROFILE),
            ("lich hen cua toi", Route.HUMAN_HANDOFF, Intent.APPOINTMENT_STATUS),
        ]

        for message, route, intent in cases:
            async def fake_route(state, route=route, intent=intent):
                return _decision(route, intent)

            with self.subTest(message=message):
                with patch("graph.nodes.intent_router_node.route_with_llm", side_effect=fake_route):
                    result = await intent_router_node({"message": message})

                self.assertEqual(result["route"], route.value)
                self.assertEqual(result["intent"], intent.value)
                self.assertEqual(result["metadata"]["router"]["source"], "llm")

    async def test_llm_emergency_gets_standard_emergency_patch(self) -> None:
        async def fake_route(state):
            return _decision(Route.EMERGENCY, Intent.EMERGENCY)

        with patch("graph.nodes.intent_router_node.route_with_llm", side_effect=fake_route):
            result = await intent_router_node({"message": "toi thay rat bat on"})

        self.assertEqual(result["route"], "EMERGENCY")
        self.assertEqual(result["intent"], "EMERGENCY")
        self.assertTrue(result["needs_handoff"])
        self.assertIn("emergency", result["safety_flags"])
        self.assertIn("115", result["answer"])
        self.assertEqual(result["metadata"]["router"]["source"], "llm")

    async def test_fallback_handles_clear_fhir_and_handoff_when_llm_unavailable(self) -> None:
        cases = [
            ("ket qua xet nghiem cua toi", Route.AUTHENTICATED_FHIR, Intent.LAB_RESULT),
            ("ho so cua toi", Route.AUTHENTICATED_FHIR, Intent.PATIENT_PROFILE),
            ("don thuoc cua toi", Route.AUTHENTICATED_FHIR, Intent.MEDICATION_INFORMATION),
            ("lan kham cua toi", Route.AUTHENTICATED_FHIR, Intent.PATIENT_ENCOUNTER),
            ("lich hen cua toi", Route.HUMAN_HANDOFF, Intent.APPOINTMENT_STATUS),
            ("toi muon gap nhan vien", Route.HUMAN_HANDOFF, Intent.HUMAN_SUPPORT),
        ]

        async def failing_route(state):
            raise LlmRouterError("OPENAI_API_KEY is not configured.")

        for message, route, intent in cases:
            with self.subTest(message=message):
                with patch("graph.nodes.intent_router_node.route_with_llm", side_effect=failing_route):
                    result = await intent_router_node({"message": message})

                self.assertEqual(result["route"], route.value)
                self.assertEqual(result["intent"], intent.value)
                self.assertEqual(result["metadata"]["router"]["source"], "fallback")
                self.assertEqual(result["metadata"]["router"]["status"], "fallback")

    async def test_fallback_handles_only_narrow_public_tool_phrases(self) -> None:
        cases = [
            ("dat lich kham", Intent.APPOINTMENT_BOOKING),
            ("bang gia kham", Intent.SERVICE_PRICE),
            ("lich bac si tim mach", Intent.DOCTOR_SCHEDULE),
            ("bhyt can giay to gi", Intent.BHYT_INFORMATION),
        ]

        async def failing_route(state):
            raise LlmRouterError("LLM router is disabled.")

        for message, expected_intent in cases:
            with self.subTest(message=message):
                with patch("graph.nodes.intent_router_node.route_with_llm", side_effect=failing_route):
                    result = await intent_router_node({"message": message})

                self.assertEqual(result["route"], "PUBLIC_TOOL")
                self.assertEqual(result["intent"], expected_intent.value)
                self.assertEqual(result["metadata"]["router"]["source"], "fallback")

    async def test_broad_keywords_do_not_force_public_tool_when_llm_unavailable(self) -> None:
        async def failing_route(state):
            raise LlmRouterError("LLM router is disabled.")

        with patch("graph.nodes.intent_router_node.route_with_llm", side_effect=failing_route):
            department_result = await intent_router_node({"message": "toi muon hoi ve khoa tim mach"})
            doctor_result = await intent_router_node({"message": "bac si giai thich giup toi ve dau nguc"})

        self.assertEqual(department_result["route"], "PUBLIC_RAG")
        self.assertEqual(department_result["intent"], "UNKNOWN")
        self.assertEqual(department_result["metadata"]["router"]["source"], "fallback")

        self.assertEqual(doctor_result["route"], "PUBLIC_RAG")
        self.assertEqual(doctor_result["intent"], "SYMPTOM_QUESTION")
        self.assertEqual(doctor_result["metadata"]["router"]["source"], "fallback")

    async def test_invalid_llm_decision_falls_back_safely(self) -> None:
        async def fake_route(state):
            return _decision(Route.PUBLIC_RAG, Intent.LAB_RESULT, confidence=0.95)

        with patch("graph.nodes.intent_router_node.route_with_llm", side_effect=fake_route):
            result = await intent_router_node({"message": "toi muon hoi dieu gi do"})

        self.assertEqual(result["route"], "PUBLIC_RAG")
        self.assertEqual(result["intent"], "UNKNOWN")
        self.assertEqual(result["metadata"]["router"]["source"], "fallback")
        self.assertEqual(result["metadata"]["router"]["status"], "fallback")


if __name__ == "__main__":
    unittest.main()
