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


def build_chat_graph():
    graph = StateGraph(ChatState)
    graph.add_node("preprocess", preprocess_node)
    graph.add_node("emergency", emergency_node)
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
    graph.add_conditional_edges(
        "emergency",
        route_after_emergency,
        {
            "answer": "answer",
            "intent_router": "intent_router",
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
    graph.add_edge("output_safety", "memory")
    graph.add_edge("memory", "audit")
    graph.add_edge("audit", END)
    return graph.compile()
