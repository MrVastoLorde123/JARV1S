"""M9.3 worker-scoped context and knowledge boundary.

Workers receive only an explicit immutable projection of global working
context selected by their assignment. Knowledge access never grants
authority, permission, credentials, or unrestricted context access.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any, Mapping

from src.agency.workforce import WorkerAssignment, WorkerDefinition
from src.context.working_context import WorkingContext


@dataclass(frozen=True)
class WorkerContext:
    """Immutable context visible to one worker assignment."""

    worker_id: str
    assignment_id: str
    objective: str
    inputs: Mapping[str, Any] = field(default_factory=dict)
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        for name in ("worker_id", "assignment_id", "objective"):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string.")
        if not isinstance(self.inputs, Mapping):
            raise TypeError("inputs must be a mapping.")
        if not isinstance(self.metadata, Mapping):
            raise TypeError("metadata must be a mapping.")
        object.__setattr__(self, "inputs", MappingProxyType(dict(self.inputs)))
        object.__setattr__(self, "metadata", MappingProxyType(dict(self.metadata)))

    def to_context(self) -> dict[str, Any]:
        return {
            "worker_id": self.worker_id,
            "assignment_id": self.assignment_id,
            "objective": self.objective,
            "inputs": dict(self.inputs),
            "metadata": dict(self.metadata),
            "authority_granted": False,
            "global_context_access": False,
        }


class WorkerContextProjector:
    """Create a worker-visible projection strictly from assignment input scope."""

    _AVAILABLE_FIELDS = frozenset({"request", "context_items", "instructions", "observations", "task"})

    def project(
        self,
        worker: WorkerDefinition,
        assignment: WorkerAssignment,
        global_context: WorkingContext,
    ) -> WorkerContext:
        if not isinstance(worker, WorkerDefinition):
            raise TypeError("worker must be a WorkerDefinition.")
        if not isinstance(assignment, WorkerAssignment):
            raise TypeError("assignment must be a WorkerAssignment.")
        if not isinstance(global_context, WorkingContext):
            raise TypeError("global_context must be a WorkingContext.")
        if assignment.worker_id != worker.worker_id:
            raise ValueError("assignment worker identity does not match worker identity.")
        if not worker.accepts(assignment):
            raise ValueError("assignment exceeds worker bounds.")
        unknown = set(assignment.input_scope) - self._AVAILABLE_FIELDS
        if unknown:
            raise ValueError(f"assignment input_scope contains unsupported fields: {sorted(unknown)}")

        available: dict[str, Any] = {
            "request": global_context.request,
            "context_items": tuple(global_context.context_package.items),
            "instructions": tuple(global_context.context_package.instructions),
            "observations": tuple(global_context.observations),
        }
        if global_context.task is not None:
            available["task"] = global_context.task

        inputs = {key: available[key] for key in assignment.input_scope if key in available}
        return WorkerContext(
            worker_id=worker.worker_id,
            assignment_id=assignment.assignment_id,
            objective=assignment.objective,
            inputs=inputs,
            metadata={
                "context_boundary": "m9.3",
                "input_scope": assignment.input_scope,
                "output_scope": assignment.output_scope,
            },
        )
