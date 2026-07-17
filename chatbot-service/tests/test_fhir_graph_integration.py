import unittest
from unittest.mock import patch

from core.contracts import Evidence
from core.enums import SourceType
from graph.builder import build_chat_graph


class FhirGraphIntegrationTest(unittest.IsolatedAsyncioTestCase):
    async def test_graph_routes_fhir_question_to_fhir_node(self) -> None:
        async def fake_retrieve(state):
            return [
                Evidence(
                    source_type=SourceType.FHIR,
                    title="Observation/obs-1",
                    data={"resource_type": "Observation", "id": "obs-1", "code": "HbA1c"},
                )
            ]

        graph = build_chat_graph()
        with patch("graph.nodes.fhir_node.retrieve_fhir_evidence", side_effect=fake_retrieve) as mocked:
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
        self.assertIn("Observation/obs-1", result["answer"])


if __name__ == "__main__":
    unittest.main()
