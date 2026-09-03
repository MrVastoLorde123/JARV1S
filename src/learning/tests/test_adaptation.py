import unittest

from src.learning.adaptation import (
    AdaptationConflictError,
    AdaptationController,
    AdaptationKind,
    AdaptationState,
    AdaptationStore,
)
from src.learning.evaluation import Evidence, EvaluationState, OutcomeAssessment, OutcomeEvaluator
from src.learning.experience import Experience


class AdaptationTests(unittest.TestCase):
    def evaluation(self, state=EvaluationState.SUCCESS):
        experience = Experience("exp-1", "execution", outcome="done")
        evidence = (Evidence("e1", "completion observed", True),)
        result = OutcomeEvaluator().evaluate(experience, OutcomeAssessment("done", evidence))
        self.assertEqual(result.state, state)
        return result

    def proposal(self, **overrides):
        values = {
            "proposal_id": "adapt-1",
            "kind": AdaptationKind.PREFERENCE,
            "target": "response.format",
            "current_value": "verbose",
            "proposed_value": "concise",
            "evaluations": (self.evaluation(),),
            "rationale": "repeated successful concise interactions",
            "confidence": 0.8,
        }
        values.update(overrides)
        return AdaptationController().propose(**values)

    def test_proposal_requires_evaluated_evidence(self):
        with self.assertRaises(ValueError):
            AdaptationController().propose(
                proposal_id="adapt-1",
                kind=AdaptationKind.PREFERENCE,
                target="response.format",
                current_value="verbose",
                proposed_value="concise",
                evaluations=(),
                rationale="none",
            )

    def test_proposal_is_bounded_and_non_authoritative(self):
        payload = self.proposal().to_dict()
        self.assertTrue(payload["reversible"])
        self.assertFalse(payload["authority_granted"])
        self.assertFalse(payload["authorization_granted"])
        self.assertFalse(payload["execution_requested"])
        self.assertFalse(payload["policy_mutation"])

    def test_explicit_user_preference_is_not_silently_mutated(self):
        proposal = self.proposal(explicit_user_preference=True)
        self.assertTrue(proposal.explicit_user_preference)
        record = AdaptationController().accept(proposal, "user-approval-1")
        self.assertEqual(record.state, AdaptationState.ACCEPTED)
        self.assertEqual(record.acceptance_reference, "user-approval-1")

    def test_acceptance_requires_explicit_reference(self):
        with self.assertRaises(ValueError):
            AdaptationController().accept(self.proposal(), "")

    def test_rejection_is_non_mutating_and_explicit(self):
        record = AdaptationController().reject(self.proposal(), "user-rejection-1")
        self.assertEqual(record.state, AdaptationState.REJECTED)
        self.assertEqual(record.acceptance_reference, "user-rejection-1")

    def test_accepted_adaptation_is_reversible(self):
        controller = AdaptationController()
        record = controller.accept(self.proposal(), "user-approval-1")
        reversed_record = controller.reverse(record, "user-reversal-1")
        self.assertEqual(reversed_record.state, AdaptationState.REVERSED)
        self.assertEqual(reversed_record.reversal_reference, "user-reversal-1")
        self.assertEqual(reversed_record.proposal.current_value, "verbose")

    def test_only_accepted_adaptations_can_be_reversed(self):
        record = AdaptationController().reject(self.proposal(), "user-rejection-1")
        with self.assertRaises(ValueError):
            AdaptationController().reverse(record, "user-reversal-1")

    def test_confidence_is_bounded(self):
        with self.assertRaises(ValueError):
            self.proposal(confidence=1.1)
        with self.assertRaises(ValueError):
            self.proposal(confidence=-0.1)

    def test_store_is_immutable_and_conflict_aware(self):
        record = AdaptationController().accept(self.proposal(), "user-approval-1")
        store = AdaptationStore()
        updated = store.append(record)
        self.assertEqual(len(store.list()), 0)
        self.assertEqual(updated.get(record.record_id), record)
        with self.assertRaises(AdaptationConflictError):
            updated.append(record)

    def test_serialization_never_grants_authority(self):
        record = AdaptationController().accept(self.proposal(), "user-approval-1")
        payload = record.to_dict()
        self.assertFalse(payload["authority_granted"])
        self.assertFalse(payload["authorization_granted"])
        self.assertFalse(payload["execution_requested"])
        self.assertFalse(payload["policy_mutation"])


if __name__ == "__main__":
    unittest.main()
