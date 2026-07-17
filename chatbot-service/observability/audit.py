import logging

from core.state import ChatState


log = logging.getLogger(__name__)


async def write_audit_event(state: ChatState) -> None:
    log.info(
        "chat_audit session_id=%s user_role=%s intent=%s route=%s flags=%s",
        state.get("session_id"),
        state.get("user_role"),
        state.get("intent"),
        state.get("route"),
        state.get("safety_flags") or [],
    )
