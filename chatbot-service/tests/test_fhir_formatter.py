import unittest

from fhir.formatter import NO_FHIR_DATA_MESSAGE, generate_fhir_answer


def _state(evidence):
    return {
        "route": "AUTHENTICATED_FHIR",
        "intent": "LAB_RESULT",
        "normalized_message": "ket qua xet nghiem cua toi",
        "evidence": evidence,
    }


def _evidence(resource_type, data):
    payload = {"resource_type": resource_type, **data}
    return {
        "source_type": "fhir",
        "title": f"{resource_type}/{payload.get('id', 'test')}",
        "data": payload,
        "confidence": 1.0,
    }


class FhirFormatterTest(unittest.TestCase):
    def test_observation_answer_contains_value_unit_and_time(self) -> None:
        answer = generate_fhir_answer(
            _state(
                [
                    _evidence(
                        "Observation",
                        {
                            "id": "obs-1",
                            "code": "HbA1c",
                            "value": {"value": 7.2, "unit": "%"},
                            "effective_time": "2026-07-01T09:00:00+07:00",
                            "reference_range": [{"text": "4.0 - 6.0 %"}],
                        },
                    )
                ]
            )
        )

        self.assertIsNotNone(answer)
        self.assertIn("HbA1c", answer)
        self.assertIn("7.2 %", answer)
        self.assertIn("09:00 ngay 01/07/2026", answer)
        self.assertIn("4.0 - 6.0 %", answer)

    def test_diagnostic_report_answer_contains_status_conclusion_and_result_refs(self) -> None:
        answer = generate_fhir_answer(
            _state(
                [
                    _evidence(
                        "DiagnosticReport",
                        {
                            "id": "dr-1",
                            "code": "Blood test",
                            "status": "final",
                            "effective_time": "2026-07-01",
                            "conclusion": "Da co ket qua",
                            "result": [{"reference": "Observation/obs-1", "display": "HbA1c"}],
                        },
                    )
                ]
            )
        )

        self.assertIn("Blood test", answer)
        self.assertIn("trang thai: final", answer)
        self.assertIn("ket luan: Da co ket qua", answer)
        self.assertIn("HbA1c", answer)

    def test_medication_answer_contains_medication_dosage_and_authored_on(self) -> None:
        answer = generate_fhir_answer(
            {
                "route": "AUTHENTICATED_FHIR",
                "normalized_message": "don thuoc cua toi",
                "evidence": [
                    _evidence(
                        "MedicationRequest",
                        {
                            "id": "med-1",
                            "medication": "Aspirin",
                            "dosage": ["Uong 1 vien moi ngay"],
                            "authored_on": "2026-07-01",
                        },
                    )
                ],
            }
        )

        self.assertIn("Aspirin", answer)
        self.assertIn("Uong 1 vien moi ngay", answer)
        self.assertIn("01/07/2026", answer)

    def test_appointment_answer_contains_start_end_status_and_participant(self) -> None:
        answer = generate_fhir_answer(
            {
                "route": "AUTHENTICATED_FHIR",
                "normalized_message": "lich hen cua toi",
                "evidence": [
                    _evidence(
                        "Appointment",
                        {
                            "id": "apt-1",
                            "description": "Tai kham tim mach",
                            "start": "2026-07-20T08:00:00+07:00",
                            "end": "2026-07-20T08:30:00+07:00",
                            "status": "booked",
                            "participant": [{"actor": {"display": "BS Nguyen Van A"}}],
                        },
                    )
                ],
            }
        )

        self.assertIn("Tai kham tim mach", answer)
        self.assertIn("08:00 ngay 20/07/2026", answer)
        self.assertIn("08:30 ngay 20/07/2026", answer)
        self.assertIn("booked", answer)
        self.assertIn("BS Nguyen Van A", answer)

    def test_encounter_answer_contains_period_status_type_and_location(self) -> None:
        answer = generate_fhir_answer(
            {
                "route": "AUTHENTICATED_FHIR",
                "normalized_message": "lan kham cua toi",
                "evidence": [
                    _evidence(
                        "Encounter",
                        {
                            "id": "enc-1",
                            "status": "finished",
                            "type": [{"text": "Kham ngoai tru"}],
                            "period": {
                                "start": "2026-07-01T08:00:00+07:00",
                                "end": "2026-07-01T09:00:00+07:00",
                            },
                            "location": [{"location": {"display": "Phong kham Tim mach"}}],
                        },
                    )
                ],
            }
        )

        self.assertIn("Kham ngoai tru", answer)
        self.assertIn("08:00 ngay 01/07/2026", answer)
        self.assertIn("09:00 ngay 01/07/2026", answer)
        self.assertIn("finished", answer)
        self.assertIn("Phong kham Tim mach", answer)

    def test_patient_answer_contains_basic_profile(self) -> None:
        answer = generate_fhir_answer(
            {
                "route": "AUTHENTICATED_FHIR",
                "normalized_message": "ho so cua toi",
                "evidence": [
                    _evidence(
                        "Patient",
                        {
                            "id": "patient-1",
                            "name": "Nguyen Van B",
                            "birth_date": "1990-02-03",
                            "gender": "male",
                            "identifier": [{"value": "BN001"}],
                            "telecom": [{"value": "0900000000"}],
                        },
                    )
                ],
            }
        )

        self.assertIn("Nguyen Van B", answer)
        self.assertIn("03/02/1990", answer)
        self.assertIn("BN001", answer)
        self.assertIn("0900000000", answer)

    def test_no_evidence_returns_fhir_no_data_message(self) -> None:
        answer = generate_fhir_answer(_state([]))

        self.assertEqual(answer, NO_FHIR_DATA_MESSAGE)
        self.assertNotIn("{", answer)


if __name__ == "__main__":
    unittest.main()
