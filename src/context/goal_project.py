"""M14.3 goal and project context boundary.

Goal/project context describes the current contextual relationship between
work, goals, and projects. It is not an instruction, policy, authorization,
or execution request.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from enum import Enum
from types import MappingProxyType
from typing import Any, Mapping


class GoalProjectContextValidationError(ValueError):
    """Raised when goal/project context violates the M14.3 boundary."""


class GoalStatus(str, Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    BLOCKED = "blocked"
    COMPLETED = "completed"
    ABANDONED = "abandoned"
    UNKNOWN = "unknown"


class ProjectStatus(str, Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    BLOCKED = "blocked"
    COMPLETED = "completed"
    ARCHIVED = "archived"
    UNKNOWN = "unknown"


MAX_ID_LENGTH = 256
MAX_NAME_LENGTH = 512
MAX_ITEMS = 128
MAX_REFERENCE_LENGTH = 256


def _text(value: str, field_name: str, maximum: int) -> str:
    if not isinstance(value, str) or not value.strip():
        raise GoalProjectContextValidationError(f"{field_name} must be a non-empty string")
    if len(value) > maximum:
        raise GoalProjectContextValidationError(
            f"{field_name} exceeds maximum length of {maximum}"
        )
    return value


def _freeze(value: Any, path: str = "metadata") -> Any:
    if value is None or isinstance(value, (str, int, float, bool)):
        if isinstance(value, float) and not (value == value and abs(value) != float("inf")):
            raise GoalProjectContextValidationError(f"{path} contains a non-finite number")
        return value
    if isinstance(value, Mapping):
        frozen: dict[str, Any] = {}
        for key, item in value.items():
            if not isinstance(key, str) or not key.strip():
                raise GoalProjectContextValidationError(f"{path} keys must be non-empty strings")
            frozen[key] = _freeze(item, f"{path}.{key}")
        return MappingProxyType(frozen)
    if isinstance(value, (list, tuple)):
        return tuple(_freeze(item, f"{path}[]") for item in value)
    raise GoalProjectContextValidationError(
        f"{path} contains unsupported value type: {type(value).__name__}"
    )


def _thaw(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {key: _thaw(item) for key, item in value.items()}
    if isinstance(value, tuple):
        return [_thaw(item) for item in value]
    return value


@dataclass(frozen=True)
class GoalContext:
    """Immutable contextual description of one goal."""

    goal_id: str
    name: str
    status: GoalStatus = GoalStatus.UNKNOWN
    project_id: str | None = None
    metadata: Mapping[str, Any] = None  # type: ignore[assignment]
    source_refs: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        _text(self.goal_id, "goal_id", MAX_ID_LENGTH)
        _text(self.name, "name", MAX_NAME_LENGTH)
        if not isinstance(self.status, GoalStatus):
            try:
                object.__setattr__(self, "status", GoalStatus(self.status))
            except (TypeError, ValueError) as exc:
                raise GoalProjectContextValidationError("status must be supported GoalStatus") from exc
        if self.project_id is not None:
            _text(self.project_id, "project_id", MAX_ID_LENGTH)
        metadata = {} if self.metadata is None else self.metadata
        if not isinstance(metadata, Mapping):
            raise GoalProjectContextValidationError("metadata must be a mapping")
        if len(metadata) > MAX_ITEMS:
            raise GoalProjectContextValidationError("metadata exceeds maximum item count")
        object.__setattr__(self, "metadata", _freeze(metadata))
        if not isinstance(self.source_refs, tuple):
            raise GoalProjectContextValidationError("source_refs must be a tuple")
        if len(self.source_refs) > MAX_ITEMS:
            raise GoalProjectContextValidationError("source_refs exceeds maximum count")
        if len(set(self.source_refs)) != len(self.source_refs):
            raise GoalProjectContextValidationError("source_refs must be unique")
        for index, ref in enumerate(self.source_refs):
            _text(ref, f"source_refs[{index}]", MAX_REFERENCE_LENGTH)

    def to_dict(self) -> dict[str, Any]:
        return {
            "goal_id": self.goal_id,
            "name": self.name,
            "status": self.status.value,
            "project_id": self.project_id,
            "metadata": _thaw(self.metadata),
            "source_refs": list(self.source_refs),
            "goal_is_instruction": False,
            "truth_guaranteed": False,
            "fact_guaranteed": False,
            "intent_guaranteed": False,
            "authorization_granted": False,
            "policy_authority": False,
            "execution_requested": False,
        }


@dataclass(frozen=True)
class ProjectContext:
    """Immutable contextual description of one project."""

    project_id: str
    name: str
    status: ProjectStatus = ProjectStatus.UNKNOWN
    goal_ids: tuple[str, ...] = ()
    metadata: Mapping[str, Any] = None  # type: ignore[assignment]
    source_refs: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        _text(self.project_id, "project_id", MAX_ID_LENGTH)
        _text(self.name, "name", MAX_NAME_LENGTH)
        if not isinstance(self.status, ProjectStatus):
            try:
                object.__setattr__(self, "status", ProjectStatus(self.status))
            except (TypeError, ValueError) as exc:
                raise GoalProjectContextValidationError("status must be supported ProjectStatus") from exc
        if not isinstance(self.goal_ids, tuple):
            raise GoalProjectContextValidationError("goal_ids must be a tuple")
        if len(self.goal_ids) > MAX_ITEMS:
            raise GoalProjectContextValidationError("goal_ids exceeds maximum count")
        if len(set(self.goal_ids)) != len(self.goal_ids):
            raise GoalProjectContextValidationError("goal_ids must be unique")
        for index, goal_id in enumerate(self.goal_ids):
            _text(goal_id, f"goal_ids[{index}]", MAX_ID_LENGTH)
        metadata = {} if self.metadata is None else self.metadata
        if not isinstance(metadata, Mapping):
            raise GoalProjectContextValidationError("metadata must be a mapping")
        if len(metadata) > MAX_ITEMS:
            raise GoalProjectContextValidationError("metadata exceeds maximum item count")
        object.__setattr__(self, "metadata", _freeze(metadata))
        if not isinstance(self.source_refs, tuple):
            raise GoalProjectContextValidationError("source_refs must be a tuple")
        if len(self.source_refs) > MAX_ITEMS:
            raise GoalProjectContextValidationError("source_refs exceeds maximum count")
        if len(set(self.source_refs)) != len(self.source_refs):
            raise GoalProjectContextValidationError("source_refs must be unique")
        for index, ref in enumerate(self.source_refs):
            _text(ref, f"source_refs[{index}]", MAX_REFERENCE_LENGTH)

    def to_dict(self) -> dict[str, Any]:
        return {
            "project_id": self.project_id,
            "name": self.name,
            "status": self.status.value,
            "goal_ids": list(self.goal_ids),
            "metadata": _thaw(self.metadata),
            "source_refs": list(self.source_refs),
            "project_is_instruction": False,
            "truth_guaranteed": False,
            "fact_guaranteed": False,
            "intent_guaranteed": False,
            "authorization_granted": False,
            "policy_authority": False,
            "execution_requested": False,
        }


@dataclass(frozen=True)
class GoalProjectContext:
    """Immutable bounded collection of contextual goal/project state."""

    goals: tuple[GoalContext, ...] = ()
    projects: tuple[ProjectContext, ...] = ()

    def __post_init__(self) -> None:
        if not isinstance(self.goals, tuple) or not isinstance(self.projects, tuple):
            raise GoalProjectContextValidationError("goals and projects must be tuples")
        if len(self.goals) > MAX_ITEMS or len(self.projects) > MAX_ITEMS:
            raise GoalProjectContextValidationError("goal/project count exceeds maximum")
        if any(not isinstance(item, GoalContext) for item in self.goals):
            raise GoalProjectContextValidationError("goals must contain GoalContext values")
        if any(not isinstance(item, ProjectContext) for item in self.projects):
            raise GoalProjectContextValidationError("projects must contain ProjectContext values")
        if len({item.goal_id for item in self.goals}) != len(self.goals):
            raise GoalProjectContextValidationError("goal IDs must be unique")
        if len({item.project_id for item in self.projects}) != len(self.projects):
            raise GoalProjectContextValidationError("project IDs must be unique")
        known_projects = {item.project_id for item in self.projects}
        for goal in self.goals:
            if goal.project_id is not None and goal.project_id not in known_projects:
                raise GoalProjectContextValidationError(
                    "goal project_id must refer to a project in the context"
                )
        known_goals = {item.goal_id for item in self.goals}
        for project in self.projects:
            missing = [goal_id for goal_id in project.goal_ids if goal_id not in known_goals]
            if missing:
                raise GoalProjectContextValidationError(
                    "project goal_ids must refer to goals in the context: " + ", ".join(missing)
                )

    def for_goal(self, goal_id: str) -> GoalContext | None:
        return next((goal for goal in self.goals if goal.goal_id == goal_id), None)

    def for_project(self, project_id: str) -> ProjectContext | None:
        return next((project for project in self.projects if project.project_id == project_id), None)

    def active_goals(self) -> tuple[GoalContext, ...]:
        return tuple(goal for goal in self.goals if goal.status is GoalStatus.ACTIVE)

    def active_projects(self) -> tuple[ProjectContext, ...]:
        return tuple(project for project in self.projects if project.status is ProjectStatus.ACTIVE)

    def to_dict(self) -> dict[str, Any]:
        return {
            "goals": [goal.to_dict() for goal in self.goals],
            "projects": [project.to_dict() for project in self.projects],
            "goal_is_instruction": False,
            "project_is_instruction": False,
            "truth_guaranteed": False,
            "fact_guaranteed": False,
            "intent_guaranteed": False,
            "authorization_granted": False,
            "policy_authority": False,
            "execution_requested": False,
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), sort_keys=True, default=str)
