import unittest
from types import SimpleNamespace
from unittest.mock import patch

from graph.nodes.emergency_node import emergency_node


class EmergencyNodeTest(unittest.IsolatedAsyncioTestCase):
    async def test_emergency_node_returns_standard_response_and_metadata(self) -> None:
        with patch(
            "graph.nodes.emergency_node.get_settings",
            return_value=SimpleNamespace(emergency_number="115", hotline="1900-0000"),
        ):
            result = await emergency_node(
                {
                    "normalized_message": "toi dau nguc du doi va kho tho",
                    "safety_flags": ["existing_flag"],
                    "metadata": {"preprocessed": True},
                }
            )

        self.assertEqual(result["intent"], "EMERGENCY")
        self.assertEqual(result["route"], "EMERGENCY")
        self.assertIn("emergency", result["safety_flags"])
        self.assertIn("existing_flag", result["safety_flags"])
        self.assertTrue(result["needs_handoff"])
        self.assertIn("115", result["answer"])
        self.assertIn("1900-0000", result["answer"])
        self.assertTrue(result["metadata"]["preprocessed"])
        self.assertTrue(result["metadata"]["emergency"]["detected"])
        self.assertEqual(result["metadata"]["emergency"]["matched_keyword"], "dau nguc du doi")

    async def test_emergency_node_returns_empty_patch_when_not_detected(self) -> None:
        result = await emergency_node({"normalized_message": "toi muon hoi quy trinh kham"})

        self.assertEqual(result, {})


if __name__ == "__main__":
    unittest.main()
