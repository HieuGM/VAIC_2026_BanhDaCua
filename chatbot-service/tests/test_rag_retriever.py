"""retrieve_public_knowledge orchestration: return-[] discipline, dense gate,
threshold, never-raise. Seams (embedder/store/sparse/rerank) are mocked so no
model, Qdrant file, or network is needed."""

import unittest
from types import SimpleNamespace
from unittest.mock import patch

from core.enums import SourceType
from rag import retriever
from rag.config import RagSettings

# Fixed settings so boundary tests can't be flipped by a dev/CI .env override.
_TEST_SETTINGS = RagSettings(
    dense_min_score=0.5, rerank_min_score=0.1, rerank_top_k=5, prefetch_limit=20
)


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


def _patches(store):
    return [
        patch.object(retriever, "get_settings", return_value=_TEST_SETTINGS),
        patch.object(retriever, "get_store", return_value=store),
        patch.object(retriever, "get_embedder", return_value=_FakeEmbedder()),
        patch.object(retriever, "_sparse_query", return_value={"indices": [1], "values": [1.0]}),
        patch.object(retriever, "rerank_evidence", _passthrough_rerank),
    ]


class RetrieverTest(unittest.IsolatedAsyncioTestCase):
    async def _run(self, msg, store):
        ctxs = _patches(store)
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


if __name__ == "__main__":
    unittest.main()
