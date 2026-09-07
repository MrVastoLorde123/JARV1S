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


class M23_135LearningStateValidationTests(unittest.TestCase):
    def _make_integrity(self):
        return LearningStateExecutionLearningStateTransitionIntegrity(
            integrity_id="transition-integrity-134",
            transition_id="transition-133",
            evidence_id="evidence-132",
            transition_fingerprint="a" * 64,
            computed_transition_fingerprint="a" * 64,
            state_key="demo.state",
            state_before={"threshold": 0.8},
            state_after={"threshold": 0.95},
            application_id="application-130",
            decision_id="decision-129",
            proposal_id="proposal-128",
            eligibility_id="learning-eligibility-127",
            source_integrity_id="application-integrity-131",
            signal_id="signal-125",
            evaluation_id="evaluation-124",
            feedback_id="feedback-123",
            outcome_id="outcome-122",
            attempt_id="attempt-121",
            admission_id="admission-120",
            validation_id="validation-113",
            use_id="use-112",
            request_id="semantic-use-111",
            interpretation_id="interpretation-108",
            source_request_id="request-107",
            read_validation_id="read-validation-106",
            read_id="read-105",
            consumption_request_id="consumption-104",
            source_validation_id="source-validation-103",
            source_application_fingerprint="b" * 64,
            computed_application_fingerprint="c" * 64,
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
            status=LearningStateExecutionLearningStateTransitionIntegrityStatus.VALID,
            reasons=("transition integrity passed",),
            lineage={"integrity_id": "transition-integrity-134", "transition_id": "transition-133", "evidence_id": "evidence-132"},
        )

    def test_valid_integrity_produces_validated_state(self):
        result = LearningStateExecutionLearningStateValidationService().validate(
            self._make_integrity(),
            validation_id="learning-state-validation-135",
            validator_id="validator-A",
            validation_purpose="gate-learning-state-consumption",
            validation_rationale={"basis": "validated-transition-integrity"},
        )
        self.assertIs(result.status, LearningStateExecutionLearningStateValidationStatus.VALIDATED)
        self.assertTrue(result.is_validated)
        self.assertTrue(result.admits_consumption)
        self.assertTrue(result.validates_learning_state)

    def test_exact_integrity_type_is_required(self):
        with self.assertRaises(TypeError):
            LearningStateExecutionLearningStateValidationService().validate(
                object(),
                validation_id="learning-state-validation-135",
                validator_id="validator-A",
                validation_purpose="gate-learning-state-consumption",
                validation_rationale={"basis": "test"},
            )

    def test_required_validation_metadata_is_enforced(self):
        service = LearningStateExecutionLearningStateValidationService()
        integrity = self._make_integrity()
        for kwargs in (
            {"validation_id": " ", "validator_id": "validator-A", "validation_purpose": "gate", "validation_rationale": {}},
            {"validation_id": "validation-135", "validator_id": " ", "validation_purpose": "gate", "validation_rationale": {}},
            {"validation_id": "validation-135", "validator_id": "validator-A", "validation_purpose": " ", "validation_rationale": {}},
        ):
            with self.subTest(kwargs=kwargs):
                with self.assertRaises(ValueError):
                    service.validate(integrity, **kwargs)
        with self.assertRaises(ValueError):
            service.validate(
                integrity,
                validation_id="validation-135",
                validator_id="validator-A",
                validation_purpose="gate",
                validation_rationale=None,
            )

    def test_invalid_integrity_is_rejected_fail_closed(self):
        integrity = self._make_integrity()
        object.__setattr__(integrity, "status", LearningStateExecutionLearningStateTransitionIntegrityStatus.INVALID)
        result = LearningStateExecutionLearningStateValidationService().validate(
            integrity,
            validation_id="learning-state-validation-135",
            validator_id="validator-A",
            validation_purpose="gate-learning-state-consumption",
            validation_rationale={"basis": "test"},
        )
        self.assertIs(result.status, LearningStateExecutionLearningStateValidationStatus.REJECTED)
        self.assertFalse(result.is_validated)
        self.assertFalse(result.admits_consumption)
        self.assertIn("transition integrity is not VALID", result.reasons)

    def test_integrity_lineage_is_checked_fail_closed(self):
        integrity = self._make_integrity()
        object.__setattr__(integrity, "lineage", MappingProxyType({"integrity_id": "tampered-integrity", "transition_id": "transition-133", "evidence_id": "evidence-132"}))
        result = LearningStateExecutionLearningStateValidationService().validate(
            integrity,
            validation_id="validation-135",
            validator_id="validator-A",
            validation_purpose="gate",
            validation_rationale={"basis": "test"},
        )
        self.assertIs(result.status, LearningStateExecutionLearningStateValidationStatus.REJECTED)
        self.assertIn("integrity lineage mismatch", result.reasons)

    def test_transition_lineage_is_checked_fail_closed(self):
        integrity = self._make_integrity()
        object.__setattr__(integrity, "lineage", MappingProxyType({"integrity_id": integrity.integrity_id, "transition_id": "tampered-transition", "evidence_id": integrity.evidence_id}))
        result = LearningStateExecutionLearningStateValidationService().validate(
            integrity,
            validation_id="validation-135",
            validator_id="validator-A",
            validation_purpose="gate",
            validation_rationale={"basis": "test"},
        )
        self.assertIs(result.status, LearningStateExecutionLearningStateValidationStatus.REJECTED)
        self.assertIn("transition lineage mismatch", result.reasons)

    def test_evidence_lineage_is_checked_fail_closed(self):
        integrity = self._make_integrity()
        object.__setattr__(integrity, "lineage", MappingProxyType({"integrity_id": integrity.integrity_id, "transition_id": integrity.transition_id, "evidence_id": "tampered-evidence"}))
        result = LearningStateExecutionLearningStateValidationService().validate(
            integrity,
            validation_id="validation-135",
            validator_id="validator-A",
            validation_purpose="gate",
            validation_rationale={"basis": "test"},
        )
        self.assertIs(result.status, LearningStateExecutionLearningStateValidationStatus.REJECTED)
        self.assertIn("evidence lineage mismatch", result.reasons)

    def test_fingerprint_mismatch_is_rejected_without_repair(self):
        integrity = self._make_integrity()
        object.__setattr__(integrity, "transition_fingerprint", "tampered")
        result = LearningStateExecutionLearningStateValidationService().validate(
            integrity,
            validation_id="validation-135",
            validator_id="validator-A",
            validation_purpose="gate",
            validation_rationale={"basis": "test"},
        )
        self.assertIs(result.status, LearningStateExecutionLearningStateValidationStatus.REJECTED)
        self.assertIn("transition fingerprint mismatch", result.reasons)
        self.assertEqual(result.transition_fingerprint, "tampered")

    def test_identical_before_and_after_state_is_rejected(self):
        integrity = self._make_integrity()
        object.__setattr__(integrity, "state_after", integrity.state_before)
        result = LearningStateExecutionLearningStateValidationService().validate(
            integrity,
            validation_id="validation-135",
            validator_id="validator-A",
            validation_purpose="gate",
            validation_rationale={"basis": "test"},
        )
        self.assertIs(result.status, LearningStateExecutionLearningStateValidationStatus.REJECTED)
        self.assertIn("state before and after are identical", result.reasons)

    def test_integrity_identity_must_be_distinct_from_transition(self):
        integrity = self._make_integrity()
        object.__setattr__(integrity, "integrity_id", integrity.transition_id)
        result = LearningStateExecutionLearningStateValidationService().validate(
            integrity,
            validation_id="validation-135",
            validator_id="validator-A",
            validation_purpose="gate",
            validation_rationale={"basis": "test"},
        )
        self.assertIs(result.status, LearningStateExecutionLearningStateValidationStatus.REJECTED)
        self.assertIn("integrity identity must be distinct from transition identity", result.reasons)

    def test_provenance_and_validation_metadata_are_preserved(self):
        integrity = self._make_integrity()
        result = LearningStateExecutionLearningStateValidationService().validate(
            integrity,
            validation_id="validation-135",
            validator_id="validator-A",
            validation_purpose="gate-learning-state-consumption",
            validation_rationale={"basis": ["validated", {"scope": "bounded"}]},
        )
        for field in (
            "integrity_id", "transition_id", "evidence_id", "state_key", "state_before", "state_after",
            "transition_fingerprint", "computed_transition_fingerprint", "source_application_fingerprint",
            "computed_application_fingerprint", "application_id", "decision_id", "proposal_id", "eligibility_id",
            "source_integrity_id", "signal_id", "evaluation_id", "feedback_id", "outcome_id", "attempt_id",
            "admission_id", "use_id", "request_id", "interpretation_id", "source_request_id", "read_validation_id",
            "read_id", "consumption_request_id", "confidence", "application_status", "execution_target_id",
            "evidence_payload", "transition_rationale",
        ):
            self.assertEqual(getattr(result, field), getattr(integrity, field))
        self.assertEqual(result.source_validation_id, integrity.validation_id)
        self.assertEqual(result.validation_id, "validation-135")
        self.assertEqual(result.validator_id, "validator-A")
        self.assertEqual(result.validation_purpose, "gate-learning-state-consumption")

    def test_nested_payloads_and_lineage_are_recursively_frozen(self):
        result = LearningStateExecutionLearningStateValidationService().validate(
            self._make_integrity(),
            validation_id="validation-135",
            validator_id="validator-A",
            validation_purpose="gate",
            validation_rationale={"basis": [{"scope": "bounded"}]},
            lineage={"chain": ["integrity-134", {"transition": "transition-133"}]},
        )
        self.assertIsInstance(result.state_before, MappingProxyType)
        self.assertIsInstance(result.state_after, MappingProxyType)
        self.assertIsInstance(result.application_evidence, MappingProxyType)
        self.assertIsInstance(result.validation_rationale, MappingProxyType)
        self.assertIsInstance(result.lineage, MappingProxyType)
        self.assertIsInstance(result.lineage["chain"], tuple)
        self.assertIsInstance(result.lineage["chain"][1], MappingProxyType)

    def test_caller_reasons_and_lineage_are_preserved_and_frozen(self):
        result = LearningStateExecutionLearningStateValidationService().validate(
            self._make_integrity(),
            validation_id="validation-135",
            validator_id="validator-A",
            validation_purpose="gate",
            validation_rationale={"basis": "test"},
            reasons=("caller-reason",),
            lineage={"source": {"integrity_id": "integrity-134"}},
        )
        self.assertEqual(result.reasons, ("caller-reason",))
        self.assertIsInstance(result.lineage, MappingProxyType)
        self.assertEqual(result.lineage["source"]["integrity_id"], "integrity-134")

    def test_malformed_reasons_are_rejected(self):
        with self.assertRaises(TypeError):
            LearningStateExecutionLearningStateValidationService().validate(
                self._make_integrity(),
                validation_id="validation-135",
                validator_id="validator-A",
                validation_purpose="gate",
                validation_rationale={"basis": "test"},
                reasons=("ok", " "),
            )

    def test_source_integrity_is_not_mutated(self):
        integrity = self._make_integrity()
        before = integrity.lineage
        result = LearningStateExecutionLearningStateValidationService().validate(
            integrity,
            validation_id="validation-135",
            validator_id="validator-A",
            validation_purpose="gate",
            validation_rationale={"basis": "test"},
        )
        self.assertEqual(integrity.lineage, before)
        self.assertEqual(integrity.integrity_id, "transition-integrity-134")
        self.assertEqual(result.integrity_id, integrity.integrity_id)

    def test_validation_is_deterministic_for_same_inputs(self):
        service = LearningStateExecutionLearningStateValidationService()
        first = service.validate(
            self._make_integrity(),
            validation_id="validation-135",
            validator_id="validator-A",
            validation_purpose="gate",
            validation_rationale={"basis": "test"},
        )
        second = service.validate(
            self._make_integrity(),
            validation_id="validation-135",
            validator_id="validator-A",
            validation_purpose="gate",
            validation_rationale={"basis": "test"},
        )
        self.assertEqual(first, second)

    def test_validation_artifact_is_immutable(self):
        result = LearningStateExecutionLearningStateValidationService().validate(
            self._make_integrity(),
            validation_id="validation-135",
            validator_id="validator-A",
            validation_purpose="gate",
            validation_rationale={"basis": "test"},
        )
        with self.assertRaises((AttributeError, FrozenInstanceError)):
            result.status = LearningStateExecutionLearningStateValidationStatus.REJECTED

    def test_validation_has_no_learning_state_or_execution_powers(self):
        result = LearningStateExecutionLearningStateValidationService().validate(
            self._make_integrity(),
            validation_id="validation-135",
            validator_id="validator-A",
            validation_purpose="gate",
            validation_rationale={"basis": "test"},
        )
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
