from core.contracts import Citation, Evidence


def citations_from_evidence(items: list[Evidence]) -> list[Citation]:
    return [item.citation for item in items if item.citation is not None]
