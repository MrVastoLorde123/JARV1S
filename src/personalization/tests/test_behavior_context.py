import unittest

from src.learning.adaptation import AdaptationController, AdaptationKind, AdaptationState
from src.learning.evaluation import Evaluation
from src.personalization.behavior_context import BehaviorAdaptationResolver


class BehaviorAdaptationResolverTests(unittest.TestCase):
    def record(self, kind=AdaptationKind.BEHAVIOR, state=AdaptationState.ACCEPTED):
        evaluation = Evaluation(
            evaluation_id="eval-1",
            memory_id=None,
            outcome="useful",
            score=0.9,
            evidence_ids=(),
            confidence=0.9,
        )
        controller = AdaptationController()
        proposal = controller.propose(
            proposal_id="proposal-1",
            kind=kind,
            target="response_style",
            current_value="standard",
            proposed_value="concise",
            evaluations=(evaluation,),
            rationale="Observed repeated preference for concise replies.",
            confidence=0.85,
            explicit_user_preference=True,
        )
        if state == AdaptationState.ACCEPTED:
            return controller.accept(proposal, "accept-1")
        if state == AdaptationState.REJECTED:
            return controller.reject(proposal, "reject-1")
        return controller.accept(proposal, "accept-1")

    def test_resolves_only_accepted_behavior_adaptations(self):
        accepted = self.record()
        rejected = self.record(state=AdaptationState.REJECTED)
        profile = BehaviorAdaptationResolver().resolve((accepted, rejected))
        self.assertEqual(len(profile.behaviors), 1)
        self.assertEqual(profile.behaviors[0].value, "concise")

    def test_ignores_preference_adaptations(self):
        preference = self.record(kind=AdaptationKind.PREFERENCE)
        profile = BehaviorAdaptationResolver().resolve((preference,))
        self.assertEqual(profile.behaviors, ())

    def test_preserves_adaptation_and_evaluation_provenance(self):
        record = self.record()
        signal = BehaviorAdaptationResolver().resolve((record,)).behaviors[0]
        self.assertEqual(
            signal.source_ids,
            ("adaptation:proposal-1:record", "evaluation:eval-1"),
        )
        self.assertEqual(signal.metadata["acceptance_reference"], "accept-1")
        self.assertTrue(signal.metadata["reversible"])

    def test_projection_is_non_authoritative(self):
        profile = BehaviorAdaptationResolver().resolve((self.record(),))
        data = profile.to_dict()
        self.assertFalse(data["authority_granted"])
        self.assertFalse(data["authorization_granted"])
        self.assertFalse(data["policy_mutation"])
        self.assertFalse(data["execution_requested"])

    def test_invalid_input_is_rejected(self):
        with self.assertRaises(TypeError):
            BehaviorAdaptationResolver().resolve((object(),))


if __name__ == "__main__":
    unittest.main(verbosity=2)
