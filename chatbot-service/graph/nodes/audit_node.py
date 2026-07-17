from core.state import ChatState
from observability.audit import write_audit_event


async def audit_node(state: ChatState) -> dict:
    await write_audit_event(state)
    metadata = dict(state.get("metadata") or {})
    metadata["audit_logged"] = True
    return {"metadata": metadata}
