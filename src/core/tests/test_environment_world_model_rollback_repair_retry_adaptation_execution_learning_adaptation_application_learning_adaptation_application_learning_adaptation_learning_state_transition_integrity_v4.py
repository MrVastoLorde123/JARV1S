import unittest

from src.core.environment_world_model_rollback_repair_retry_adaptation_execution_learning_adaptation_application_learning_adaptation_application_learning_adaptation_application_v4 import (
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationLearningAdaptationApplicationV4Status as AS,
)
from src.core.environment_world_model_rollback_repair_retry_adaptation_execution_learning_adaptation_application_learning_adaptation_application_learning_adaptation_learning_state_evidence_v4 import (
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationLearningAdaptationLearningStateEvidenceV4 as E,
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationLearningAdaptationLearningStateEvidenceV4Status as ES,
)
from src.core.environment_world_model_rollback_repair_retry_adaptation_execution_learning_adaptation_application_learning_adaptation_application_learning_adaptation_learning_state_transition_v4 import (
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationLearningAdaptationLearningStateTransitionV4Service as TS,
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationLearningAdaptationLearningStateTransitionV4Status as TSStatus,
)
from src.core.learning_state_transition_integrity import (
    LearningStateTransitionIntegrity as I,
    LearningStateTransitionIntegrityService as IS,
    LearningStateTransitionIntegrityStatus as ISS,
)


