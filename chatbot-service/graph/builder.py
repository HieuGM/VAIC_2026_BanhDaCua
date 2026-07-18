from langgraph.graph import END, StateGraph

from core.state import ChatState
from graph.edges import route_after_emergency, route_after_intent
from graph.nodes.answer_node import answer_node
from graph.nodes.audit_node import audit_node
from graph.nodes.emergency_node import emergency_node
from graph.nodes.fhir_node import fhir_node
from graph.nodes.hybrid_node import hybrid_node
from graph.nodes.intent_router_node import intent_router_node
from graph.nodes.memory_node import memory_node
from graph.nodes.merge_evidence_node import merge_evidence_node
from graph.nodes.output_safety_node import output_safety_node
from graph.nodes.preprocess import preprocess_node
from graph.nodes.public_tool_node import public_tool_node
from graph.nodes.rag_node import rag_node
from graph.nodes.response_cache_node import (
    response_cache_lookup_node,
    response_cache_store_node,
    route_after_response_cache,
)


def build_chat_graph():
    graph = StateGraph(ChatState)
    graph.add_node("preprocess", preprocess_node)
    graph.add_node("emergency", emergency_node)
    # Response cache: exact-match short-circuit for repeated public questions.
    # Lookup after emergency (emergency always runs); store after output_safety.
    graph.add_node("response_cache_lookup", response_cache_lookup_node)
    graph.add_node("response_cache_store", response_cache_store_node)
    graph.add_node("intent_router", intent_router_node)
    graph.add_node("rag", rag_node)
    graph.add_node("public_tool", public_tool_node)
    graph.add_node("fhir", fhir_node)
    graph.add_node("hybrid", hybrid_node)
    graph.add_node("merge_evidence", merge_evidence_node)
    graph.add_node("answer", answer_node)
    graph.add_node("output_safety", output_safety_node)
    graph.add_node("memory", memory_node)
    graph.add_node("audit", audit_node)

    graph.set_entry_point("preprocess")
    graph.add_edge("preprocess", "emergency")
    # Non-emergency turns pass through the cache lookup (route_after_emergency
    # still returns "intent_router"; we remap that key to the lookup node here so
    # edges.py is untouched).
    graph.add_conditional_edges(
        "emergency",
        route_after_emergency,
        {
            "answer": "answer",
            "intent_router": "response_cache_lookup",
        },
    )
    graph.add_conditional_edges(
        "response_cache_lookup",
        route_after_response_cache,
        {
            "hit": "output_safety",  # replay cached answer, skip router/retrieval
            "miss": "intent_router",
        },
    )
    graph.add_conditional_edges(
        "intent_router",
        route_after_intent,
        {
            "rag": "rag",
            "public_tool": "public_tool",
            "fhir": "fhir",
            "hybrid": "hybrid",
            "answer": "answer",
        },
    )
    graph.add_edge("rag", "merge_evidence")
    graph.add_edge("public_tool", "merge_evidence")
    graph.add_edge("fhir", "merge_evidence")
    graph.add_edge("hybrid", "merge_evidence")
    graph.add_edge("merge_evidence", "answer")
    graph.add_edge("answer", "output_safety")
    # Cache the safety-checked final answer (public routes only), then continue.
    graph.add_edge("output_safety", "response_cache_store")
    graph.add_edge("response_cache_store", "memory")
    graph.add_edge("memory", "audit")
    graph.add_edge("audit", END)
    return graph.compile()
