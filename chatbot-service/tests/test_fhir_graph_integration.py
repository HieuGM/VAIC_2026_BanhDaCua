import unittest
from unittest.mock import patch

from core.contracts import Evidence, RouteDecision
from core.enums import Intent, Route, SourceType
from fhir.client import FhirClientError
from graph.builder import build_chat_graph


async def _fake_lab_route(state):
    return RouteDecision(
        route=Route.AUTHENTICATED_FHIR,
        intent=Intent.LAB_RESULT,
        confidence=0.9,
        reason="mocked FHIR lab route",
    )


class FhirGraphIntegrationTest(unittest.IsolatedAsyncioTestCase):
    async def test_graph_routes_fhir_question_to_fhir_node_and_formats_answer(self) -> None:
        async def fake_retrieve(state):
            return [
                Evidence(
                    source_type=SourceType.FHIR,
                    title="Observation/obs-1",
                    data={
                        "resource_type": "Observation",
                        "id": "obs-1",
                        "code": "HbA1c",
                        "value": {"value": 7.2, "unit": "%"},
                        "effective_time": "2026-07-01T09:00:00+07:00",
                    },
                )
            ]

        graph = build_chat_graph()
        with (
            patch("graph.nodes.intent_router_node.route_with_llm", side_effect=_fake_lab_route),
            patch("graph.nodes.fhir_node.retrieve_fhir_evidence", side_effect=fake_retrieve) as mocked,
        ):
            result = await graph.ainvoke(
                {
                    "session_id": "test-fhir",
                    "user_role": "USER",
                    "message": "ket qua xet nghiem cua toi",
                    "allowed_patient_ids": ["patient-1"],
                    "context": {},
                }
            )

        self.assertTrue(mocked.called)
        self.assertEqual(result["route"], "AUTHENTICATED_FHIR")
        self.assertEqual(result["evidence"][0]["source_type"], "fhir")
        self.assertIn("HbA1c", result["answer"])
        self.assertIn("7.2 %", result["answer"])
        self.assertNotIn("{", result["answer"])
        self.assertEqual(result["metadata"]["fhir"]["status"], "ok")
        self.assertEqual(result["metadata"]["fhir"]["resource_types"], ["Observation"])

    async def test_graph_fhir_no_data_does_not_handoff(self) -> None:
        async def fake_retrieve(state):
            return []

        graph = build_chat_graph()
        with (
            patch("graph.nodes.intent_router_node.route_with_llm", side_effect=_fake_lab_route),
            patch("graph.nodes.fhir_node.retrieve_fhir_evidence", side_effect=fake_retrieve),
        ):
            result = await graph.ainvoke(
                {
                    "session_id": "test-fhir-empty",
                    "user_role": "USER",
                    "message": "ket qua xet nghiem cua toi",
                    "allowed_patient_ids": ["patient-1"],
                    "context": {},
                }
            )

        self.assertEqual(result["route"], "AUTHENTICATED_FHIR")
        self.assertFalse(result.get("needs_handoff", False))
        self.assertIn("Mình chưa tìm thấy dữ liệu phù hợp", result["answer"])
        self.assertEqual(result["metadata"]["fhir"]["status"], "no_data")

    async def test_graph_fhir_permission_error_handoffs_safely(self) -> None:
        graph = build_chat_graph()
        with patch("graph.nodes.intent_router_node.route_with_llm", side_effect=_fake_lab_route):
            result = await graph.ainvoke(
                {
                    "session_id": "test-fhir-denied",
                    "user_role": "USER",
                    "message": "ket qua xet nghiem cua toi",
                    "allowed_patient_ids": [],
                    "context": {},
                }
            )

        self.assertEqual(result["route"], "AUTHENTICATED_FHIR")
        self.assertTrue(result["needs_handoff"])
        self.assertIn("unauthorized_patient_access", result["safety_flags"])
        self.assertEqual(result["metadata"]["fhir"]["status"], "permission_denied")

    async def test_graph_fhir_upstream_error_handoffs_without_raw_exception(self) -> None:
        async def failing_retrieve(state):
            raise FhirClientError("FHIR server is unavailable.", "connection failed: secret host")

        graph = build_chat_graph()
        with (
            patch("graph.nodes.intent_router_node.route_with_llm", side_effect=_fake_lab_route),
            patch("graph.nodes.fhir_node.retrieve_fhir_evidence", side_effect=failing_retrieve),
        ):
            result = await graph.ainvoke(
                {
                    "session_id": "test-fhir-error",
                    "user_role": "USER",
                    "message": "ket qua xet nghiem cua toi",
                    "allowed_patient_ids": ["patient-1"],
                    "context": {},
                }
            )

        self.assertEqual(result["route"], "AUTHENTICATED_FHIR")
        self.assertTrue(result["needs_handoff"])
        self.assertEqual(result["error"]["message"], "FHIR server is unavailable.")
        self.assertNotIn("secret host", result["answer"])
        self.assertEqual(result["metadata"]["fhir"]["status"], "upstream_error")


if __name__ == "__main__":
    unittest.main()
