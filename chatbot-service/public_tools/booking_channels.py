from app.config import get_settings
from core.contracts import Evidence
from core.enums import SourceType
from core.state import ChatState


async def get_booking_channels(state: ChatState) -> dict:
    settings = get_settings()
    channels = {
        "website": settings.booking_website_url,
        "zalo": settings.booking_zalo_url,
        "hotline": settings.hotline,
    }
    evidence = Evidence(
        source_type=SourceType.PUBLIC_API,
        title="Official booking channels",
        data={"channels": channels},
        confidence=0.8,
    )
    return {
        "evidence": [evidence.model_dump(mode="json")],
        "redirection": channels,
    }
