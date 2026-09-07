import unittest
from dataclasses import FrozenInstanceError
from types import MappingProxyType

from src.core.learning_state_execution_learning_proposal_application import LearningStateExecutionLearningProposalApplication, LearningStateExecutionLearningProposalApplicationStatus
from src.core.learning_state_execution_learning_proposal_application_integrity import LearningStateExecutionLearningProposalApplicationIntegrityService
from src.core.learning_state_execution_learning_state_evidence import LearningStateExecutionLearningStateEvidenceService, LearningStateExecutionLearningStateEvidenceStatus
from src.core.learning_state_execution_learning_state_transition import LearningStateExecutionLearningStateTransitionService, LearningStateExecutionLearningStateTransitionStatus, _transition_fingerprint


class M23_165LearningStateTransitionTests(unittest.TestCase):
    def _make_evidence(self):
        application = LearningStateExecutionLearningProposalApplication(
            application_id="application-162", decision_id="decision-161", proposal_id="proposal-160", eligibility_id="eligibility-159",
            integrity_id="integrity-158", signal_id="signal-157", evaluation_id="evaluation-156", feedback_id="feedback-155",
            outcome_id="outcome-154", attempt_id="attempt-153", admission_id="admission-152", eligibility_source_id="integrity-151",
            handling_id="handling-150", consumption_id="consumption-149", receipt_id="receipt-148", handoff_id="handoff-147",
            inherited_integrity_id="integrity-146", validation_id="validation-145", semantic_use_id="semantic-use-144", source_request_id="request-143",
            source_request_lineage_id="request-lineage-143", source_validation_id="source-validation-142", source_validation_lineage_id="source-validation-lineage-142",
            interpretation_id="interpretation-141", read_id="read-140", consumption_request_id="consumption-139", requester_id="requester-A", consumer_id="consumer-A",
            handoff_target_id="handoff-target-A", recipient_id="recipient-A", handling_target_id="handler-A", execution_target_id="executor-A",
            signal_kind="POSITIVE", signal_purpose="feed-learning", signal_context={"features": ["stable", {"score": 0.9}]}, signal_status="RECORDED",
            source_signal_fingerprint="a" * 64, computed_signal_fingerprint="a" * 64, learner_id="learner-A", eligibility_purpose="future-learning",
            proposer_id="proposer-A", proposal_purpose="candidate-learning", proposed_change={"threshold": 0.95}, proposal_rationale={"why": {"score": 0.8}},
            decision_maker_id="decision-maker-A", decision_purpose="review-candidate", decision_rationale={"basis": "bounded-review"}, applier_id="applier-A",
            application_purpose="apply-approved-learning", application_rationale={"basis": ["approved", {"scope": "bounded"}]}, application_evidence={"checks": [{"name": "decision"}]},
            status=LearningStateExecutionLearningProposalApplicationStatus.APPLIED, reasons=("learning proposal decision is APPROVED",),
            lineage={"application_id": "application-162", "decision_id": "decision-161"},
        )
        integrity = LearningStateExecutionLearningProposalApplicationIntegrityService().verify(application, integrity_id="application-integrity-163")
        return LearningStateExecutionLearningStateEvidenceService().record(
            integrity, evidence_id="evidence-164", evidence_collector_id="collector-A", evidence_purpose="record-state-effect",
            evidence_rationale={"basis": "integrity"}, evidence_payload={"candidate_state": {"threshold": 0.95}, "observed": [1, 2]},
            lineage={"evidence_id": "evidence-164", "integrity_id": integrity.integrity_id, "application_id": integrity.application_id, "source_integrity_id": integrity.source_integrity_id},
        )

    def _formulate(self, evidence=None, **overrides):
        values = {"transition_id": "transition-165", "state_key": "demo.state", "state_before": {"threshold": 0.8}, "state_after": {"threshold": 0.95}, "transition_actor_id": "transition-actor-A", "transition_purpose": "apply-recorded-learning-state-change", "transition_rationale": {"basis": ["recorded-evidence", {"scope": "bounded"}]}}
        values.update(overrides)
        return LearningStateExecutionLearningStateTransitionService().formulate(evidence or self._make_evidence(), **values)

    def test_recorded_evidence_produces_formulated_transition(self):
        result = self._formulate()
        self.assertIs(result.status, LearningStateExecutionLearningStateTransitionStatus.FORMULATED)
        self.assertTrue(result.is_formulated)
        self.assertTrue(result.represents_transition)

    def test_rejected_evidence_fails_closed(self):
        evidence = self._make_evidence()
        object.__setattr__(evidence, "status", LearningStateExecutionLearningStateEvidenceStatus.REJECTED)
        result = self._formulate(evidence)
        self.assertIs(result.status, LearningStateExecutionLearningStateTransitionStatus.REJECTED)
        self.assertIn("learning-state evidence is not recorded", result.reasons)

    def test_exact_evidence_type_is_required(self):
        with self.assertRaises(TypeError):
            self._formulate(object())

    def test_required_transition_metadata_is_enforced(self):
        for field in ("transition_id", "state_key", "transition_actor_id", "transition_purpose"):
            with self.subTest(field=field):
                with self.assertRaises(ValueError):
                    self._formulate(**{field: " "})
        with self.assertRaises(ValueError):
            self._formulate(transition_rationale=None)

    def test_transition_identity_must_be_distinct(self):
        with self.assertRaises(ValueError):
            self._formulate(transition_id="evidence-164")
        with self.assertRaises(ValueError):
            self._formulate(transition_id="application-integrity-163")

    def test_lineage_tampering_fails_closed(self):
        evidence = self._make_evidence()
        object.__setattr__(evidence, "lineage", MappingProxyType({"evidence_id": "wrong-evidence", "integrity_id": evidence.integrity_id, "application_id": evidence.application_id, "source_integrity_id": evidence.source_integrity_id}))
        result = self._formulate(evidence)
        self.assertIs(result.status, LearningStateExecutionLearningStateTransitionStatus.REJECTED)
        self.assertIn("learning-state evidence lineage is not valid", result.reasons)

    def test_transition_metadata_and_states_are_explicit(self):
        result = self._formulate()
        self.assertEqual(result.transition_id, "transition-165")
        self.assertEqual(result.state_key, "demo.state")
        self.assertEqual(result.transition_actor_id, "transition-actor-A")
        self.assertEqual(result.state_before["threshold"], 0.8)
        self.assertEqual(result.state_after["threshold"], 0.95)

    def test_transition_fingerprint_is_deterministic(self):
        first = self._formulate()
        second = self._formulate()
        self.assertEqual(first.transition_fingerprint, second.transition_fingerprint)
        expected = _transition_fingerprint(transition_id="transition-165", state_key="demo.state", state_before={"threshold": 0.8}, state_after={"threshold": 0.95}, evidence_id="evidence-164", integrity_id="application-integrity-163", proposed_change=first.proposed_change)
        self.assertEqual(first.transition_fingerprint, expected)
        self.assertEqual(len(first.transition_fingerprint), 64)

    def test_transition_fingerprint_changes_with_state(self):
        first = self._formulate(state_after={"threshold": 0.95})
        second = self._formulate(state_after={"threshold": 0.96})
        self.assertNotEqual(first.transition_fingerprint, second.transition_fingerprint)

    def test_provenance_is_preserved(self):
        evidence = self._make_evidence()
        result = self._formulate(evidence)
        for field in ("evidence_id", "integrity_id", "application_id", "decision_id", "proposal_id", "eligibility_id", "source_integrity_id", "signal_id", "evaluation_id", "feedback_id", "outcome_id", "attempt_id", "admission_id", "eligibility_source_id", "handling_id", "consumption_id", "receipt_id", "handoff_id", "inherited_integrity_id", "validation_id", "semantic_use_id", "source_request_id", "source_request_lineage_id", "source_validation_id", "source_validation_lineage_id", "interpretation_id", "read_id", "consumption_request_id", "requester_id", "consumer_id", "handoff_target_id", "recipient_id", "handling_target_id", "execution_target_id", "signal_kind", "signal_purpose", "signal_context", "signal_status", "source_signal_fingerprint", "computed_signal_fingerprint", "learner_id", "eligibility_purpose", "proposer_id", "proposal_purpose", "proposed_change", "proposal_rationale", "decision_maker_id", "decision_purpose", "decision_rationale", "applier_id", "application_purpose", "application_rationale", "application_evidence", "application_status", "evidence_collector_id", "evidence_purpose", "evidence_rationale", "evidence_payload"):
            self.assertEqual(getattr(result, field), getattr(evidence, field))

    def test_nested_states_and_lineage_are_recursively_frozen(self):
        result = self._formulate(state_before={"threshold": {"value": 0.8, "items": [1, {"x": True}]}}, lineage={"transition_id": "transition-165", "chain": {"step": [4, {"nested": True}]}})
        self.assertIsInstance(result.state_before, MappingProxyType)
        self.assertIsInstance(result.state_before["threshold"], MappingProxyType)
        self.assertIsInstance(result.state_before["threshold"]["items"], tuple)
        self.assertIsInstance(result.lineage, MappingProxyType)
        self.assertIsInstance(result.lineage["chain"], MappingProxyType)
        self.assertIsInstance(result.lineage["chain"]["step"], tuple)

    def test_reasons_and_lineage_are_preserved(self):
        result = self._formulate(reasons=("caller-reason",), lineage={"transition_id": "transition-165", "source": {"evidence_id": "evidence-164"}})
        self.assertEqual(result.reasons, ("caller-reason",))
        self.assertEqual(result.lineage["source"]["evidence_id"], "evidence-164")

    def test_source_evidence_is_not_mutated(self):
        evidence = self._make_evidence()
        before = evidence.status
        result = self._formulate(evidence)
        self.assertIs(evidence.status, before)
        self.assertEqual(evidence.evidence_id, "evidence-164")
        self.assertEqual(result.evidence_id, evidence.evidence_id)

    def test_transition_artifact_is_immutable(self):
        result = self._formulate()
        with self.assertRaises((AttributeError, FrozenInstanceError)):
            result.status = LearningStateExecutionLearningStateTransitionStatus.REJECTED
        with self.assertRaises(TypeError):
            result.lineage["x"] = "y"

    def test_transition_does_not_mutate_or_persist_state(self):
        result = self._formulate()
        self.assertFalse(result.transitions_state)
        self.assertFalse(result.mutates_state)
        self.assertFalse(result.persists_state)

    def test_transition_has_no_execution_or_authority_powers(self):
        result = self._formulate()
        for name in ("is_learning", "applies_learning", "authorizes_learning", "authorizes_execution", "authorizes_retry", "invokes_learner", "invokes_executor", "schedules_work", "plans_work", "updates_model", "mutates_memory", "mutates_policy", "establishes_truth", "establishes_correctness", "establishes_certainty", "establishes_usefulness"):
            self.assertFalse(getattr(result, name))

    def test_transition_rationale_is_frozen(self):
        result = self._formulate()
        self.assertIsInstance(result.transition_rationale, MappingProxyType)
        self.assertIsInstance(result.transition_rationale["basis"], tuple)
        self.assertIsInstance(result.evidence_rationale, MappingProxyType)

    def test_before_and_after_are_distinct_explicit_values(self):
        result = self._formulate()
        self.assertNotEqual(result.state_before, result.state_after)

    def test_lineage_is_explicitly_anchored_by_default(self):
        result = self._formulate()
        self.assertEqual(result.lineage["transition_id"], "transition-165")
        self.assertEqual(result.lineage["evidence_id"], "evidence-164")
        self.assertEqual(result.lineage["integrity_id"], "application-integrity-163")
        self.assertEqual(result.lineage["application_id"], "application-162")
        self.assertEqual(result.lineage["source_integrity_id"], "integrity-158")


if __name__ == "__main__":
    unittest.main()
