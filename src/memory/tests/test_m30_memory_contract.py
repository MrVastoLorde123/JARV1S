from __future__ import annotations

import unittest

from src.memory.m30_memory_contract import (
    MemoryEvidenceRef,
    MemoryQuery,
    MemoryRecord,
    MemoryRetrieval,
    MemorySourceKind,
    MemoryStatus,
)


class M30MemoryContractTests(unittest.TestCase):
    def test_memory_requires_bounded_identity_and_confidence(self) -> None:
        record = MemoryRecord(
            memory_id="memory-1",
            memory_key="user.goal.focus",
            content="Build JARVIS consistently.",
            category="GOAL",
            confidence=0.9,
            importance=0.8,
            source_kind=MemorySourceKind.CONVERSATION,
            source_id="conversation-1",
        )
        self.assertEqual(record.status, MemoryStatus.ACTIVE)

        with self.assertRaises(ValueError):
            MemoryRecord(
                memory_id="memory-1",
                memory_key="user.goal.focus",
                content="Build JARVIS consistently.",
                category="GOAL",
                confidence=1.1,
                importance=0.8,
            )

    def test_evidence_is_explicit_and_bounded(self) -> None:
        evidence = MemoryEvidenceRef(
            evidence_id="evidence-1",
            source_kind=MemorySourceKind.CONVERSATION,
            source_id="conversation-1",
            summary="User explicitly stated the goal.",
            confidence=1.0,
        )
        record = MemoryRecord(
            memory_id="memory-1",
            memory_key="user.goal.focus",
            content="Build JARVIS consistently.",
            category="GOAL",
            confidence=0.9,
            importance=0.8,
            evidence=(evidence,),
        )
        self.assertIs(record.evidence[0], evidence)

    def test_retrieval_is_read_only_and_status_filtered(self) -> None:
        query = MemoryQuery(text="JARVIS", status=MemoryStatus.ACTIVE, limit=10)
        record = MemoryRecord(
            memory_id="memory-1",
            memory_key="project.jarvis",
            content="JARVIS is a trusted system under user control.",
            category="PROJECT",
            confidence=0.95,
            importance=1.0,
        )
        retrieval = MemoryRetrieval(
            query=query,
            records=(record,),
            generated_at="2026-09-16T22:00:00+00:00",
        )
        self.assertEqual(retrieval.query.status, MemoryStatus.ACTIVE)
        self.assertEqual(len(retrieval.records), 1)

    def test_memory_does_not_expose_authority(self) -> None:
        record = MemoryRecord(
            memory_id="memory-1",
            memory_key="capability.example",
            content="The environment has a capability.",
            category="ENVIRONMENT",
            confidence=0.8,
            importance=0.5,
        )
        self.assertFalse(hasattr(record, "authorized"))
        self.assertFalse(hasattr(record, "execute"))


if __name__ == "__main__":
    unittest.main()
