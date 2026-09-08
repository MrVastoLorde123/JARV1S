import unittest
from dataclasses import FrozenInstanceError
from types import MappingProxyType

from src.core.learning_state_execution_learning_state_transition_integrity import (
    LearningStateExecutionLearningStateTransitionIntegrity,
    LearningStateExecutionLearningStateTransitionIntegrityStatus,
)
from src.core.learning_state_execution_learning_state_validation import (
    LearningStateExecutionLearningStateValidationService,
    LearningStateExecutionLearningStateValidationStatus,
)
from src.core.learning_state_execution_learning_state_validation_integrity import (
    LearningStateExecutionLearningStateValidationIntegrityService,
    LearningStateExecutionLearningStateValidationIntegrityStatus,
)


class M23_168LearningStateValidationIntegrityTests(unittest.TestCase):
    def _make_validation(self):
        integrity = LearningStateExecutionLearningStateTransitionIntegrity(
            integrity_id="transition-integrity-166",
            transition_id="transition-165",
            evidence_id="evidence-164",
            source_integrity_id="integrity-163",
            application_id="application-162",
            decision_id="decision-161",
            proposal_id="proposal-160",
            eligibility_id="eligibility-159",
            transition_fingerprint="a" * 64,
            computed_transition_fingerprint="a" * 64,
            transition_status="FORMULATED",
            state_key="demo.state",
            state_before={"threshold": 0.8, "nested": {"items": [1, {"x": True}]}},
            state_after={"threshold": 0.95, "nested": {"items": [2, {"x": True}]}},
            proposed_change={"threshold": {"from": 0.8, "to": 0.95}},
            status=LearningStateExecutionLearningStateTransitionIntegrityStatus.VALID,
            reasons=("transition integrity passed",),
            lineage={
                "integrity_id": "transition-integrity-166",
                "transition_id": "transition-165",
                "evidence_id": "evidence-164",
                "application_id": "application-162",
                "source_integrity_id": "integrity-163",
            },
            signal_id="signal-158",
            evaluation_id="evaluation-157",
            feedback_id="feedback-156",
            outcome_id="outcome-155",
            attempt_id="attempt-154",
            admission_id="admission-153",
            validation_id="validation-152",
            use_id="use-151",
            request_id="request-150",
            interpretation_id="interpretation-149",
            source_request_id="source-request-148",
            read_validation_id="read-validation-147",
            read_id="read-146",
            consumption_request_id="consumption-145",
            source_validation_id="source-validation-144",
            source_application_fingerprint="b" * 64,
            computed_application_fingerprint="b" * 64,
            confidence=0.91,
            consumer_id="consumer-A",
            execution_target_id="executor-X",
            execution_purpose="perform",
            objective="reach-target",
            evaluator_id="evaluator-A",
            evaluation_purpose="assess",
            signal_kind="POSITIVE",
            signal_purpose="feed-learning",
            learner_id="learner-A",
            eligibility_purpose="future-learning",
            proposer_id="proposer-A",
            proposal_purpose="candidate-learning",
            proposal_rationale={"why": {"score": 0.8}},
            decision_maker_id="decision-maker-A",
            decision_purpose="review-candidate",
            decision_rationale={"basis": "bounded-review"},
            applier_id="applier-A",
            application_purpose="apply-approved-learning",
            application_rationale={"basis": ["approved", {"scope": "bounded"}]},
            application_evidence={"attempt": [{"step": 1}, {"step": 2}]},
            application_status="APPLIED",
            evidence_collector_id="collector-A",
            evidence_purpose="record-state-effect",
            evidence_rationale={"basis": "integrity"},
            evidence_payload={"candidate_state": {"threshold": 0.95}, "observed": [1, 2]},
            transition_actor_id="transition-actor-A",
            transition_purpose="apply-recorded-learning-state-change",
            transition_rationale={"basis": ["recorded-evidence", {"scope": "bounded"}]},
            validator_id="validator-A",
            validation_purpose="validate-transition-integrity",
            validation_rationale={"basis": "anchored-integrity"},
        )
        return LearningStateExecutionLearningStateValidationService().validate(
            integrity,
            validation_id="learning-state-validation-167",
            validator_id="validator-A",
            validation_purpose="validate-transition-integrity",
            validation_rationale={"basis": "anchored-integrity"},
            lineage={
                "validation_id": "learning-state-validation-167",
                "integrity_id": "transition-integrity-166",
                "transition_id": "transition-165",
                "evidence_id": "evidence-164",
                "application_id": "application-162",
                "source_integrity_id": "integrity-163",
                "source_validation_id": "validation-152",
            },
        )

    def _integritize(self, validation=None, **overrides):
        values = {
            "integrity_id": "validation-integrity-168",
        }
        values.update(overrides)
        return LearningStateExecutionLearningStateValidationIntegrityService().validate(
            validation or self._make_validation(),
            **values,
        )

    def test_valid_validation_produces_valid_integrity(self):
        result = self._integritize()
        self.assertIs(result.status, LearningStateExecutionLearningStateValidationIntegrityStatus.VALID)
        self.assertTrue(result.is_valid)
        self.assertTrue(result.validates_integrity)

    def test_exact_validation_type_is_required(self):
        with self.assertRaises(TypeError):
            LearningStateExecutionLearningStateValidationIntegrityService().validate(
                object(), integrity_id="validation-integrity-168"
            )

    def test_integrity_identity_must_be_explicit_and_distinct(self):
        service = LearningStateExecutionLearningStateValidationIntegrityService()
        validation = self._make_validation()
        with self.assertRaises(ValueError):
            service.validate(validation, integrity_id=" ")
        result = self._integritize(integrity_id=validation.validation_id)
        self.assertIs(result.status, LearningStateExecutionLearningStateValidationIntegrityStatus.INVALID)
        self.assertIn("integrity identity must be distinct from validation identity", result.reasons)

    def test_source_validation_status_is_required_for_valid_integrity(self):
        validation = self._make_validation()
        object.__setattr__(validation, "status", LearningStateExecutionLearningStateValidationStatus.REJECTED)
        result = self._integritize(validation)
        self.assertIs(result.status, LearningStateExecutionLearningStateValidationIntegrityStatus.INVALID)
        self.assertIn("learning-state validation is not VALIDATED", result.reasons)

    def test_anchored_lineage_is_rechecked(self):
        validation = self._make_validation()
        original = validation.lineage
        for field, value in (
            ("validation_id", "tampered-validation"),
            ("integrity_id", "tampered-integrity"),
            ("transition_id", "tampered-transition"),
            ("evidence_id", "tampered-evidence"),
            ("application_id", "tampered-application"),
            ("source_integrity_id", "tampered-source-integrity"),
            ("source_validation_id", "tampered-source-validation"),
        ):
            tampered = dict(original)
            tampered[field] = value
            object.__setattr__(validation, "lineage", MappingProxyType(tampered))
            result = self._integritize(validation)
            self.assertIs(result.status, LearningStateExecutionLearningStateValidationIntegrityStatus.INVALID, msg=field)
            object.__setattr__(validation, "lineage", original)

    def test_transition_fingerprint_mismatch_fails_closed(self):
        validation = self._make_validation()
        object.__setattr__(validation, "computed_transition_fingerprint", "d" * 64)
        result = self._integritize(validation)
        self.assertIs(result.status, LearningStateExecutionLearningStateValidationIntegrityStatus.INVALID)
        self.assertIn("transition fingerprint mismatch", result.reasons)

    def test_application_fingerprint_mismatch_fails_closed(self):
        validation = self._make_validation()
        object.__setattr__(validation, "computed_application_fingerprint", "d" * 64)
        result = self._integritize(validation)
        self.assertIs(result.status, LearningStateExecutionLearningStateValidationIntegrityStatus.INVALID)
        self.assertIn("application fingerprint mismatch", result.reasons)

    def test_malformed_fingerprints_are_rejection_evidence(self):
        validation = self._make_validation()
        object.__setattr__(validation, "transition_fingerprint", "not-sha256")
        result = self._integritize(validation)
        self.assertIs(result.status, LearningStateExecutionLearningStateValidationIntegrityStatus.INVALID)
        self.assertTrue(any("transition_fingerprint is not SHA-256" in reason for reason in result.reasons))

    def test_identical_states_are_rejected(self):
        validation = self._make_validation()
        object.__setattr__(validation, "state_after", validation.state_before)
        result = self._integritize(validation)
        self.assertIs(result.status, LearningStateExecutionLearningStateValidationIntegrityStatus.INVALID)
        self.assertIn("state before and after are identical", result.reasons)

    def test_confidence_bounds_are_checked(self):
        validation = self._make_validation()
        object.__setattr__(validation, "confidence", 1.5)
        result = self._integritize(validation)
        self.assertIs(result.status, LearningStateExecutionLearningStateValidationIntegrityStatus.INVALID)
        self.assertIn("confidence is outside bounds", result.reasons)

    def test_preserves_validation_identity_and_provenance(self):
        validation = self._make_validation()
        result = self._integritize(validation)
        for field in (
            "validation_id", "transition_id", "evidence_id", "application_id", "decision_id",
            "proposal_id", "eligibility_id", "source_integrity_id", "source_validation_id", "state_key",
            "transition_fingerprint", "computed_transition_fingerprint", "source_application_fingerprint",
            "computed_application_fingerprint", "confidence", "validation_purpose", "validator_id",
        ):
            self.assertEqual(getattr(result, field), getattr(validation, field))
        self.assertIs(result.integrity_source_status, validation.status)

    def test_integrity_fingerprint_is_deterministic(self):
        first = self._integritize()
        second = self._integritize()
        self.assertEqual(first, second)
        self.assertEqual(first.integrity_fingerprint, first.computed_integrity_fingerprint)
        self.assertEqual(len(first.integrity_fingerprint), 64)

    def test_custom_reasons_and_lineage_are_preserved_and_frozen(self):
        custom_lineage = {
            "integrity_id": "validation-integrity-168",
            "validation_id": "learning-state-validation-167",
            "chain": ["a", {"step": 2}],
        }
        result = self._integritize(reasons=("caller-supplied",), lineage=custom_lineage)
        self.assertEqual(result.reasons, ("caller-supplied",))
        self.assertIsInstance(result.lineage, MappingProxyType)
        self.assertIsInstance(result.lineage["chain"], tuple)
        self.assertIsInstance(result.lineage["chain"][1], MappingProxyType)
        with self.assertRaises(TypeError):
            result.lineage["x"] = "y"

    def test_source_validation_is_not_mutated(self):
        validation = self._make_validation()
        before = validation
        self._integritize(validation)
        self.assertEqual(validation, before)

    def test_integrity_artifact_is_immutable(self):
        result = self._integritize()
        with self.assertRaises((AttributeError, FrozenInstanceError)):
            result.status = LearningStateExecutionLearningStateValidationIntegrityStatus.INVALID

    def test_integrity_has_no_learning_or_authority_powers(self):
        result = self._integritize()
        for name in (
            "mutates_state", "persists_state", "consumes_state", "is_learning", "applies_learning",
            "authorizes_learning", "authorizes_execution", "authorizes_retry", "invokes_learner",
            "invokes_executor", "schedules_work", "plans_work", "updates_model", "mutates_memory",
            "mutates_policy", "establishes_truth", "establishes_correctness", "establishes_certainty",
            "establishes_usefulness",
        ):
            self.assertFalse(getattr(result, name))


if __name__ == "__main__":
    unittest.main()
