import unittest

from guardrails.emergency import detect_emergency, normalize_emergency_text


class EmergencyDetectorTest(unittest.TestCase):
    def test_normalizes_vietnamese_accents(self) -> None:
        self.assertEqual(
            normalize_emergency_text("Tôi đau ngực dữ dội và khó thở"),
            "toi dau nguc du doi va kho tho",
        )

    def test_detects_accented_emergency_sentence(self) -> None:
        result = detect_emergency("Tôi đau ngực dữ dội và khó thở")

        self.assertTrue(result.detected)
        self.assertEqual(result.matched_keyword, "dau nguc du doi")
        self.assertGreaterEqual(result.confidence, 0.9)

    def test_detects_unaccented_emergency_sentence(self) -> None:
        result = detect_emergency("toi dau nguc du doi va kho tho")

        self.assertTrue(result.detected)
        self.assertEqual(result.matched_keyword, "dau nguc du doi")

    def test_detects_family_member_unconscious(self) -> None:
        result = detect_emergency("bo toi dang bat tinh")

        self.assertTrue(result.detected)
        self.assertEqual(result.matched_keyword, "bat tinh")

    def test_detects_chest_pain_radiating_to_arm_shoulder_or_jaw(self) -> None:
        for text in [
            "toi dau nguc lan len tay trai",
            "toi dau nguc lan vai",
            "toi dau nguc lan len ham",
        ]:
            with self.subTest(text=text):
                result = detect_emergency(text)
                self.assertTrue(result.detected)
                self.assertEqual(result.matched_keyword, "dau nguc lan tay/vai/ham")

    def test_detects_convulsion_cyanosis_and_serious_bleeding(self) -> None:
        for text, keyword in [
            ("benh nhan dang co giat", "co giat"),
            ("moi va tay bi tim tai", "tim tai"),
            ("toi bi chay mau nghiem trong", "chay mau nghiem trong"),
        ]:
            with self.subTest(text=text):
                result = detect_emergency(text)
                self.assertTrue(result.detected)
                self.assertEqual(result.matched_keyword, keyword)

    def test_does_not_detect_negated_chest_pain_or_shortness_of_breath(self) -> None:
        for text in ["toi khong dau nguc", "toi khong kho tho", "toi khong bi ngat"]:
            with self.subTest(text=text):
                result = detect_emergency(text)
                self.assertFalse(result.detected)

    def test_marks_negated_keyword_when_rule_was_skipped(self) -> None:
        result = detect_emergency("toi khong kho tho")

        self.assertFalse(result.detected)
        self.assertTrue(result.negated)
        self.assertEqual(result.matched_keyword, "kho tho")

    def test_does_not_detect_resolved_past_context(self) -> None:
        result = detect_emergency("hom qua toi kho tho nhung gio da het")

        self.assertFalse(result.detected)
        self.assertEqual(result.reason, "resolved_past_keyword:kho tho")

    def test_detects_current_emergency_after_past_symptom(self) -> None:
        result = detect_emergency("hom qua dau nguc, bay gio kho tho")

        self.assertTrue(result.detected)
        self.assertEqual(result.matched_keyword, "kho tho")


if __name__ == "__main__":
    unittest.main()
