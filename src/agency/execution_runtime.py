"""Controlled M8.1 execution runtime.

M7 establishes authority and produces a READY provider-neutral execution
handoff. M8.1 consumes that handoff, delegates one execution attempt to an
injected adapter, and returns an explicit provider-neutral observation.

Capability resolution remains outside this runtime. The adapter is the
integration boundary that knows how to perform the operation; the formal
capability/plugin mapping is defined in M8.2.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Mapping, Protocol

from src.context.execution_semantics import ExecutionPreparation, ExecutionPreparationStatus


class ExecutionStatus(str, Enum):
    """Concrete outcome state for one execution attempt."""

    NOT_ATTEMPTED = "not_attempted"
    ATTEMPTED = "attempted"
    SUCCEEDED = "succeeded"
    FAILED = "failed"

    @property
    def attempted(self) -> bool:
        return self is not ExecutionStatus.NOT_ATTEMPTED

    @property
    def completed(self) -> bool:
        return self in {ExecutionStatus.SUCCEEDED, ExecutionStatus.FAILED}

    @property
    def succeeded(self) -> bool:
        return self is ExecutionStatus.SUCCEEDED


@dataclass(frozen=True)
class ExecutionOutcome:
    """Provider-neutral outcome returned by one execution adapter."""

    success: bool
    content: Any = None
    error: Mapping[str, Any] | None = None
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.success, bool):
            raise TypeError("success must be a bool.")
        if self.success and self.error is not None:
            raise ValueError("successful outcomes cannot contain an error.")
        if not self.success and self.error is None:
            raise ValueError("failed outcomes must contain an error.")
        if self.error is not None and not isinstance(self.error, Mapping):
            raise TypeError("error must be a mapping or None.")
        if not isinstance(self.metadata, Mapping):
            raise TypeError("metadata must be a mapping.")


@dataclass(frozen=True)
class ExecutionObservation:
    """Provider-neutral observation of what M8.1 actually did."""

    execution_id: str
    request: str
    proposal_id: str | None
    validation_id: str | None
    policy_decision_id: str | None
    confirmation_id: str | None
    authorization_id: str | None
    operation: str | None
    status: ExecutionStatus
    attempted: bool
    completed: bool
    succeeded: bool
    outcome: ExecutionOutcome | None = None
    error: Mapping[str, Any] | None = None
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.execution_id, str) or not self.execution_id.strip():
            raise ValueError("execution_id must be a non-empty string.")
        if not isinstance(self.request, str) or not self.request.strip():
            raise ValueError("request must be a non-empty string.")
        if not isinstance(self.status, ExecutionStatus):
            raise TypeError("status must be an ExecutionStatus value.")
        if (self.attempted, self.completed, self.succeeded) != (
            self.status.attempted,
            self.status.completed,
            self.status.succeeded,
        ):
            raise ValueError("attempted/completed/succeeded must match status semantics.")
        if self.outcome is not None and not isinstance(self.outcome, ExecutionOutcome):
            raise TypeError("outcome must be an ExecutionOutcome or None.")
        if self.error is not None and not isinstance(self.error, Mapping):
            raise TypeError("error must be a mapping or None.")
        if not isinstance(self.metadata, Mapping):
            raise TypeError("metadata must be a mapping.")

    def to_context(self) -> dict[str, Any]:
        """Serialize the observation without introducing authority controls."""
        return {
            "execution_id": self.execution_id,
            "request": self.request,
            "proposal_id": self.proposal_id,
            "validation_id": self.validation_id,
            "policy_decision_id": self.policy_decision_id,
            "confirmation_id": self.confirmation_id,
            "authorization_id": self.authorization_id,
            "operation": self.operation,
            "status": self.status.value,
            "attempted": self.attempted,
            "completed": self.completed,
            "succeeded": self.succeeded,
            "outcome": None
            if self.outcome is None
            else {
                "success": self.outcome.success,
                "content": self.outcome.content,
                "error": None if self.outcome.error is None else dict(self.outcome.error),
                "metadata": dict(self.outcome.metadata),
            },
            "error": None if self.error is None else dict(self.error),
            "metadata": dict(self.metadata),
        }


class ExecutionAdapter(Protocol):
    """Adapter that performs one concrete execution for a handoff."""

    def execute(self, request: Any) -> ExecutionOutcome:
        """Execute the handoff and return an outcome."""
        ...


class ExecutionRuntime:
    """Execute exactly one M7 READY handoff through an injected adapter."""

    def __init__(self, adapter: ExecutionAdapter) -> None:
        if not hasattr(adapter, "execute") or not callable(adapter.execute):
            raise TypeError("adapter must expose a callable execute(request) method.")
        self._adapter = adapter

    def execute(self, preparation: ExecutionPreparation) -> ExecutionObservation:
        """Consume one preparation and return an explicit execution observation."""
        if not isinstance(preparation, ExecutionPreparation):
            raise TypeError("preparation must be an ExecutionPreparation.")
        if preparation.status is not ExecutionPreparationStatus.READY:
            return self._not_attempted(preparation)

        request = preparation.execution_request
        if request is None:  # Defensive; M7 semantic validation rejects this state.
            return self._failure(
                preparation,
                None,
                {"code": "missing_execution_request", "message": "READY preparation has no execution request."},
            )

        try:
            outcome = self._adapter.execute(request)
        except Exception as exc:  # noqa: BLE001 - adapter failure is an execution observation
            return self._failure(
                preparation,
                request,
                {
                    "code": "execution_adapter_error",
                    "message": str(exc) or exc.__class__.__name__,
                    "exception_type": exc.__class__.__name__,
                },
            )

        if not isinstance(outcome, ExecutionOutcome):
            return self._failure(
                preparation,
                request,
                {
                    "code": "invalid_execution_outcome",
                    "message": f"adapter returned {type(outcome).__name__}; expected ExecutionOutcome.",
                },
            )

        if outcome.success:
            return self._success(preparation, request, outcome)
        return self._failure(preparation, request, dict(outcome.error), outcome=outcome)

    @staticmethod
    def _success(preparation: ExecutionPreparation, request: Any, outcome: ExecutionOutcome) -> ExecutionObservation:
        return ExecutionObservation(
            execution_id=request.execution_id,
            request=preparation.request,
            proposal_id=request.proposal_id,
            validation_id=request.validation_id,
            policy_decision_id=request.policy_decision_id,
            confirmation_id=request.confirmation_id,
            authorization_id=request.authorization_id,
            operation=request.operation,
            status=ExecutionStatus.SUCCEEDED,
            attempted=True,
            completed=True,
            succeeded=True,
            outcome=outcome,
            metadata={"execution_runtime": "m8.1"},
        )

    @staticmethod
    def _not_attempted(preparation: ExecutionPreparation) -> ExecutionObservation:
        return ExecutionObservation(
            execution_id=preparation.execution_id,
            request=preparation.request,
            proposal_id=None,
            validation_id=None,
            policy_decision_id=None,
            confirmation_id=None,
            authorization_id=None,
            operation=None,
            status=ExecutionStatus.NOT_ATTEMPTED,
            attempted=False,
            completed=False,
            succeeded=False,
            error={
                "code": "execution_not_attempted",
                "message": "Execution preparation was BLOCKED; adapter invocation was not attempted.",
            },
            metadata={"execution_runtime": "m8.1"},
        )

    @staticmethod
    def _failure(
        preparation: ExecutionPreparation,
        request: Any,
        error: Mapping[str, Any],
        outcome: ExecutionOutcome | None = None,
    ) -> ExecutionObservation:
        return ExecutionObservation(
            execution_id=preparation.execution_id,
            request=preparation.request,
            proposal_id=None if request is None else request.proposal_id,
            validation_id=None if request is None else request.validation_id,
            policy_decision_id=None if request is None else request.policy_decision_id,
            confirmation_id=None if request is None else request.confirmation_id,
            authorization_id=None if request is None else request.authorization_id,
            operation=None if request is None else request.operation,
            status=ExecutionStatus.FAILED,
            attempted=True,
            completed=True,
            succeeded=False,
            outcome=outcome,
            error=dict(error),
            metadata={"execution_runtime": "m8.1"},
        )
