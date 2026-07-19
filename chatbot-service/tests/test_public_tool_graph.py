import unittest
from unittest.mock import patch

from core.contracts import RouteDecision
from core.enums import Intent, Route
from graph.builder import build_chat_graph
from public_tools.tool_response import public_evidence, public_tool_patch


def _router_decision(intent: Intent) -> RouteDecision:
    return RouteDecision(
        route=Route.PUBLIC_TOOL,
        intent=intent,
        confidence=0.9,
        reason="mocked public tool route",
    )


class PublicToolGraphTest(unittest.IsolatedAsyncioTestCase):
    async def test_graph_routes_booking_to_public_tool_and_formats_answer(self) -> None:
        async def fake_booking_channels(state):
            return public_tool_patch(
                state=state,
                tool="get_booking_channels",
                status="ok",
                evidence=[
                    public_evidence(
                        "Kênh đặt lịch",
                        {
                            "channels": [
                                {
                                    "channelType": "hotline",
                                    "label": "Tong dai dat lich",
                                    "phone": "1900",
                                }
                            ]
                        },
                    )
                ],
                queried_endpoints=["/channels"],
            )

        async def fake_route(state):
            return _router_decision(Intent.APPOINTMENT_BOOKING)

        graph = build_chat_graph()
        with (
            patch("graph.nodes.intent_router_node.route_with_llm", side_effect=fake_route),
            patch("graph.nodes.public_tool_node.get_booking_channels", side_effect=fake_booking_channels) as mocked,
        ):
            result = await graph.ainvoke(
                {
                    "session_id": "test-public-tool",
                    "user_role": "ANONYMOUS",
                    "message": "dat lich kham",
                    "context": {},
                }
            )

        self.assertTrue(mocked.called)
        self.assertEqual(result["route"], "PUBLIC_TOOL")
        self.assertEqual(result["intent"], "APPOINTMENT_BOOKING")
        self.assertEqual(result["metadata"]["public_tool"]["status"], "ok")
        self.assertEqual(result["evidence"][0]["source_type"], "public_api")
        self.assertIn("Các kênh hỗ trợ/đặt lịch", result["answer"])
        self.assertIn("Tong dai dat lich", result["answer"])
        self.assertNotIn("{", result["answer"])

    async def test_graph_routes_bhyt_to_public_tool_without_rag(self) -> None:
        async def fake_bhyt(state):
            return public_tool_patch(
                state=state,
                tool="get_bhyt_policies",
                status="ok",
                evidence=[
                    public_evidence(
                        "Thông tin BHYT",
                        {"policies": [{"title": "Muc huong BHYT", "summary": "Thong tin cong khai."}]},
                    )
                ],
                queried_endpoints=["/bhyt-policies"],
            )

        async def fake_route(state):
            return _router_decision(Intent.BHYT_INFORMATION)

        graph = build_chat_graph()
        with (
            patch("graph.nodes.intent_router_node.route_with_llm", side_effect=fake_route),
            patch("graph.nodes.public_tool_node.get_bhyt_policies", side_effect=fake_bhyt) as mocked,
        ):
            result = await graph.ainvoke(
                {
                    "session_id": "test-public-tool-bhyt",
                    "user_role": "ANONYMOUS",
                    "message": "bhyt can giay to gi",
                    "context": {},
                }
            )

        self.assertTrue(mocked.called)
        self.assertEqual(result["route"], "PUBLIC_TOOL")
        self.assertEqual(result["intent"], "BHYT_INFORMATION")
        self.assertIn("Thông tin BHYT", result["answer"])
        self.assertIn("Muc huong BHYT", result["answer"])

    async def test_graph_routes_doctor_schedule_to_public_tool_with_llm_router(self) -> None:
        async def fake_doctor_schedule(state):
            return public_tool_patch(
                state=state,
                tool="get_doctor_schedule",
                status="ok",
                evidence=[
                    public_evidence(
                        "Lịch bác sĩ Võ Thị Ngọc Anh",
                        {
                            "doctor": {"id": 8, "fullName": "Võ Thị Ngọc Anh"},
                            "schedules": [{"dayOfWeek": 3, "startTime": "09:00"}],
                        },
                    )
                ],
                queried_endpoints=["/doctors", "/doctors/8/schedules"],
            )

        async def fake_route(state):
            return _router_decision(Intent.DOCTOR_SCHEDULE)

        graph = build_chat_graph()
        with (
            patch("graph.nodes.intent_router_node.route_with_llm", side_effect=fake_route),
            patch("graph.nodes.public_tool_node.get_doctor_schedule", side_effect=fake_doctor_schedule) as mocked,
        ):
            result = await graph.ainvoke(
                {
                    "session_id": "test-public-tool-doctor",
                    "user_role": "ANONYMOUS",
                    "message": "Bác sĩ Võ Thị Ngọc Anh có lịch khám ngày nào?",
                    "context": {},
                }
            )

        self.assertTrue(mocked.called)
        self.assertEqual(result["route"], "PUBLIC_TOOL")
        self.assertEqual(result["intent"], "DOCTOR_SCHEDULE")
        self.assertEqual(result["metadata"]["router"]["source"], "llm")
        self.assertIn("Võ Thị Ngọc Anh", result["answer"])


if __name__ == "__main__":
    unittest.main()
