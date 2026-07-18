import unittest

from core.enums import Route
from public_tools.formatter import generate_public_tool_answer
from public_tools.tool_response import public_evidence


class PublicToolFormatterTest(unittest.TestCase):
    def test_hospital_info_does_not_render_raw_json(self) -> None:
        answer = generate_public_tool_answer(
            {
                "route": Route.PUBLIC_TOOL.value,
                "metadata": {
                    "public_tool": {
                        "tool": "get_hospital_info",
                        "status": "ok",
                    }
                },
                "evidence": [
                    public_evidence(
                        "Thong tin benh vien",
                        {
                            "hospital_info": {
                                "name": "Benh vien Tim Ha Noi",
                                "hotline": "024",
                                "addresses": [{"main": "92 Tran Hung Dao"}],
                                "workingHours": {"weekday": "07:00-17:00"},
                            }
                        },
                    )
                ],
            }
        )

        self.assertIn("92 Tran Hung Dao", answer)
        self.assertIn("07:00-17:00", answer)
        self.assertNotIn("{", answer)


if __name__ == "__main__":
    unittest.main()
