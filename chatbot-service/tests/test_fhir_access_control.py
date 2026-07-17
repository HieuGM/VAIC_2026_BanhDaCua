import unittest

from core.errors import PermissionDenied
from fhir.access_control import resolve_allowed_patient_id


class FhirAccessControlTest(unittest.TestCase):
    def test_user_with_allowed_patient_ids_resolves_first_patient(self) -> None:
        patient_id = resolve_allowed_patient_id(
            {
                "user_role": "USER",
                "allowed_patient_ids": ["patient-1"],
                "message": "ket qua xet nghiem cua toi",
            }
        )
        self.assertEqual(patient_id, "patient-1")

    def test_user_with_patient_reference_scope_is_normalized(self) -> None:
        patient_id = resolve_allowed_patient_id(
            {
                "user_role": "USER",
                "allowed_patient_ids": ["Patient/patient-1"],
            }
        )
        self.assertEqual(patient_id, "patient-1")

    def test_user_without_allowed_patient_ids_is_denied(self) -> None:
        with self.assertRaises(PermissionDenied):
            resolve_allowed_patient_id({"user_role": "USER", "allowed_patient_ids": []})

    def test_anonymous_is_denied(self) -> None:
        with self.assertRaises(PermissionDenied):
            resolve_allowed_patient_id({"user_role": "ANONYMOUS", "allowed_patient_ids": ["patient-1"]})

    def test_message_patient_id_is_ignored(self) -> None:
        patient_id = resolve_allowed_patient_id(
            {
                "user_role": "USER",
                "allowed_patient_ids": ["patient-1"],
                "message": "Cho toi xem Patient/patient-999",
            }
        )
        self.assertEqual(patient_id, "patient-1")


if __name__ == "__main__":
    unittest.main()
