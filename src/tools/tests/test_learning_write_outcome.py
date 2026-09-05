from __future__ import annotations

import unittest
from dataclasses import FrozenInstanceError

from src.tools.learning_write_admission import (
    DeterministicLearningWriteAdmissionProvider,
    LearningWriteAdmissionContext,
    LearningWriteAdmissionService,
)
from src.tools.learning_write_execution import (
    LearningWriteExecutionError,
    LearningWriteExecutionRequest,
    LearningWriteExecutionResult,
    LearningWriteExecutionStatus,
)
from src.tools.learning_write_outcome import (
    LearningWriteOutcomeError,
    LearningWriteOutcomeService,
    LearningWriteOutcomeStatus,
)
from src.tools.learning_write_proposal import LearningWriteDomain


class LearningWriteOutcomeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.request = LearningWriteExecutionRequest(
            execution_id="exec-1",
            admission_id="admission-1",
            proposal_id="proposal-1",
            decision_id="decision-1",
            candidate_id="candidate-1",
            domain=LearningWriteDomain.SEMANTIC.value,
            payload={"content": "learn this"},
        )
        self.service = LearningWriteOutcomeService()

    @staticmethod
    def _completed_result(**overrides) -> LearningWriteExecutionResult:
        values = {
            "execution_id": "exec-1",
            "admission_id": "admission-1",
            "proposal_id": "proposal-1",
            "decision_id": "decision-1",
            "candidate_id": "candidate-1",
            "domain": LearningWriteDomain.SEMANTIC.value,
            "status": LearningWriteExecutionStatus.COMPLETED,
            "write_result": {"memory_id": 42},
        }
        values.update(overrides)
        return LearningWriteExecutionResult(**values)

    def test_completed_write_is_succeeded(self) -> None:
        outcome = self.service.interpret(self._completed_result(), self.request)
        self.assertEqual(outcome.status, LearningWriteOutcomeStatus.SUCCEEDED)
        self.assertTrue(outcome.succeeded)
        self.assertIsNotNone(outcome.result_fingerprint)

    def test_failed_write_is_failed(self) -> None:
        result = LearningWriteExecutionResult(
            execution_id="exec-1",
            admission_id="admission-1",
            proposal_id="proposal-1",
            decision_id="decision-1",
            candidate_id="candidate-1",
            domain=LearningWriteDomain.SEMANTIC.value,
            status=LearningWriteExecutionStatus.FAILED,
            reason="database unavailable",
        )
        outcome = self.service.interpret(result, self.request)
        self.assertEqual(outcome.status, LearningWriteOutcomeStatus.FAILED)
        self.assertFalse(outcome.succeeded)
        self.assertEqual(outcome.reason, "database unavailable")

    def test_result_is_immutable(self) -> None:
        outcome = self.service.interpret(self._completed_result(), self.request)
        with self.assertRaises(FrozenInstanceError):
            outcome.status = LearningWriteOutcomeStatus.FAILED  # type: ignore[misc]

    def test_identity_mismatch_is_rejected(self) -> None:
        result = self._completed_result(proposal_id="other-proposal")
        with self.assertRaises(LearningWriteOutcomeError):
            self.service.interpret(result, self.request)

    def test_admission_identity_mismatch_is_rejected(self) -> None:
        result = self._completed_result(admission_id="other-admission")
        with self.assertRaises(LearningWriteOutcomeError):
            self.service.interpret(result, self.request)

    def test_decision_identity_mismatch_is_rejected(self) -> None:
        result = self._completed_result(decision_id="other-decision")
        with self.assertRaises(LearningWriteOutcomeError):
            self.service.interpret(result, self.request)

    def test_candidate_identity_mismatch_is_rejected(self) -> None:
        result = self._completed_result(candidate_id="other-candidate")
        with self.assertRaises(LearningWriteOutcomeError):
            self.service.interpret(result, self.request)

    def test_domain_mismatch_is_rejected(self) -> None:
        result = self._completed_result(domain=LearningWriteDomain.PROCEDURAL.value)
        with self.assertRaises(LearningWriteOutcomeError):
            self.service.interpret(result, self.request)

    def test_result_fingerprint_is_deterministic(self) -> None:
        first = self.service.interpret(self._completed_result(), self.request)
        second = self.service.interpret(self._completed_result(), self.request)
        self.assertEqual(first.result_fingerprint, second.result_fingerprint)

    def test_different_write_results_change_fingerprint(self) -> None:
        first = self.service.interpret(self._completed_result(write_result={"memory_id": 42}), self.request)
        second = self.service.interpret(self._completed_result(write_result={"memory_id": 43}), self.request)
        self.assertNotEqual(first.result_fingerprint, second.result_fingerprint)

    def test_to_context_has_no_authority_or_retry(self) -> None:
        outcome = self.service.interpret(self._completed_result(), self.request)
        context = outcome.to_context()
        self.assertTrue(context["learning_written"])
        self.assertFalse(context["memory_mutated"])
        self.assertFalse(context["authority_granted"])
        self.assertFalse(context["authorization_granted"])
        self.assertFalse(context["execution_requested"])
        self.assertFalse(context["retry_requested"])
        self.assertFalse(context["revocation_requested"])

    def test_completed_outcome_requires_fingerprint(self) -> None:
        with self.assertRaises(LearningWriteOutcomeError):
            from src.tools.learning_write_outcome import LearningWriteOutcome
            LearningWriteOutcome(
                execution_id="exec-1",
                admission_id="admission-1",
                proposal_id="proposal-1",
                decision_id="decision-1",
                candidate_id="candidate-1",
                domain=LearningWriteDomain.SEMANTIC.value,
                status=LearningWriteOutcomeStatus.SUCCEEDED,
            )

    def test_failed_result_requires_reason(self) -> None:
        with self.assertRaises(ValueError):
            LearningWriteExecutionResult(
                execution_id="exec-1",
                admission_id="admission-1",
                proposal_id="proposal-1",
                decision_id="decision-1",
                candidate_id="candidate-1",
                domain=LearningWriteDomain.SEMANTIC.value,
                status=LearningWriteExecutionStatus.FAILED,
            )

    def test_invalid_result_type_is_rejected(self) -> None:
        with self.assertRaises(TypeError):
            self.service.interpret({"status": "completed"}, self.request)  # type: ignore[arg-type]

    def test_invalid_request_type_is_rejected(self) -> None:
        with self.assertRaises(TypeError):
            self.service.interpret(self._completed_result(), {"execution_id": "exec-1"})  # type: ignore[arg-type]


if __name__ == "__main__":
    unittest.main()
