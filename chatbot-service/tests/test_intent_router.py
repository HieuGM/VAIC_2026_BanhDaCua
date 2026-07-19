import unittest
from unittest.mock import patch

from core.contracts import RouteDecision
from core.enums import Intent, Route
from graph.nodes.intent_router_node import intent_router_node


class IntentRouterTest(unittest.IsolatedAsyncioTestCase):
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
        async def fake_route(state):
            return RouteDecision(
                route=Route.AUTHENTICATED_FHIR,
                intent=Intent.PATIENT_PROFILE,
                confidence=0.82,
                reason="Ambiguous profile question.",
            )

        with patch("graph.nodes.intent_router_node.route_with_llm", side_effect=fake_route):
            result = await intent_router_node({"message": "toi muon kiem tra thong tin cua minh"})

        self.assertEqual(result["route"], "AUTHENTICATED_FHIR")
        self.assertEqual(result["intent"], "PATIENT_PROFILE")
        self.assertEqual(result["metadata"]["router"]["source"], "llm")

    async def test_llm_emergency_gets_standard_emergency_patch(self) -> None:
        async def fake_route(state):
            return RouteDecision(
                route=Route.EMERGENCY,
                intent=Intent.EMERGENCY,
                confidence=0.9,
                reason="Possible emergency.",
            )

        with patch("graph.nodes.intent_router_node.route_with_llm", side_effect=fake_route):
            result = await intent_router_node({"message": "toi thay rat bat on"})

        self.assertEqual(result["route"], "EMERGENCY")
        self.assertEqual(result["intent"], "EMERGENCY")
        self.assertTrue(result["needs_handoff"])
        self.assertIn("emergency", result["safety_flags"])
        self.assertIn("115", result["answer"])

    async def test_invalid_llm_decision_falls_back_safely(self) -> None:
        async def fake_route(state):
            return RouteDecision(
                route=Route.PUBLIC_RAG,
                intent=Intent.LAB_RESULT,
                confidence=0.95,
                reason="Invalid pair.",
            )

        with patch("graph.nodes.intent_router_node.route_with_llm", side_effect=fake_route):
            result = await intent_router_node({"message": "toi muon hoi dieu gi do"})

        self.assertEqual(result["route"], "PUBLIC_RAG")
        self.assertEqual(result["intent"], "HOSPITAL_INFORMATION")
        self.assertEqual(result["metadata"]["router"]["source"], "fallback")
        self.assertEqual(result["metadata"]["router"]["status"], "fallback")


if __name__ == "__main__":
    unittest.main()
