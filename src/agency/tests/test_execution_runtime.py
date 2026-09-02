from __future__ import annotations

import unittest

from src.agency.execution_runtime import (
    ExecutionOutcome,
    ExecutionRuntime,
    ExecutionStatus,
)
from src.context.execution_semantics import (
    ExecutionPreparation,
    ExecutionPreparationStatus,
    ExecutionPreparationViolation,
    ExecutionRequest,
)


def ready_preparation() -> ExecutionPreparation:
    request = ExecutionRequest(
        execution_id="execution:1",
        request="inspect the file",
        proposal_id="proposal:1",
        validation_id="validation:1",
        policy_decision_id="policy:1",
        confirmation_id=None,
        authorization_id="authorization:1",
        operation="inspect_file",
        arguments={"path": "example.txt"},
        metadata={"source": "test"},
    )
    return ExecutionPreparation(
        request="inspect the file",
        execution_id="execution:1",
        status=ExecutionPreparationStatus.READY,
        execution_request=request,
    )


def blocked_preparation() -> ExecutionPreparation:
    return ExecutionPreparation(
        request="delete the file",
        execution_id="execution:blocked",
        status=ExecutionPreparationStatus.BLOCKED,
        violations=(
            ExecutionPreparationViolation(
                code="authorization_required",
                message="execution requires an AUTHORIZED authorization decision.",
            ),
        ),
    )


class RecordingAdapter:
    def __init__(self, outcome: ExecutionOutcome | None = None) -> None:
        self.calls = 0
        self.requests = []
        self.outcome = outcome or ExecutionOutcome(success=True, content={"ok": True})

    def execute(self, request: ExecutionRequest) -> ExecutionOutcome:
        self.calls += 1
        self.requests.append(request)
        return self.outcome


class RaisingAdapter:
    def __init__(self) -> None:
        self.calls = 0

    def execute(self, request: ExecutionRequest) -> ExecutionOutcome:
        self.calls += 1
        raise RuntimeError("device offline")


class ExecutionRuntimeTests(unittest.TestCase):
    def test_ready_execution_returns_success_observation_and_preserves_identity(self) -> None:
        adapter = RecordingAdapter()
        observation = ExecutionRuntime(adapter).execute(ready_preparation())

        self.assertIs(observation.status, ExecutionStatus.SUCCEEDED)
        self.assertTrue(observation.attempted)
        self.assertTrue(observation.completed)
        self.assertTrue(observation.succeeded)
        self.assertEqual(observation.execution_id, "execution:1")
        self.assertEqual(observation.proposal_id, "proposal:1")
        self.assertEqual(observation.validation_id, "validation:1")
        self.assertEqual(observation.policy_decision_id, "policy:1")
        self.assertEqual(observation.authorization_id, "authorization:1")
        self.assertEqual(observation.operation, "inspect_file")
        self.assertIsNotNone(observation.outcome)
        self.assertTrue(observation.outcome.success)
        self.assertEqual(adapter.calls, 1)
        self.assertEqual(adapter.requests[0].operation, "inspect_file")

    def test_failed_adapter_outcome_remains_failed(self) -> None:
        adapter = RecordingAdapter(
            ExecutionOutcome(
                success=False,
                error={"code": "permission_denied", "message": "access denied"},
            )
        )

        observation = ExecutionRuntime(adapter).execute(ready_preparation())

        self.assertIs(observation.status, ExecutionStatus.FAILED)
        self.assertTrue(observation.attempted)
        self.assertTrue(observation.completed)
        self.assertFalse(observation.succeeded)
        self.assertEqual(
            observation.error,
            {"code": "permission_denied", "message": "access denied"},
        )

    def test_adapter_exception_becomes_failed_observation(self) -> None:
        adapter = RaisingAdapter()

        observation = ExecutionRuntime(adapter).execute(ready_preparation())

        self.assertIs(observation.status, ExecutionStatus.FAILED)
        self.assertTrue(observation.attempted)
        self.assertTrue(observation.completed)
        self.assertFalse(observation.succeeded)
        self.assertIsNotNone(observation.error)
        self.assertEqual(observation.error["code"], "execution_adapter_error")
        self.assertEqual(observation.error["exception_type"], "RuntimeError")
        self.assertEqual(adapter.calls, 1)

    def test_blocked_preparation_never_reaches_adapter(self) -> None:
        adapter = RecordingAdapter()

        observation = ExecutionRuntime(adapter).execute(blocked_preparation())

        self.assertIs(observation.status, ExecutionStatus.NOT_ATTEMPTED)
        self.assertFalse(observation.attempted)
        self.assertFalse(observation.completed)
        self.assertFalse(observation.succeeded)
        self.assertIsNotNone(observation.error)
        self.assertEqual(observation.error["code"], "execution_not_attempted")
        self.assertEqual(adapter.calls, 0)

    def test_invalid_adapter_result_is_failed_observation(self) -> None:
        class InvalidAdapter:
            def execute(self, request: ExecutionRequest):
                return object()

        observation = ExecutionRuntime(InvalidAdapter()).execute(ready_preparation())

        self.assertIs(observation.status, ExecutionStatus.FAILED)
        self.assertFalse(observation.succeeded)
        self.assertIsNotNone(observation.error)
        self.assertEqual(observation.error["code"], "invalid_execution_outcome")

    def test_observation_serialization_does_not_add_authority_controls(self) -> None:
        observation = ExecutionRuntime(RecordingAdapter()).execute(ready_preparation())

        context = observation.to_context()

        self.assertEqual(context["execution_id"], "execution:1")
        self.assertEqual(context["status"], "succeeded")
        self.assertNotIn("authorization", context)
        self.assertNotIn("authorized", context)
        self.assertNotIn("tool_handle", context)
        self.assertNotIn("credential", context)

    def test_runtime_requires_an_execution_adapter(self) -> None:
        with self.assertRaises(TypeError):
            ExecutionRuntime(object())

    def test_runtime_requires_an_execution_preparation(self) -> None:
        adapter = RecordingAdapter()

        with self.assertRaises(TypeError):
            ExecutionRuntime(adapter).execute(object())


if __name__ == "__main__":
    unittest.main()
