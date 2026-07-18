from core.enums import Intent
from core.state import ChatState
from public_tools.bhyt_policies import get_bhyt_policies
from public_tools.booking_channels import get_booking_channels
from public_tools.departments import get_departments
from public_tools.doctor_schedule import get_doctor_schedule
from public_tools.hospital_info import get_hospital_info
from public_tools.procedures import get_procedures
from public_tools.service_price import get_service_prices


async def public_tool_node(state: ChatState) -> dict:
    intent = state.get("intent")
    if intent == Intent.APPOINTMENT_BOOKING.value:
        return await get_booking_channels(state)
    if intent == Intent.SERVICE_PRICE.value:
        return await get_service_prices(state)
    if intent == Intent.DOCTOR_SCHEDULE.value:
        return await get_doctor_schedule(state)
    if intent in {
        Intent.HOSPITAL_CONTACT.value,
        Intent.WORKING_HOURS.value,
        Intent.HOSPITAL_INFORMATION.value,
    }:
        return await get_hospital_info(state)
    if intent == Intent.DEPARTMENT_INFORMATION.value:
        return await get_departments(state)
    if intent in {
        Intent.EXAMINATION_PROCEDURE.value,
        Intent.APPOINTMENT_GUIDANCE.value,
    }:
        return await get_procedures(state)
    if intent == Intent.BHYT_INFORMATION.value:
        return await get_bhyt_policies(state)
    return await get_hospital_info(state)
