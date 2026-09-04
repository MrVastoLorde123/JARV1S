"""M20.1 durable goal/objective boundary.

Goals and objectives describe work to be pursued. They do not grant
permission, authorization, policy authority, or execution rights.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from types import MappingProxyType
from typing import Any, Mapping


class GoalState(str, Enum):
    ACTIVE = "ACTIVE"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"
    SUPERSEDED = "SUPERSEDED"


class ObjectiveState(str, Enum):
    PROPOSED = "PROPOSED"
    ACTIVE = "ACTIVE"
    PAUSED = "PAUSED"
    BLOCKED = "BLOCKED"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"
    SUPERSEDED = "SUPERSEDED"


class ObjectiveTransitionError(ValueError):
    """Raised when an objective lifecycle transition is invalid."""


@dataclass(frozen=True)
class Provenance:
    """Immutable origin reference for a goal or objective."""

    source: str
    reference_id: str

    def __post_init__(self) -> None:
        for name in ("source", "reference_id"):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string")

    def to_dict(self) -> dict[str, str]:
        return {"source": self.source, "reference_id": self.reference_id}


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
class Goal:
    """Durable human-level desired outcome."""

    goal_id: str
    title: str
    description: str
    provenance: Provenance
    state: GoalState = GoalState.ACTIVE
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        _validate_id(self.goal_id, "goal_id")
        _validate_text(self.title, "title")
        _validate_text(self.description, "description")
        if not isinstance(self.provenance, Provenance):
            raise TypeError("provenance must be a Provenance")
        if not isinstance(self.state, GoalState):
            try:
                object.__setattr__(self, "state", GoalState(self.state))
            except (TypeError, ValueError) as exc:
                raise TypeError("state must be a GoalState") from exc
        _validate_text(self.created_at, "created_at")
        object.__setattr__(self, "metadata", _normalize_metadata(self.metadata))

    def to_context(self) -> dict[str, Any]:
        return {
            "goal_id": self.goal_id,
            "title": self.title,
            "description": self.description,
            "state": self.state.value,
            "provenance": self.provenance.to_dict(),
            "metadata": dict(self.metadata),
            "authority_granted": False,
            "authorization_granted": False,
            "execution_requested": False,
        }


@dataclass(frozen=True)
class Objective:
    """Durable bounded operational objective belonging to a goal."""

    objective_id: str
    goal_id: str
    title: str
    description: str
    provenance: Provenance
    state: ObjectiveState = ObjectiveState.PROPOSED
    priority: int = 0
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        _validate_id(self.objective_id, "objective_id")
        _validate_id(self.goal_id, "goal_id")
        _validate_text(self.title, "title")
        _validate_text(self.description, "description")
        if not isinstance(self.provenance, Provenance):
            raise TypeError("provenance must be a Provenance")
        if not isinstance(self.state, ObjectiveState):
            try:
                object.__setattr__(self, "state", ObjectiveState(self.state))
            except (TypeError, ValueError) as exc:
                raise TypeError("state must be an ObjectiveState") from exc
        if not isinstance(self.priority, int) or isinstance(self.priority, bool) or self.priority < 0:
            raise ValueError("priority must be a non-negative integer")
        _validate_text(self.created_at, "created_at")
        _validate_text(self.updated_at, "updated_at")
        object.__setattr__(self, "metadata", _normalize_metadata(self.metadata))

    def to_context(self) -> dict[str, Any]:
        return {
            "objective_id": self.objective_id,
            "goal_id": self.goal_id,
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

    def transition(self, new_state: ObjectiveState, *, reference_id: str) -> "Objective":
        """Return a new objective with an explicit valid lifecycle transition."""
        _validate_id(reference_id, "reference_id")
        if not isinstance(new_state, ObjectiveState):
            try:
                new_state = ObjectiveState(new_state)
            except (TypeError, ValueError) as exc:
                raise TypeError("new_state must be an ObjectiveState") from exc

        allowed: dict[ObjectiveState, set[ObjectiveState]] = {
            ObjectiveState.PROPOSED: {ObjectiveState.ACTIVE, ObjectiveState.CANCELLED},
            ObjectiveState.ACTIVE: {
                ObjectiveState.PAUSED,
                ObjectiveState.BLOCKED,
                ObjectiveState.COMPLETED,
                ObjectiveState.CANCELLED,
                ObjectiveState.SUPERSEDED,
            },
            ObjectiveState.PAUSED: {ObjectiveState.ACTIVE, ObjectiveState.CANCELLED, ObjectiveState.SUPERSEDED},
            ObjectiveState.BLOCKED: {ObjectiveState.ACTIVE, ObjectiveState.CANCELLED, ObjectiveState.SUPERSEDED},
            ObjectiveState.COMPLETED: set(),
            ObjectiveState.CANCELLED: set(),
            ObjectiveState.SUPERSEDED: set(),
        }
        if new_state == self.state:
            raise ObjectiveTransitionError("objective is already in the requested state")
        if new_state not in allowed[self.state]:
            raise ObjectiveTransitionError(f"invalid objective transition: {self.state.value} -> {new_state.value}")

        metadata = dict(self.metadata)
        metadata["last_transition_reference"] = reference_id
        return Objective(
            objective_id=self.objective_id,
            goal_id=self.goal_id,
            title=self.title,
            description=self.description,
            provenance=self.provenance,
            state=new_state,
            priority=self.priority,
            created_at=self.created_at,
            updated_at=datetime.now(timezone.utc).isoformat(),
            metadata=metadata,
        )


class GoalObjectiveStore:
    """Immutable-by-replacement conflict-aware in-memory goal/objective store."""

    def __init__(self) -> None:
        self._goals: dict[str, Goal] = {}
        self._objectives: dict[str, Objective] = {}

    def put_goal(self, goal: Goal) -> None:
        if not isinstance(goal, Goal):
            raise TypeError("goal must be a Goal")
        existing = self._goals.get(goal.goal_id)
        if existing is not None and existing != goal:
            raise ValueError(f"goal identity conflict: {goal.goal_id}")
        self._goals[goal.goal_id] = goal

    def put_objective(self, objective: Objective) -> None:
        if not isinstance(objective, Objective):
            raise TypeError("objective must be an Objective")
        if objective.goal_id not in self._goals:
            raise ValueError("objective references unknown goal_id")
        existing = self._objectives.get(objective.objective_id)
        if existing is not None and existing != objective:
            raise ValueError(f"objective identity conflict: {objective.objective_id}")
        self._objectives[objective.objective_id] = objective

    def get_goal(self, goal_id: str) -> Goal | None:
        _validate_id(goal_id, "goal_id")
        return self._goals.get(goal_id)

    def get_objective(self, objective_id: str) -> Objective | None:
        _validate_id(objective_id, "objective_id")
        return self._objectives.get(objective_id)

    def list_objectives(self, goal_id: str, *, include_terminal: bool = True) -> tuple[Objective, ...]:
        _validate_id(goal_id, "goal_id")
        values = [item for item in self._objectives.values() if item.goal_id == goal_id]
        if not include_terminal:
            values = [
                item
                for item in values
                if item.state not in {
                    ObjectiveState.COMPLETED,
                    ObjectiveState.CANCELLED,
                    ObjectiveState.SUPERSEDED,
                }
            ]
        return tuple(sorted(values, key=lambda item: (-item.priority, item.objective_id)))

    def replace_objective(self, objective: Objective) -> None:
        existing = self._objectives.get(objective.objective_id)
        if existing is None:
            raise KeyError(objective.objective_id)
        if existing.goal_id != objective.goal_id:
            raise ValueError("objective goal identity cannot change")
        self._objectives[objective.objective_id] = objective

    def all_goals(self) -> tuple[Goal, ...]:
        return tuple(sorted(self._goals.values(), key=lambda item: item.goal_id))

    def all_objectives(self) -> tuple[Objective, ...]:
        return tuple(sorted(self._objectives.values(), key=lambda item: item.objective_id))
