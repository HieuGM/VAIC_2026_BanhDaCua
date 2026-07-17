import unittest

from fhir.tools import (
    get_lab_results,
    get_medications,
    get_patient_appointments,
    get_patient_encounters,
    retrieve_fhir_evidence,
)


class FakeFhirClient:
    def __init__(self, resources_by_type=None):
        self.resources_by_type = resources_by_type or {}
        self.calls = []

    async def search_patient_resources(self, resource_type, patient_id, *, count=10, sort=None):
        self.calls.append(
            {
                "resource_type": resource_type,
                "patient_id": patient_id,
                "count": count,
                "sort": sort,
            }
        )
        resources = self.resources_by_type.get(resource_type, [])
        return {
            "resourceType": "Bundle",
            "entry": [{"resource": resource} for resource in resources],
        }

    async def get_patient(self, patient_id):
        self.calls.append({"resource_type": "Patient", "patient_id": patient_id})
        return {"resourceType": "Patient", "id": patient_id, "name": [{"text": "Demo Patient"}]}


def _state(message="ket qua xet nghiem cua toi"):
    return {
        "user_role": "USER",
        "allowed_patient_ids": ["patient-1"],
        "normalized_message": message,
        "context": {"limit": 5},
    }


class FhirToolsTest(unittest.IsolatedAsyncioTestCase):
    async def test_get_lab_results_calls_observation_and_diagnostic_report(self) -> None:
        client = FakeFhirClient(
            {
                "Observation": [{"resourceType": "Observation", "id": "obs-1", "code": {"text": "HbA1c"}}],
                "DiagnosticReport": [{"resourceType": "DiagnosticReport", "id": "dr-1", "code": {"text": "Blood test"}}],
            }
        )

        evidence = await get_lab_results(_state(), client=client)

        self.assertEqual([call["resource_type"] for call in client.calls], ["Observation", "DiagnosticReport"])
        self.assertEqual([item.source_type.value for item in evidence], ["fhir", "fhir"])

    async def test_get_medications_calls_medication_request(self) -> None:
        client = FakeFhirClient(
            {
                "MedicationRequest": [
                    {
                        "resourceType": "MedicationRequest",
                        "id": "med-1",
                        "medicationCodeableConcept": {"text": "Aspirin"},
                    }
                ]
            }
        )

        evidence = await get_medications(_state("don thuoc cua toi"), client=client)

        self.assertEqual(client.calls[0]["resource_type"], "MedicationRequest")
        self.assertEqual(evidence[0].data["medication"], "Aspirin")

    async def test_get_patient_appointments_calls_appointment(self) -> None:
        client = FakeFhirClient({"Appointment": [{"resourceType": "Appointment", "id": "apt-1", "status": "booked"}]})

        evidence = await get_patient_appointments(_state("lich hen cua toi"), client=client)

        self.assertEqual(client.calls[0]["resource_type"], "Appointment")
        self.assertEqual(evidence[0].data["status"], "booked")

    async def test_get_patient_encounters_calls_encounter(self) -> None:
        client = FakeFhirClient({"Encounter": [{"resourceType": "Encounter", "id": "enc-1", "status": "finished"}]})

        evidence = await get_patient_encounters(_state("lan kham cua toi"), client=client)

        self.assertEqual(client.calls[0]["resource_type"], "Encounter")
        self.assertEqual(evidence[0].title, "Encounter/enc-1")

    async def test_empty_bundle_returns_empty_evidence(self) -> None:
        client = FakeFhirClient({"MedicationRequest": []})

        evidence = await get_medications(_state("don thuoc cua toi"), client=client)

        self.assertEqual(evidence, [])

    async def test_retrieve_uses_allowed_patient_not_message_patient(self) -> None:
        client = FakeFhirClient({"MedicationRequest": [{"resourceType": "MedicationRequest", "id": "med-1"}]})
        state = _state("don thuoc cua Patient/patient-999")

        await retrieve_fhir_evidence(state, client=client)

        self.assertEqual(client.calls[0]["patient_id"], "patient-1")

    async def test_retrieve_supports_vietnamese_with_accents_directly(self) -> None:
        client = FakeFhirClient({"Observation": [{"resourceType": "Observation", "id": "obs-1"}]})
        state = _state("kết quả xét nghiệm của tôi")

        await retrieve_fhir_evidence(state, client=client)

        self.assertEqual(client.calls[0]["resource_type"], "Observation")


if __name__ == "__main__":
    unittest.main()
