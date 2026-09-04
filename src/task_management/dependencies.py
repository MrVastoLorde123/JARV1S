"""M20.3 dependency relationships and deterministic task graph boundary."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


class DependencyError(ValueError):
    """Raised when a task dependency relationship is invalid."""


@dataclass(frozen=True)
class TaskDependency:
    """Directed relationship: dependent_task_id requires prerequisite_task_id."""

    prerequisite_task_id: str
    dependent_task_id: str

    def __post_init__(self) -> None:
        _validate_id(self.prerequisite_task_id, "prerequisite_task_id")
        _validate_id(self.dependent_task_id, "dependent_task_id")
        if self.prerequisite_task_id == self.dependent_task_id:
            raise DependencyError("a task cannot depend on itself")

    @property
    def edge(self) -> tuple[str, str]:
        return (self.prerequisite_task_id, self.dependent_task_id)


def _validate_id(value: str, name: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} must be a non-empty string")


class TaskDependencyGraph:
    """Conflict-aware directed acyclic graph over existing task identities."""

    def __init__(self, task_ids: Iterable[str] = ()) -> None:
        self._task_ids: set[str] = set()
        self._prerequisites: dict[str, set[str]] = {}
        self._dependents: dict[str, set[str]] = {}
        for task_id in task_ids:
            self.register_task(task_id)

    def register_task(self, task_id: str) -> None:
        _validate_id(task_id, "task_id")
        if task_id in self._task_ids:
            return
        self._task_ids.add(task_id)
        self._prerequisites.setdefault(task_id, set())
        self._dependents.setdefault(task_id, set())

    def add_dependency(self, prerequisite_task_id: str, dependent_task_id: str) -> TaskDependency:
        dependency = TaskDependency(prerequisite_task_id, dependent_task_id)
        self._require_registered(dependency.prerequisite_task_id)
        self._require_registered(dependency.dependent_task_id)

        if dependency.prerequisite_task_id in self._prerequisites[dependency.dependent_task_id]:
            return dependency

        if self._would_create_cycle(dependency.prerequisite_task_id, dependency.dependent_task_id):
            raise DependencyError(
                "dependency would create a cycle: "
                f"{dependency.prerequisite_task_id} -> {dependency.dependent_task_id}"
            )

        self._prerequisites[dependency.dependent_task_id].add(dependency.prerequisite_task_id)
        self._dependents[dependency.prerequisite_task_id].add(dependency.dependent_task_id)
        return dependency

    def remove_dependency(self, prerequisite_task_id: str, dependent_task_id: str) -> bool:
        dependency = TaskDependency(prerequisite_task_id, dependent_task_id)
        self._require_registered(dependency.prerequisite_task_id)
        self._require_registered(dependency.dependent_task_id)
        existed = dependency.prerequisite_task_id in self._prerequisites[dependency.dependent_task_id]
        self._prerequisites[dependency.dependent_task_id].discard(dependency.prerequisite_task_id)
        self._dependents[dependency.prerequisite_task_id].discard(dependency.dependent_task_id)
        return existed

    def prerequisites(self, task_id: str) -> tuple[str, ...]:
        self._require_registered(task_id)
        return tuple(sorted(self._prerequisites[task_id]))

    def dependents(self, task_id: str) -> tuple[str, ...]:
        self._require_registered(task_id)
        return tuple(sorted(self._dependents[task_id]))

    def dependencies(self) -> tuple[TaskDependency, ...]:
        edges = [
            TaskDependency(prerequisite, dependent)
            for dependent, prerequisites in self._prerequisites.items()
            for prerequisite in prerequisites
        ]
        return tuple(sorted(edges, key=lambda item: item.edge))

    def topological_order(self) -> tuple[str, ...]:
        """Return deterministic graph order; this is structural, not scheduling."""
        indegree = {task_id: len(self._prerequisites[task_id]) for task_id in self._task_ids}
        ready = sorted(task_id for task_id, degree in indegree.items() if degree == 0)
        result: list[str] = []

        while ready:
            task_id = ready.pop(0)
            result.append(task_id)
            for dependent in sorted(self._dependents[task_id]):
                indegree[dependent] -= 1
                if indegree[dependent] == 0:
                    ready.append(dependent)
                    ready.sort()

        if len(result) != len(self._task_ids):
            raise DependencyError("task dependency graph contains a cycle")
        return tuple(result)

    def root_tasks(self) -> tuple[str, ...]:
        return tuple(sorted(task_id for task_id in self._task_ids if not self._prerequisites[task_id]))

    def leaf_tasks(self) -> tuple[str, ...]:
        return tuple(sorted(task_id for task_id in self._task_ids if not self._dependents[task_id]))

    def all_task_ids(self) -> tuple[str, ...]:
        return tuple(sorted(self._task_ids))

    def _require_registered(self, task_id: str) -> None:
        if task_id not in self._task_ids:
            raise DependencyError(f"unknown task_id: {task_id}")

    def _would_create_cycle(self, prerequisite_task_id: str, dependent_task_id: str) -> bool:
        stack = [dependent_task_id]
        visited: set[str] = set()
        while stack:
            current = stack.pop()
            if current == prerequisite_task_id:
                return True
            if current in visited:
                continue
            visited.add(current)
            stack.extend(self._dependents[current])
        return False
