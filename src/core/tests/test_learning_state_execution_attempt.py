import unittest
from types import MappingProxyType

from src.core.learning_state_execution_admission import (
    LearningStateExecutionAdmission,
    LearningStateExecutionAdmissionStatus,
)
from src.core.learning_state_execution_attempt import (
    LearningStateExecutionAttemptService,
    LearningStateExecutionAttemptStatus,
)


class M23_121ExecutionAttemptTests(unittest.TestCase):
    def _admission(self, *, status=LearningStateExecutionAdmissionStatus.AUTHORIZED):
        return LearningStateExecutionAdmission(
            admission_id="admission-120",
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
            eligibility_status=__import__(
                "src.core.learning_state_execution_eligibility",
                fromlist=["LearningStateExecutionEligibilityStatus"],
            ).LearningStateExecutionEligibilityStatus.ELIGIBLE,
            admission_status=status,
            result={"decision": "bounded", "nested": {"score": 7}},
            reasons={"source": "m23.120"},
            lineage={"parent": "admission-120"},
        )

    def test_authorized_admission_invokes_executor_once(self):
        calls = []

        def executor(result, target, purpose):
            calls.append((result, target, purpose))
            return {"raw": "executor-return", "value": 7}

        artifact = LearningStateExecutionAttemptService().attempt(
            self._admission(), executor,
            attempt_id="attempt-121",
            execution_target_id="executor-X",
            execution_purpose="perform-bounded-work",
        )
        self.assertEqual(len(calls), 1)
        self.assertEqual(artifact.attempt_status, LearningStateExecutionAttemptStatus.ATTEMPTED)
        self.assertTrue(artifact.is_attempted)
        self.assertEqual(artifact.executor_output["raw"], "executor-return")

    def test_rejected_admission_cannot_execute(self):
        calls = []

        with self.assertRaises(ValueError):
            LearningStateExecutionAttemptService().attempt(
                self._admission(status=LearningStateExecutionAdmissionStatus.REJECTED),
                lambda *_: calls.append(True),
                attempt_id="attempt-121",
                execution_target_id="executor-X",
                execution_purpose="perform-bounded-work",
            )
        self.assertEqual(calls, [])

    def test_exact_admission_type_is_required(self):
        with self.assertRaises(TypeError):
            LearningStateExecutionAttemptService().attempt(
                object(), lambda *_: None,
                attempt_id="attempt-121",
                execution_target_id="executor-X",
                execution_purpose="purpose",
            )

    def test_executor_must_be_callable(self):
        with self.assertRaises(TypeError):
            LearningStateExecutionAttemptService().attempt(
                self._admission(), object(),
                attempt_id="attempt-121",
                execution_target_id="executor-X",
                execution_purpose="purpose",
            )

    def test_attempt_id_must_be_non_empty(self):
        with self.assertRaises(ValueError):
            LearningStateExecutionAttemptService().attempt(
                self._admission(), lambda *_: None,
                attempt_id=" ", execution_target_id="executor-X", execution_purpose="purpose"
            )

    def test_target_and_purpose_must_match_admission(self):
        service = LearningStateExecutionAttemptService()
        with self.assertRaises(ValueError):
            service.attempt(self._admission(), lambda *_: None, attempt_id="attempt-121", execution_target_id="executor-Y", execution_purpose="perform-bounded-work")
        with self.assertRaises(ValueError):
            service.attempt(self._admission(), lambda *_: None, attempt_id="attempt-121", execution_target_id="executor-X", execution_purpose="other")

    def test_executor_output_is_recursively_frozen(self):
        def executor(*_):
            return {"nested": {"value": 7}, "items": [1, 2]}

        artifact = LearningStateExecutionAttemptService().attempt(
            self._admission(), executor,
            attempt_id="attempt-121", execution_target_id="executor-X", execution_purpose="perform-bounded-work"
        )
        self.assertIsInstance(artifact.executor_output, MappingProxyType)
        self.assertIsInstance(artifact.executor_output["nested"], MappingProxyType)
        self.assertEqual(artifact.executor_output["items"], (1, 2))

    def test_executor_exception_is_recorded_as_failed_attempt(self):
        def executor(*_):
            raise RuntimeError("device unavailable")

        artifact = LearningStateExecutionAttemptService().attempt(
            self._admission(), executor,
            attempt_id="attempt-121", execution_target_id="executor-X", execution_purpose="perform-bounded-work"
        )
        self.assertEqual(artifact.attempt_status, LearningStateExecutionAttemptStatus.FAILED)
        self.assertTrue(artifact.is_failed)
        self.assertEqual(artifact.failure_type, "RuntimeError")
        self.assertEqual(artifact.failure_message, "device unavailable")
        self.assertIsNone(artifact.executor_output)

    def test_attempt_does_not_establish_outcome_success_or_failure_truth(self):
        artifact = LearningStateExecutionAttemptService().attempt(
            self._admission(), lambda *_: {"status": "ok"},
            attempt_id="attempt-121", execution_target_id="executor-X", execution_purpose="perform-bounded-work"
        )
        self.assertFalse(artifact.establishes_outcome)
        self.assertFalse(artifact.establishes_success)
        self.assertFalse(artifact.establishes_failure_truth)

    def test_attempt_does_not_transform_or_interpret_semantics(self):
        artifact = LearningStateExecutionAttemptService().attempt(
            self._admission(), lambda result, *_: result,
            attempt_id="attempt-121", execution_target_id="executor-X", execution_purpose="perform-bounded-work"
        )
        self.assertFalse(artifact.transforms_semantic_result)
        self.assertFalse(artifact.interprets_semantic_result)

    def test_attempt_has_no_learning_memory_policy_or_authority_power(self):
        artifact = LearningStateExecutionAttemptService().attempt(
            self._admission(), lambda *_: None,
            attempt_id="attempt-121", execution_target_id="executor-X", execution_purpose="perform-bounded-work"
        )
        self.assertFalse(artifact.invokes_learner)
        self.assertFalse(artifact.updates_model)
        self.assertFalse(artifact.mutates_memory)
        self.assertFalse(artifact.mutates_policy)
        self.assertFalse(artifact.authorizes_execution)

    def test_attempt_has_no_planning_or_scheduling_power(self):
        artifact = LearningStateExecutionAttemptService().attempt(
            self._admission(), lambda *_: None,
            attempt_id="attempt-121", execution_target_id="executor-X", execution_purpose="perform-bounded-work"
        )
        self.assertFalse(artifact.plans_work)
        self.assertFalse(artifact.schedules_work)

    def test_provenance_and_fingerprints_are_preserved(self):
        source = self._admission()
        artifact = LearningStateExecutionAttemptService().attempt(
            source, lambda *_: "raw",
            attempt_id="attempt-121", execution_target_id="executor-X", execution_purpose="perform-bounded-work"
        )
        for field in (
            "admission_id", "eligibility_id", "handling_id", "consumption_id", "receipt_id", "handoff_id",
            "integrity_id", "validation_id", "use_id", "request_id", "interpretation_id", "transition_id",
            "evidence_id", "application_id", "state_key", "transition_fingerprint", "source_application_fingerprint",
            "computed_application_fingerprint", "consumer_id", "use_purpose", "downstream_recipient_id",
            "downstream_handler_id", "handling_purpose", "execution_target_id", "execution_purpose",
        ):
            self.assertEqual(getattr(artifact, field), getattr(source, field))

    def test_source_admission_is_not_mutated(self):
        source = self._admission()
        before = source.result
        LearningStateExecutionAttemptService().attempt(
            source, lambda *_: {"done": True},
            attempt_id="attempt-121", execution_target_id="executor-X", execution_purpose="perform-bounded-work"
        )
        self.assertEqual(source.result, before)

    def test_attempt_artifact_is_immutable(self):
        artifact = LearningStateExecutionAttemptService().attempt(
            self._admission(), lambda *_: None,
            attempt_id="attempt-121", execution_target_id="executor-X", execution_purpose="perform-bounded-work"
        )
        with self.assertRaises(AttributeError):
            artifact.attempt_status = LearningStateExecutionAttemptStatus.FAILED

    def test_deterministic_for_same_non_side_effecting_executor(self):
        def executor(*_):
            return {"raw": "same"}

        service = LearningStateExecutionAttemptService()
        left = service.attempt(self._admission(), executor, attempt_id="attempt-121", execution_target_id="executor-X", execution_purpose="perform-bounded-work")
        right = service.attempt(self._admission(), executor, attempt_id="attempt-121", execution_target_id="executor-X", execution_purpose="perform-bounded-work")
        self.assertEqual(left, right)

    def test_executor_receives_only_sealed_result_and_explicit_context(self):
        captured = []

        def executor(*args):
            captured.append(args)
            return "raw"

        source = self._admission()
        LearningStateExecutionAttemptService().attempt(
            source, executor,
            attempt_id="attempt-121", execution_target_id="executor-X", execution_purpose="perform-bounded-work"
        )
        self.assertEqual(captured[0][0], source.result)
        self.assertEqual(captured[0][1:], ("executor-X", "perform-bounded-work"))

    def test_executor_exception_is_not_re_raised(self):
        artifact = LearningStateExecutionAttemptService().attempt(
            self._admission(), lambda *_: 1 / 0,
            attempt_id="attempt-121", execution_target_id="executor-X", execution_purpose="perform-bounded-work"
        )
        self.assertEqual(artifact.failure_type, "ZeroDivisionError")


if __name__ == "__main__":
    unittest.main()
