import unittest
from dataclasses import FrozenInstanceError
from types import MappingProxyType

from src.core.learning_state_execution_learning_proposal import (
    LearningStateExecutionLearningProposal,
    LearningStateExecutionLearningProposalStatus,
)
from src.core.learning_state_execution_learning_proposal_decision import (
    LearningStateExecutionLearningProposalDecisionService,
)
from src.core.learning_state_execution_learning_proposal_application import (
    LearningStateExecutionLearningProposalApplicationService,
)
from src.core.learning_state_execution_learning_proposal_application_integrity import (
    LearningStateExecutionLearningProposalApplicationIntegrityService,
    LearningStateExecutionLearningProposalApplicationIntegrityStatus,
)
from src.core.learning_state_execution_learning_state_evidence import (
    LearningStateExecutionLearningStateEvidenceService,
    LearningStateExecutionLearningStateEvidenceStatus,
)


class M23_164LearningStateEvidenceTests(unittest.TestCase):
    def _make_proposal(self):
        return LearningStateExecutionLearningProposal(
            proposal_id="proposal-160",
            eligibility_id="learning-eligibility-159",
            integrity_id="integrity-158",
            signal_id="signal-157",
            evaluation_id="evaluation-156",
            feedback_id="feedback-155",
            outcome_id="outcome-154",
            attempt_id="attempt-153",
            admission_id="admission-152",
            eligibility_source_id="integrity-158",
            handling_id="handling-150",
            consumption_id="consumption-149",
            receipt_id="receipt-148",
            handoff_id="handoff-147",
            inherited_integrity_id="integrity-previous",
            validation_id="validation-145",
            semantic_use_id="semantic-use-144",
            source_request_id="request-143",
            source_request_lineage_id="request-lineage-143",
            source_validation_id="source-validation-142",
            source_validation_lineage_id="source-validation-lineage-142",
            interpretation_id="interpretation-141",
            read_id="read-140",
            consumption_request_id="consumption-139",
            requester_id="requester-A",
            consumer_id="consumer-A",
            handoff_target_id="handoff-target-A",
            recipient_id="recipient-A",
            handling_target_id="handler-A",
            execution_target_id="executor-A",
            signal_kind="POSITIVE",
            signal_purpose="feed-learning",
            signal_context={
                "source": "execution-feedback",
                "features": ["stable", {"score": 0.9}],
            },
            signal_status="RECORDED",
            source_signal_fingerprint="a" * 64,
            computed_signal_fingerprint="a" * 64,
            learner_id="learner-A",
            eligibility_purpose="enter-future-learning",
            proposer_id="proposer-A",
            proposal_purpose="candidate-learning",
            proposed_change={"threshold": 0.95, "nested": ["stable"]},
            rationale={"why": {"score": 0.8}},
            status=LearningStateExecutionLearningProposalStatus.PROPOSED,
            reasons=("learning eligibility is ELIGIBLE",),
            lineage={
                "proposal_id": "proposal-160",
                "eligibility_id": "learning-eligibility-159",
            },
        )

    def _make_application(self):
        decision = LearningStateExecutionLearningProposalDecisionService().decide(
            self._make_proposal(),
            decision_id="decision-161",
            decision_maker_id="decision-maker-A",
            decision_purpose="review-candidate",
            decision_rationale={"basis": "bounded-review"},
        )
        return LearningStateExecutionLearningProposalApplicationService().apply(
            decision,
            application_id="application-162",
            applier_id="applier-A",
            application_purpose="apply-candidate",
            application_rationale={"basis": "approved-decision"},
            application_evidence={"checks": [{"name": "decision"}]},
            lineage={
                "application_id": "application-162",
                "decision_id": "decision-161",
            },
        )

    def _make_integrity(self):
        application = self._make_application()
        return LearningStateExecutionLearningProposalApplicationIntegrityService().verify(
            application,
            integrity_id="application-integrity-163",
        )

    def _record(self, integrity=None, **overrides):
        values = {
            "evidence_id": "evidence-164",
            "evidence_collector_id": "collector-A",
            "evidence_purpose": "record-candidate-state-effect",
            "evidence_rationale": {"basis": ["valid-integrity", {"scope": "bounded"}]},
            "evidence_payload": {
                "candidate_state": {"threshold": 0.95},
                "observed": [1, 2],
            },
        }
        values.update(overrides)
        return LearningStateExecutionLearningStateEvidenceService().record(
            integrity or self._make_integrity(),
            **values,
        )

    def test_valid_integrity_produces_recorded_evidence(self):
        result = self._record()
        self.assertIs(
            result.status,
            LearningStateExecutionLearningStateEvidenceStatus.RECORDED,
        )
        self.assertTrue(result.is_recorded)
        self.assertTrue(result.records_state_evidence)

    def test_exact_integrity_type_is_required(self):
        with self.assertRaises(TypeError):
            LearningStateExecutionLearningStateEvidenceService().record(
                object(),
                evidence_id="evidence-164",
                evidence_collector_id="collector-A",
                evidence_purpose="record",
                evidence_rationale={"basis": "x"},
                evidence_payload={"x": 1},
            )

    def test_required_evidence_metadata_is_enforced(self):
        service = LearningStateExecutionLearningStateEvidenceService()
        integrity = self._make_integrity()

        for field in (
            "evidence_id",
            "evidence_collector_id",
            "evidence_purpose",
        ):
            values = {
                "evidence_id": "evidence-164",
                "evidence_collector_id": "collector-A",
                "evidence_purpose": "record",
                "evidence_rationale": {"basis": "x"},
                "evidence_payload": {"x": 1},
            }
            values[field] = " "
            with self.subTest(field=field):
                with self.assertRaises(ValueError):
                    service.record(integrity, **values)

        with self.assertRaises(ValueError):
            service.record(
                integrity,
                evidence_id="evidence-164",
                evidence_collector_id="collector-A",
                evidence_purpose="record",
                evidence_rationale=None,
                evidence_payload={"x": 1},
            )

    def test_invalid_integrity_fails_closed(self):
        integrity = self._make_integrity()
        object.__setattr__(
            integrity,
            "status",
            LearningStateExecutionLearningProposalApplicationIntegrityStatus.INVALID,
        )

        result = self._record(integrity)

        self.assertIs(
            result.status,
            LearningStateExecutionLearningStateEvidenceStatus.REJECTED,
        )
        self.assertTrue(result.is_rejected)
        self.assertFalse(result.is_recorded)

    def test_integrity_lineage_is_checked_fail_closed(self):
        integrity = self._make_integrity()
        object.__setattr__(
            integrity,
            "lineage",
            MappingProxyType(
                {
                    "integrity_id": "tampered-integrity",
                    "application_id": integrity.application_id,
                    "source_integrity_id": integrity.source_integrity_id,
                }
            ),
        )

        result = self._record(integrity)

        self.assertIs(
            result.status,
            LearningStateExecutionLearningStateEvidenceStatus.REJECTED,
        )
        self.assertIn(
            "application integrity lineage is not valid",
            result.reasons,
        )

    def test_provenance_is_preserved(self):
        integrity = self._make_integrity()
        result = self._record(integrity)

        for field in (
            "integrity_id",
            "application_id",
            "decision_id",
            "proposal_id",
            "eligibility_id",
            "source_integrity_id",
            "signal_id",
            "evaluation_id",
            "feedback_id",
            "outcome_id",
            "attempt_id",
            "admission_id",
            "eligibility_source_id",
            "handling_id",
            "consumption_id",
            "receipt_id",
            "handoff_id",
            "inherited_integrity_id",
            "validation_id",
            "semantic_use_id",
            "source_request_id",
            "source_request_lineage_id",
            "source_validation_id",
            "source_validation_lineage_id",
            "interpretation_id",
            "read_id",
            "consumption_request_id",
            "requester_id",
            "consumer_id",
            "handoff_target_id",
            "recipient_id",
            "handling_target_id",
            "execution_target_id",
            "signal_kind",
            "signal_purpose",
            "signal_status",
            "source_signal_fingerprint",
            "computed_signal_fingerprint",
            "learner_id",
            "eligibility_purpose",
            "proposer_id",
            "proposal_purpose",
            "proposed_change",
            "decision_maker_id",
            "decision_purpose",
            "applier_id",
            "application_purpose",
            "application_status",
        ):
            self.assertEqual(
                getattr(result, field),
                getattr(integrity, field),
            )

    def test_evidence_metadata_is_recorded_explicitly(self):
        result = self._record()

        self.assertEqual(result.evidence_id, "evidence-164")
        self.assertEqual(result.evidence_collector_id, "collector-A")
        self.assertEqual(
            result.evidence_purpose,
            "record-candidate-state-effect",
        )
        self.assertEqual(
            result.evidence_rationale["basis"][0],
            "valid-integrity",
        )

    def test_nested_payload_and_lineage_are_recursively_frozen(self):
        result = self._record(
            evidence_rationale={"basis": [{"scope": "bounded"}]},
            evidence_payload={
                "candidate_state": {"threshold": 0.95},
                "observed": [1, 2],
            },
            lineage={
                "chain": [
                    "application-integrity-163",
                    {"application": "application-162"},
                ]
            },
        )

        self.assertIsInstance(result.evidence_payload, MappingProxyType)
        self.assertIsInstance(
            result.evidence_payload["candidate_state"],
            MappingProxyType,
        )
        self.assertIsInstance(
            result.evidence_payload["observed"],
            tuple,
        )
        self.assertIsInstance(result.evidence_rationale, MappingProxyType)
        self.assertIsInstance(result.lineage, MappingProxyType)
        self.assertIsInstance(result.lineage["chain"], tuple)
        self.assertIsInstance(
            result.lineage["chain"][1],
            MappingProxyType,
        )

    def test_caller_lineage_is_preserved(self):
        custom_lineage = {
            "evidence_id": "evidence-164",
            "integrity_id": "application-integrity-163",
            "chain": {"step": 3},
        }

        result = self._record(lineage=custom_lineage)

        self.assertEqual(result.lineage["evidence_id"], "evidence-164")
        self.assertEqual(
            result.lineage["integrity_id"],
            "application-integrity-163",
        )
        self.assertEqual(result.lineage["chain"]["step"], 3)

    def test_source_integrity_is_not_mutated(self):
        integrity = self._make_integrity()
        before = integrity

        result = self._record(integrity)

        self.assertEqual(integrity, before)
        self.assertEqual(
            result.integrity_id,
            integrity.integrity_id,
        )

    def test_evidence_artifact_is_immutable(self):
        result = self._record()

        with self.assertRaises((AttributeError, FrozenInstanceError)):
            result.status = LearningStateExecutionLearningStateEvidenceStatus.REJECTED

        with self.assertRaises(TypeError):
            result.lineage["x"] = "y"

    def test_evidence_is_deterministic_for_same_inputs(self):
        first = self._record()
        second = self._record()
        self.assertEqual(first, second)

    def test_evidence_has_no_learning_or_authority_powers(self):
        result = self._record()

        for name in (
            "transitions_state",
            "mutates_state",
            "persists_state",
            "is_learning",
            "applies_learning",
            "authorizes_learning",
            "authorizes_execution",
            "authorizes_retry",
            "invokes_learner",
            "invokes_executor",
            "schedules_work",
            "plans_work",
            "updates_model",
            "mutates_memory",
            "mutates_policy",
            "establishes_truth",
            "establishes_correctness",
            "establishes_certainty",
            "establishes_usefulness",
            "proposes_adaptation",
        ):
            self.assertFalse(getattr(result, name))


    def test_source_integrity_lineage_is_checked_fail_closed(self):
        integrity = self._make_integrity()
        object.__setattr__(
            integrity,
            "lineage",
            MappingProxyType(
                {
                    "integrity_id": integrity.integrity_id,
                    "application_id": integrity.application_id,
                    "source_integrity_id": "tampered-source-integrity",
                }
            ),
        )

        result = self._record(integrity)

        self.assertIs(
            result.status,
            LearningStateExecutionLearningStateEvidenceStatus.REJECTED,
        )
        self.assertTrue(result.is_rejected)

if __name__ == "__main__":
    unittest.main()
