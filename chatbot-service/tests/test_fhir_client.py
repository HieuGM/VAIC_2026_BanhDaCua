import unittest

import httpx

from fhir.client import FhirClient, FhirClientError, FhirNotFoundError


class FhirClientTest(unittest.IsolatedAsyncioTestCase):
    async def test_get_metadata_uses_fhir_rest_json(self) -> None:
        seen = {}

        async def handler(request: httpx.Request) -> httpx.Response:
            seen["url"] = str(request.url)
            seen["accept"] = request.headers.get("accept")
            return httpx.Response(200, json={"resourceType": "CapabilityStatement"})

        client = FhirClient(
            base_url="http://fhir.test/fhir",
            transport=httpx.MockTransport(handler),
        )
        payload = await client.get_metadata()

        self.assertEqual(payload["resourceType"], "CapabilityStatement")
        self.assertEqual(seen["url"], "http://fhir.test/fhir/metadata")
        self.assertEqual(seen["accept"], "application/fhir+json")

    async def test_404_becomes_not_found_error(self) -> None:
        client = FhirClient(
            base_url="http://fhir.test/fhir",
            transport=httpx.MockTransport(lambda request: httpx.Response(404, json={})),
        )

        with self.assertRaises(FhirNotFoundError):
            await client.get_patient("missing")

    async def test_invalid_json_becomes_client_error(self) -> None:
        client = FhirClient(
            base_url="http://fhir.test/fhir",
            transport=httpx.MockTransport(lambda request: httpx.Response(200, text="not-json")),
        )

        with self.assertRaises(FhirClientError):
            await client.get_metadata()


if __name__ == "__main__":
    unittest.main()
