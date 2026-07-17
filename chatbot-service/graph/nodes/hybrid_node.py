from core.state import ChatState
from rag.retriever import retrieve_public_knowledge


async def hybrid_node(state: ChatState) -> dict:
    # MVP placeholder: run RAG only. Later this node can combine RAG + public tools/FHIR.
    evidence = await retrieve_public_knowledge(state)
    return {
        "evidence": [item.model_dump(mode="json") for item in evidence],
        "metadata": {"hybrid_mode": "rag_only_placeholder"},
    }
