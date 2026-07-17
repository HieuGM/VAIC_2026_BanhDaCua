import unittest

from core.contracts import Citation, Evidence
from core.enums import SourceType


class ContractSmokeTest(unittest.TestCase):
    def test_evidence_contract_serializes(self) -> None:
        item = Evidence(
            source_type=SourceType.RAG,
            title="Test",
            content="Evidence",
            citation=Citation(source="kb", title="Doc", chunk_id="c1"),
        )
        payload = item.model_dump(mode="json")
        self.assertEqual(payload["source_type"], "rag")
        self.assertEqual(payload["citation"]["chunk_id"], "c1")


if __name__ == "__main__":
    unittest.main()
