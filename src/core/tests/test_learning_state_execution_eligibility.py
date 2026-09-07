import unittest
from types import MappingProxyType

from src.core.learning_state_downstream_semantic_handling import (
    LearningStateDownstreamSemanticHandling,
    LearningStateDownstreamSemanticHandlingStatus,
)
from src.core.learning_state_execution_eligibility import (
    LearningStateExecutionEligibilityService,
    LearningStateExecutionEligibilityStatus,
)


class M23_119ExecutionEligibilityTests(unittest.TestCase):
    def _handling(self, *, status=LearningStateDownstreamSemanticHandlingStatus.READY):
        return LearningStateDownstreamSemanticHandling(
            handling_id="handling-118",
            consumption_id="consumption-117",
            receipt_id="receipt-116",
            handoff_id="handoff-115",
            integrity_id="integrity-114",
            validation_id="validation-113",
            use_id="use-112",
            request_id="semantic-use-111",
            interpretation_id="interpretation-108",
            source_request_id="request-107",
            read_validation_id="read-validation-106",
            read_id="read-105",
            consumption_request_id="consumption-104",
            source_validation_id="source-validation-103",
            source_integrity_id="source-integrity-102",
            transition_id="transition-98",
            evidence_id="evidence-97",
            application_id="application-96",
            state_key="demo.state",
            transition_fingerprint="a" * 64,
            source_application_fingerprint="b" * 64,
            computed_application_fingerprint="c" * 64,
            confidence=0.91,
            consumer_id="consumer-A",
            use_purpose="downstream-semantic-use",
            downstream_recipient_id="receiver-X",
            downstream_handler_id="handler-X",
            handling_purpose="route-for-processing",
            consumption_status=__import__(
                "src.core.learning_state_semantic_use_consumption",
                fromlist=["LearningStateSemanticUseConsumptionStatus"],
            ).LearningStateSemanticUseConsumptionStatus.CONSUMED,
            handling_status=status,
            result={"decision": "bounded", "nested": {"score": 7}},
            reasons={"source": "m23.118"},
            lineage={"parent": "handling-118"},
        )

    def test_ready_handling_becomes_execution_eligible(self):
        artifact = LearningStateExecutionEligibilityService().assess(
            self._handling(),
            eligibility_id="eligibility-119",
            execution_target_id="target-X",
            execution_purpose="process-semantic-result",
        )
        self.assertEqual(artifact.eligibility_status, LearningStateExecutionEligibilityStatus.ELIGIBLE)
        self.assertTrue(artifact.is_eligible)

    def test_exact_handling_type_is_required(self):
        with self.assertRaises(TypeError):
            LearningStateExecutionEligibilityService().assess(
                object(), eligibility_id="eligibility-119", execution_target_id="target-X", execution_purpose="purpose"
            )

    def test_handling_must_be_ready(self):
        with self.assertRaises(ValueError):
            LearningStateExecutionEligibilityService().assess(
                self._handling(status=LearningStateDownstreamSemanticHandlingStatus.REJECTED),
                eligibility_id="eligibility-119", execution_target_id="target-X", execution_purpose="purpose"
            )

    def test_eligibility_id_must_be_non_empty(self):
        with self.assertRaises(ValueError):
            LearningStateExecutionEligibilityService().assess(
                self._handling(), eligibility_id=" ", execution_target_id="target-X", execution_purpose="purpose"
            )

    def test_execution_target_must_be_non_empty(self):
        with self.assertRaises(ValueError):
            LearningStateExecutionEligibilityService().assess(
                self._handling(), eligibility_id="eligibility-119", execution_target_id="", execution_purpose="purpose"
            )

    def test_execution_purpose_must_be_non_empty(self):
        with self.assertRaises(ValueError):
            LearningStateExecutionEligibilityService().assess(
                self._handling(), eligibility_id="eligibility-119", execution_target_id="target-X", execution_purpose=""
            )

    def test_execution_target_and_purpose_are_explicit(self):
        artifact = LearningStateExecutionEligibilityService().assess(
            self._handling(),
            eligibility_id="eligibility-119",
            execution_target_id="target-X",
            execution_purpose="process-semantic-result",
        )
        self.assertEqual(artifact.execution_target_id, "target-X")
        self.assertEqual(artifact.execution_purpose, "process-semantic-result")

    def test_semantic_result_is_preserved(self):
        artifact = LearningStateExecutionEligibilityService().assess(
            self._handling(),
            eligibility_id="eligibility-119",
            execution_target_id="target-X",
            execution_purpose="purpose",
        )
        self.assertEqual(artifact.result["decision"], "bounded")
        self.assertEqual(artifact.result["nested"]["score"], 7)

    def test_result_is_recursively_frozen(self):
        artifact = LearningStateExecutionEligibilityService().assess(
            self._handling(), eligibility_id="eligibility-119", execution_target_id="target-X", execution_purpose="purpose"
        )
        self.assertIsInstance(artifact.result, MappingProxyType)
        self.assertIsInstance(artifact.result["nested"], MappingProxyType)
        with self.assertRaises(TypeError):
            artifact.result["decision"] = "changed"

    def test_source_handling_is_not_mutated(self):
        source = self._handling()
        original = source.result
        artifact = LearningStateExecutionEligibilityService().assess(
            source, eligibility_id="eligibility-119", execution_target_id="target-X", execution_purpose="purpose"
        )
        self.assertEqual(source.result, original)
        self.assertEqual(artifact.handling_id, source.handling_id)

    def test_provenance_and_fingerprints_are_preserved(self):
        source = self._handling()
        artifact = LearningStateExecutionEligibilityService().assess(
            source, eligibility_id="eligibility-119", execution_target_id="target-X", execution_purpose="purpose"
        )
        for field in (
            "handling_id", "consumption_id", "receipt_id", "handoff_id", "integrity_id", "validation_id",
            "use_id", "request_id", "interpretation_id", "transition_id", "evidence_id", "application_id",
            "state_key", "transition_fingerprint", "source_application_fingerprint",
            "computed_application_fingerprint", "consumer_id", "use_purpose", "downstream_recipient_id",
            "downstream_handler_id", "handling_purpose",
        ):
            self.assertEqual(getattr(artifact, field), getattr(source, field))

    def test_deterministic_for_same_inputs(self):
        service = LearningStateExecutionEligibilityService()
        source = self._handling()
        left = service.assess(
            source, eligibility_id="eligibility-119", execution_target_id="target-X", execution_purpose="purpose"
        )
        right = service.assess(
            source, eligibility_id="eligibility-119", execution_target_id="target-X", execution_purpose="purpose"
        )
        self.assertEqual(left, right)

    def test_custom_reasons_and_lineage_are_frozen(self):
        artifact = LearningStateExecutionEligibilityService().assess(
            self._handling(),
            eligibility_id="eligibility-119",
            execution_target_id="target-X",
            execution_purpose="purpose",
            reasons={"reason": {"nested": True}},
            lineage={"lineage": ["a", "b"]},
        )
        self.assertIsInstance(artifact.reasons, MappingProxyType)
        self.assertIsInstance(artifact.reasons["reason"], MappingProxyType)
        self.assertIsInstance(artifact.lineage, MappingProxyType)
        self.assertEqual(artifact.lineage["lineage"], ("a", "b"))

    def test_no_handler_or_worker_is_invoked(self):
        artifact = LearningStateExecutionEligibilityService().assess(
            self._handling(), eligibility_id="eligibility-119", execution_target_id="target-X", execution_purpose="purpose"
        )
        self.assertFalse(artifact.invokes_handler)
        self.assertFalse(artifact.invokes_worker)

    def test_eligibility_is_not_execution_authorization_or_permission(self):
        artifact = LearningStateExecutionEligibilityService().assess(
            self._handling(), eligibility_id="eligibility-119", execution_target_id="target-X", execution_purpose="purpose"
        )
        self.assertTrue(artifact.is_eligible)
        self.assertFalse(artifact.executes_action)
        self.assertFalse(artifact.authorizes_execution)
        self.assertFalse(artifact.grants_permission)

    def test_eligibility_has_no_planning_or_scheduling_power(self):
        artifact = LearningStateExecutionEligibilityService().assess(
            self._handling(), eligibility_id="eligibility-119", execution_target_id="target-X", execution_purpose="purpose"
        )
        self.assertFalse(artifact.plans_work)
        self.assertFalse(artifact.schedules_work)

    def test_eligibility_has_no_semantic_transformation_or_judgment(self):
        artifact = LearningStateExecutionEligibilityService().assess(
            self._handling(), eligibility_id="eligibility-119", execution_target_id="target-X", execution_purpose="purpose"
        )
        self.assertFalse(artifact.transforms_semantic_result)
        self.assertFalse(artifact.interprets_semantic_result)
        self.assertFalse(artifact.establishes_truth)
        self.assertFalse(artifact.establishes_correctness)
        self.assertFalse(artifact.establishes_certainty)
        self.assertFalse(artifact.establishes_usefulness)

    def test_eligibility_has_no_learning_memory_or_policy_power(self):
        artifact = LearningStateExecutionEligibilityService().assess(
            self._handling(), eligibility_id="eligibility-119", execution_target_id="target-X", execution_purpose="purpose"
        )
        self.assertFalse(artifact.invokes_learner)
        self.assertFalse(artifact.updates_model)
        self.assertFalse(artifact.mutates_memory)
        self.assertFalse(artifact.mutates_policy)

    def test_artifact_is_immutable(self):
        artifact = LearningStateExecutionEligibilityService().assess(
            self._handling(), eligibility_id="eligibility-119", execution_target_id="target-X", execution_purpose="purpose"
        )
        with self.assertRaises(AttributeError):
            artifact.execution_target_id = "target-Y"

    def test_reasons_and_lineage_are_present(self):
        artifact = LearningStateExecutionEligibilityService().assess(
            self._handling(), eligibility_id="eligibility-119", execution_target_id="target-X", execution_purpose="purpose"
        )
        self.assertEqual(artifact.reasons["eligibility_status"], "ELIGIBLE")
        self.assertEqual(artifact.lineage["handling_id"], "handling-118")


if __name__ == "__main__":
    unittest.main()
