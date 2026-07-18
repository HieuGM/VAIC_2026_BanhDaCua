"""rerank_evidence: passthrough when disabled/empty, re-score+sort, confidence
clamp, graceful degrade. The cross-encoder is mocked (no model load)."""

import unittest
from unittest.mock import patch

from core.contracts import Citation, Evidence
from core.enums import SourceType
from rag import reranker
from rag.config import RagSettings


def _ev(title, confidence):
    return Evidence(
        source_type=SourceType.RAG, title=title, content=f"content {title}",
        citation=Citation(source="s", title=title, chunk_id=title), confidence=confidence,
    )


class _FakeReranker:
    def __init__(self, scores):
        self._scores = scores

    def score(self, query, docs):
        return self._scores


class _BoomReranker:
    def score(self, query, docs):
        raise RuntimeError("model crashed")


def _settings(**kw):
    base = {"rerank_enabled": True, "rerank_provider": "cross_encoder"}
    base.update(kw)
    return RagSettings(**base)


class RerankTest(unittest.IsolatedAsyncioTestCase):
    async def test_empty_items_returns_empty(self):
        with patch.object(reranker, "get_settings", return_value=_settings()):
            self.assertEqual(await reranker.rerank_evidence([], "q"), [])

    async def test_disabled_is_passthrough(self):
        items = [_ev("a", 0.9), _ev("b", 0.1)]
        with patch.object(reranker, "get_settings", return_value=_settings(rerank_enabled=False)):
            out = await reranker.rerank_evidence(items, "q")
        self.assertEqual([e.title for e in out], ["a", "b"])  # untouched order

    async def test_provider_none_is_passthrough(self):
        items = [_ev("a", 0.9)]
        with patch.object(reranker, "get_settings", return_value=_settings(rerank_provider="none")):
            out = await reranker.rerank_evidence(items, "q")
        self.assertEqual(out, items)

    async def test_rescore_and_sort_desc(self):
        items = [_ev("a", 0.5), _ev("b", 0.5)]  # 'b' should win after rerank
        with patch.object(reranker, "get_settings", return_value=_settings()), \
             patch.object(reranker, "get_reranker", return_value=_FakeReranker([0.2, 0.9])):
            out = await reranker.rerank_evidence(items, "q")
        self.assertEqual([e.title for e in out], ["b", "a"])
        self.assertAlmostEqual(out[0].confidence, 0.9)
        self.assertAlmostEqual(out[1].confidence, 0.2)

    async def test_confidence_clamped(self):
        items = [_ev("a", 0.5), _ev("b", 0.5)]
        with patch.object(reranker, "get_settings", return_value=_settings()), \
             patch.object(reranker, "get_reranker", return_value=_FakeReranker([1.5, -0.3])):
            out = await reranker.rerank_evidence(items, "q")
        confs = {e.title: e.confidence for e in out}
        self.assertEqual(confs["a"], 1.0)
        self.assertEqual(confs["b"], 0.0)

    async def test_graceful_degrade_on_error(self):
        items = [_ev("a", 0.7), _ev("b", 0.3)]
        with patch.object(reranker, "get_settings", return_value=_settings()), \
             patch.object(reranker, "get_reranker", return_value=_BoomReranker()), \
             self.assertLogs("rag.reranker", level="ERROR"):  # captures + asserts log
            out = await reranker.rerank_evidence(items, "q")
        self.assertEqual(out, items)  # unchanged, no raise


if __name__ == "__main__":
    unittest.main()
