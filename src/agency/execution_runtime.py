"""Controlled M8.1 execution runtime.

M7 establishes authority and produces a READY provider-neutral execution
handoff. This module performs the first real agency step: it consumes that
handoff, delegates execution to an injected adapter, and returns an explicit
execution observation.

The runtime deliberately does not select capabilities, grant authority,
perform confirmation, retry, schedule, or integrate observations into the
working-context store. Those responsibilities belong to later M8 milestones.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Mapping, Protocol

from src.context.execution_semantics import ExecutionPreparation, ExecutionPreparationStatus
from src.tools.models import ToolRequest, ToolResult


class ExecutionStatus(str, Enum):
    """Concrete outcome state for one runtime attempt."""

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
class ExecutionObservation:
    """Provider-neutral observation of what the runtime actually attempted."""

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
    result: ToolResult | None = None
    error: Mapping[str, Any] | None = None
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.execution_id, str) or not self.execution_id.strip():
            raise ValueError("execution_id must be a non-empty string.")
        if not isinstance(self.request, str) or not self.request.strip():
            raise ValueError("request must be a non-empty string.")
        if not isinstance(self.status, ExecutionStatus):
            raise TypeError("status must be an ExecutionStatus value.")
        if not isinstance(self.attempted, bool) or not isinstance(self.completed, bool) or not isinstance(self.succeeded, bool):
            raise TypeError("attempted, completed, and succeeded must be bool values.")
        if self.attempted != self.status.attempted:
            raise ValueError("attempted must match status semantics.")
        if self.completed != self.status.completed:
            raise ValueError("completed must match status semantics.")
        if self.succeeded != self.status.succeeded:
            raise ValueError("succeeded must match status semantics.")
        if self.result is not None and not isinstance(self.result, ToolResult):
            raise TypeError("result must be a ToolResult or None.")
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
            "result": self.result,
            "error": None if self.error is None else dict(self.error),
            "metadata": dict(self.metadata),
        }


class ExecutionAdapter(Protocol):
    """Provider-neutral adapter for one concrete execution attempt."""

    def execute(self, request: ToolRequest) -> ToolResult:
        """Execute one concrete tool request and return its result."""
        ...


class ToolServiceExecutionAdapter:
    """Adapter over the existing ToolService invocation boundary."""

    def __init__(self, service: Any) -> None:
        if not hasattr(service, "invoke") or not callable(service.invoke):
            raise TypeError("service must expose a callable invoke(request) method.")
        self._service = service

    def execute(self, request: ToolRequest) -> ToolResult:
        return self._service.invoke(request)


class ExecutionRuntime:
    """Execute exactly one M7 READY handoff through an injected adapter."""

    def __init__(self, adapter: ExecutionAdapter) -> None:
        if not hasattr(adapter, "execute") or not callable(adapter.execute):
            raise TypeError("adapter must expose a callable execute(request) method.")
        self._adapter = adapter

    def execute(self, preparation: ExecutionPreparation) -> ExecutionObservation:
        """Consume one preparation and return an explicit execution observation.

        BLOCKED preparations never reach the adapter. For READY preparations,
        this runtime creates a concrete ToolRequest only from the provider-
        neutral operation already supplied by the execution adapter boundary.
        M8.1 does not resolve capability identity; the adapter owns that mapping.
        """
        if not isinstance(preparation, ExecutionPreparation):
            raise TypeError("preparation must be an ExecutionPreparation.")

        if preparation.status is not ExecutionPreparationStatus.READY:
            return self._not_attempted(preparation)

        request = preparation.execution_request
        if request is None:  # Defensive; the semantic model rejects this state.
            return self._failure(
                preparation,
                None,
                {"code": "missing_execution_request", "message": "READY preparation has no execution request."},
            )

        concrete_request = ToolRequest(
            tool_name=request.operation,
            arguments=dict(request.arguments),
            metadata={
                **dict(request.metadata),
                "execution_id": request.execution_id,
                "proposal_id": request.proposal_id,
                "validation_id": request.validation_id,
                "policy_decision_id": request.policy_decision_id,
                "confirmation_id": request.confirmation_id,
                "authorization_id": request.authorization_id,
            },
            invocation_id=request.execution_id,
        )

        try:
            result = self._adapter.execute(concrete_request)
        except Exception as exc:  # noqa: BLE001 - execution failures are observations
            return self._failure(
                preparation,
                request,
                {
                    "code": "execution_adapter_error",
                    "message": str(exc) or exc.__class__.__name__,
                    "exception_type": exc.__class__.__name__,
                },
            )

        if not isinstance(result, ToolResult):
            return self._failure(
                preparation,
                request,
                {
                    "code": "invalid_execution_result",
                    "message": f"adapter returned {type(result).__name__}; expected ToolResult.",
                },
            )

        if result.success:
            return self._success(preparation, request, result)

        return self._failure(
            preparation,
            request,
            {
                "code": result.error.code,
                "message": result.error.message,
            },
            result=result,
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
    def _success(
        preparation: ExecutionPreparation,
        request: Any,
        result: ToolResult,
    ) -> ExecutionObservation:
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
            result=result,
            metadata={"execution_runtime": "m8.1"},
        )

    @staticmethod
    def _failure(
        preparation: ExecutionPreparation,
        request: Any,
        error: Mapping[str, Any],
        result: ToolResult | None = None,
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
            result=result,
            error=dict(error),
            metadata={"execution_runtime": "m8.1"},
        )
