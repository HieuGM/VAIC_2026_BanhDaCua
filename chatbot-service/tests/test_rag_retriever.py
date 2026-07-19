"""retrieve_public_knowledge orchestration: return-[] discipline, dense gate,
threshold, never-raise. Seams (embedder/store/sparse/rerank) are mocked so no
model, Qdrant file, or network is needed."""

import unittest
from types import SimpleNamespace
from unittest.mock import patch

from core.enums import SourceType
from rag import retriever
from rag.config import RagSettings
from rag.semantic_cache import SemanticCache

# Fixed settings so boundary tests can't be flipped by a dev/CI .env override.
_TEST_SETTINGS = RagSettings(
    dense_min_score=0.5, rerank_min_score=0.1, rerank_top_k=5, prefetch_limit=20
)


def _disabled_cache() -> SemanticCache:
    # Pipeline-behavior tests must exercise the real path every call, so the
    # process-wide cache is replaced by a disabled instance (also isolates
    # tests that reuse the same query string).
    return SemanticCache(RagSettings(cache_enabled=False))


def _hit(score, chunk_id):
    return SimpleNamespace(score=score, payload={
        "title": "T", "content": "nội dung", "source": "s.txt",
        "source_type": "document", "chunk_id": chunk_id, "snippet": "snip",
        "url": None, "updated_at": None,
    })


async def _passthrough_rerank(items, query):  # identity; retriever sorts itself
    return items


class _FakeStore:
    def __init__(self, dense_hits, hybrid_hits):
        self._d, self._h = dense_hits, hybrid_hits

    def dense_search(self, vec, *, limit, query_filter=None):
        return self._d

    def hybrid_search(self, dvec, svec, *, limit, query_filter=None):
        return self._h


class _FakeEmbedder:
    def embed_query(self, text):
        return [0.1, 0.2, 0.3, 0.4]


def _patches(store, cache=None):
    return [
        patch.object(retriever, "get_settings", return_value=_TEST_SETTINGS),
        patch.object(retriever, "get_store", return_value=store),
        patch.object(retriever, "get_embedder", return_value=_FakeEmbedder()),
        patch.object(retriever, "_sparse_query", return_value={"indices": [1], "values": [1.0]}),
        patch.object(retriever, "rerank_evidence", _passthrough_rerank),
        patch.object(retriever, "get_cache", return_value=cache or _disabled_cache()),
    ]


class RetrieverTest(unittest.IsolatedAsyncioTestCase):
    async def _run(self, msg, store, cache=None):
        ctxs = _patches(store, cache)
        for c in ctxs:
            c.start()
        try:
            return await retriever.retrieve_public_knowledge({"normalized_message": msg})
        finally:
            for c in ctxs:
                c.stop()

    async def test_empty_query_returns_empty(self):
        self.assertEqual(await retriever.retrieve_public_knowledge({"normalized_message": ""}), [])

    async def test_whitespace_query_returns_empty(self):
        self.assertEqual(await retriever.retrieve_public_knowledge({"normalized_message": "   "}), [])

    async def test_no_dense_hits_returns_empty(self):
        out = await self._run("giờ làm việc", _FakeStore([], []))
        self.assertEqual(out, [])

    async def test_below_dense_gate_returns_empty(self):
        # Top cosine 0.4 < dense_min_score 0.5 -> safe fallback [].
        store = _FakeStore([_hit(0.4, "a")], [_hit(0.4, "a")])
        self.assertEqual(await self._run("câu hỏi mơ hồ", store), [])

    async def test_happy_path_returns_grounded_evidence(self):
        dense = [_hit(0.9, "a"), _hit(0.7, "b")]
        store = _FakeStore(dense, [_hit(0.9, "a"), _hit(0.7, "b")])
        out = await self._run("giá khám bệnh", store)
        self.assertEqual(len(out), 2)
        self.assertTrue(all(e.source_type == SourceType.RAG for e in out))
        self.assertEqual(out[0].citation.chunk_id, "a")  # sorted by confidence desc
        self.assertGreaterEqual(out[0].confidence, out[1].confidence)

    async def test_low_confidence_candidate_dropped_by_threshold(self):
        # Gate passes (top 0.9) but 'b' cosine 0.05 < rerank_min_score 0.1 -> dropped.
        dense = [_hit(0.9, "a"), _hit(0.05, "b")]
        store = _FakeStore(dense, [_hit(0.9, "a"), _hit(0.05, "b")])
        out = await self._run("giá khám bệnh", store)
        self.assertEqual([e.citation.chunk_id for e in out], ["a"])

    async def test_sparse_only_hit_gets_dense_floor(self):
        # 'b' is a sparse-only hybrid hit (absent from dense) -> confidence floor
        # = dense_min_score (0.5), still above the 0.1 threshold so it's kept.
        store = _FakeStore([_hit(0.9, "a")], [_hit(0.9, "a"), _hit(0.8, "b")])
        out = await self._run("giá dịch vụ", store)
        conf = {e.citation.chunk_id: e.confidence for e in out}
        self.assertEqual(conf["a"], 0.9)
        self.assertEqual(conf["b"], 0.5)  # floor, not the hybrid 0.8 score

    async def test_respects_top_k(self):
        dense = [_hit(0.9 - i * 0.01, f"c{i}") for i in range(12)]
        store = _FakeStore(dense, list(dense))
        out = await self._run("nhiều ứng viên", store)
        self.assertLessEqual(len(out), 5)  # rerank_top_k

    async def test_never_raises_into_graph(self):
        class Boom:
            def dense_search(self, *a, **k):
                raise RuntimeError("qdrant down")
        with self.assertLogs("rag.retriever", level="ERROR"):  # captures + asserts log
            out = await self._run("giờ làm việc", Boom())
        self.assertEqual(out, [])  # exception swallowed -> []


