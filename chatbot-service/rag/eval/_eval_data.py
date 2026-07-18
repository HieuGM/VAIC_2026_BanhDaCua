"""Shared loader for the labeled eval sets (document QA + price/schedule extra)."""

import json
from pathlib import Path

DATA = Path(__file__).parent / "data"


def load_eval_qa() -> list[dict]:
    """Merged QA with a `group` on every item (document | price | schedule)."""
    items = []
    for line in (DATA / "qa_eval.jsonl").read_text(encoding="utf-8").splitlines():
        if line.strip():
            items.append({**json.loads(line), "group": "document"})
    extra = DATA / "qa_extra.jsonl"
    if extra.exists():
        for line in extra.read_text(encoding="utf-8").splitlines():
            if line.strip():
                items.append(json.loads(line))  # already carries `group`
    return items


def by_group(items: list[dict]) -> dict[str, list[dict]]:
    groups: dict[str, list[dict]] = {}
    for it in items:
        groups.setdefault(it["group"], []).append(it)
    return groups
