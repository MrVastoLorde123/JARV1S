"""M9.5 bounded delegation and coordination.

The coordinator distributes bounded worker assignments and determines a
stable execution order. It never creates authority, authorization, execution
requests, credentials, or worker-to-worker permission.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any, Mapping

from src.agency.workforce import WorkerAssignment, WorkerRegistry


class DelegationConflictError(ValueError):
    """Raised when delegation identities or dependencies conflict."""


@dataclass(frozen=True)
class DelegationPlan:
    """Immutable deterministic plan for a bounded set of worker assignments."""

    plan_id: str
    assignments: tuple[WorkerAssignment, ...]
    dependencies: Mapping[str, tuple[str, ...]] = field(default_factory=dict)
    max_assignments: int = 1
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.plan_id, str) or not self.plan_id.strip():
            raise ValueError("plan_id must be a non-empty string")
        if not isinstance(self.assignments, tuple):
            raise TypeError("assignments must be a tuple")
        if not isinstance(self.max_assignments, int) or isinstance(self.max_assignments, bool) or self.max_assignments <= 0:
            raise ValueError("max_assignments must be a positive integer")
        if len(self.assignments) > self.max_assignments:
            raise ValueError("assignments exceed max_assignments")
        seen: set[str] = set()
        for assignment in self.assignments:
            if not isinstance(assignment, WorkerAssignment):
                raise TypeError("assignments must contain WorkerAssignment values")
            if assignment.assignment_id in seen:
                raise DelegationConflictError(f"duplicate assignment_id: {assignment.assignment_id}")
            seen.add(assignment.assignment_id)
        if not isinstance(self.dependencies, Mapping):
            raise TypeError("dependencies must be a mapping")
        normalized: dict[str, tuple[str, ...]] = {}
        assignment_ids = seen
        for assignment_id, dependency_ids in self.dependencies.items():
            if assignment_id not in assignment_ids:
                raise ValueError(f"dependency references unknown assignment: {assignment_id}")
            if isinstance(dependency_ids, (str, bytes)) or not isinstance(dependency_ids, (tuple, list, set, frozenset)):
                raise TypeError("dependency values must be collections of assignment ids")
            values = tuple(str(value).strip() for value in dependency_ids)
            if any(not value for value in values):
                raise ValueError("dependency assignment ids must be non-empty strings")
            if len(set(values)) != len(values):
                raise DelegationConflictError(f"duplicate dependency for assignment: {assignment_id}")
            if assignment_id in values:
                raise DelegationConflictError(f"assignment cannot depend on itself: {assignment_id}")
            unknown = set(values) - assignment_ids
            if unknown:
                raise ValueError(f"unknown dependency assignments: {sorted(unknown)}")
            normalized[assignment_id] = values
        object.__setattr__(self, "dependencies", MappingProxyType(normalized))
        if not isinstance(self.metadata, Mapping):
            raise TypeError("metadata must be a mapping")
        object.__setattr__(self, "metadata", MappingProxyType(dict(self.metadata)))

    def ordered_assignment_ids(self) -> tuple[str, ...]:
        """Return a deterministic topological order; reject dependency cycles."""
        assignment_ids = {item.assignment_id for item in self.assignments}
        deps = {key: set(value) for key, value in self.dependencies.items()}
        for assignment_id in assignment_ids:
            deps.setdefault(assignment_id, set())

        ordered: list[str] = []
        remaining = set(assignment_ids)
        while remaining:
            ready = sorted(item for item in remaining if deps[item].isdisjoint(remaining))
            if not ready:
                raise DelegationConflictError("delegation dependencies contain a cycle")
            ordered.extend(ready)
            remaining.difference_update(ready)
        return tuple(ordered)

    def to_context(self) -> dict[str, Any]:
        return {
            "plan_id": self.plan_id,
            "assignments": tuple(item.to_context() for item in self.assignments),
            "dependencies": {key: value for key, value in self.dependencies.items()},
            "ordered_assignment_ids": self.ordered_assignment_ids(),
            "max_assignments": self.max_assignments,
            "metadata": dict(self.metadata),
            "authorization_granted": False,
            "authority_escalation": False,
        }


@dataclass(frozen=True)
class DelegationResult:
    """Immutable result of validating and ordering a delegation plan."""

    plan: DelegationPlan
    ordered_assignments: tuple[WorkerAssignment, ...]

    @property
    def assignment_ids(self) -> tuple[str, ...]:
        return tuple(item.assignment_id for item in self.ordered_assignments)

    def to_context(self) -> dict[str, Any]:
        return {
            "plan_id": self.plan.plan_id,
            "assignment_ids": self.assignment_ids,
            "assignments": tuple(item.to_context() for item in self.ordered_assignments),
            "authorization_granted": False,
            "authority_escalation": False,
        }


class DelegationCoordinator:
    """Validate and deterministically order bounded worker assignments."""

    def __init__(self, registry: WorkerRegistry) -> None:
        if not isinstance(registry, WorkerRegistry):
            raise TypeError("registry must be a WorkerRegistry")
        self._registry = registry

    def coordinate(self, plan: DelegationPlan) -> DelegationResult:
        if not isinstance(plan, DelegationPlan):
            raise TypeError("plan must be a DelegationPlan")
        for assignment in plan.assignments:
            self._registry.validate_assignment(assignment)
        lookup = {item.assignment_id: item for item in plan.assignments}
        ordered = tuple(lookup[item_id] for item_id in plan.ordered_assignment_ids())
        return DelegationResult(plan=plan, ordered_assignments=ordered)