class _CountingStore:
    """Records how many times Qdrant is touched so tests can prove a cache hit
    skipped the search."""

    def __init__(self, dense_hits, hybrid_hits):
        self._d, self._h = dense_hits, hybrid_hits
        self.dense_calls = 0

    def dense_search(self, vec, *, limit, query_filter=None):
        self.dense_calls += 1
        return self._d

    def hybrid_search(self, dvec, svec, *, limit, query_filter=None):
        return self._h


class _MapEmbedder:
    """Returns a chosen vector per query text; counts embed calls."""

    def __init__(self, mapping):
        self._map = mapping
        self.calls = 0

    def embed_query(self, text):
        self.calls += 1
        return self._map[text]


class SemanticCacheIntegrationTest(unittest.IsolatedAsyncioTestCase):
    """retrieve_public_knowledge short-circuits via the cache (real cache, not
    disabled). The reranker is still patched to passthrough."""

    async def _run(self, msg, store, embedder, cache):
        ctxs = [
            patch.object(retriever, "get_settings", return_value=_TEST_SETTINGS),
            patch.object(retriever, "get_store", return_value=store),
            patch.object(retriever, "get_embedder", return_value=embedder),
            patch.object(retriever, "_sparse_query",
                         return_value={"indices": [1], "values": [1.0]}),
            patch.object(retriever, "rerank_evidence", _passthrough_rerank),
            patch.object(retriever, "get_cache", return_value=cache),
        ]
        for c in ctxs:
            c.start()
        try:
            return await retriever.retrieve_public_knowledge({"normalized_message": msg})
        finally:
            for c in ctxs:
                c.stop()

    async def test_exact_hit_skips_embed_and_search(self):
        cache = SemanticCache(RagSettings(cache_enabled=True, cache_similarity_threshold=0.95))
        store = _CountingStore([_hit(0.9, "a")], [_hit(0.9, "a")])
        emb = _MapEmbedder({"giá khám bệnh": [1.0, 0.0, 0.0, 0.0]})
        first = await self._run("giá khám bệnh", store, emb, cache)
        # Identical query (different case/spacing) → exact hit, no new work.
        second = await self._run("  Giá  Khám  Bệnh  ", store, emb, cache)
        self.assertEqual([e.citation.chunk_id for e in first], ["a"])
        self.assertEqual([e.citation.chunk_id for e in second], ["a"])
        self.assertEqual(store.dense_calls, 1)  # 2nd call served from cache
        self.assertEqual(emb.calls, 1)  # exact match never embeds
        self.assertEqual(cache.hits_exact, 1)

    async def test_semantic_hit_skips_search_but_embeds(self):
        cache = SemanticCache(RagSettings(cache_enabled=True, cache_similarity_threshold=0.95))
        store = _CountingStore([_hit(0.9, "a")], [_hit(0.9, "a")])
        # Two DIFFERENT strings whose vectors are nearly identical (cos ~0.9998).
        emb = _MapEmbedder({
            "giá khám bệnh bao nhiêu": [1.0, 0.0, 0.0, 0.0],
            "chi phí khám bệnh là bao nhiêu": [0.999, 0.02, 0.0, 0.0],
        })
        await self._run("giá khám bệnh bao nhiêu", store, emb, cache)
        out = await self._run("chi phí khám bệnh là bao nhiêu", store, emb, cache)
        self.assertEqual([e.citation.chunk_id for e in out], ["a"])
        self.assertEqual(store.dense_calls, 1)  # 2nd query reused via similarity
        self.assertEqual(emb.calls, 2)  # semantic lookup needs the vector
        self.assertEqual(cache.hits_semantic, 1)

    async def test_dissimilar_query_misses_and_searches(self):
        cache = SemanticCache(RagSettings(cache_enabled=True, cache_similarity_threshold=0.95))
        store = _CountingStore([_hit(0.9, "a")], [_hit(0.9, "a")])
        emb = _MapEmbedder({
            "giá khám bệnh": [1.0, 0.0, 0.0, 0.0],
            "địa chỉ bệnh viện": [0.0, 1.0, 0.0, 0.0],  # orthogonal → cos 0
        })
        await self._run("giá khám bệnh", store, emb, cache)
        await self._run("địa chỉ bệnh viện", store, emb, cache)
        self.assertEqual(store.dense_calls, 2)  # unrelated query runs full search
        self.assertEqual(cache.hits_semantic, 0)

    async def test_empty_result_not_cached(self):
        # Below-gate query returns [] and must not be stored (no LRU pollution,
        # no chance to suppress a later real query).
        cache = SemanticCache(RagSettings(cache_enabled=True))
        store = _CountingStore([_hit(0.4, "a")], [_hit(0.4, "a")])  # 0.4 < gate 0.5
        emb = _MapEmbedder({"câu mơ hồ": [1.0, 0.0, 0.0, 0.0]})
        self.assertEqual(await self._run("câu mơ hồ", store, emb, cache), [])
        self.assertEqual(cache.stats()["size"], 0)


if __name__ == "__main__":
    unittest.main()