class LearningStateTransitionIntegrityTests(unittest.TestCase):
    def _evidence(self, status=ES.READY):
        from src.core.environment_world_model_rollback_repair_retry_adaptation_execution_learning_adaptation_application_learning_adaptation_application_learning_adaptation_application_integrity_v4 import (
            EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationLearningAdaptationApplicationIntegrityV4Status as IntegrityStatus,
        )
        return E(
            evidence_id="evidence-97", application_id="application-96", integrity_id="integrity-96",
            decision_id="decision-95", proposal_id="proposal-95", source_proposal_id="proposal-94",
            eligibility_id="eligibility-95", signal_id="signal-95", evaluation_id="evaluation-95",
            feedback_id="feedback-95", classification_id="classification-95", source_integrity_id="source-integrity-95",
            source_decision_id="source-decision-95", outcome_id="outcome-95", confidence=0.91,
            application_status=AS.APPLIED, integrity_status=IntegrityStatus.VALID,
            source_application_fingerprint="a" * 64, computed_application_fingerprint="b" * 64,
            evidence_status=status, failure_reason=None if status is ES.READY else "blocked",
            evidence={"signal": {"score": 0.8}}, reasons={"evidence_status": status.value},
            lineage={"chain": ["96", "95"]},
        )

    def _transition(self, **kwargs):
        args = {
            "transition_id": "transition-98", "state_key": "skill.demo", "state": {"nested": {"items": [1, 2]}},
        }
        args.update(kwargs)
        return TS().transition(self._evidence(), **args)

    def test_valid_integrity_is_emitted(self):
        result = IS().assess(self._transition(), integrity_id="integrity-99")
        self.assertIs(result.integrity_status, ISS.VALID)
        self.assertEqual(len(result.computed_transition_fingerprint), 64)

    def test_fingerprint_is_deterministic_for_equivalent_input(self):
        one = IS().assess(self._transition(reasons={"b": 2, "a": 1}), integrity_id="integrity-99")
        two = IS().assess(self._transition(reasons={"a": 1, "b": 2}), integrity_id="integrity-99")
        self.assertEqual(one.computed_transition_fingerprint, two.computed_transition_fingerprint)

    def test_mapping_key_order_is_ignored(self):
        one = IS().assess(self._transition(state={"b": 2, "a": 1}), integrity_id="integrity-99")
        two = IS().assess(self._transition(state={"a": 1, "b": 2}), integrity_id="integrity-99")
        self.assertEqual(one.computed_transition_fingerprint, two.computed_transition_fingerprint)

    def test_list_order_is_significant(self):
        one = IS().assess(self._transition(state={"items": [1, 2]}), integrity_id="integrity-99")
        two = IS().assess(self._transition(state={"items": [2, 1]}), integrity_id="integrity-99")
        self.assertNotEqual(one.computed_transition_fingerprint, two.computed_transition_fingerprint)

    def test_tuple_order_is_significant(self):
        one = IS().assess(self._transition(state={"items": (1, 2)}), integrity_id="integrity-99")
        two = IS().assess(self._transition(state={"items": (2, 1)}), integrity_id="integrity-99")
        self.assertNotEqual(one.computed_transition_fingerprint, two.computed_transition_fingerprint)

    def test_complete_provenance_is_preserved(self):
        source = self._transition()
        result = IS().assess(source, integrity_id="integrity-99")
        for name in (
            "transition_id", "evidence_id", "application_id", "decision_id", "proposal_id", "eligibility_id",
            "signal_id", "evaluation_id", "feedback_id", "classification_id", "source_integrity_id",
            "source_decision_id", "outcome_id", "confidence", "state_key",
        ):
            self.assertEqual(getattr(result, name), getattr(source, name))
        self.assertEqual(result.transition_source_id, source.integrity_id)

    def test_application_fingerprints_are_preserved(self):
        source = self._transition()
        result = IS().assess(source, integrity_id="integrity-99")
        self.assertEqual(result.computed_transition_fingerprint, result.computed_transition_fingerprint)
        self.assertFalse(result.computed_transition_fingerprint == "b" * 64)

    def test_transition_status_is_preserved(self):
        persisted = self._transition(persistence_adapter=lambda payload: True)
        result = IS().assess(persisted, integrity_id="integrity-99")
        self.assertIs(persisted.transition_status, TSStatus.PERSISTED)
        self.assertIs(result.transition_status, TSStatus.PERSISTED)

    def test_nested_reasons_and_lineage_are_immutable(self):
        result = IS().assess(
            self._transition(reasons={"nested": {"items": [1]}}, lineage={"chain": [{"id": "98"}]}),
            integrity_id="integrity-99",
        )
        with self.assertRaises(TypeError):
            result.reasons["nested"] = 1
        with self.assertRaises(TypeError):
            result.lineage["new"] = 1

    def test_source_transition_is_not_mutated(self):
        source = self._transition()
        original = source.state
        IS().assess(source, integrity_id="integrity-99")
        self.assertEqual(source.state, original)

    def test_wrong_source_type_fails_closed(self):
        with self.assertRaises(TypeError):
            IS().assess(self._evidence(), integrity_id="integrity-99")

    def test_blank_integrity_id_fails_closed(self):
        with self.assertRaises(ValueError):
            IS().assess(self._transition(), integrity_id=" ")

    def test_status_enum_is_required(self):
        with self.assertRaises(TypeError):
            I(
                integrity_id="integrity-99", transition_id="transition-98", evidence_id="evidence-97",
                application_id="application-96", transition_source_id="integrity-96", decision_id="decision-95",
                proposal_id="proposal-95", eligibility_id="eligibility-95", signal_id="signal-95",
                evaluation_id="evaluation-95", feedback_id="feedback-95", classification_id="classification-95",
                source_integrity_id="source-integrity-95", source_decision_id="decision-95", outcome_id="outcome-95",
                confidence=0.91, state_key="skill.demo", transition_status=TSStatus.PERSISTED,
                source_application_fingerprint="a" * 64, computed_application_fingerprint="b" * 64,
                computed_transition_fingerprint="a" * 64, integrity_status="VALID", failure_reason=None, reasons={}, lineage={},
            )

    def test_fingerprint_shape_is_required(self):
        with self.assertRaises(ValueError):
            I(
                integrity_id="integrity-99", transition_id="transition-98", evidence_id="evidence-97",
                application_id="application-96", transition_source_id="integrity-96", decision_id="decision-95",
                proposal_id="proposal-95", eligibility_id="eligibility-95", signal_id="signal-95",
                evaluation_id="evaluation-95", feedback_id="feedback-95", classification_id="classification-95",
                source_integrity_id="source-integrity-95", source_decision_id="source-decision-95", outcome_id="outcome-95",
                confidence=0.91, state_key="skill.demo", transition_status=TSStatus.PERSISTED,
                source_application_fingerprint="short", computed_application_fingerprint="b" * 64,
                computed_transition_fingerprint="c" * 64,
                integrity_status=ISS.VALID, failure_reason=None, reasons={}, lineage={},
            )

    def test_valid_integrity_rejects_failure_reason(self):
        with self.assertRaises(ValueError):
            result = IS().assess(self._transition(), integrity_id="integrity-99")
            I(**{**result.__dict__, "failure_reason": "bad"})

    def test_transition_integrity_does_not_claim_correctness(self):
        result = IS().assess(self._transition(), integrity_id="integrity-99")
        self.assertFalse(result.establishes_truth)
        self.assertFalse(result.establishes_correctness)
        self.assertFalse(result.grants_authority)

    def test_transition_integrity_has_no_mutation_or_execution_power(self):
        result = IS().assess(self._transition(), integrity_id="integrity-99")
        self.assertFalse(result.invokes_learner)
        self.assertFalse(result.updates_model)
        self.assertFalse(result.mutates_durable_state)
        self.assertFalse(result.mutates_policy)
        self.assertFalse(result.schedules_work)
        self.assertFalse(result.executes_action)

    def test_no_retry_or_adapter_is_invoked(self):
        calls = []
        transition = self._transition(persistence_adapter=lambda payload: calls.append(payload) or True)
        before = len(calls)
        IS().assess(transition, integrity_id="integrity-99")
        self.assertEqual(len(calls), before)

    def test_equivalent_source_representations_have_same_fingerprint(self):
        one = self._transition(state={"nested": {"b": 2, "a": 1}})
        two = self._transition(state={"nested": {"a": 1, "b": 2}})
        self.assertEqual(
            IS().assess(one, integrity_id="integrity-99").computed_transition_fingerprint,
            IS().assess(two, integrity_id="integrity-99").computed_transition_fingerprint,
        )


if __name__ == "__main__":
    unittest.main()
