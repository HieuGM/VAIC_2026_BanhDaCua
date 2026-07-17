from core.contracts import Evidence
from core.enums import SourceType
from core.state import ChatState


async def get_service_prices(state: ChatState) -> dict:
    # TODO: connect official/public service price source.
    evidence = Evidence(
        source_type=SourceType.PUBLIC_API,
        title="Service price placeholder",
        data={"message": "Service price API is not connected yet."},
        confidence=0.1,
    )
    return {"evidence": [evidence.model_dump(mode="json")]}
