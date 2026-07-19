import unittest
from pathlib import Path

from graph.nodes.output_safety_node import output_safety_node


ROOT = Path(__file__).resolve().parents[1]

USER_FACING_TEMPLATE_FILES = [
    ROOT / "fhir" / "formatter.py",
    ROOT / "public_tools" / "formatter.py",
    ROOT / "public_tools" / "booking_channels.py",
    ROOT / "public_tools" / "doctor_schedule.py",
    ROOT / "public_tools" / "service_price.py",
    ROOT / "public_tools" / "hospital_info.py",
    ROOT / "public_tools" / "departments.py",
    ROOT / "public_tools" / "procedures.py",
    ROOT / "public_tools" / "bhyt_policies.py",
    ROOT / "public_tools" / "data_api_client.py",
    ROOT / "llm" / "answer_generator.py",
    ROOT / "graph" / "nodes" / "answer_node.py",
    ROOT / "graph" / "nodes" / "emergency_node.py",
    ROOT / "graph" / "nodes" / "output_safety_node.py",
]

OLD_NO_DIACRITIC_PHRASES = [
    "Minh chua",
    "du lieu",
    "benh vien",
    "Vui long",
    "cap cuu",
    "ho so",
    "xet nghiem",
]


class UserFacingVietnameseTest(unittest.IsolatedAsyncioTestCase):
    def test_user_facing_templates_do_not_use_old_unaccented_phrases(self):
        offenders = []
        for path in USER_FACING_TEMPLATE_FILES:
            text = path.read_text(encoding="utf-8")
            for phrase in OLD_NO_DIACRITIC_PHRASES:
                if phrase in text:
                    offenders.append(f"{path.relative_to(ROOT)}: {phrase}")

        self.assertEqual(offenders, [])

    async def test_output_safety_fallback_has_diacritics(self):
        result = await output_safety_node({"answer": "hay dung thuoc"})

        self.assertIn(
            "Mình chưa thể trả lời nội dung này một cách an toàn",
            result["answer"],
        )
        self.assertTrue(result["needs_handoff"])
