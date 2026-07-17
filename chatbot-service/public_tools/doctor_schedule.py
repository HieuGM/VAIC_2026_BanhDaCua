from core.contracts import Evidence
from core.enums import SourceType
from core.state import ChatState


async def get_doctor_schedule(state: ChatState) -> dict:
    # TODO: connect official/public doctor schedule source.
    evidence = Evidence(
        source_type=SourceType.PUBLIC_API,
        title="Doctor schedule placeholder",
        data={"message": "Doctor schedule API is not connected yet."},
        confidence=0.1,
    )
    return {"evidence": [evidence.model_dump(mode="json")]}
