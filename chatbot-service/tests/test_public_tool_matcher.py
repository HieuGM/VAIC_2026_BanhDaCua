import unittest
from datetime import date

from public_tools.matcher import page_items, select_best_match
from public_tools.param_extractor import (
    extract_bhyt_category,
    extract_date_range,
    extract_doctor_query,
    extract_procedure_code,
    extract_service_category,
    extract_service_query,
    normalize_text,
)


class PublicToolMatcherTest(unittest.TestCase):
    def test_normalize_vietnamese_accents(self) -> None:
        self.assertEqual(normalize_text("Đặt lịch khám Tim mạch"), "dat lich kham tim mach")

    def test_service_query_and_category(self) -> None:
        self.assertEqual(extract_service_category("giá siêu âm doppler tim"), "imaging")
        self.assertEqual(extract_service_query("giá siêu âm doppler tim"), "sieu am doppler tim")
        self.assertIsNone(extract_service_query("gia dich vu"))

    def test_bhyt_procedure_and_date_extraction(self) -> None:
        self.assertEqual(extract_bhyt_category("bhyt dong chi tra the nao"), "copay")
        self.assertEqual(extract_procedure_code("quy trinh kham"), "QT.25.01")
        self.assertEqual(extract_date_range("xem lich ngay 2026-07-18"), ("2026-07-18", "2026-07-18"))

    def test_doctor_query_and_slash_date_extraction(self) -> None:
        self.assertEqual(
            extract_doctor_query("Bác sĩ Võ Thị Ngọc Anh có lịch khám ngày nào?"),
            "vo thi ngoc anh",
        )
        self.assertEqual(
            extract_doctor_query("Lịch bác sĩ tim mạch ngày 16/7"),
            "tim mach",
        )
        self.assertIsNone(extract_doctor_query("ngày 16/7 có khám không"))
        self.assertEqual(
            extract_date_range("ngày 16/7", today=date(2026, 7, 19)),
            ("2026-07-16", "2026-07-16"),
        )

    def test_fuzzy_match_typo(self) -> None:
        result = select_best_match(
            "sieu am dopler tim",
            [{"id": 1, "name": "Siêu âm Doppler tim"}],
            fields=["name"],
        )

        self.assertEqual(result.status, "ok")
        self.assertEqual(result.selected["id"], 1)

    def test_many_close_matches_need_selection(self) -> None:
        result = select_best_match(
            "sieu am",
            [
                {"id": 1, "name": "Siêu âm tim"},
                {"id": 2, "name": "Siêu âm Doppler tim"},
            ],
            fields=["name"],
        )

        self.assertEqual(result.status, "needs_selection")
        self.assertEqual(len(result.options), 2)

    def test_no_match_and_page_items(self) -> None:
        result = select_best_match("sieu am tim", [{"id": 1, "name": "Xet nghiem mau"}], fields=["name"])
        self.assertEqual(result.status, "no_data")

        items, truncated, total = page_items({"items": [{"id": 1}], "total": 10})
        self.assertEqual(items, [{"id": 1}])
        self.assertTrue(truncated)
        self.assertEqual(total, 10)


if __name__ == "__main__":
    unittest.main()
