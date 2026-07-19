"""Graph response cache: exact-match lookup/store, PII/route exclusion, TTL,
LRU, route function, and that build_chat_graph() still compiles with the two
new nodes wired in. No network/model."""

import unittest

from core.enums import Route
from graph.nodes import response_cache_node as rc


def _state(**kw):
    base = {"normalized_message": "giá khám bệnh", "route": Route.PUBLIC_RAG.value,
            "answer": "Giá khám là 42.100đ.", "citations": [{"source": "s"}],
            "confidence": 0.9, "intent": "SERVICE_PRICE"}
    base.update(kw)
    return base


class LookupStoreTest(unittest.TestCase):
    def setUp(self):
        rc.reset_response_cache()

    def test_miss_returns_empty_patch(self):
        self.assertEqual(rc.response_cache_lookup_node(_state()), {})

    def test_store_then_hit_replays_response(self):
        rc.response_cache_store_node(_state())
        hit = rc.response_cache_lookup_node(_state())
        self.assertEqual(hit["answer"], "Giá khám là 42.100đ.")
        self.assertEqual(hit["route"], Route.PUBLIC_RAG.value)
        self.assertEqual(hit["metadata"]["response_cache"], "hit")

    def test_key_normalized(self):
        rc.response_cache_store_node(_state(normalized_message="giá khám bệnh"))
        hit = rc.response_cache_lookup_node(_state(normalized_message="  GIÁ  Khám  Bệnh "))
        self.assertIsNotNone(hit.get("answer"))

    def test_hit_result_isolated_from_cache(self):
        rc.response_cache_store_node(_state())
        first = rc.response_cache_lookup_node(_state())
        first["citations"].append({"source": "HACK"})
        second = rc.response_cache_lookup_node(_state())
        self.assertEqual(len(second["citations"]), 1)  # cache untouched


class RouteExclusionTest(unittest.TestCase):
    def setUp(self):
        rc.reset_response_cache()

    def _stored(self, **kw):
        rc.response_cache_store_node(_state(**kw))
        return rc.get_response_cache().size()

    def test_fhir_not_cached(self):
        self.assertEqual(self._stored(route=Route.AUTHENTICATED_FHIR.value), 0)

    def test_hybrid_not_cached(self):
        self.assertEqual(self._stored(route=Route.FIXED_HYBRID.value), 0)

    def test_public_rag_and_tool_cached(self):
        self.assertEqual(self._stored(route=Route.PUBLIC_RAG.value), 1)
        rc.reset_response_cache()
        self.assertEqual(self._stored(route=Route.PUBLIC_TOOL.value), 1)

    def test_handoff_not_cached(self):
        self.assertEqual(self._stored(needs_handoff=True), 0)

    def test_safety_flagged_not_cached(self):
        self.assertEqual(self._stored(safety_flags=["EMERGENCY"]), 0)

    def test_error_not_cached(self):
        self.assertEqual(self._stored(error={"code": "x"}), 0)

    def test_empty_answer_not_cached(self):
        self.assertEqual(self._stored(answer=""), 0)

    def test_cache_hit_turn_not_restored(self):
        # A turn already served from cache must not be re-stored.
        st = _state(metadata={"response_cache": "hit"})
        rc.response_cache_store_node(st)
        self.assertEqual(rc.get_response_cache().size(), 0)


class RouteFunctionTest(unittest.TestCase):
    def test_route_after_cache(self):
        self.assertEqual(rc.route_after_response_cache({}), "miss")
        self.assertEqual(
            rc.route_after_response_cache({"metadata": {"response_cache": "hit"}}), "hit"
        )


class CacheEvictionTest(unittest.TestCase):
    def test_ttl_expiry(self):
        import time
        cache = rc.ResponseCache(ttl=0.0)  # everything is immediately stale
        cache.put("q", {"answer": "a"})
        time.sleep(0.01)
        self.assertIsNone(cache.get("q"))

    def test_lru_eviction(self):
        cache = rc.ResponseCache(max_entries=2)
        cache.put("a", {"answer": "a"})
        cache.put("b", {"answer": "b"})
        cache.get("a")  # touch a → b is LRU
        cache.put("c", {"answer": "c"})
        self.assertIsNotNone(cache.get("a"))
        self.assertIsNone(cache.get("b"))
        self.assertIsNotNone(cache.get("c"))


class GraphCompileTest(unittest.TestCase):
    def test_build_chat_graph_compiles_with_cache_nodes(self):
        from graph.builder import build_chat_graph

        compiled = build_chat_graph()  # raises if nodes/edges are miswired
        self.assertIsNotNone(compiled)


if __name__ == "__main__":
    unittest.main()
