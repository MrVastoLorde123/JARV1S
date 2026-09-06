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


class M23_98LearningStateTransitionV4Tests(unittest.TestCase):
    def _evidence(self, status=ES.READY):
        from src.core.environment_world_model_rollback_repair_retry_adaptation_execution_learning_adaptation_application_learning_adaptation_application_learning_adaptation_application_integrity_v4 import (
            EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationLearningAdaptationApplicationIntegrityV4Status as IntegrityStatus,
        )

        return E(
            evidence_id="evidence-97",
            application_id="application-96",
            integrity_id="integrity-96",
            decision_id="decision-95",
            proposal_id="proposal-95",
            source_proposal_id="proposal-94",
            eligibility_id="eligibility-95",
            signal_id="signal-95",
            evaluation_id="evaluation-95",
            feedback_id="feedback-95",
            classification_id="classification-95",
            source_integrity_id="source-integrity-95",
            source_decision_id="source-decision-95",
            outcome_id="outcome-95",
            confidence=0.91,
            application_status=AS.APPLIED,
            integrity_status=IntegrityStatus.VALID,
            source_application_fingerprint="a" * 64,
            computed_application_fingerprint="b" * 64,
            evidence_status=status,
            failure_reason=None if status is ES.READY else "blocked",
            evidence={"signal": {"score": 0.8}},
            reasons={"evidence_status": status.value},
            lineage={"chain": ["96", "95"]},
        )

    def test_persists_only_with_true_adapter_result(self):
        calls = []

        def adapter(payload):
            calls.append(payload)
            return True

        result = TS().transition(self._evidence(), transition_id="transition-98", state_key="skill.demo", state={"value": 7}, persistence_adapter=adapter)
        self.assertIs(result.transition_status, TSStatus.PERSISTED)
        self.assertEqual(len(calls), 1)

    def test_false_adapter_result_is_not_persisted(self):
        result = TS().transition(self._evidence(), transition_id="transition-98", state_key="skill.demo", state={"value": 7}, persistence_adapter=lambda payload: False)
        self.assertIs(result.transition_status, TSStatus.NOT_PERSISTED)

    def test_absent_adapter_fails_closed(self):
        result = TS().transition(self._evidence(), transition_id="transition-98", state_key="skill.demo", state={"value": 7})
        self.assertIs(result.transition_status, TSStatus.NOT_PERSISTED)

    def test_adapter_exception_fails_closed_without_retry(self):
        calls = []

        def adapter(payload):
            calls.append(payload)
            raise RuntimeError("storage failed")

        result = TS().transition(self._evidence(), transition_id="transition-98", state_key="skill.demo", state={"value": 7}, persistence_adapter=adapter)
        self.assertIs(result.transition_status, TSStatus.NOT_PERSISTED)
        self.assertEqual(len(calls), 1)

    def test_malformed_adapter_result_fails_closed(self):
        result = TS().transition(self._evidence(), transition_id="transition-98", state_key="skill.demo", state={"value": 7}, persistence_adapter=lambda payload: "yes")
        self.assertIs(result.transition_status, TSStatus.NOT_PERSISTED)

    def test_adapter_receives_only_bounded_transition_input(self):
        captured = {}

        def adapter(payload):
            captured.update(payload)
            return True

        TS().transition(self._evidence(), transition_id="transition-98", state_key="skill.demo", state={"value": 7}, persistence_adapter=adapter)
        self.assertEqual(set(captured), {"transition_id", "evidence_id", "application_id", "state_key", "state"})
        self.assertNotIn("evidence", captured)
        self.assertNotIn("reasons", captured)
        self.assertNotIn("lineage", captured)

    def test_adapter_state_payload_is_immutable(self):
        captured = []

        def adapter(payload):
            captured.append(payload)
            return True

        TS().transition(self._evidence(), transition_id="transition-98", state_key="skill.demo", state={"nested": {"items": [1, 2]}}, persistence_adapter=adapter)
        with self.assertRaises(TypeError):
            captured[0]["state"]["new"] = 1
        with self.assertRaises(TypeError):
            captured[0]["state"]["nested"]["items"] = 3

    def test_complete_upstream_provenance_and_fingerprints_are_preserved(self):
        source = self._evidence()
        result = TS().transition(source, transition_id="transition-98", state_key="skill.demo", state={"value": 7})
        self.assertEqual(result.evidence_id, source.evidence_id)
        self.assertEqual(result.application_id, source.application_id)
        self.assertEqual(result.integrity_id, source.integrity_id)
        self.assertEqual(result.decision_id, source.decision_id)
        self.assertEqual(result.proposal_id, source.proposal_id)
        self.assertEqual(result.eligibility_id, source.eligibility_id)
        self.assertEqual(result.signal_id, source.signal_id)
        self.assertEqual(result.evaluation_id, source.evaluation_id)
        self.assertEqual(result.feedback_id, source.feedback_id)
        self.assertEqual(result.classification_id, source.classification_id)
        self.assertEqual(result.source_integrity_id, source.source_integrity_id)
        self.assertEqual(result.source_decision_id, source.source_decision_id)
        self.assertEqual(result.outcome_id, source.outcome_id)
        self.assertEqual(result.confidence, source.confidence)
        self.assertEqual(result.source_application_fingerprint, source.source_application_fingerprint)
        self.assertEqual(result.computed_application_fingerprint, source.computed_application_fingerprint)

    def test_transition_identity_and_state_key_are_required(self):
        service = TS()
        with self.assertRaises(ValueError):
            service.transition(self._evidence(), transition_id=" ", state_key="skill.demo", state={"value": 7})
        with self.assertRaises(ValueError):
            service.transition(self._evidence(), transition_id="transition-98", state_key=" ", state={"value": 7})

    def test_state_must_be_a_mapping(self):
        with self.assertRaises(TypeError):
            TS().transition(self._evidence(), transition_id="transition-98", state_key="skill.demo", state=[1, 2])

    def test_nested_state_reasons_and_lineage_are_immutable(self):
        result = TS().transition(
            self._evidence(),
            transition_id="transition-98",
            state_key="skill.demo",
            state={"nested": {"items": [1, 2]}},
            reasons={"why": {"items": ["x"]}},
            lineage={"chain": [{"id": "97"}]},
        )
        with self.assertRaises(TypeError):
            result.state["new"] = 1
        with self.assertRaises(TypeError):
            result.state["nested"]["items"] = 3
        with self.assertRaises(TypeError):
            result.reasons["why"] = 1
        with self.assertRaises(TypeError):
            result.lineage["new"] = 1

    def test_source_evidence_is_not_mutated(self):
        source = self._evidence()
        original = source.evidence
        TS().transition(source, transition_id="transition-98", state_key="skill.demo", state={"value": 7}, persistence_adapter=lambda payload: True)
        self.assertEqual(source.evidence, original)

    def test_non_ready_evidence_is_blocked(self):
        source = self._evidence(status=ES.BLOCKED)
        with self.assertRaises(ValueError):
            TS().transition(source, transition_id="transition-98", state_key="skill.demo", state={"value": 7})

    def test_authority_and_mutation_walls_are_closed(self):
        result = TS().transition(self._evidence(), transition_id="transition-98", state_key="skill.demo", state={"value": 7})
        self.assertFalse(result.establishes_truth)
        self.assertFalse(result.grants_authority)
        self.assertFalse(result.invokes_learner)
        self.assertFalse(result.updates_model)
        self.assertFalse(result.mutates_policy)
        self.assertFalse(result.schedules_work)
        self.assertFalse(result.executes_action)

    def test_no_implicit_learner_or_policy_objects_are_created(self):
        result = TS().transition(self._evidence(), transition_id="transition-98", state_key="skill.demo", state={"value": 7})
        self.assertFalse(hasattr(result, "learner"))
        self.assertFalse(hasattr(result, "policy"))
        self.assertFalse(hasattr(result, "authorization"))

    def test_transition_artifact_is_immutable(self):
        result = TS().transition(self._evidence(), transition_id="transition-98", state_key="skill.demo", state={"value": 7})
        with self.assertRaises(Exception):
            result.transition_id = "changed"

if __name__ == "__main__":
    unittest.main()
