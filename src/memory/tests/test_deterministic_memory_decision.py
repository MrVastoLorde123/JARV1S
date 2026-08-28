import unittest

from src.memory.memory_decision_models import (
    CREATE,
    CONFIRM,
    UPDATE,
    CONTRADICT,
    IGNORE,
    MemoryDecisionContext,
)

from src.memory.memory_models import (
    CandidateMemory,
)

from src.memory.memory_retrieval import (
    MemoryResult,
)

from src.memory.providers.deterministic_memory_decision import (
    DeterministicMemoryDecisionProvider,
)


class DeterministicMemoryDecisionTests(
    unittest.TestCase
):

    def setUp(
        self,
    ):

        self.provider = (
            DeterministicMemoryDecisionProvider()
        )

        self.candidate = CandidateMemory(
            content=(
                "User is learning PCVUE v17."
            ),
            category="SKILL",
            memory_key="pcvue_v17_skill",
            subject="PCVUE v17",
            evidence_text=(
                "I'm learning PCVUE v17."
            ),
        )

    def _memory(
        self,
        content,
    ):

        return MemoryResult(
            memory_id=1,
            memory_key="pcvue_skill",
            content=content,
            category="SKILL",
            confidence=0.95,
            importance=0.90,
            status="ACTIVE",
        )

    def test_provider_name(
        self,
    ):

        self.assertEqual(
            self.provider.provider_name(),
            "deterministic",
        )

    def test_no_existing_memory_creates(
        self,
    ):

        context = MemoryDecisionContext(
            candidate=self.candidate,
            existing_memory=None,
        )

        decision = self.provider.decide(
            context
        )

        self.assertEqual(
            decision.action,
            CREATE,
        )

    def test_exact_same_memory_confirms(
        self,
    ):

        existing = self._memory(
            "User is learning PCVUE v17."
        )

        context = MemoryDecisionContext(
            candidate=self.candidate,
            existing_memory=existing,
        )

        decision = self.provider.decide(
            context
        )

        self.assertEqual(
            decision.action,
            CONFIRM,
        )

        self.assertEqual(
            decision.memory_id,
            1,
        )

    def test_candidate_with_more_specific_detail_updates(
        self,
    ):

        existing = self._memory(
            "User is learning PCVUE."
        )

        candidate = CandidateMemory(
            content=(
                "User is learning PCVUE v17."
            ),
            category="SKILL",
            memory_key="pcvue_v17_skill",
            subject="PCVUE v17",
            evidence_text=(
                "I'm learning PCVUE v17."
            ),
        )

        context = MemoryDecisionContext(
            candidate=candidate,
            existing_memory=existing,
        )

        decision = self.provider.decide(
            context
        )

        self.assertEqual(
            decision.action,
            UPDATE,
        )

    def test_explicit_negation_contradicts(
        self,
    ):

        existing = self._memory(
            "User works at QSC."
        )

        candidate = CandidateMemory(
            content=(
                "User no longer works at QSC."
            ),
            category="FACT",
            memory_key="qsc_work",
            subject="works at QSC",
            evidence_text=(
                "I no longer work at QSC."
            ),
        )

        context = MemoryDecisionContext(
            candidate=candidate,
            existing_memory=existing,
        )

        decision = self.provider.decide(
            context
        )

        self.assertEqual(
            decision.action,
            CONTRADICT,
        )

    def test_unrelated_existing_memory_is_ignored(
        self,
    ):

        existing = self._memory(
            "User is learning Java."
        )

        context = MemoryDecisionContext(
            candidate=self.candidate,
            existing_memory=existing,
        )

        decision = self.provider.decide(
            context
        )

        self.assertEqual(
            decision.action,
            IGNORE,
        )

    def test_empty_candidate_is_ignored(
        self,
    ):

        candidate = CandidateMemory(
            content="",
            category="SKILL",
            memory_key="empty",
            subject="something",
            evidence_text="",
        )

        context = MemoryDecisionContext(
            candidate=candidate,
        )

        decision = self.provider.decide(
            context
        )

        self.assertEqual(
            decision.action,
            IGNORE,
        )

    def test_low_similarity_does_not_mutate(
        self,
    ):

        existing = self._memory(
            "User is learning Java."
        )

        candidate = CandidateMemory(
            content=(
                "User is building a house."
            ),
            category="PROJECT",
            memory_key="house_project",
            subject="a house",
            evidence_text=(
                "I'm building a house."
            ),
        )

        context = MemoryDecisionContext(
            candidate=candidate,
            existing_memory=existing,
        )

        decision = self.provider.decide(
            context
        )

        self.assertEqual(
            decision.action,
            IGNORE,
        )

    def test_decision_contains_reason(
        self,
    ):

        context = MemoryDecisionContext(
            candidate=self.candidate,
        )

        decision = self.provider.decide(
            context
        )

        self.assertTrue(
            decision.reason
        )

    def test_decision_confidence_is_bounded(
        self,
    ):

        context = MemoryDecisionContext(
            candidate=self.candidate,
        )

        decision = self.provider.decide(
            context
        )

        self.assertGreaterEqual(
            decision.confidence,
            0.0,
        )

        self.assertLessEqual(
            decision.confidence,
            1.0,
        )

    def test_candidate_is_update_when_existing_claim_is_fully_contained(
            self,
    ):
        existing = self._memory(
            "User is learning PCVUE."
        )

        candidate = CandidateMemory(
            content=(
                "User is learning PCVUE v17."
            ),
            category="SKILL",
            memory_key="pcvue_v17_skill",
            subject="PCVUE v17",
            evidence_text=(
                "I'm learning PCVUE v17."
            ),
        )

        context = MemoryDecisionContext(
            candidate=candidate,
            existing_memory=existing,
        )

        decision = self.provider.decide(
            context
        )

        self.assertEqual(
            decision.action,
            UPDATE,
        )

    def test_similar_but_different_claim_is_not_updated(
            self,
    ):
        existing = self._memory(
            "User is learning PCVUE."
        )

        candidate = CandidateMemory(
            content=(
                "User is teaching PCVUE."
            ),
            category="SKILL",
            memory_key="pcvue_teaching",
            subject="teaching PCVUE",
            evidence_text=(
                "I'm teaching PCVUE."
            ),
        )

        context = MemoryDecisionContext(
            candidate=candidate,
            existing_memory=existing,
        )

        decision = self.provider.decide(
            context
        )

        self.assertEqual(
            decision.action,
            IGNORE,
        )


if __name__ == "__main__":
    unittest.main(
        verbosity=2,
    )