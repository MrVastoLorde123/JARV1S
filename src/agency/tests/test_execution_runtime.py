from __future__ import annotations

import pytest

from src.agency.execution_runtime import (
    ExecutionAdapter,
    ExecutionObservation,
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


def test_ready_execution_returns_success_observation_and_preserves_identity() -> None:
    adapter = RecordingAdapter()
    observation = ExecutionRuntime(adapter).execute(ready_preparation())

    assert observation.status is ExecutionStatus.SUCCEEDED
    assert observation.attempted is True
    assert observation.completed is True
    assert observation.succeeded is True
    assert observation.execution_id == "execution:1"
    assert observation.proposal_id == "proposal:1"
    assert observation.validation_id == "validation:1"
    assert observation.policy_decision_id == "policy:1"
    assert observation.authorization_id == "authorization:1"
    assert observation.operation == "inspect_file"
    assert observation.outcome is not None
    assert observation.outcome.success is True
    assert adapter.calls == 1
    assert adapter.requests[0].operation == "inspect_file"


def test_failed_adapter_outcome_remains_failed() -> None:
    adapter = RecordingAdapter(
        ExecutionOutcome(
            success=False,
            error={"code": "permission_denied", "message": "access denied"},
        )
    )

    observation = ExecutionRuntime(adapter).execute(ready_preparation())

    assert observation.status is ExecutionStatus.FAILED
    assert observation.attempted is True
    assert observation.completed is True
    assert observation.succeeded is False
    assert observation.error == {"code": "permission_denied", "message": "access denied"}


def test_adapter_exception_becomes_failed_observation() -> None:
    adapter = RaisingAdapter()

    observation = ExecutionRuntime(adapter).execute(ready_preparation())

    assert observation.status is ExecutionStatus.FAILED
    assert observation.attempted is True
    assert observation.completed is True
    assert observation.succeeded is False
    assert observation.error is not None
    assert observation.error["code"] == "execution_adapter_error"
    assert observation.error["exception_type"] == "RuntimeError"
    assert adapter.calls == 1


def test_blocked_preparation_never_reaches_adapter() -> None:
    adapter = RecordingAdapter()

    observation = ExecutionRuntime(adapter).execute(blocked_preparation())

    assert observation.status is ExecutionStatus.NOT_ATTEMPTED
    assert observation.attempted is False
    assert observation.completed is False
    assert observation.succeeded is False
    assert observation.error is not None
    assert observation.error["code"] == "execution_not_attempted"
    assert adapter.calls == 0


def test_invalid_adapter_result_is_failed_observation() -> None:
    class InvalidAdapter:
        def execute(self, request: ExecutionRequest):
            return object()

    observation = ExecutionRuntime(InvalidAdapter()).execute(ready_preparation())

    assert observation.status is ExecutionStatus.FAILED
    assert observation.succeeded is False
    assert observation.error is not None
    assert observation.error["code"] == "invalid_execution_outcome"


def test_observation_serialization_does_not_add_authority_controls() -> None:
    adapter = RecordingAdapter()
    observation = ExecutionRuntime(adapter).execute(ready_preparation())

    context = observation.to_context()

    assert context["execution_id"] == "execution:1"
    assert context["status"] == "succeeded"
    assert "authorization" not in context
    assert "authorized" not in context
    assert "tool_handle" not in context
    assert "credential" not in context


def test_runtime_requires_an_execution_adapter() -> None:
    with pytest.raises(TypeError):
        ExecutionRuntime(object())  # type: ignore[arg-type]


def test_runtime_requires_an_execution_preparation() -> None:
    adapter = RecordingAdapter()

    with pytest.raises(TypeError):
        ExecutionRuntime(adapter).execute(object())  # type: ignore[arg-type]
