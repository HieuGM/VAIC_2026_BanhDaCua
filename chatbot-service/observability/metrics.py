from core.state import ChatState


async def record_chat_metrics(state: ChatState) -> None:
    # TODO: expose counters for route, intent, fallback, emergency, latency.
    return None
