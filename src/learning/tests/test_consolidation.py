import unittest

from src.learning.adaptation import AdaptationController, AdaptationKind
from src.learning.consolidation import (
    ConsolidatedMemory,
    ConsolidationConflictError,
    ConsolidationState,
    MemoryCandidate,
    MemoryConsolidator,
    MemoryRetriever,
    MemoryStore,
)
from src.learning.evaluation import Evidence, EvaluationState, OutcomeAssessment, OutcomeEvaluator
from src.learning.experience import Experience


class ConsolidationTests(unittest.TestCase):
    def experience(self, **overrides):
        values = {
            "experience_id": "exp-1",
            "source": "execution",
            "outcome": "The task completed successfully.",
            "confidence": 0.8,
        }
        values.update(overrides)
        return Experience(**values)

    def evaluation(self, *, experience=None, state=EvaluationState.SUCCESS):
        experience = experience or self.experience()
        supports_success = state == EvaluationState.SUCCESS
        if state == EvaluationState.FAILURE:
            supports_success = False
        evidence = (Evidence("e1", "explicit outcome signal", supports_success),)
        result = OutcomeEvaluator().evaluate(
            experience,
            OutcomeAssessment(experience.outcome, evidence),
        )
        self.assertEqual(result.state, state)
        return result

    def candidate(self, **overrides):
        experience = self.experience()
        evaluation = self.evaluation(experience=experience)
        values = {
            "experience": experience,
            "evaluation": evaluation,
            "content": "Use the reliable deployment checklist for production changes.",
        }
        values.update(overrides)
        return MemoryConsolidator().propose(**values)

    def test_consolidation_requires_directional_evaluation(self):
        experience = self.experience()
        inconclusive = OutcomeEvaluator().evaluate(
            experience,
            OutcomeAssessment(experience.outcome, (Evidence("e1", "ambiguous", None),)),
        )
        with self.assertRaises(ValueError):
            MemoryConsolidator().propose(experience, inconclusive)

    def test_candidate_preserves_experience_and_evaluation_provenance(self):
        candidate = self.candidate()
        self.assertEqual(candidate.experience_id, "exp-1")
        self.assertEqual(candidate.evaluation_id, "exp-1:evaluation")
        self.assertEqual(candidate.provenance["source"], "m10.4")
        self.assertEqual(candidate.provenance["evaluation_state"], "SUCCESS")

    def test_accepted_adaptation_can_be_used_as_consolidation_evidence(self):
        experience = self.experience()
        evaluation = self.evaluation(experience=experience)
        adaptation = AdaptationController().accept(
            AdaptationController().propose(
                proposal_id="adapt-1",
                kind=AdaptationKind.PREFERENCE,
                target="response.format",
                current_value="verbose",
                proposed_value="concise",
                evaluations=(evaluation,),
                rationale="successful concise responses",
            ),
            "user-approval-1",
        )
        candidate = MemoryConsolidator().propose(
            experience,
            evaluation,
            adaptation=adaptation,
        )
        self.assertEqual(
            candidate.source_kind,
            "EVALUATED_EXPERIENCE_AND_ACCEPTED_ADAPTATION",
        )
        self.assertEqual(candidate.provenance["adaptation_record_id"], adaptation.record_id)

    def test_rejected_adaptation_cannot_be_consolidated(self):
        experience = self.experience()
        evaluation = self.evaluation(experience=experience)
        controller = AdaptationController()
        proposal = controller.propose(
            proposal_id="adapt-1",
            kind=AdaptationKind.PREFERENCE,
            target="response.format",
            current_value="verbose",
            proposed_value="concise",
            evaluations=(evaluation,),
            rationale="candidate",
        )
        rejected = controller.reject(proposal, "user-rejection-1")
        with self.assertRaises(ValueError):
            MemoryConsolidator().propose(experience, evaluation, adaptation=rejected)

    def test_acceptance_requires_explicit_reference(self):
        with self.assertRaises(ValueError):
            MemoryConsolidator().accept(self.candidate(), "")

    def test_rejected_memory_preserves_rejection_reference(self):
        memory = MemoryConsolidator().reject(self.candidate(), "review-1")
        self.assertEqual(memory.state, ConsolidationState.REJECTED)
        self.assertEqual(memory.rejection_reference, "review-1")

    def test_accepted_memory_is_reversible(self):
        consolidator = MemoryConsolidator()
        memory = consolidator.accept(self.candidate(), "user-approval-1")
        reversed_memory = consolidator.reverse(memory, "user-reversal-1")
        self.assertEqual(reversed_memory.state, ConsolidationState.REVERSED)
        self.assertEqual(reversed_memory.candidate.content, memory.candidate.content)
        self.assertEqual(reversed_memory.acceptance_reference, "user-approval-1")

    def test_store_is_immutable_and_conflict_aware(self):
        memory = MemoryConsolidator().accept(self.candidate(), "user-approval-1")
        store = MemoryStore()
        updated = store.append(memory)
        self.assertEqual(store.list(), ())
        self.assertEqual(updated.list(), (memory,))
        with self.assertRaises(ConsolidationConflictError):
            updated.append(memory)

    def test_retrieval_uses_only_accepted_memories(self):
        consolidator = MemoryConsolidator()
        accepted = consolidator.accept(self.candidate(), "approval-1")
        rejected = consolidator.reject(
            self.candidate(
                content="Never use the deprecated deployment path.",
            ),
            "rejection-1",
        )
        store = MemoryStore((accepted, rejected))
        results = MemoryRetriever().retrieve(store, "deployment checklist")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].memory_id, accepted.memory_id)

    def test_retrieval_ranking_is_deterministic_and_confidence_aware(self):
        first_experience = self.experience(experience_id="exp-a", confidence=1.0)
        second_experience = self.experience(experience_id="exp-b", confidence=0.2)
        consolidator = MemoryConsolidator()
        first = consolidator.accept(
            consolidator.propose(first_experience, self.evaluation(experience=first_experience), content="Python deployment checklist"),
            "approval-a",
        )
        second = consolidator.accept(
            consolidator.propose(second_experience, self.evaluation(experience=second_experience), content="Python deployment checklist"),
            "approval-b",
        )
        results = MemoryRetriever().retrieve(MemoryStore((second, first)), "python deployment")
        self.assertEqual([item.memory_id for item in results], [first.memory_id, second.memory_id])
        self.assertGreater(results[0].score, results[1].score)

    def test_retrieval_serialization_never_grants_authority(self):
        memory = MemoryConsolidator().accept(self.candidate(), "approval-1")
        results = MemoryRetriever().retrieve(MemoryStore((memory,)), "deployment checklist")
        payload = results[0].to_dict()
        self.assertFalse(payload["truth_guaranteed"])
        self.assertFalse(payload["authority_granted"])
        self.assertFalse(payload["authorization_granted"])
        self.assertFalse(payload["execution_requested"])

    def test_candidate_and_memory_are_immutable(self):
        candidate = self.candidate()
        with self.assertRaises(Exception):
            candidate.content = "changed"
        memory = MemoryConsolidator().accept(candidate, "approval-1")
        with self.assertRaises(Exception):
            memory.state = ConsolidationState.REVERSED


if __name__ == "__main__":
    unittest.main()
