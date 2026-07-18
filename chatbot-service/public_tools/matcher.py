from __future__ import annotations

from dataclasses import dataclass
from difflib import SequenceMatcher
from typing import Any

from public_tools.param_extractor import normalize_text


@dataclass(frozen=True)
class MatchCandidate:
    item: dict[str, Any]
    score: float
    label: str

    def as_option(self) -> dict[str, Any]:
        return {
            "id": self.item.get("id"),
            "label": self.label,
            "score": round(self.score, 3),
        }


@dataclass(frozen=True)
class MatchResult:
    status: str
    selected: dict[str, Any] | None = None
    options: list[dict[str, Any]] | None = None


def select_best_match(
    query: str | None,
    items: list[dict[str, Any]],
    *,
    fields: list[str],
    label_field: str = "name",
    min_score: float = 0.45,
    select_score: float = 0.78,
    ambiguity_gap: float = 0.08,
    max_options: int = 5,
) -> MatchResult:
    normalized_query = normalize_text(query or "")
    if not normalized_query:
        return MatchResult("needs_clarification", options=[])
    if not items:
        return MatchResult("no_data", options=[])

    candidates = sorted(
        (
            _candidate(normalized_query, item, fields=fields, label_field=label_field)
            for item in items
            if isinstance(item, dict)
        ),
        key=lambda candidate: candidate.score,
        reverse=True,
    )
    if not candidates or candidates[0].score < min_score:
        return MatchResult("no_data", options=[])

    top = candidates[0]
    viable = [candidate for candidate in candidates[:max_options] if candidate.score >= min_score]
    if len(normalized_query.split()) <= 2 and len(viable) > 1:
        return MatchResult("needs_selection", options=[candidate.as_option() for candidate in viable])

    close = [
        candidate
        for candidate in candidates[:max_options]
        if candidate.score >= min_score and top.score - candidate.score <= ambiguity_gap
    ]
    if top.score >= select_score and len(close) == 1:
        return MatchResult("ok", selected=top.item, options=[top.as_option()])
    if top.score >= 0.93:
        return MatchResult("ok", selected=top.item, options=[top.as_option()])
    return MatchResult("needs_selection", options=[candidate.as_option() for candidate in close or candidates[:max_options]])


def _candidate(
    query: str,
    item: dict[str, Any],
    *,
    fields: list[str],
    label_field: str,
) -> MatchCandidate:
    values = [
        str(item.get(field) or "")
        for field in fields
        if item.get(field) not in (None, "")
    ]
    text = normalize_text(" ".join(values))
    score = _score(query, text)
    label = str(item.get(label_field) or item.get("fullName") or item.get("title") or item.get("code") or item.get("id") or "Lua chon")
    return MatchCandidate(item=item, score=score, label=label)


def _score(query: str, candidate: str) -> float:
    if not query or not candidate:
        return 0.0
    query_tokens = set(query.split())
    candidate_tokens = set(candidate.split())
    overlap = len(query_tokens & candidate_tokens) / max(1, len(query_tokens))
    ratio = SequenceMatcher(None, query, candidate).ratio()
    reverse_ratio = SequenceMatcher(None, candidate, query).ratio()
    substring_bonus = 0.12 if query in candidate or candidate in query else 0.0
    return min(1.0, max(ratio, reverse_ratio) * 0.55 + overlap * 0.45 + substring_bonus)


def page_items(payload: Any) -> tuple[list[dict[str, Any]], bool, int | None]:
    if isinstance(payload, dict) and isinstance(payload.get("items"), list):
        items = [item for item in payload["items"] if isinstance(item, dict)]
        total = payload.get("total") if isinstance(payload.get("total"), int) else None
        truncated = bool(total is not None and total > len(items))
        return items, truncated, total
    if isinstance(payload, list):
        return [item for item in payload if isinstance(item, dict)], False, None
    return [], False, None
