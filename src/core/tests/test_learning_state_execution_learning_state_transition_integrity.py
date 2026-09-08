import unittest
from dataclasses import FrozenInstanceError
from types import MappingProxyType

from src.core.learning_state_execution_learning_state_transition import (
    LearningStateExecutionLearningStateTransition,
    LearningStateExecutionLearningStateTransitionStatus,
    _transition_fingerprint,
)
from src.core.learning_state_execution_learning_state_transition_integrity import (
    LearningStateExecutionLearningStateTransitionIntegrityService,
    LearningStateExecutionLearningStateTransitionIntegrityStatus,
    _recompute_transition_fingerprint,
    _transition_integrity_fingerprint,
)


class M23_166LearningStateTransitionIntegrityTests(unittest.TestCase):
    def _make_transition(self):
        state_before = {"threshold": {"value": 0.8, "items": [1, {"x": True}]}}
        state_after = {"threshold": {"value": 0.95, "items": [1, {"x": True}]}}
        proposed_change = {"threshold": 0.95}
        transition_id = "transition-165"
        transition_fingerprint = _transition_fingerprint(
            transition_id=transition_id,
            state_key="demo.state",
            state_before=state_before,
            state_after=state_after,
            evidence_id="evidence-164",
            integrity_id="application-integrity-163",
            proposed_change=proposed_change,
        )
        return LearningStateExecutionLearningStateTransition(
            transition_id=transition_id, evidence_id="evidence-164", integrity_id="application-integrity-163",
            application_id="application-162", decision_id="decision-161", proposal_id="proposal-160", eligibility_id="eligibility-159",
            source_integrity_id="integrity-158", source_application_fingerprint="b" * 64, computed_application_fingerprint="c" * 64, signal_id="signal-157", evaluation_id="evaluation-156", feedback_id="feedback-155",
            outcome_id="outcome-154", attempt_id="attempt-153", admission_id="admission-152", eligibility_source_id="integrity-151",
            handling_id="handling-150", consumption_id="consumption-149", receipt_id="receipt-148", handoff_id="handoff-147",
            inherited_integrity_id="integrity-146", validation_id="validation-145", semantic_use_id="semantic-use-144",
            source_request_id="request-143", source_request_lineage_id="request-lineage-143", source_validation_id="source-validation-142",
            source_validation_lineage_id="source-validation-lineage-142", interpretation_id="interpretation-141", read_id="read-140",
            consumption_request_id="consumption-139", requester_id="requester-A", consumer_id="consumer-A",
            handoff_target_id="handoff-target-A", recipient_id="recipient-A", handling_target_id="handler-A", execution_target_id="executor-A",
            signal_kind="POSITIVE", signal_purpose="feed-learning", signal_context={"features": ["stable", {"score": 0.9}]},
            signal_status="RECORDED", source_signal_fingerprint="a" * 64, computed_signal_fingerprint="a" * 64,
            learner_id="learner-A", eligibility_purpose="future-learning", proposer_id="proposer-A", proposal_purpose="candidate-learning",
            proposed_change=proposed_change, proposal_rationale={"why": {"score": 0.8}}, decision_maker_id="decision-maker-A",
            decision_purpose="review-candidate", decision_rationale={"basis": "bounded-review"}, applier_id="applier-A",
            application_purpose="apply-approved-learning", application_rationale={"basis": ["approved"]}, application_evidence={"checks": [{"name": "decision"}]},
            application_status="APPLIED", evidence_collector_id="collector-A", evidence_purpose="record-state-effect",
            evidence_rationale={"basis": "integrity"}, evidence_payload={"candidate_state": state_after}, state_key="demo.state",
            state_before=state_before, state_after=state_after, transition_actor_id="transition-actor-A",
            transition_purpose="apply-recorded-learning-state-change", transition_rationale={"basis": ["recorded-evidence"]},
            transition_fingerprint=transition_fingerprint, status=LearningStateExecutionLearningStateTransitionStatus.FORMULATED,
            reasons=("learning-state evidence is RECORDED",),
            lineage={"transition_id": transition_id, "evidence_id": "evidence-164", "integrity_id": "application-integrity-163", "application_id": "application-162", "source_integrity_id": "integrity-158"},
        )

    def _verify(self, transition=None, **kwargs):
        return LearningStateExecutionLearningStateTransitionIntegrityService().verify(
            transition or self._make_transition(), integrity_id=kwargs.pop("integrity_id", "transition-integrity-166"), **kwargs
        )

    def test_formulated_transition_produces_valid_integrity(self):
        result = self._verify()
        self.assertIs(result.status, LearningStateExecutionLearningStateTransitionIntegrityStatus.VALID)
        self.assertTrue(result.is_valid)
        self.assertTrue(result.validates_transition)

    def test_exact_transition_type_is_required(self):
        with self.assertRaises(TypeError):
            self._verify(object())

    def test_integrity_id_is_required(self):
        with self.assertRaises(ValueError):
            self._verify(integrity_id=" ")

    def test_integrity_identity_must_be_distinct(self):
        with self.assertRaises(ValueError):
            self._verify(integrity_id="transition-165")
        with self.assertRaises(ValueError):
            self._verify(integrity_id="application-integrity-163")

    def test_transition_lineage_is_checked(self):
        transition = self._make_transition()
        object.__setattr__(transition, "lineage", MappingProxyType({"transition_id": "wrong-transition", "evidence_id": transition.evidence_id, "integrity_id": transition.integrity_id, "application_id": transition.application_id, "source_integrity_id": transition.source_integrity_id}))
        result = self._verify(transition)
        self.assertIs(result.status, LearningStateExecutionLearningStateTransitionIntegrityStatus.INVALID)
        self.assertIn("learning-state transition lineage is not valid", result.reasons)

    def test_transition_fingerprint_is_recomputed_and_preserved(self):
        transition = self._make_transition()
        result = self._verify(transition)
        expected = _recompute_transition_fingerprint(transition)
        self.assertEqual(result.computed_transition_fingerprint, expected)
        self.assertEqual(result.transition_fingerprint, expected)
        self.assertEqual(len(expected), 64)

    def test_transition_fingerprint_mismatch_is_rejected_without_repair(self):
        transition = self._make_transition()
        object.__setattr__(transition, "transition_fingerprint", "b" * 64)
        result = self._verify(transition)
        self.assertIs(result.status, LearningStateExecutionLearningStateTransitionIntegrityStatus.INVALID)
        self.assertIn("learning-state transition fingerprint mismatch", result.reasons)
        self.assertEqual(result.transition_fingerprint, "b" * 64)

    def test_integrity_fingerprint_lineage_mismatch_is_rejected(self):
        transition = self._make_transition()
        lineage = dict(transition.lineage)
        lineage["transition_integrity_fingerprint"] = "c" * 64
        object.__setattr__(transition, "lineage", MappingProxyType(lineage))
        result = self._verify(transition)
        self.assertIs(result.status, LearningStateExecutionLearningStateTransitionIntegrityStatus.INVALID)
        self.assertIn("learning-state transition integrity fingerprint mismatch", result.reasons)

    def test_non_formulated_transition_fails_closed(self):
        transition = self._make_transition()
        object.__setattr__(transition, "status", LearningStateExecutionLearningStateTransitionStatus.REJECTED)
        result = self._verify(transition)
        self.assertIs(result.status, LearningStateExecutionLearningStateTransitionIntegrityStatus.INVALID)
        self.assertIn("learning-state transition is not formulated", result.reasons)

    def test_transition_provenance_is_preserved(self):
        transition = self._make_transition()
        result = self._verify(transition)
        for field in ("transition_id", "evidence_id", "source_integrity_id", "application_id", "decision_id", "proposal_id", "eligibility_id", "state_key", "state_before", "state_after", "proposed_change", "transition_actor_id", "transition_purpose", "transition_rationale"):
            self.assertEqual(getattr(result, field), getattr(transition, field))

    def test_integrity_lineage_is_explicitly_anchored(self):
        result = self._verify()
        self.assertEqual(result.lineage["integrity_id"], "transition-integrity-166")
        self.assertEqual(result.lineage["transition_id"], "transition-165")
        self.assertEqual(result.lineage["evidence_id"], "evidence-164")
        self.assertEqual(result.lineage["application_id"], "application-162")
        self.assertEqual(result.lineage["source_integrity_id"], "integrity-158")
        self.assertEqual(result.lineage["transition_integrity_fingerprint"], _transition_integrity_fingerprint(self._make_transition()))

    def test_nested_transition_values_and_lineage_are_recursively_frozen(self):
        result = self._verify()
        self.assertIsInstance(result.state_before, MappingProxyType)
        self.assertIsInstance(result.state_before["threshold"], MappingProxyType)
        self.assertIsInstance(result.state_before["threshold"]["items"], tuple)
        self.assertIsInstance(result.lineage, MappingProxyType)

    def test_integrity_artifact_is_immutable(self):
        result = self._verify()
        with self.assertRaises((AttributeError, FrozenInstanceError)):
            result.status = LearningStateExecutionLearningStateTransitionIntegrityStatus.INVALID
        with self.assertRaises(TypeError):
            result.lineage["x"] = "y"

    def test_integrity_is_deterministic_for_same_transition(self):
        first = self._verify()
        second = self._verify()
        self.assertEqual(first, second)

    def test_integrity_has_no_application_learning_or_execution_power(self):
        result = self._verify()
        for name in ("is_learning", "applies_learning", "authorizes_learning", "authorizes_execution", "authorizes_retry", "invokes_learner", "invokes_executor", "schedules_work", "plans_work", "updates_model", "mutates_memory", "mutates_policy", "transitions_state", "mutates_state", "persists_state", "repairs_transition"):
            self.assertFalse(getattr(result, name))

    def test_source_transition_is_not_mutated(self):
        transition = self._make_transition()
        before = transition.status
        self._verify(transition)
        self.assertIs(transition.status, before)
        self.assertEqual(transition.transition_id, "transition-165")


if __name__ == "__main__":
    unittest.main()
