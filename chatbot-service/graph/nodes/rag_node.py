from core.state import ChatState
from rag.retriever import retrieve_public_knowledge


async def rag_node(state: ChatState) -> dict:
    evidence = await retrieve_public_knowledge(state)
    return {"evidence": [item.model_dump(mode="json") for item in evidence]}
