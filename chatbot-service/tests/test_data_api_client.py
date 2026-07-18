import unittest

import httpx

from public_tools.data_api_client import DataApiClient, DataApiError


class DataApiClientTest(unittest.IsolatedAsyncioTestCase):
    async def test_get_uses_base_url_and_api_key(self) -> None:
        seen = {}

        def handler(request: httpx.Request) -> httpx.Response:
            seen["url"] = str(request.url)
            seen["api_key"] = request.headers.get("X-API-Key")
            return httpx.Response(200, json={"ok": True})

        client = DataApiClient(
            base_url="http://data.test/data/v1/",
            api_key="secret",
            transport=httpx.MockTransport(handler),
        )

        result = await client.get("/channels", params={"active": True, "empty": ""})

        self.assertEqual(result, {"ok": True})
        self.assertEqual(seen["api_key"], "secret")
        self.assertEqual(seen["url"], "http://data.test/data/v1/channels?active=true")

    async def test_http_error_becomes_data_api_error(self) -> None:
        client = DataApiClient(
            base_url="http://data.test/data/v1",
            transport=httpx.MockTransport(lambda request: httpx.Response(500, json={"error": "boom"})),
        )

        with self.assertRaises(DataApiError) as context:
            await client.get("/hospital-info")

        self.assertEqual(context.exception.status_code, 500)

    async def test_network_error_becomes_data_api_error(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            raise httpx.ConnectError("network down", request=request)

        client = DataApiClient(
            base_url="http://data.test/data/v1",
            transport=httpx.MockTransport(handler),
        )

        with self.assertRaises(DataApiError):
            await client.get("/channels")

    async def test_invalid_json_becomes_data_api_error(self) -> None:
        client = DataApiClient(
            base_url="http://data.test/data/v1",
            transport=httpx.MockTransport(lambda request: httpx.Response(200, text="not-json")),
        )

        with self.assertRaises(DataApiError):
            await client.get("/channels")


if __name__ == "__main__":
    unittest.main()
