"""Graph-level response cache — short-circuits the pipeline for a repeated
PUBLIC question, returning the finalized answer WITHOUT calling the intent
router LLM (the per-day rate-limited model), retrieval, or answer generation.

Placement (see graph/builder.py):
  ... -> emergency -> [response_cache_lookup] -> intent_router -> ...
       ... -> output_safety -> [response_cache_store] -> memory -> ...
- Lookup sits AFTER emergency: emergency detection MUST run on every turn and is
  never served from cache (patient safety).
- Store sits AFTER output_safety: the cached text is the safety-checked final
  answer.

EXACT-match only (normalized query string), on purpose:
- a graph cache serves the answer VERBATIM with no grounding/rerank safety net,
  so a semantic (paraphrase) match here is riskier than in rag_node's evidence
  cache (which re-synthesizes the answer). Exact match = zero false positives.
- the SEMANTIC layer already lives where it is safe: inside rag_node.

Only PUBLIC answers are cached (PUBLIC_RAG / PUBLIC_TOOL). Patient-specific
routes (FHIR / hybrid), human handoff, emergencies, errors and any safety-
flagged turn are never cached (PII + correctness).
"""

import copy
import logging
import threading
import time
import unicodedata
from collections import OrderedDict

from core.enums import Route
from core.state import ChatState

_log = logging.getLogger(__name__)

# Only these routes yield public, non-personalized answers safe to reuse.
_CACHEABLE_ROUTES = {Route.PUBLIC_RAG.value, Route.PUBLIC_TOOL.value}
# Fields that make up the response we replay on a hit.
_RESPONSE_FIELDS = ("answer", "citations", "confidence", "route", "intent", "redirection")

_TTL_SECONDS = 86400.0  # 24h — bounds staleness (prices/schedules change)
_MAX_ENTRIES = 512


def _key(state: ChatState) -> str:
    text = state.get("normalized_message") or state.get("message") or ""
    return " ".join(unicodedata.normalize("NFC", text).lower().split())


class ResponseCache:
    """In-process exact-match LRU+TTL cache of normalized query -> response."""

    def __init__(self, ttl: float = _TTL_SECONDS, max_entries: int = _MAX_ENTRIES):
        self._ttl = ttl
        self._max = max_entries
        self._store: "OrderedDict[str, tuple[dict, float]]" = OrderedDict()
        self._lock = threading.Lock()
        self.hits = 0

    def get(self, key: str) -> dict | None:
        if not key:
            return None
        with self._lock:
            item = self._store.get(key)
            if item is None:
                return None
            payload, created = item
            if time.time() - created > self._ttl:
                del self._store[key]
                return None
            self._store.move_to_end(key)
            self.hits += 1
            return copy.deepcopy(payload)  # isolate cached entry from the caller

    def put(self, key: str, payload: dict) -> None:
        if not key or not payload.get("answer"):
            return
        with self._lock:
            self._store[key] = (copy.deepcopy(payload), time.time())
            self._store.move_to_end(key)
            while len(self._store) > self._max:
                self._store.popitem(last=False)

    def clear(self) -> None:
        with self._lock:
            self._store.clear()

    def size(self) -> int:
        with self._lock:
            return len(self._store)


_CACHE = ResponseCache()


def get_response_cache() -> ResponseCache:
    return _CACHE


def reset_response_cache() -> None:
    _CACHE.clear()


def response_cache_lookup_node(state: ChatState) -> dict:
    """After emergency, before intent_router. On an exact hit, replay the cached
    response and mark the turn so routing skips straight to output_safety."""
    hit = _CACHE.get(_key(state))
    if hit is None:
        return {}  # miss → run the normal pipeline
    metadata = dict(state.get("metadata") or {})
    metadata["response_cache"] = "hit"
    _log.info("response cache HIT — skipped router/retrieval/answer")
    return {**hit, "metadata": metadata}


def route_after_response_cache(state: ChatState) -> str:
    metadata = state.get("metadata") or {}
    return "hit" if metadata.get("response_cache") == "hit" else "miss"


def response_cache_store_node(state: ChatState) -> dict:
    """After output_safety. Cache only public, clean, non-personalized answers."""
    metadata = state.get("metadata") or {}
    if metadata.get("response_cache") == "hit":
        return {}  # already came from cache — nothing to store
    if state.get("route") not in _CACHEABLE_ROUTES:
        return {}  # FHIR/hybrid/handoff/emergency/direct → never cached (PII)
    if state.get("needs_handoff") or state.get("safety_flags") or state.get("error"):
        return {}
    payload = {k: state.get(k) for k in _RESPONSE_FIELDS if state.get(k) is not None}
    _CACHE.put(_key(state), payload)
    return {}
