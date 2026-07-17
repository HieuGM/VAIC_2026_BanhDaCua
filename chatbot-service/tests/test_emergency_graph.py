import unittest
from unittest.mock import patch

import graph.builder as graph_builder


async def fail_if_called(state):
    raise AssertionError("Regular graph node should not be called for emergency route")


class EmergencyGraphTest(unittest.IsolatedAsyncioTestCase):
    async def test_emergency_route_short_circuits_regular_nodes(self) -> None:
        with (
            patch.object(graph_builder, "intent_router_node", fail_if_called),
            patch.object(graph_builder, "rag_node", fail_if_called),
            patch.object(graph_builder, "fhir_node", fail_if_called),
            patch.object(graph_builder, "public_tool_node", fail_if_called),
            patch.object(graph_builder, "hybrid_node", fail_if_called),
        ):
            graph = graph_builder.build_chat_graph()
            result = await graph.ainvoke(
                {
                    "session_id": "test-emergency",
                    "user_role": "ANONYMOUS",
                    "message": "Toi dau nguc du doi va kho tho",
                    "context": {},
                }
            )

        self.assertEqual(result["route"], "EMERGENCY")
        self.assertEqual(result["intent"], "EMERGENCY")
        self.assertTrue(result["needs_handoff"])
        self.assertIn("emergency", result["safety_flags"])
        self.assertIn("115", result["answer"])
        self.assertTrue(result["metadata"]["emergency"]["detected"])
        self.assertEqual(result["metadata"]["emergency"]["matched_keyword"], "dau nguc du doi")


if __name__ == "__main__":
    unittest.main()
