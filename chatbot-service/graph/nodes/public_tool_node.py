from core.enums import Intent
from core.state import ChatState
from public_tools.booking_channels import get_booking_channels
from public_tools.doctor_schedule import get_doctor_schedule
from public_tools.service_price import get_service_prices


async def public_tool_node(state: ChatState) -> dict:
    intent = state.get("intent")
    if intent == Intent.APPOINTMENT_BOOKING.value:
        return await get_booking_channels(state)
    if intent == Intent.SERVICE_PRICE.value:
        return await get_service_prices(state)
    return await get_doctor_schedule(state)
