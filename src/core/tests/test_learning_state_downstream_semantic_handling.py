import unittest
from types import MappingProxyType

from src.core.learning_state_semantic_use_consumption import (
    LearningStateSemanticUseConsumption,
    LearningStateSemanticUseConsumptionStatus,
)
from src.core.learning_state_downstream_semantic_handling import (
    LearningStateDownstreamSemanticHandlingService,
    LearningStateDownstreamSemanticHandlingStatus,
)


class M23_118DownstreamSemanticHandlingTests(unittest.TestCase):
    def _consumption(self, *, status=LearningStateSemanticUseConsumptionStatus.CONSUMED):
        return LearningStateSemanticUseConsumption(
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
            handoff_status=__import__(
                "src.core.learning_state_semantic_use_handoff",
                fromlist=["LearningStateSemanticUseHandoffStatus"],
            ).LearningStateSemanticUseHandoffStatus.READY,
            receipt_status=__import__(
                "src.core.learning_state_semantic_use_receipt",
                fromlist=["LearningStateSemanticUseReceiptStatus"],
            ).LearningStateSemanticUseReceiptStatus.RECEIVED,
            consumption_status=status,
            result={"decision": "bounded", "nested": {"score": 7}},
            reasons={"source": "m23.117"},
            lineage={"parent": "consumption-117"},
        )

    def test_consumed_artifact_is_bound_for_downstream_handling(self):
        artifact = LearningStateDownstreamSemanticHandlingService().handle(
            self._consumption(),
            handling_id="handling-118",
            downstream_handler_id="handler-X",
            handling_purpose="route-for-processing",
        )
        self.assertEqual(artifact.handling_status, LearningStateDownstreamSemanticHandlingStatus.READY)
        self.assertTrue(artifact.is_ready)

    def test_exact_consumption_type_is_required(self):
        with self.assertRaises(TypeError):
            LearningStateDownstreamSemanticHandlingService().handle(
                object(), handling_id="handling-118", downstream_handler_id="handler-X", handling_purpose="purpose"
            )

    def test_consumption_must_be_consumed(self):
        with self.assertRaises(ValueError):
            LearningStateDownstreamSemanticHandlingService().handle(
                self._consumption(status=LearningStateSemanticUseConsumptionStatus.REJECTED),
                handling_id="handling-118", downstream_handler_id="handler-X", handling_purpose="purpose"
            )

    def test_handling_id_must_be_non_empty(self):
        with self.assertRaises(ValueError):
            LearningStateDownstreamSemanticHandlingService().handle(
                self._consumption(), handling_id=" ", downstream_handler_id="handler-X", handling_purpose="purpose"
            )

    def test_handler_id_must_be_non_empty(self):
        with self.assertRaises(ValueError):
            LearningStateDownstreamSemanticHandlingService().handle(
                self._consumption(), handling_id="handling-118", downstream_handler_id="", handling_purpose="purpose"
            )

    def test_handling_purpose_must_be_non_empty(self):
        with self.assertRaises(ValueError):
            LearningStateDownstreamSemanticHandlingService().handle(
                self._consumption(), handling_id="handling-118", downstream_handler_id="handler-X", handling_purpose=""
            )

    def test_semantic_result_is_preserved(self):
        artifact = LearningStateDownstreamSemanticHandlingService().handle(
            self._consumption(),
            handling_id="handling-118",
            downstream_handler_id="handler-X",
            handling_purpose="purpose",
        )
        self.assertEqual(artifact.result["decision"], "bounded")
        self.assertEqual(artifact.result["nested"]["score"], 7)

    def test_result_is_recursively_frozen(self):
        artifact = LearningStateDownstreamSemanticHandlingService().handle(
            self._consumption(), handling_id="handling-118", downstream_handler_id="handler-X", handling_purpose="purpose"
        )
        self.assertIsInstance(artifact.result, MappingProxyType)
        self.assertIsInstance(artifact.result["nested"], MappingProxyType)
        with self.assertRaises(TypeError):
            artifact.result["decision"] = "changed"

    def test_source_consumption_is_not_mutated(self):
        source = self._consumption()
        original = source.result
        artifact = LearningStateDownstreamSemanticHandlingService().handle(
            source, handling_id="handling-118", downstream_handler_id="handler-X", handling_purpose="purpose"
        )
        self.assertEqual(source.result, original)
        self.assertEqual(artifact.consumption_id, source.consumption_id)

    def test_provenance_and_fingerprints_are_preserved(self):
        source = self._consumption()
        artifact = LearningStateDownstreamSemanticHandlingService().handle(
            source, handling_id="handling-118", downstream_handler_id="handler-X", handling_purpose="purpose"
        )
        for field in (
            "consumption_id", "receipt_id", "handoff_id", "integrity_id", "validation_id", "use_id",
            "request_id", "interpretation_id", "transition_id", "evidence_id", "application_id",
            "state_key", "transition_fingerprint", "source_application_fingerprint",
            "computed_application_fingerprint", "consumer_id", "use_purpose", "downstream_recipient_id",
        ):
            self.assertEqual(getattr(artifact, field), getattr(source, field))

    def test_handler_identity_and_purpose_are_explicit(self):
        artifact = LearningStateDownstreamSemanticHandlingService().handle(
            self._consumption(),
            handling_id="handling-118",
            downstream_handler_id="handler-X",
            handling_purpose="route-for-processing",
        )
        self.assertEqual(artifact.downstream_handler_id, "handler-X")
        self.assertEqual(artifact.handling_purpose, "route-for-processing")

    def test_deterministic_for_same_inputs(self):
        service = LearningStateDownstreamSemanticHandlingService()
        source = self._consumption()
        left = service.handle(
            source, handling_id="handling-118", downstream_handler_id="handler-X", handling_purpose="purpose"
        )
        right = service.handle(
            source, handling_id="handling-118", downstream_handler_id="handler-X", handling_purpose="purpose"
        )
        self.assertEqual(left, right)

    def test_custom_reasons_and_lineage_are_frozen(self):
        artifact = LearningStateDownstreamSemanticHandlingService().handle(
            self._consumption(),
            handling_id="handling-118",
            downstream_handler_id="handler-X",
            handling_purpose="purpose",
            reasons={"reason": {"nested": True}},
            lineage={"lineage": ["a", "b"]},
        )
        self.assertIsInstance(artifact.reasons, MappingProxyType)
        self.assertIsInstance(artifact.reasons["reason"], MappingProxyType)
        self.assertIsInstance(artifact.lineage, MappingProxyType)
        self.assertEqual(artifact.lineage["lineage"], ("a", "b"))

    def test_handler_is_never_invoked(self):
        invoked = []
        service = LearningStateDownstreamSemanticHandlingService()
        artifact = service.handle(
            self._consumption(), handling_id="handling-118", downstream_handler_id="handler-X", handling_purpose="purpose"
        )
        invoked.append(artifact.invokes_handler)
        self.assertEqual(invoked, [False])

    def test_handling_does_not_transform_or_interpret_result(self):
        artifact = LearningStateDownstreamSemanticHandlingService().handle(
            self._consumption(), handling_id="handling-118", downstream_handler_id="handler-X", handling_purpose="purpose"
        )
        self.assertFalse(artifact.transforms_semantic_result)
        self.assertFalse(artifact.interprets_semantic_result)

    def test_handling_does_not_establish_semantic_judgments(self):
        artifact = LearningStateDownstreamSemanticHandlingService().handle(
            self._consumption(), handling_id="handling-118", downstream_handler_id="handler-X", handling_purpose="purpose"
        )
        self.assertFalse(artifact.establishes_truth)
        self.assertFalse(artifact.establishes_correctness)
        self.assertFalse(artifact.establishes_certainty)
        self.assertFalse(artifact.establishes_usefulness)

    def test_handling_has_no_learning_or_model_power(self):
        artifact = LearningStateDownstreamSemanticHandlingService().handle(
            self._consumption(), handling_id="handling-118", downstream_handler_id="handler-X", handling_purpose="purpose"
        )
        self.assertFalse(artifact.invokes_learner)
        self.assertFalse(artifact.updates_model)

    def test_handling_has_no_memory_policy_or_authority_power(self):
        artifact = LearningStateDownstreamSemanticHandlingService().handle(
            self._consumption(), handling_id="handling-118", downstream_handler_id="handler-X", handling_purpose="purpose"
        )
        self.assertFalse(artifact.mutates_memory)
        self.assertFalse(artifact.mutates_policy)
        self.assertFalse(artifact.grants_authority)

    def test_handling_has_no_planning_scheduling_or_execution_power(self):
        artifact = LearningStateDownstreamSemanticHandlingService().handle(
            self._consumption(), handling_id="handling-118", downstream_handler_id="handler-X", handling_purpose="purpose"
        )
        self.assertFalse(artifact.schedules_work)
        self.assertFalse(artifact.executes_action)

    def test_handling_is_not_authorization_or_permission(self):
        artifact = LearningStateDownstreamSemanticHandlingService().handle(
            self._consumption(), handling_id="handling-118", downstream_handler_id="handler-X", handling_purpose="purpose"
        )
        self.assertTrue(artifact.is_ready)
        self.assertFalse(artifact.grants_authority)

    def test_artifact_is_immutable(self):
        artifact = LearningStateDownstreamSemanticHandlingService().handle(
            self._consumption(), handling_id="handling-118", downstream_handler_id="handler-X", handling_purpose="purpose"
        )
        with self.assertRaises(AttributeError):
            artifact.downstream_handler_id = "handler-Y"


if __name__ == "__main__":
    unittest.main()
