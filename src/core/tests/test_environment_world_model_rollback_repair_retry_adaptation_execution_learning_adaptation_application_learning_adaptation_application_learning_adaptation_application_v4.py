"""Focused tests for M23.95 application-learning adaptation application v4."""
import unittest
from types import MappingProxyType

from src.core.environment_world_model_rollback_repair_retry_adaptation_execution_learning_adaptation_application_learning_adaptation_application_learning_adaptation_decision_v4 import (
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationLearningAdaptationDecisionV4Service as DS,
)
from src.core.environment_world_model_rollback_repair_retry_adaptation_execution_learning_adaptation_application_learning_adaptation_application_learning_adaptation_proposal_v4 import (
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationLearningAdaptationProposalV4Service as PS,
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationLearningAdaptationProposalV4Status as P,
)
from src.core.environment_world_model_rollback_repair_retry_adaptation_execution_learning_adaptation_application_learning_adaptation_application_learning_adaptation_application_v4 import (
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationLearningAdaptationApplicationV4 as A,
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationLearningAdaptationApplicationV4Service as AS,
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationLearningAdaptationApplicationV4Status as S,
)


class M23_95ApplicationV4Tests(unittest.TestCase):
    def _decision(self, accept=True, blocked=False):
        from src.core.environment_world_model_rollback_repair_retry_adaptation_execution_learning_adaptation_application_learning_adaptation_application_learning_signal_integrity_v4 import (
            EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationLearningSignalIntegrityV4Status as I,
        )
        from src.core.environment_world_model_rollback_repair_retry_adaptation_execution_learning_adaptation_application_learning_adaptation_application_learning_eligibility_v4 import (
            EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationLearningEligibilityV4,
            EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationLearningEligibilityV4Status as E,
        )
        e = EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationLearningEligibilityV4(
            eligibility_id="eligibility-95", integrity_id="integrity-92", signal_id="signal-90", evaluation_id="evaluation-89",
            feedback_id="feedback-88", feedback_source_id="feedback-source-88", classification_id="classification-87",
            source_integrity_id="integrity-91", application_id="application-86", decision_id="decision-85",
            proposal_id="source-proposal-84", outcome_id="outcome-83", outcome_status="SUCCEEDED", feedback_status="VALID",
            confidence=0.91, signal_fingerprint="a"*64, source_signal_fingerprint="b"*64, result_fingerprint="c"*64,
            application_fingerprint="d"*64, failure_reason="eligibility blocked" if blocked else None,
            evaluation_status="VALID", signal_status="VALID", integrity_status=I.INVALID if blocked else I.VALID,
            status=E.INELIGIBLE if blocked else E.ELIGIBLE, reasons={"r":{"x":[1,2]}}, lineage={"l":[3,4]},
        )
        p = PS().propose(e, proposal_id="proposal-95", proposal_payload={"change": {"parameter": "learning_rate", "value": 0.02}})
        return DS().decide(p, decision_id="decision-95", accept=accept)

    def test_accepted_decision_applies_through_injected_applier(self):
        seen = []
        result = AS().apply(self._decision(), application_id="application-95", learning_applier=lambda payload: seen.append(payload) or {"ok": True, "applied": payload["proposal_id"]})
        self.assertEqual(result.application_status, S.APPLIED)
        self.assertEqual(result.application_result["applied"], "proposal-95")
        self.assertEqual(seen[0]["decision_id"], "decision-95")

    def test_missing_applier_fails_closed(self):
        result = AS().apply(self._decision(), application_id="application-95")
        self.assertEqual(result.application_status, S.NOT_APPLIED)
        self.assertIn("injected learning applier", result.failure_reason)

    def test_applier_exception_fails_closed(self):
        def fail(_):
            raise RuntimeError("boom")
        result = AS().apply(self._decision(), application_id="application-95", learning_applier=fail)
        self.assertEqual(result.application_status, S.NOT_APPLIED)
        self.assertIn("boom", result.failure_reason)

    def test_applier_non_mapping_result_fails_closed(self):
        result = AS().apply(self._decision(), application_id="application-95", learning_applier=lambda _: True)
        self.assertEqual(result.application_status, S.NOT_APPLIED)
        self.assertIn("mapping result", result.failure_reason)

    def test_rejected_decision_is_inert(self):
        called = []
        result = AS().apply(self._decision(accept=False), application_id="application-95", learning_applier=lambda _: called.append(1) or {})
        self.assertEqual(result.application_status, S.REJECTED)
        self.assertEqual(called, [])

    def test_blocked_decision_is_inert(self):
        called = []
        result = AS().apply(self._decision(blocked=True), application_id="application-95", learning_applier=lambda _: called.append(1) or {})
        self.assertEqual(result.application_status, S.BLOCKED)
        self.assertEqual(called, [])

    def test_application_identity_is_new_and_source_identities_preserved(self):
        source = self._decision()
        result = AS().apply(source, application_id="application-95", learning_applier=lambda _: {})
        self.assertEqual(result.application_id, "application-95")
        self.assertNotEqual(result.application_id, source.application_id)
        self.assertEqual(result.decision_id, "decision-95")
        self.assertEqual(result.proposal_id, "proposal-95")
        self.assertEqual(result.source_proposal_id, "source-proposal-84")
        self.assertEqual(result.eligibility_id, "eligibility-95")

    def test_provenance_and_fingerprints_are_preserved(self):
        source = self._decision()
        result = AS().apply(source, application_id="application-95", learning_applier=lambda _: {})
        for name in ("integrity_id", "signal_id", "evaluation_id", "feedback_id", "classification_id", "source_integrity_id", "outcome_id"):
            self.assertEqual(getattr(result, name), getattr(source, name))
        self.assertEqual(result.application_id, "application-95")
        self.assertNotEqual(result.application_id, source.application_id)
        for name in ("signal_fingerprint", "source_signal_fingerprint", "result_fingerprint", "application_fingerprint"):
            self.assertEqual(getattr(result, name), getattr(source, name))

    def test_application_result_reasons_and_lineage_are_recursively_immutable(self):
        result = AS().apply(
            self._decision(), application_id="application-95",
            learning_applier=lambda _: {"nested": {"items": [1, {"x": 2}] }},
            reasons={"r": {"items": [1,2]}}, lineage={"l": {"items": [3,4]}},
        )
        self.assertIsInstance(result.application_result, MappingProxyType)
        self.assertIsInstance(result.reasons, MappingProxyType)
        self.assertIsInstance(result.lineage, MappingProxyType)
        self.assertIsInstance(result.application_result["nested"]["items"], tuple)
        with self.assertRaises(TypeError):
            result.application_result["nested"] = {}
        with self.assertRaises(TypeError):
            result.reasons["r"] = {}

    def test_source_is_not_mutated(self):
        source = self._decision()
        before = source
        AS().apply(source, application_id="application-95", learning_applier=lambda _: {})
        self.assertEqual(source, before)

    def test_blank_application_id_fails_closed(self):
        with self.assertRaises(ValueError):
            AS().apply(self._decision(), application_id=" ", learning_applier=lambda _: {})

    def test_wrong_source_type_fails_closed(self):
        with self.assertRaises(TypeError):
            AS().apply(object(), application_id="application-95", learning_applier=lambda _: {})

    def test_authority_and_mutation_walls_are_false(self):
        result = AS().apply(self._decision(), application_id="application-95", learning_applier=lambda _: {})
        self.assertTrue(result.is_advisory_only)
        for name in ("authorizes_adaptation", "grants_authority", "updates_model", "mutates_memory", "mutates_policy", "mutates_persistence", "schedules_work", "executes_action"):
            self.assertFalse(getattr(result, name))

    def test_application_result_must_be_mapping_for_applied_evidence(self):
        source = self._decision()
        with self.assertRaises(TypeError):
            A(
                application_id="application-95", decision_id=source.decision_id, proposal_id=source.proposal_id, source_proposal_id=source.source_proposal_id,
                eligibility_id=source.eligibility_id, integrity_id=source.integrity_id, signal_id=source.signal_id, evaluation_id=source.evaluation_id,
                feedback_id=source.feedback_id, feedback_source_id=source.feedback_source_id, classification_id=source.classification_id,
                source_integrity_id=source.source_integrity_id, source_decision_id=source.source_decision_id, outcome_id=source.outcome_id,
                outcome_status=source.outcome_status, feedback_status=source.feedback_status, confidence=source.confidence,
                signal_fingerprint=source.signal_fingerprint, source_signal_fingerprint=source.source_signal_fingerprint, result_fingerprint=source.result_fingerprint,
                application_fingerprint=source.application_fingerprint, failure_reason=None, evaluation_status=source.evaluation_status,
                signal_status=source.signal_status, integrity_status=source.integrity_status, eligibility_status=source.eligibility_status,
                proposal_status=source.proposal_status, proposal_kind=source.proposal_kind, decision_status=source.decision_status,
                application_status=S.APPLIED, application_result=[]
            )

    def test_applied_evidence_requires_accepted_decision(self):
        source = self._decision(accept=False)
        with self.assertRaises(ValueError):
            A(
                application_id="application-95", decision_id=source.decision_id, proposal_id=source.proposal_id, source_proposal_id=source.source_proposal_id,
                eligibility_id=source.eligibility_id, integrity_id=source.integrity_id, signal_id=source.signal_id, evaluation_id=source.evaluation_id,
                feedback_id=source.feedback_id, feedback_source_id=source.feedback_source_id, classification_id=source.classification_id,
                source_integrity_id=source.source_integrity_id, source_decision_id=source.source_decision_id, outcome_id=source.outcome_id,
                outcome_status=source.outcome_status, feedback_status=source.feedback_status, confidence=source.confidence,
                signal_fingerprint=source.signal_fingerprint, source_signal_fingerprint=source.source_signal_fingerprint, result_fingerprint=source.result_fingerprint,
                application_fingerprint=source.application_fingerprint, failure_reason=None, evaluation_status=source.evaluation_status,
                signal_status=source.signal_status, integrity_status=source.integrity_status, eligibility_status=source.eligibility_status,
                proposal_status=source.proposal_status, proposal_kind=source.proposal_kind, decision_status=source.decision_status,
                application_status=S.APPLIED, application_result={"ok": True}
            )

    def test_blocked_status_requires_blocked_application_evidence(self):
        source = self._decision(blocked=True)
        with self.assertRaises(ValueError):
            A(
                application_id="application-95", decision_id=source.decision_id, proposal_id=source.proposal_id, source_proposal_id=source.source_proposal_id,
                eligibility_id=source.eligibility_id, integrity_id=source.integrity_id, signal_id=source.signal_id, evaluation_id=source.evaluation_id,
                feedback_id=source.feedback_id, feedback_source_id=source.feedback_source_id, classification_id=source.classification_id,
                source_integrity_id=source.source_integrity_id, source_decision_id=source.source_decision_id, outcome_id=source.outcome_id,
                outcome_status=source.outcome_status, feedback_status=source.feedback_status, confidence=source.confidence,
                signal_fingerprint=source.signal_fingerprint, source_signal_fingerprint=source.source_signal_fingerprint, result_fingerprint=source.result_fingerprint,
                application_fingerprint=source.application_fingerprint, failure_reason=None, evaluation_status=source.evaluation_status,
                signal_status=source.signal_status, integrity_status=source.integrity_status, eligibility_status=source.eligibility_status,
                proposal_status=source.proposal_status, proposal_kind=source.proposal_kind, decision_status=source.decision_status,
                application_status=S.APPLIED, application_result={"ok": True}
            )

    def test_non_applied_evidence_cannot_carry_result(self):
        source = self._decision()
        with self.assertRaises(ValueError):
            A(
                application_id="application-95", decision_id=source.decision_id, proposal_id=source.proposal_id, source_proposal_id=source.source_proposal_id,
                eligibility_id=source.eligibility_id, integrity_id=source.integrity_id, signal_id=source.signal_id, evaluation_id=source.evaluation_id,
                feedback_id=source.feedback_id, feedback_source_id=source.feedback_source_id, classification_id=source.classification_id,
                source_integrity_id=source.source_integrity_id, source_decision_id=source.source_decision_id, outcome_id=source.outcome_id,
                outcome_status=source.outcome_status, feedback_status=source.feedback_status, confidence=source.confidence,
                signal_fingerprint=source.signal_fingerprint, source_signal_fingerprint=source.source_signal_fingerprint, result_fingerprint=source.result_fingerprint,
                application_fingerprint=source.application_fingerprint, failure_reason="failed", evaluation_status=source.evaluation_status,
                signal_status=source.signal_status, integrity_status=source.integrity_status, eligibility_status=source.eligibility_status,
                proposal_status=source.proposal_status, proposal_kind=source.proposal_kind, decision_status=source.decision_status,
                application_status=S.NOT_APPLIED, application_result={"should": "fail"}
            )


if __name__ == "__main__":
    unittest.main()
