"""M20.2 task model and explicit lifecycle boundary."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from types import MappingProxyType
from typing import Any, Mapping

from .goals import Provenance


class TaskState(str, Enum):
    PROPOSED = "PROPOSED"
    READY = "READY"
    IN_PROGRESS = "IN_PROGRESS"
    BLOCKED = "BLOCKED"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"
    SUPERSEDED = "SUPERSEDED"


class TaskTransitionError(ValueError):
    """Raised when a task lifecycle transition is invalid."""


def _validate_id(value: str, name: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} must be a non-empty string")


def _validate_text(value: str, name: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} must be a non-empty string")


def _normalize_metadata(metadata: Mapping[str, Any]) -> Mapping[str, Any]:
    if not isinstance(metadata, Mapping):
        raise TypeError("metadata must be a mapping")
    return MappingProxyType(dict(metadata))


@dataclass(frozen=True)
class Task:
    """Immutable bounded unit of work belonging to one objective."""

    task_id: str
    objective_id: str
    title: str
    description: str
    provenance: Provenance
    state: TaskState = TaskState.PROPOSED
    priority: int = 0
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        _validate_id(self.task_id, "task_id")
        _validate_id(self.objective_id, "objective_id")
        _validate_text(self.title, "title")
        _validate_text(self.description, "description")
        if not isinstance(self.provenance, Provenance):
            raise TypeError("provenance must be a Provenance")
        if not isinstance(self.state, TaskState):
            try:
                object.__setattr__(self, "state", TaskState(self.state))
            except (TypeError, ValueError) as exc:
                raise TypeError("state must be a TaskState") from exc
        if not isinstance(self.priority, int) or isinstance(self.priority, bool) or self.priority < 0:
            raise ValueError("priority must be a non-negative integer")
        _validate_text(self.created_at, "created_at")
        _validate_text(self.updated_at, "updated_at")
        object.__setattr__(self, "metadata", _normalize_metadata(self.metadata))

    def to_context(self) -> dict[str, Any]:
        return {
            "task_id": self.task_id,
            "objective_id": self.objective_id,
            "title": self.title,
            "description": self.description,
            "state": self.state.value,
            "priority": self.priority,
            "provenance": self.provenance.to_dict(),
            "metadata": dict(self.metadata),
            "authority_granted": False,
            "authorization_granted": False,
            "execution_requested": False,
        }

    def transition(self, new_state: TaskState, *, reference_id: str) -> "Task":
        """Return a new task with an explicit valid lifecycle transition."""
        _validate_id(reference_id, "reference_id")
        if not isinstance(new_state, TaskState):
            try:
                new_state = TaskState(new_state)
            except (TypeError, ValueError) as exc:
                raise TypeError("new_state must be a TaskState") from exc

        allowed: dict[TaskState, set[TaskState]] = {
            TaskState.PROPOSED: {TaskState.READY, TaskState.CANCELLED, TaskState.SUPERSEDED},
            TaskState.READY: {TaskState.IN_PROGRESS, TaskState.BLOCKED, TaskState.CANCELLED, TaskState.SUPERSEDED},
            TaskState.IN_PROGRESS: {TaskState.READY, TaskState.BLOCKED, TaskState.COMPLETED, TaskState.CANCELLED, TaskState.SUPERSEDED},
            TaskState.BLOCKED: {TaskState.READY, TaskState.IN_PROGRESS, TaskState.CANCELLED, TaskState.SUPERSEDED},
            TaskState.COMPLETED: set(),
            TaskState.CANCELLED: set(),
            TaskState.SUPERSEDED: set(),
        }
        if new_state == self.state:
            raise TaskTransitionError("task is already in the requested state")
        if new_state not in allowed[self.state]:
            raise TaskTransitionError(f"invalid task transition: {self.state.value} -> {new_state.value}")

        metadata = dict(self.metadata)
        metadata["last_transition_reference"] = reference_id
        return Task(
            task_id=self.task_id,
            objective_id=self.objective_id,
            title=self.title,
            description=self.description,
            provenance=self.provenance,
            state=new_state,
            priority=self.priority,
            created_at=self.created_at,
            updated_at=datetime.now(timezone.utc).isoformat(),
            metadata=metadata,
        )


class TaskStore:
    """Conflict-aware in-memory task store; updates replace immutable values."""

    _TERMINAL = {TaskState.COMPLETED, TaskState.CANCELLED, TaskState.SUPERSEDED}

    def __init__(self, *, objective_ids: set[str] | None = None) -> None:
        self._tasks: dict[str, Task] = {}
        self._objective_ids = None if objective_ids is None else set(objective_ids)

    def register_objective(self, objective_id: str) -> None:
        _validate_id(objective_id, "objective_id")
        if self._objective_ids is None:
            self._objective_ids = set()
        self._objective_ids.add(objective_id)

    def put_task(self, task: Task) -> None:
        if not isinstance(task, Task):
            raise TypeError("task must be a Task")
        if self._objective_ids is not None and task.objective_id not in self._objective_ids:
            raise ValueError("task references unknown objective_id")
        existing = self._tasks.get(task.task_id)
        if existing is not None and existing != task:
            raise ValueError(f"task identity conflict: {task.task_id}")
        self._tasks[task.task_id] = task

    def get_task(self, task_id: str) -> Task | None:
        _validate_id(task_id, "task_id")
        return self._tasks.get(task_id)

    def replace_task(self, task: Task) -> None:
        if not isinstance(task, Task):
            raise TypeError("task must be a Task")
        existing = self._tasks.get(task.task_id)
        if existing is None:
            raise KeyError(task.task_id)
        if existing.objective_id != task.objective_id:
            raise ValueError("task objective identity cannot change")
        self._tasks[task.task_id] = task

    def list_tasks(self, objective_id: str, *, include_terminal: bool = True) -> tuple[Task, ...]:
        _validate_id(objective_id, "objective_id")
        values = [item for item in self._tasks.values() if item.objective_id == objective_id]
        if not include_terminal:
            values = [item for item in values if item.state not in self._TERMINAL]
        return tuple(sorted(values, key=lambda item: (-item.priority, item.task_id)))

    def all_tasks(self) -> tuple[Task, ...]:
        return tuple(sorted(self._tasks.values(), key=lambda item: item.task_id))
