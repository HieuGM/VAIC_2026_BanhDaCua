import unittest

from fhir.normalizer import normalize_fhir_resource


class FhirNormalizerTest(unittest.TestCase):
    def test_observation_evidence_contains_value_and_reference_range(self) -> None:
        evidence = normalize_fhir_resource(
            {
                "resourceType": "Observation",
                "id": "obs-1",
                "status": "final",
                "code": {"text": "HbA1c"},
                "valueQuantity": {"value": 7.2, "unit": "%"},
                "referenceRange": [{"text": "Normal threshold"}],
            }
        )

        payload = evidence.model_dump(mode="json")
        self.assertEqual(payload["source_type"], "fhir")
        self.assertEqual(payload["title"], "Observation/obs-1")
        self.assertEqual(payload["data"]["value"]["value"], 7.2)
        self.assertEqual(payload["data"]["reference_range"][0]["text"], "Normal threshold")

    def test_medication_request_evidence_contains_medication_and_dosage(self) -> None:
        evidence = normalize_fhir_resource(
            {
                "resourceType": "MedicationRequest",
                "id": "med-1",
                "status": "active",
                "intent": "order",
                "medicationCodeableConcept": {"text": "Aspirin"},
                "authoredOn": "2026-07-01",
                "dosageInstruction": [{"text": "Uong 1 vien moi ngay"}],
            }
        )

        self.assertEqual(evidence.source_type.value, "fhir")
        self.assertEqual(evidence.data["medication"], "Aspirin")
        self.assertEqual(evidence.data["dosage"], ["Uong 1 vien moi ngay"])
        self.assertEqual(evidence.updated_at, "2026-07-01")

    def test_encounter_evidence_contains_period_and_type(self) -> None:
        evidence = normalize_fhir_resource(
            {
                "resourceType": "Encounter",
                "id": "enc-1",
                "status": "finished",
                "type": [{"text": "Kham ngoai tru"}],
                "period": {"start": "2026-07-01T08:00:00+07:00"},
            }
        )

        self.assertEqual(evidence.data["period"]["start"], "2026-07-01T08:00:00+07:00")
        self.assertEqual(evidence.data["type"][0]["text"], "Kham ngoai tru")

    def test_appointment_evidence_contains_start_end_status(self) -> None:
        evidence = normalize_fhir_resource(
            {
                "resourceType": "Appointment",
                "id": "apt-1",
                "status": "booked",
                "start": "2026-07-20T08:00:00+07:00",
                "end": "2026-07-20T08:30:00+07:00",
            }
        )

        self.assertEqual(evidence.data["status"], "booked")
        self.assertEqual(evidence.data["start"], "2026-07-20T08:00:00+07:00")
        self.assertEqual(evidence.data["end"], "2026-07-20T08:30:00+07:00")

    def test_diagnostic_report_evidence_contains_result_refs(self) -> None:
        evidence = normalize_fhir_resource(
            {
                "resourceType": "DiagnosticReport",
                "id": "dr-1",
                "status": "final",
                "code": {"text": "Blood test"},
                "effectiveDateTime": "2026-07-01T09:00:00+07:00",
                "result": [{"reference": "Observation/obs-1", "display": "HbA1c"}],
            }
        )

        self.assertEqual(evidence.data["code"], "Blood test")
        self.assertEqual(evidence.data["result"][0]["reference"], "Observation/obs-1")
        self.assertEqual(evidence.updated_at, "2026-07-01T09:00:00+07:00")


if __name__ == "__main__":
    unittest.main()
