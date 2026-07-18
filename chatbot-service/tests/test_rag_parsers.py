"""Ingest parsers/chunker on the REAL data files (offline, no network).

Verifies mandatory metadata, effective dates, SOP document_code, and that the
meta-section leakage fix keeps eval/spec text out of the corpus."""

import unittest
from pathlib import Path

from rag.ingest.chunker import finalize_chunks
from rag.ingest.loader import load_sources
from rag.ingest.parsers import parse_source

# Resolve data dir from the repo root, independent of the test cwd.
DATA_DIR = Path(__file__).resolve().parents[2] / "data"

MANDATORY_KEYS = {
    "chunk_id", "title", "source", "source_type", "content", "snippet",
    "approved", "deprecated", "effective_from", "effective_to", "updated_at",
}
META_MARKERS = ("Câu trả lời chuẩn", "[QA_", "MẪU GROUNDTRUTH", "KHÔNG NÊN DÙNG",
                "QUY TẮC SỬ DỤNG", "CẤU TRÚC GỢI Ý")


@unittest.skipUnless(DATA_DIR.exists(), f"data dir not found: {DATA_DIR}")
class ParserMetadataTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.by_source = {}
        for src in load_sources(DATA_DIR):
            chunks = finalize_chunks(parse_source(src["text"], src["meta"]), src["meta"])
            cls.by_source[src["meta"]["source"]] = chunks
        cls.all = [c for chunks in cls.by_source.values() for c in chunks]

    def test_every_chunk_has_mandatory_keys(self):
        for c in self.all:
            self.assertTrue(MANDATORY_KEYS.issubset(c), f"missing keys in {c.get('chunk_id')}")

    def test_all_approved_not_deprecated(self):
        self.assertTrue(all(c["approved"] and not c["deprecated"] for c in self.all))

    def test_content_within_cap(self):
        self.assertTrue(all(len(c["content"]) <= 1200 for c in self.all))

    def test_schedule_chunks_carry_effective_window(self):
        sched = [c for c in self.all if c["source_type"] == "schedule"]
        self.assertTrue(sched, "no schedule chunks parsed")
        for c in sched:
            self.assertEqual(c["effective_to"], "2026-07-19")
            self.assertEqual(c["eff_to_int"], 20260719)
            self.assertEqual(c["eff_from_int"], 20260629)

    def test_sop_chunks_have_document_code(self):
        sop = [c for c in self.all if c.get("document_code") == "QT.25.01"]
        self.assertTrue(sop, "SOP document_code QT.25.01 not found on any chunk")

    def test_no_meta_leakage_in_corpus(self):
        for c in self.all:
            blob = (c.get("category") or "") + c["content"]
            for marker in META_MARKERS:
                self.assertNotIn(marker, blob, f"leaked meta marker {marker!r}")

    def test_chunk_ids_unique(self):
        ids = [c["chunk_id"] for c in self.all]
        self.assertEqual(len(ids), len(set(ids)), "duplicate chunk_id")

    def test_no_orphan_heading_chunks(self):
        # Regression: a document chunk must never be just a bare heading/title
        # (e.g. the 31-char "Hướng dẫn liên hệ đặt lịch khám" that ranked #1
        # with no substance). Every document chunk carries real body content.
        for c in self.all:
            if c["source_type"] != "document":
                continue
            self.assertGreaterEqual(
                len(c["content"]), 80, f"orphan-ish chunk: {c['content']!r}"
            )


if __name__ == "__main__":
    unittest.main()
