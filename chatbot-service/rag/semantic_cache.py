"""In-process semantic cache for RAG retrieval results.

Skips repeated retrieval work for repetitive FAQ traffic (hospital: giá khám,
lịch khám, BHYT...). Two lookup levels:

1. Exact-match on the normalized query string — a byte-identical repeat returns
   the cached Evidence with ZERO correctness risk and ZERO API calls (no embed,
   no Qdrant, no rerank).
2. Semantic — cosine of the query's dense embedding vs cached query embeddings.
   A paraphrase at/above `cache_similarity_threshold` returns the cached
   Evidence, skipping Qdrant + rerank (the embed call already happened, since we
   need the vector to look up).

Correctness guards (medical domain — a wrong cached answer is dangerous):
- Conservative default threshold (0.95); the value is calibrated on the eval set
  (rag/eval/measure_semantic_cache.py), not guessed.
- Only NON-EMPTY results are cached — an off-topic/below-gate query is never
  stored, so it can neither pollute the LRU nor suppress a later real query.
- TTL eviction bounds staleness (prices/schedules change; effective-date drift).
- Date-scoped namespace: keys carry today's date, so the day rollover (when the
  effective-date filter changes) stops matching yesterday's answers.
- In-process only: a redeploy / re-ingest starts a fresh process → empty cache,
  so a KB change can never serve stale entries across versions.

Single-process deployment (embedded Qdrant holds a single-process lock, so the
server runs one worker) → a plain in-memory store is correct and needs no Redis.
Thread-safe: retrieve_public_knowledge runs in asyncio + to_thread workers.
"""

import logging
import threading
import time
import unicodedata
from collections import OrderedDict
from dataclasses import dataclass
from datetime import date

import numpy as np

from core.contracts import Evidence
from rag.config import RagSettings, get_settings

_log = logging.getLogger(__name__)


def normalize_query(text: str) -> str:
    """Stable exact-match key: NFC, lowercased, whitespace collapsed. Cheap and
    deterministic — two visually identical questions map to the same key."""
    return " ".join(unicodedata.normalize("NFC", text).lower().split())


def _l2_normalize(vec: np.ndarray) -> np.ndarray:
    """Unit-length so a dot product equals cosine similarity."""
    norm = float(np.linalg.norm(vec))
    return vec / norm if norm > 0.0 else vec


def _copy_evidence(items: list[Evidence]) -> list[Evidence]:
    """Deep copy so cached entries and returned lists never alias — the graph or
    a concurrent request must not mutate what the next hit will serve."""
    return [e.model_copy(deep=True) for e in items]


@dataclass
class _Entry:
    vector: np.ndarray  # L2-normalized query embedding (float32)
    evidence: list[Evidence]
    created: float  # epoch seconds, for TTL


class SemanticCache:
    """LRU + TTL cache of query -> Evidence. Exact and semantic lookup."""

    def __init__(self, settings: RagSettings):
        self._enabled = settings.cache_enabled
        self._max = settings.cache_max_entries
        self._ttl = settings.cache_ttl_seconds
        self._threshold = settings.cache_similarity_threshold
        self._version = settings.cache_version
        self._store: "OrderedDict[str, _Entry]" = OrderedDict()
        self._lock = threading.Lock()
        # Observability — measure real hit rate in prod, don't guess.
        self.hits_exact = 0
        self.hits_semantic = 0
        self.misses = 0

    @property
    def enabled(self) -> bool:
        return self._enabled

    def _key(self, query: str) -> str:
        # Version + date namespace so a config bump or the midnight rollover
        # (effective-date filter change) invalidates prior answers.
        return f"{self._version}|{date.today().isoformat()}|{normalize_query(query)}"

    def _is_fresh(self, entry: _Entry, now: float) -> bool:
        return (now - entry.created) <= self._ttl

    def get_exact(self, query: str) -> list[Evidence] | None:
        """Byte-identical (normalized) hit — no embed/Qdrant/rerank needed."""
        if not self._enabled:
            return None
        key = self._key(query)
        with self._lock:
            entry = self._store.get(key)
            if entry is None:
                return None
            if not self._is_fresh(entry, time.time()):
                del self._store[key]
                return None
            self._store.move_to_end(key)  # LRU touch
            self.hits_exact += 1
            _log.info("semantic cache HIT (exact) — skipped embed+Qdrant+rerank")
            return _copy_evidence(entry.evidence)

    def get_semantic(self, vector: list[float]) -> list[Evidence] | None:
        """Nearest cached query by cosine; hit only if >= threshold. Skips
        Qdrant + rerank. Evicts expired entries encountered during the scan."""
        if not self._enabled:
            return None
        v = _l2_normalize(np.asarray(vector, dtype=np.float32))
        now = time.time()
        with self._lock:
            best_key: str | None = None
            best_sim = -1.0
            expired: list[str] = []
            for key, entry in self._store.items():
                if not self._is_fresh(entry, now):
                    expired.append(key)
                    continue
                sim = float(entry.vector @ v)
                if sim > best_sim:
                    best_sim, best_key = sim, key
            for key in expired:
                del self._store[key]
            if best_key is not None and best_sim >= self._threshold:
                self._store.move_to_end(best_key)
                self.hits_semantic += 1
                _log.info("semantic cache HIT (semantic sim=%.4f) — skipped Qdrant+rerank", best_sim)
                return _copy_evidence(self._store[best_key].evidence)
            return None

    def put(self, query: str, vector: list[float], evidence: list[Evidence]) -> None:
        """Store a NON-EMPTY result. Empty results are intentionally not cached
        (see module docstring). Evicts LRU entries past the size bound."""
        if not self._enabled or not evidence:
            return
        key = self._key(query)
        v = _l2_normalize(np.asarray(vector, dtype=np.float32))
        with self._lock:
            self._store[key] = _Entry(
                vector=v, evidence=_copy_evidence(evidence), created=time.time()
            )
            self._store.move_to_end(key)
            self.misses += 1
            while len(self._store) > self._max:
                self._store.popitem(last=False)  # drop least-recently-used

    def clear(self) -> None:
        with self._lock:
            self._store.clear()

    def stats(self) -> dict[str, int]:
        with self._lock:
            return {
                "size": len(self._store),
                "hits_exact": self.hits_exact,
                "hits_semantic": self.hits_semantic,
                "misses": self.misses,
            }


_CACHE: SemanticCache | None = None
_CACHE_LOCK = threading.Lock()


def get_cache(settings: RagSettings | None = None) -> SemanticCache:
    """Process-wide singleton (thread-safe double-checked init)."""
    global _CACHE
    if _CACHE is None:
        with _CACHE_LOCK:
            if _CACHE is None:
                _CACHE = SemanticCache(settings or get_settings())
    return _CACHE


def reset_cache() -> None:
    """Drop the cached instance (test isolation / config change)."""
    global _CACHE
    _CACHE = None
