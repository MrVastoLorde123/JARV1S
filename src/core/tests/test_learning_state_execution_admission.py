import unittest
from types import MappingProxyType

from src.core.learning_state_execution_eligibility import (
    LearningStateExecutionEligibility,
    LearningStateExecutionEligibilityStatus,
)
from src.core.learning_state_execution_admission import (
    LearningStateExecutionAdmissionService,
    LearningStateExecutionAdmissionStatus,
)


class M23_120ExecutionAdmissionTests(unittest.TestCase):
    def _eligibility(self, *, status=LearningStateExecutionEligibilityStatus.ELIGIBLE):
        return LearningStateExecutionEligibility(
            eligibility_id="eligibility-119",
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
            execution_target_id="executor-X",
            execution_purpose="perform-bounded-work",
            handling_status=__import__(
                "src.core.learning_state_downstream_semantic_handling",
                fromlist=["LearningStateDownstreamSemanticHandlingStatus"],
            ).LearningStateDownstreamSemanticHandlingStatus.READY,
            eligibility_status=status,
            result={"decision": "bounded", "nested": {"score": 7}},
            reasons={"source": "m23.119"},
            lineage={"parent": "eligibility-119"},
        )

    def test_eligible_artifact_is_authorized_when_granted(self):
        artifact = LearningStateExecutionAdmissionService().admit(
            self._eligibility(),
            admission_id="admission-120",
            authorization_granted=True,
            execution_target_id="executor-X",
            execution_purpose="perform-bounded-work",
        )
        self.assertEqual(artifact.admission_status, LearningStateExecutionAdmissionStatus.AUTHORIZED)
        self.assertTrue(artifact.is_authorized)
        self.assertTrue(artifact.authorizes_execution)

    def test_denied_authorization_is_rejected(self):
        artifact = LearningStateExecutionAdmissionService().admit(
            self._eligibility(),
            admission_id="admission-120",
            authorization_granted=False,
            execution_target_id="executor-X",
            execution_purpose="perform-bounded-work",
        )
        self.assertEqual(artifact.admission_status, LearningStateExecutionAdmissionStatus.REJECTED)
        self.assertFalse(artifact.is_authorized)

    def test_exact_eligibility_type_is_required(self):
        with self.assertRaises(TypeError):
            LearningStateExecutionAdmissionService().admit(
                object(), admission_id="admission-120", authorization_granted=True,
                execution_target_id="executor-X", execution_purpose="purpose"
            )

    def test_eligibility_must_be_eligible(self):
        with self.assertRaises(ValueError):
            LearningStateExecutionAdmissionService().admit(
                self._eligibility(status=LearningStateExecutionEligibilityStatus.REJECTED),
                admission_id="admission-120", authorization_granted=True,
                execution_target_id="executor-X", execution_purpose="purpose"
            )

    def test_admission_id_must_be_non_empty(self):
        with self.assertRaises(ValueError):
            LearningStateExecutionAdmissionService().admit(
                self._eligibility(), admission_id=" ", authorization_granted=True,
                execution_target_id="executor-X", execution_purpose="purpose"
            )

    def test_authorization_flag_must_be_boolean(self):
        with self.assertRaises(TypeError):
            LearningStateExecutionAdmissionService().admit(
                self._eligibility(), admission_id="admission-120", authorization_granted="yes",
                execution_target_id="executor-X", execution_purpose="purpose"
            )

    def test_execution_target_must_match_eligibility(self):
        with self.assertRaises(ValueError):
            LearningStateExecutionAdmissionService().admit(
                self._eligibility(), admission_id="admission-120", authorization_granted=True,
                execution_target_id="executor-Y", execution_purpose="perform-bounded-work"
            )

    def test_execution_purpose_must_match_eligibility(self):
        with self.assertRaises(ValueError):
            LearningStateExecutionAdmissionService().admit(
                self._eligibility(), admission_id="admission-120", authorization_granted=True,
                execution_target_id="executor-X", execution_purpose="other-work"
            )

    def test_result_is_preserved_and_recursively_frozen(self):
        artifact = LearningStateExecutionAdmissionService().admit(
            self._eligibility(), admission_id="admission-120", authorization_granted=True,
            execution_target_id="executor-X", execution_purpose="perform-bounded-work"
        )
        self.assertEqual(artifact.result["decision"], "bounded")
        self.assertIsInstance(artifact.result, MappingProxyType)
        self.assertIsInstance(artifact.result["nested"], MappingProxyType)
        with self.assertRaises(TypeError):
            artifact.result["decision"] = "changed"

    def test_reasons_and_lineage_are_frozen(self):
        artifact = LearningStateExecutionAdmissionService().admit(
            self._eligibility(), admission_id="admission-120", authorization_granted=True,
            execution_target_id="executor-X", execution_purpose="perform-bounded-work",
            reasons={"reason": {"nested": True}}, lineage={"chain": ["eligibility-119"]}
        )
        self.assertIsInstance(artifact.reasons, MappingProxyType)
        self.assertIsInstance(artifact.reasons["reason"], MappingProxyType)
        self.assertIsInstance(artifact.lineage, MappingProxyType)

    def test_provenance_and_fingerprints_are_preserved(self):
        source = self._eligibility()
        artifact = LearningStateExecutionAdmissionService().admit(
            source, admission_id="admission-120", authorization_granted=True,
            execution_target_id="executor-X", execution_purpose="perform-bounded-work"
        )
        for field in (
            "eligibility_id", "handling_id", "consumption_id", "receipt_id", "handoff_id", "integrity_id",
            "validation_id", "use_id", "request_id", "interpretation_id", "transition_id", "evidence_id",
            "application_id", "state_key", "transition_fingerprint", "source_application_fingerprint",
            "computed_application_fingerprint", "consumer_id", "use_purpose", "downstream_recipient_id",
            "downstream_handler_id", "handling_purpose", "execution_target_id", "execution_purpose",
        ):
            self.assertEqual(getattr(artifact, field), getattr(source, field))

    def test_source_eligibility_is_not_mutated(self):
        source = self._eligibility()
        before = source.result
        LearningStateExecutionAdmissionService().admit(
            source, admission_id="admission-120", authorization_granted=True,
            execution_target_id="executor-X", execution_purpose="perform-bounded-work"
        )
        self.assertEqual(source.result, before)

    def test_deterministic_for_same_inputs(self):
        service = LearningStateExecutionAdmissionService()
        source = self._eligibility()
        left = service.admit(source, admission_id="admission-120", authorization_granted=True,
                            execution_target_id="executor-X", execution_purpose="perform-bounded-work")
        right = service.admit(source, admission_id="admission-120", authorization_granted=True,
                             execution_target_id="executor-X", execution_purpose="perform-bounded-work")
        self.assertEqual(left, right)

    def test_admission_does_not_invoke_executor_handler_or_worker(self):
        artifact = LearningStateExecutionAdmissionService().admit(
            self._eligibility(), admission_id="admission-120", authorization_granted=True,
            execution_target_id="executor-X", execution_purpose="perform-bounded-work"
        )
        self.assertFalse(artifact.invokes_executor)
        self.assertFalse(artifact.invokes_handler)
        self.assertFalse(artifact.invokes_worker)
        self.assertFalse(artifact.executes_action)

    def test_admission_has_no_planning_or_scheduling_power(self):
        artifact = LearningStateExecutionAdmissionService().admit(
            self._eligibility(), admission_id="admission-120", authorization_granted=True,
            execution_target_id="executor-X", execution_purpose="perform-bounded-work"
        )
        self.assertFalse(artifact.plans_work)
        self.assertFalse(artifact.schedules_work)

    def test_admission_has_no_semantic_or_learning_power(self):
        artifact = LearningStateExecutionAdmissionService().admit(
            self._eligibility(), admission_id="admission-120", authorization_granted=True,
            execution_target_id="executor-X", execution_purpose="perform-bounded-work"
        )
        self.assertFalse(artifact.transforms_semantic_result)
        self.assertFalse(artifact.interprets_semantic_result)
        self.assertFalse(artifact.establishes_truth)
        self.assertFalse(artifact.establishes_correctness)
        self.assertFalse(artifact.establishes_certainty)
        self.assertFalse(artifact.invokes_learner)
        self.assertFalse(artifact.updates_model)
        self.assertFalse(artifact.mutates_memory)
        self.assertFalse(artifact.mutates_policy)

    def test_artifact_is_immutable(self):
        artifact = LearningStateExecutionAdmissionService().admit(
            self._eligibility(), admission_id="admission-120", authorization_granted=True,
            execution_target_id="executor-X", execution_purpose="perform-bounded-work"
        )
        with self.assertRaises(AttributeError):
            artifact.admission_status = LearningStateExecutionAdmissionStatus.REJECTED

    def test_empty_execution_target_and_purpose_are_rejected(self):
        service = LearningStateExecutionAdmissionService()
        with self.assertRaises(ValueError):
            service.admit(self._eligibility(), admission_id="admission-120", authorization_granted=True,
                          execution_target_id="", execution_purpose="perform-bounded-work")
        with self.assertRaises(ValueError):
            service.admit(self._eligibility(), admission_id="admission-120", authorization_granted=True,
                          execution_target_id="executor-X", execution_purpose=" ")


if __name__ == "__main__":
    unittest.main()
