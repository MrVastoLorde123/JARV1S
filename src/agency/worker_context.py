"""M9.3 worker context and knowledge boundary."""

from __future__ import annotations

from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any, Mapping

from src.agency.workforce import WorkerAssignment, WorkerDefinition
from src.context.working_context import WorkingContext


@dataclass(frozen=True)
class WorkerContext:
    """Immutable, assignment-scoped context visible to one worker run."""

    worker_id: str
    assignment_id: str
    objective: str
    inputs: Mapping[str, Any] = field(default_factory=dict)
    facts: tuple[Any, ...] = ()
    observations: tuple[Any, ...] = ()
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.worker_id, str) or not self.worker_id.strip():
            raise ValueError("worker_id must be a non-empty string.")
        if not isinstance(self.assignment_id, str) or not self.assignment_id.strip():
            raise ValueError("assignment_id must be a non-empty string.")
        if not isinstance(self.objective, str) or not self.objective.strip():
            raise ValueError("objective must be a non-empty string.")
        if not isinstance(self.inputs, Mapping):
            raise TypeError("inputs must be a mapping.")
        if not isinstance(self.facts, tuple):
            raise TypeError("facts must be a tuple.")
        if not isinstance(self.observations, tuple):
            raise TypeError("observations must be a tuple.")
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
            "facts": self.facts,
            "observations": self.observations,
            "metadata": dict(self.metadata),
            "authority_granted": False,
            "global_context_access": False,
        }


class WorkerContextProjector:
    """Project only assignment-authorized fields from global context."""

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

        available: dict[str, Any] = {
            "request": global_context.request,
            "context_items": tuple(global_context.context_package.items),
            "instructions": tuple(global_context.context_package.instructions),
            "observations": tuple(global_context.observations),
        }
        inputs = {
            key: available[key]
            for key in assignment.input_scope
            if key in available
        }

        return WorkerContext(
            worker_id=worker.worker_id,
            assignment_id=assignment.assignment_id,
            objective=assignment.objective,
            inputs=inputs,
            facts=(
                tuple(global_context.context_package.items)
                if "context_items" in assignment.input_scope
                else ()
            ),
            observations=(
                tuple(global_context.observations)
                if "observations" in assignment.input_scope
                else ()
            ),
            metadata={
                "context_boundary": "m9.3",
                "global_context_access": False,
                "input_scope": assignment.input_scope,
                "output_scope": assignment.output_scope,
            },
        )
