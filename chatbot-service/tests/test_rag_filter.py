"""Effective-date + approved/deprecated filter, tested against a REAL in-memory
Qdrant (offline, no models, no network) — verifies the actual filter behavior,
not a Python re-implementation of it."""

import unittest

from qdrant_client import QdrantClient, models

from rag.config import RagSettings
from rag.kb_store import DENSE_VECTOR_NAME, SPARSE_VECTOR_NAME, KnowledgeBaseStore
from rag.retriever import build_filter

DIM = 4


def _point(pid, payload):
    return models.PointStruct(
        id=pid,
        vector={
            DENSE_VECTOR_NAME: [0.1, 0.2, 0.3, 0.4],
            SPARSE_VECTOR_NAME: models.SparseVector(indices=[1], values=[1.0]),
        },
        payload=payload,
    )


class EffectiveFilterTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.settings = RagSettings(embed_dim=DIM, collection="test_kb")
        cls.store = KnowledgeBaseStore(cls.settings)
        cls.store._client = QdrantClient(":memory:")  # inject in-memory client
        cls.store.ensure_collection(recreate=True)
        cls.store.upsert([
            # document: no effective dates -> always valid
            _point("11111111-1111-1111-1111-111111111111", {
                "chunk_id": "doc1", "approved": True, "deprecated": False,
                "eff_from_int": None, "eff_to_int": None,
            }),
            # schedule: effective 2026-06-29 .. 2026-07-19
            _point("22222222-2222-2222-2222-222222222222", {
                "chunk_id": "sched1", "approved": True, "deprecated": False,
                "eff_from_int": 20260629, "eff_to_int": 20260719,
            }),
            # deprecated + unapproved: never returned
            _point("33333333-3333-3333-3333-333333333333", {
                "chunk_id": "dep1", "approved": False, "deprecated": True,
                "eff_from_int": None, "eff_to_int": None,
            }),
            # approved but deprecated: isolates the deprecated condition
            _point("44444444-4444-4444-4444-444444444444", {
                "chunk_id": "depd", "approved": True, "deprecated": True,
                "eff_from_int": None, "eff_to_int": None,
            }),
            # in-effect but unapproved: isolates the approved condition
            _point("55555555-5555-5555-5555-555555555555", {
                "chunk_id": "unapp", "approved": False, "deprecated": False,
                "eff_from_int": None, "eff_to_int": None,
            }),
        ])

    def _ids(self, today_int):
        hits = self.store.dense_search(
            [0.1, 0.2, 0.3, 0.4], limit=10, query_filter=build_filter(today_int)
        )
        return {h.payload["chunk_id"] for h in hits}

    def test_schedule_valid_within_effective_window(self):
        ids = self._ids(20260718)  # inside window
        self.assertIn("sched1", ids)
        self.assertIn("doc1", ids)

    def test_schedule_excluded_after_expiry(self):
        ids = self._ids(20260720)  # after eff_to
        self.assertNotIn("sched1", ids)
        self.assertIn("doc1", ids)  # dateless document survives

    def test_schedule_excluded_before_start(self):
        ids = self._ids(20260628)  # before eff_from
        self.assertNotIn("sched1", ids)
        self.assertIn("doc1", ids)

    def test_deprecated_and_unapproved_never_returned(self):
        for today in (20260628, 20260718, 20260720):
            self.assertNotIn("dep1", self._ids(today))

    def test_deprecated_alone_excluded(self):
        self.assertNotIn("depd", self._ids(20260718))  # approved but deprecated

    def test_unapproved_alone_excluded(self):
        self.assertNotIn("unapp", self._ids(20260718))  # in-effect but unapproved

    def test_boundary_dates_inclusive(self):
        self.assertIn("sched1", self._ids(20260719))  # last valid day
        self.assertIn("sched1", self._ids(20260629))  # first valid day


if __name__ == "__main__":
    unittest.main()
