"""M9.1 worker identity and assignment boundary.

M9.1 defines bounded workforce contracts only. Workers receive explicit
assignments and capability/context bounds, but these contracts never grant
authorization or create executable requests. Actual worker execution belongs
to later M9 layers and must continue through M7/M8 authority and execution
boundaries.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from types import MappingProxyType
from typing import Any, Mapping


_FORBIDDEN_KEYS = frozenset(
    {
        "authorize",
        "authorization",
        "authorized",
        "permission",
        "permissions",
        "confirm",
        "confirmation",
        "confirmed",
        "execute",
        "execution",
        "tool_handle",
        "invoke",
        "provider",
        "credential",
        "credentials",
    }
)


def _require_text(value: object, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field_name} must be a non-empty string.")
    return value.strip()


def _normalise_names(values: object, field_name: str) -> tuple[str, ...]:
    if isinstance(values, (str, bytes)) or not isinstance(values, (tuple, list, set, frozenset)):
        raise TypeError(f"{field_name} must be a collection of strings.")
    result = tuple(_require_text(value, field_name) for value in values)
    if len(set(result)) != len(result):
        raise ValueError(f"{field_name} must not contain duplicates.")
    return result


def _normalise_scope(values: object, field_name: str) -> tuple[str, ...]:
    if isinstance(values, (str, bytes)) or not isinstance(values, (tuple, list, set, frozenset)):
        raise TypeError(f"{field_name} must be a collection of strings.")
    result = tuple(_require_text(value, field_name) for value in values)
    if len(set(result)) != len(result):
        raise ValueError(f"{field_name} must not contain duplicates.")
    return result


def _normalise_metadata(metadata: Mapping[str, Any]) -> Mapping[str, Any]:
    if not isinstance(metadata, Mapping):
        raise TypeError("metadata must be a mapping.")
    if any(str(key).lower() in _FORBIDDEN_KEYS for key in metadata):
        raise ValueError("metadata cannot contain authority, execution, provider, or credential controls.")
    return MappingProxyType(dict(metadata))


@dataclass(frozen=True)
class WorkerDefinition:
    """Immutable identity and hard bounds for one worker class."""

    worker_id: str
    name: str
    capabilities: tuple[str, ...]
    max_steps: int
    description: str = ""
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "worker_id", _require_text(self.worker_id, "worker_id"))
        object.__setattr__(self, "name", _require_text(self.name, "name"))
        object.__setattr__(self, "capabilities", _normalise_names(self.capabilities, "capabilities"))
        if not isinstance(self.max_steps, int) or isinstance(self.max_steps, bool) or self.max_steps <= 0:
            raise ValueError("max_steps must be a positive integer.")
        if not isinstance(self.description, str):
            raise TypeError("description must be a string.")
        object.__setattr__(self, "metadata", _normalise_metadata(self.metadata))

    def accepts(self, assignment: "WorkerAssignment") -> bool:
        """Return whether this worker can accept an assignment within its bounds."""
        if not isinstance(assignment, WorkerAssignment):
            raise TypeError("assignment must be a WorkerAssignment.")
        return (
            assignment.worker_id == self.worker_id
            and set(assignment.allowed_capabilities).issubset(self.capabilities)
            and assignment.max_steps <= self.max_steps
        )


@dataclass(frozen=True)
class WorkerAssignment:
    """Non-authorizing description of work delegated to one worker."""

    assignment_id: str
    worker_id: str
    objective: str
    allowed_capabilities: tuple[str, ...]
    input_scope: tuple[str, ...]
    output_scope: tuple[str, ...]
    max_steps: int
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "assignment_id", _require_text(self.assignment_id, "assignment_id"))
        object.__setattr__(self, "worker_id", _require_text(self.worker_id, "worker_id"))
        object.__setattr__(self, "objective", _require_text(self.objective, "objective"))
        object.__setattr__(
            self,
            "allowed_capabilities",
            _normalise_names(self.allowed_capabilities, "allowed_capabilities"),
        )
        object.__setattr__(self, "input_scope", _normalise_scope(self.input_scope, "input_scope"))
        object.__setattr__(self, "output_scope", _normalise_scope(self.output_scope, "output_scope"))
        if not isinstance(self.max_steps, int) or isinstance(self.max_steps, bool) or self.max_steps <= 0:
            raise ValueError("max_steps must be a positive integer.")
        object.__setattr__(self, "metadata", _normalise_metadata(self.metadata))

    def to_context(self) -> dict[str, Any]:
        """Serialize assignment data without manufacturing authority."""
        return {
            "assignment_id": self.assignment_id,
            "worker_id": self.worker_id,
            "objective": self.objective,
            "allowed_capabilities": self.allowed_capabilities,
            "input_scope": self.input_scope,
            "output_scope": self.output_scope,
            "max_steps": self.max_steps,
            "metadata": dict(self.metadata),
            "authorization_granted": False,
        }


class WorkerReportStatus(str, Enum):
    """Outcome classification for future worker reporting."""

    COMPLETED = "completed"
    FAILED = "failed"
    BLOCKED = "blocked"
    PARTIAL = "partial"


@dataclass(frozen=True)
class WorkerReport:
    """Immutable worker report; results are evidence, not authority or truth."""

    assignment_id: str
    worker_id: str
    status: WorkerReportStatus
    outputs: Mapping[str, Any] = field(default_factory=dict)
    summary: str = ""
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "assignment_id", _require_text(self.assignment_id, "assignment_id"))
        object.__setattr__(self, "worker_id", _require_text(self.worker_id, "worker_id"))
        if not isinstance(self.status, WorkerReportStatus):
            raise TypeError("status must be a WorkerReportStatus value.")
        if not isinstance(self.outputs, Mapping):
            raise TypeError("outputs must be a mapping.")
        if not isinstance(self.summary, str):
            raise TypeError("summary must be a string.")
        object.__setattr__(self, "outputs", MappingProxyType(dict(self.outputs)))
        object.__setattr__(self, "metadata", _normalise_metadata(self.metadata))

    def to_context(self) -> dict[str, Any]:
        return {
            "assignment_id": self.assignment_id,
            "worker_id": self.worker_id,
            "status": self.status.value,
            "outputs": dict(self.outputs),
            "summary": self.summary,
            "metadata": dict(self.metadata),
            "authority_granted": False,
            "truth_guaranteed": False,
        }


class WorkerRegistry:
    """Deterministic registry of bounded worker definitions."""

    def __init__(self) -> None:
        self._workers: dict[str, WorkerDefinition] = {}

    def register(self, worker: WorkerDefinition) -> None:
        if not isinstance(worker, WorkerDefinition):
            raise TypeError("worker must be a WorkerDefinition.")
        if worker.worker_id in self._workers:
            raise ValueError(f"worker_id already registered: {worker.worker_id}")
        self._workers[worker.worker_id] = worker

    def get(self, worker_id: str) -> WorkerDefinition:
        worker_id = _require_text(worker_id, "worker_id")
        try:
            return self._workers[worker_id]
        except KeyError as exc:
            raise KeyError(f"unknown worker_id: {worker_id}") from exc

    def validate_assignment(self, assignment: WorkerAssignment) -> WorkerDefinition:
        if not isinstance(assignment, WorkerAssignment):
            raise TypeError("assignment must be a WorkerAssignment.")
        worker = self.get(assignment.worker_id)
        if not worker.accepts(assignment):
            raise ValueError(
                f"assignment {assignment.assignment_id} exceeds worker bounds for {assignment.worker_id}."
            )
        return worker

    def __len__(self) -> int:
        return len(self._workers)

    def worker_ids(self) -> tuple[str, ...]:
        return tuple(self._workers)
