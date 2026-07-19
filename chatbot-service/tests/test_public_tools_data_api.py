import unittest

from public_tools.bhyt_policies import get_bhyt_policies
from public_tools.booking_channels import get_booking_channels
from public_tools.data_api_client import DataApiError
from public_tools.departments import get_departments
from public_tools.doctor_schedule import get_doctor_schedule
from public_tools.hospital_info import get_hospital_info
from public_tools.procedures import get_procedures
from public_tools.service_price import get_service_prices


class FakeDataApiClient:
    def __init__(self, responses):
        self.responses = responses
        self.calls = []

    async def get(self, path, params=None):
        self.calls.append((path, params or {}))
        response = self.responses.get(path)
        if isinstance(response, Exception):
            raise response
        return response


class PublicToolsDataApiTest(unittest.IsolatedAsyncioTestCase):
    async def test_booking_channels_returns_evidence_and_redirection(self) -> None:
        client = FakeDataApiClient(
            {
                "/channels": [
                    {"id": 1, "channelType": "hotline", "label": "Tong dai", "phone": "1900"},
                ]
            }
        )

        result = await get_booking_channels({"metadata": {"router": {"source": "rule"}}}, client=client)

        self.assertEqual(result["metadata"]["public_tool"]["status"], "ok")
        self.assertEqual(result["metadata"]["router"]["source"], "rule")
        self.assertEqual(result["evidence"][0]["source_type"], "public_api")
        self.assertEqual(result["redirection"]["phone"], "1900")

    async def test_hospital_info_returns_contact(self) -> None:
        client = FakeDataApiClient(
            {
                "/hospital-info": {
                    "name": "Benh vien Tim Ha Noi",
                    "hotline": "024",
                    "website": "https://example.test",
                }
            }
        )

        result = await get_hospital_info({}, client=client)

        self.assertEqual(result["metadata"]["public_tool"]["status"], "ok")
        self.assertEqual(result["redirection"]["hotline"], "024")

    async def test_service_price_ok_calls_prices_endpoint(self) -> None:
        client = FakeDataApiClient(
            {
                "/services": {"items": [{"id": 11, "name": "Siêu âm Doppler tim", "category": "ct"}], "total": 1},
                "/services/11/prices": [{"priceVnd": 300000, "audience": "self_pay"}],
            }
        )

        result = await get_service_prices({"message": "gia sieu am dopler tim"}, client=client)

        self.assertEqual(result["metadata"]["public_tool"]["status"], "ok")
        self.assertEqual(client.calls[0][1]["category"], "ct")
        self.assertEqual(client.calls[1][0], "/services/11/prices")
        self.assertEqual(result["evidence"][0]["data"]["prices"][0]["priceVnd"], 300000)

    async def test_service_price_needs_selection_no_data_and_upstream_error(self) -> None:
        selection_client = FakeDataApiClient(
            {
                "/services": {
                    "items": [
                        {"id": 1, "name": "Sieu am tim"},
                        {"id": 2, "name": "Sieu am Doppler tim"},
                    ],
                    "total": 2,
                }
            }
        )
        selection = await get_service_prices({"message": "gia sieu am"}, client=selection_client)
        self.assertEqual(selection["metadata"]["public_tool"]["status"], "needs_selection")

        empty_client = FakeDataApiClient({"/services": {"items": [{"id": 1, "name": "Xet nghiem mau"}], "total": 1}})
        no_data = await get_service_prices({"message": "gia sieu am tim"}, client=empty_client)
        self.assertEqual(no_data["metadata"]["public_tool"]["status"], "no_data")

        error_client = FakeDataApiClient({"/services": DataApiError("loi cong khai")})
        upstream = await get_service_prices({"message": "gia sieu am tim"}, client=error_client)
        self.assertEqual(upstream["metadata"]["public_tool"]["status"], "upstream_error")

    async def test_doctor_schedule_ok_and_selection(self) -> None:
        client = FakeDataApiClient(
            {
                "/doctors": {
                    "items": [{"id": 7, "fullName": "Nguyen Van A", "specialty": "Tim mach"}],
                    "total": 1,
                },
                "/doctors/7/schedules": [{"doctorId": 7, "dayOfWeek": 2, "startTime": "08:00"}],
            }
        )

        result = await get_doctor_schedule({"message": "lich bac si Nguyen Van A"}, client=client)

        self.assertEqual(result["metadata"]["public_tool"]["status"], "ok")
        self.assertEqual(client.calls[1][0], "/doctors/7/schedules")

        named_client = FakeDataApiClient(
            {
                "/doctors": {
                    "items": [{"id": 8, "fullName": "Võ Thị Ngọc Anh", "specialty": "Tim mạch"}],
                    "total": 1,
                },
                "/doctors/8/schedules": [{"doctorId": 8, "dayOfWeek": 3, "startTime": "09:00"}],
            }
        )
        named = await get_doctor_schedule(
            {"message": "Bác sĩ Võ Thị Ngọc Anh có lịch khám ngày nào?"},
            client=named_client,
        )
        self.assertEqual(named["metadata"]["public_tool"]["status"], "ok")
        self.assertEqual(named_client.calls[1][0], "/doctors/8/schedules")

        clarification_client = FakeDataApiClient({})
        clarification = await get_doctor_schedule(
            {"message": "ngày 16/7 có khám không"},
            client=clarification_client,
        )
        self.assertEqual(clarification["metadata"]["public_tool"]["status"], "needs_clarification")
        self.assertEqual(clarification_client.calls, [])

        selection_client = FakeDataApiClient(
            {
                "/doctors": {
                    "items": [
                        {"id": 1, "fullName": "Nguyen Van A", "specialty": "Tim mach"},
                        {"id": 2, "fullName": "Tran Van B", "specialty": "Tim mach"},
                    ],
                    "total": 2,
                }
            }
        )
        selection = await get_doctor_schedule({"message": "lich bac si tim mach"}, client=selection_client)
        self.assertEqual(selection["metadata"]["public_tool"]["status"], "needs_selection")

    async def test_departments_procedures_and_bhyt_return_public_api_evidence(self) -> None:
        departments = await get_departments(
            {},
            client=FakeDataApiClient({"/departments": {"items": [{"name": "Khoa Tim mach"}], "total": 1}}),
        )
        procedures = await get_procedures(
            {"message": "quy trinh kham"},
            client=FakeDataApiClient({"/procedures": [{"code": "QT.25.01", "stepNo": 1, "name": "Dang ky"}]}),
        )
        bhyt = await get_bhyt_policies(
            {"message": "bhyt dong chi tra"},
            client=FakeDataApiClient({"/bhyt-policies": [{"title": "Muc huong", "category": "copay"}]}),
        )

        for result in [departments, procedures, bhyt]:
            self.assertEqual(result["metadata"]["public_tool"]["status"], "ok")
            self.assertEqual(result["evidence"][0]["source_type"], "public_api")


if __name__ == "__main__":
    unittest.main()
