"""M35: bounded handoff from dispatched work to an existing execution preparation.

The handoff pairs a bounded worker assignment with an already-authorized,
integrity-valid M7.10 ExecutionPreparation. It never creates authorization,
prepares execution, invokes tools, or executes work itself.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any, Mapping

from src.context.execution_semantics import ExecutionPreparation, ExecutionPreparationStatus

from .work_dispatch import DispatchResult


@dataclass(frozen=True)
class ExecutionHandoff:
    """Immutable pairing of dispatch evidence and a READY execution preparation."""

    dispatch: DispatchResult
    preparation: ExecutionPreparation
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.dispatch, DispatchResult):
            raise TypeError("dispatch must be a DispatchResult")
        if not isinstance(self.preparation, ExecutionPreparation):
            raise TypeError("preparation must be an ExecutionPreparation")
        if self.preparation.status is not ExecutionPreparationStatus.READY:
            raise ValueError("execution handoff requires a READY execution preparation")
        request = self.preparation.execution_request
        if request is None:
            raise ValueError("READY execution preparation must contain an execution request")
        if request.request != self.dispatch.step.title:
            raise ValueError("execution request must match dispatched step title")
        if not isinstance(self.metadata, Mapping):
            raise TypeError("metadata must be a mapping")
        object.__setattr__(self, "metadata", MappingProxyType(dict(self.metadata)))

    @property
    def execution_id(self) -> str:
        return self.preparation.execution_id

    @property
    def assignment_id(self) -> str:
        return self.dispatch.assignment.assignment_id

    def to_context(self) -> dict[str, Any]:
        return {
            "work_id": self.dispatch.step.step_id,
            "step_id": self.dispatch.step.step_id,
            "assignment_id": self.assignment_id,
            "worker_id": self.dispatch.worker_id,
            "execution_id": self.execution_id,
            "dispatch": self.dispatch.to_context(),
            "preparation": self.preparation.to_context(),
            "metadata": dict(self.metadata),
            "authorization_created": False,
            "execution_performed": False,
        }


def create_execution_handoff(
    dispatch: DispatchResult,
    preparation: ExecutionPreparation,
    *,
    metadata: Mapping[str, Any] | None = None,
) -> ExecutionHandoff:
    """Create a non-authorizing handoff from bounded dispatch to M7.10 READY prep."""
    return ExecutionHandoff(dispatch=dispatch, preparation=preparation, metadata=metadata or {})


__all__ = ["ExecutionHandoff", "create_execution_handoff"]
