from core.contracts import Citation, Evidence
from core.enums import SourceType
from core.state import ChatState


async def retrieve_public_knowledge(state: ChatState) -> list[Evidence]:
    # TODO(RAG owner): hybrid search + metadata filter + rerank.
    # Return [] when evidence is not strong enough; answer node will fallback safely.
    text = state.get("normalized_message") or ""
    if not text:
        return []
    return [
        Evidence(
            source_type=SourceType.RAG,
            title="KB placeholder",
            content="Placeholder evidence. Replace with approved hospital knowledge base chunks.",
            citation=Citation(
                source="hospital_kb",
                title="KB placeholder",
                chunk_id="placeholder",
                snippet="Replace with approved hospital knowledge base chunks.",
            ),
            confidence=0.2,
        )
    ]
