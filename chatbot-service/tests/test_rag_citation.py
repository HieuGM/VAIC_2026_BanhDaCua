"""hit_to_evidence mapping: source_type always RAG, citation fields, confidence clamp."""

import unittest
from types import SimpleNamespace

from core.enums import SourceType
from rag.retriever import _hit_to_evidence


def _hit(score, **payload):
    base = {
        "title": "Giờ làm việc",
        "content": "Bệnh viện làm việc 7h-16h30.",
        "source": "Huong_dan_dat_lich.txt",
        "source_type": "document",
        "chunk_id": "abc123",
        "snippet": "7h-16h30",
        "url": "https://benhvientimhanoi.vn",
        "updated_at": "2026-07-17",
    }
    base.update(payload)
    return SimpleNamespace(score=score, payload=base)


class HitToEvidenceTest(unittest.TestCase):
    def test_source_type_is_always_rag(self):
        # Even though the chunk payload is "document", Evidence.source_type is RAG.
        ev = _hit_to_evidence(_hit(0.9, source_type="price_table"), 0.9)
        self.assertEqual(ev.source_type, SourceType.RAG)

    def test_citation_maps_payload_fields(self):
        ev = _hit_to_evidence(_hit(0.8), 0.8)
        self.assertEqual(ev.citation.chunk_id, "abc123")
        self.assertEqual(ev.citation.snippet, "7h-16h30")
        self.assertEqual(ev.citation.source, "Huong_dan_dat_lich.txt")
        self.assertEqual(ev.citation.url, "https://benhvientimhanoi.vn")
        self.assertEqual(ev.title, "Giờ làm việc")
        self.assertIn("7h-16h30", ev.content)

    def test_confidence_clamped_low(self):
        # Qdrant cosine can be negative; must not raise pydantic ValidationError.
        ev = _hit_to_evidence(_hit(-0.4), -0.4)
        self.assertEqual(ev.confidence, 0.0)

    def test_confidence_clamped_high(self):
        ev = _hit_to_evidence(_hit(1.5), 1.5)
        self.assertEqual(ev.confidence, 1.0)

    def test_confidence_passthrough_in_range(self):
        ev = _hit_to_evidence(_hit(0.73), 0.73)
        self.assertAlmostEqual(ev.confidence, 0.73)

    def test_optional_fields_missing_ok(self):
        hit = _hit(0.5)
        del hit.payload["url"]
        del hit.payload["updated_at"]
        ev = _hit_to_evidence(hit, 0.5)
        self.assertIsNone(ev.citation.url)


if __name__ == "__main__":
    unittest.main()
