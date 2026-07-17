from core.state import ChatState


async def memory_node(state: ChatState) -> dict:
    # Store only compact, non-sensitive session hints here in later implementation.
    metadata = dict(state.get("metadata") or {})
    metadata["memory_updated"] = False
    return {"metadata": metadata}
