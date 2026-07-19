import unittest
from unittest.mock import patch

from core.contracts import Evidence
from core.enums import SourceType
from fhir.client import FhirClientError
from graph.nodes.fhir_node import fhir_node


class FhirNodeTest(unittest.IsolatedAsyncioTestCase):
    async def test_fhir_node_catches_upstream_error(self) -> None:
        async def failing_retrieve(state):
            raise FhirClientError("FHIR server is unavailable.", "connection failed")

        with patch("graph.nodes.fhir_node.retrieve_fhir_evidence", side_effect=failing_retrieve):
            result = await fhir_node(
                {
                    "user_role": "USER",
                    "allowed_patient_ids": ["patient-1"],
                    "normalized_message": "ket qua xet nghiem cua toi",
                }
            )

        self.assertEqual(result["evidence"], [])
        self.assertEqual(result["error"]["code"], "FHIR_ERROR")
        self.assertEqual(result["error"]["message"], "FHIR server is unavailable.")
        self.assertEqual(result["metadata"]["fhir"]["status"], "upstream_error")
        self.assertEqual(result["metadata"]["fhir"]["evidence_count"], 0)
        self.assertTrue(result["needs_handoff"])

    async def test_fhir_node_adds_metadata_for_no_data(self) -> None:
        async def empty_retrieve(state):
            return []

        with patch("graph.nodes.fhir_node.retrieve_fhir_evidence", side_effect=empty_retrieve):
            result = await fhir_node(
                {
                    "user_role": "USER",
                    "allowed_patient_ids": ["patient-1"],
                    "normalized_message": "ket qua xet nghiem cua toi",
                    "metadata": {"preprocessed": True},
                }
            )

        self.assertEqual(result["evidence"], [])
        self.assertEqual(result["metadata"]["preprocessed"], True)
        self.assertEqual(result["metadata"]["fhir"]["status"], "no_data")
        self.assertEqual(result["metadata"]["fhir"]["resource_types"], [])

    async def test_fhir_node_embeds_planner_metadata(self) -> None:
        async def retrieve_with_planner_metadata(state):
            metadata = dict(state.get("metadata") or {})
            metadata["fhir_planner"] = {
                "source": "llm",
                "selected_tool": "get_patient_profile",
                "confidence": 0.86,
                "reason": "profile",
            }
            state["metadata"] = metadata
            return [
                Evidence(
                    source_type=SourceType.FHIR,
                    title="Patient/patient-1",
                    data={"resource_type": "Patient", "id": "patient-1"},
                )
            ]

        with patch("graph.nodes.fhir_node.retrieve_fhir_evidence", side_effect=retrieve_with_planner_metadata):
            result = await fhir_node(
                {
                    "user_role": "USER",
                    "allowed_patient_ids": ["patient-1"],
                    "normalized_message": "thong tin cua toi",
                }
            )

        self.assertEqual(result["metadata"]["fhir"]["planner"]["source"], "llm")
        self.assertEqual(result["metadata"]["fhir"]["planner"]["selected_tool"], "get_patient_profile")
        self.assertNotIn("fhir_planner", result["metadata"])


if __name__ == "__main__":
    unittest.main()
