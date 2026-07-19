"""SemanticCache: exact + semantic lookup, TTL, LRU eviction, normalization,
threshold boundary, copy isolation, disabled passthrough. No model/network."""

import time
import unicodedata
import unittest

from core.contracts import Citation, Evidence
from core.enums import SourceType
from rag.config import RagSettings
from rag.semantic_cache import SemanticCache, normalize_query


def _ev(chunk_id, confidence=0.9):
    return Evidence(
        source_type=SourceType.RAG, title=chunk_id, content=f"content {chunk_id}",
        citation=Citation(source="s", title=chunk_id, chunk_id=chunk_id),
        confidence=confidence,
    )


def _cache(**kw):
    base = dict(cache_enabled=True, cache_max_entries=512,
               cache_ttl_seconds=86400.0, cache_similarity_threshold=0.95)
    base.update(kw)
    return SemanticCache(RagSettings(**base))


class NormalizeTest(unittest.TestCase):
    def test_case_and_whitespace_collapsed(self):
        self.assertEqual(normalize_query("  Gia  Kham  Benh  "), "gia kham benh")

    def test_unicode_nfc(self):
        # Same word, different byte sequences: NFC-precomposed vs NFD-decomposed
        # ("a" + U+0300 combining grave). normalize_query applies NFC → same key.
        precomposed = unicodedata.normalize("NFC", "khàm")  # "kham" w/ grave
        decomposed = unicodedata.normalize("NFD", precomposed)
        self.assertNotEqual(precomposed, decomposed)  # distinct raw sequences
        self.assertEqual(normalize_query(precomposed), normalize_query(decomposed))


class ExactLookupTest(unittest.TestCase):
    def test_put_then_exact_hit(self):
        c = _cache()
        c.put("gia kham", [1.0, 0.0], [_ev("a")])
        out = c.get_exact("  GIA  kham ")  # normalized to same key
        self.assertIsNotNone(out)
        self.assertEqual(out[0].citation.chunk_id, "a")
        self.assertEqual(c.hits_exact, 1)

    def test_miss_returns_none(self):
        self.assertIsNone(_cache().get_exact("chua co gi"))

    def test_returned_list_is_isolated_copy(self):
        # Mutating the returned Evidence must not corrupt the cached entry.
        c = _cache()
        c.put("q", [1.0, 0.0], [_ev("a", 0.9)])
        first = c.get_exact("q")
        first[0].confidence = 0.0
        first[0].citation.chunk_id = "HACKED"
        second = c.get_exact("q")
        self.assertEqual(second[0].confidence, 0.9)
        self.assertEqual(second[0].citation.chunk_id, "a")


class SemanticLookupTest(unittest.TestCase):
    def test_similar_vector_hits(self):
        c = _cache(cache_similarity_threshold=0.95)
        c.put("q1", [1.0, 0.0, 0.0], [_ev("a")])
        out = c.get_semantic([0.999, 0.03, 0.0])  # cos ~0.9996 >= 0.95
        self.assertIsNotNone(out)
        self.assertEqual(out[0].citation.chunk_id, "a")
        self.assertEqual(c.hits_semantic, 1)

    def test_dissimilar_vector_misses(self):
        c = _cache(cache_similarity_threshold=0.95)
        c.put("q1", [1.0, 0.0, 0.0], [_ev("a")])
        self.assertIsNone(c.get_semantic([0.0, 1.0, 0.0]))  # orthogonal, cos 0

    def test_threshold_boundary_inclusive(self):
        # sim exactly at threshold is a hit (>=). Build vectors with known cosine.
        c = _cache(cache_similarity_threshold=0.8)
        c.put("q1", [1.0, 0.0], [_ev("a")])
        # cos([1,0],[0.8,0.6]) = 0.8 exactly (0.8/1.0/1.0)
        self.assertIsNotNone(c.get_semantic([0.8, 0.6]))

    def test_just_below_threshold_misses(self):
        c = _cache(cache_similarity_threshold=0.8)
        c.put("q1", [1.0, 0.0], [_ev("a")])
        # cos([1,0],[0.6,0.8]) = 0.6 < 0.8
        self.assertIsNone(c.get_semantic([0.6, 0.8]))

    def test_picks_nearest_among_many(self):
        c = _cache(cache_similarity_threshold=0.9)
        c.put("far", [0.0, 1.0], [_ev("far")])
        c.put("near", [1.0, 0.0], [_ev("near")])
        out = c.get_semantic([0.98, 0.2])  # closest to 'near'
        self.assertEqual(out[0].citation.chunk_id, "near")


class TtlEvictionTest(unittest.TestCase):
    def test_expired_exact_entry_evicted(self):
        c = _cache(cache_ttl_seconds=0.0)  # everything is immediately stale
        c.put("q", [1.0, 0.0], [_ev("a")])
        time.sleep(0.01)
        self.assertIsNone(c.get_exact("q"))
        self.assertEqual(c.stats()["size"], 0)  # removed on access

    def test_expired_semantic_entry_evicted(self):
        c = _cache(cache_ttl_seconds=0.0)
        c.put("q", [1.0, 0.0], [_ev("a")])
        time.sleep(0.01)
        self.assertIsNone(c.get_semantic([1.0, 0.0]))
        self.assertEqual(c.stats()["size"], 0)


class LruEvictionTest(unittest.TestCase):
    def test_evicts_least_recently_used(self):
        c = _cache(cache_max_entries=2)
        c.put("a", [1.0, 0.0], [_ev("a")])
        c.put("b", [0.0, 1.0], [_ev("b")])
        c.get_exact("a")  # touch 'a' → 'b' now LRU
        c.put("c", [1.0, 1.0], [_ev("c")])  # exceeds bound → evict 'b'
        self.assertIsNotNone(c.get_exact("a"))
        self.assertIsNotNone(c.get_exact("c"))
        self.assertIsNone(c.get_exact("b"))
        self.assertEqual(c.stats()["size"], 2)


class PutPolicyTest(unittest.TestCase):
    def test_empty_result_not_stored(self):
        c = _cache()
        c.put("q", [1.0, 0.0], [])
        self.assertEqual(c.stats()["size"], 0)

    def test_stored_entry_isolated_from_caller_mutation(self):
        # Mutating the list passed to put() must not change the cached copy.
        c = _cache()
        items = [_ev("a", 0.9)]
        c.put("q", [1.0, 0.0], items)
        items[0].confidence = 0.0
        out = c.get_exact("q")
        self.assertEqual(out[0].confidence, 0.9)


class DisabledCacheTest(unittest.TestCase):
    def test_disabled_never_hits_or_stores(self):
        c = _cache(cache_enabled=False)
        c.put("q", [1.0, 0.0], [_ev("a")])
        self.assertIsNone(c.get_exact("q"))
        self.assertIsNone(c.get_semantic([1.0, 0.0]))
        self.assertEqual(c.stats()["size"], 0)


if __name__ == "__main__":
    unittest.main()
