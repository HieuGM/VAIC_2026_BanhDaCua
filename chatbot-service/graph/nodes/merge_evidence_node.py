from core.state import ChatState


async def merge_evidence_node(state: ChatState) -> dict:
    evidence = state.get("evidence") or []
    citations = []
    for item in evidence:
        citation = item.get("citation") if isinstance(item, dict) else None
        if citation:
            citations.append(citation)
    confidence = max([item.get("confidence", 0) for item in evidence if isinstance(item, dict)] or [0])
    return {"citations": citations, "confidence": confidence}
