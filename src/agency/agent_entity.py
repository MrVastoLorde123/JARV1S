"""M28.10 runtime agent identity and lifecycle contract.

An AgentEntity is a runtime instance of a bounded WorkerDefinition assigned
through a WorkerAssignment. It describes where the worker is and what it is
currently doing; it does not grant authority, permission, credentials, or
execution capability by itself.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from types import MappingProxyType
from typing import Any, Mapping


class AgentStatus(str, Enum):
    CREATED = "CREATED"
    ASSIGNED = "ASSIGNED"
    TRAVELLING = "TRAVELLING"
    EXECUTING = "EXECUTING"
    RETURNING = "RETURNING"
    HANDOFF = "HANDOFF"
    RETIRED = "RETIRED"


class AgentLandscape(str, Enum):
    OPERATIONS = "OPERATIONS"
    MIND = "MIND"
    AGENTS = "AGENTS"
    MODELS = "MODELS"
    CAPABILITIES = "CAPABILITIES"
    WORK = "WORK"
    MARKET = "MARKET"


def _text(value: object, name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} must be a non-empty string.")
    return value.strip()


def _names(values: object, name: str) -> tuple[str, ...]:
    if isinstance(values, (str, bytes)) or not isinstance(values, (tuple, list, set, frozenset)):
        raise TypeError(f"{name} must be a collection of strings.")
    result = tuple(_text(value, name) for value in values)
    if len(set(result)) != len(result):
        raise ValueError(f"{name} must not contain duplicates.")
    return result


@dataclass(frozen=True)
class AgentEntity:
    """One concrete worker instance visible to the JARVIS world."""

    agent_id: str
    display_name: str
    archetype: str
    assignment_id: str
    status: AgentStatus
    landscape: AgentLandscape
    destination: AgentLandscape | None = None
    model_id: str | None = None
    capability_ids: tuple[str, ...] = ()
    created_at: str = ""
    updated_at: str = ""
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "agent_id", _text(self.agent_id, "agent_id"))
        object.__setattr__(self, "display_name", _text(self.display_name, "display_name"))
        object.__setattr__(self, "archetype", _text(self.archetype, "archetype"))
        object.__setattr__(self, "assignment_id", _text(self.assignment_id, "assignment_id"))
        if not isinstance(self.status, AgentStatus):
            raise TypeError("status must be an AgentStatus value.")
        if not isinstance(self.landscape, AgentLandscape):
            raise TypeError("landscape must be an AgentLandscape value.")
        if self.destination is not None and not isinstance(self.destination, AgentLandscape):
            raise TypeError("destination must be an AgentLandscape value or None.")
        if self.model_id is not None:
            object.__setattr__(self, "model_id", _text(self.model_id, "model_id"))
        object.__setattr__(self, "capability_ids", _names(self.capability_ids, "capability_ids"))
        object.__setattr__(self, "created_at", _text(self.created_at, "created_at"))
        object.__setattr__(self, "updated_at", _text(self.updated_at, "updated_at"))
        if not isinstance(self.metadata, Mapping):
            raise TypeError("metadata must be a mapping.")
        object.__setattr__(self, "metadata", MappingProxyType(dict(self.metadata)))

    def move_to(self, destination: AgentLandscape, updated_at: str) -> "AgentEntity":
        if not isinstance(destination, AgentLandscape):
            raise TypeError("destination must be an AgentLandscape value.")
        return self._replace(
            status=AgentStatus.TRAVELLING,
            destination=destination,
            updated_at=_text(updated_at, "updated_at"),
        )

    def arrive(self, landscape: AgentLandscape, updated_at: str) -> "AgentEntity":
        if not isinstance(landscape, AgentLandscape):
            raise TypeError("landscape must be an AgentLandscape value.")
        return self._replace(
            status=AgentStatus.EXECUTING,
            landscape=landscape,
            destination=None,
            updated_at=_text(updated_at, "updated_at"),
        )

    def with_status(self, status: AgentStatus, updated_at: str) -> "AgentEntity":
        if not isinstance(status, AgentStatus):
            raise TypeError("status must be an AgentStatus value.")
        return self._replace(status=status, updated_at=_text(updated_at, "updated_at"))

    def to_context(self) -> dict[str, Any]:
        return {
            "agent_id": self.agent_id,
            "display_name": self.display_name,
            "archetype": self.archetype,
            "assignment_id": self.assignment_id,
            "status": self.status.value,
            "landscape": self.landscape.value,
            "destination": self.destination.value if self.destination else None,
            "model_id": self.model_id,
            "capability_ids": self.capability_ids,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "metadata": dict(self.metadata),
            "authority_granted": False,
            "permissions_granted": False,
        }

    def _replace(self, **changes: Any) -> "AgentEntity":
        values = {
            "agent_id": self.agent_id,
            "display_name": self.display_name,
            "archetype": self.archetype,
            "assignment_id": self.assignment_id,
            "status": self.status,
            "landscape": self.landscape,
            "destination": self.destination,
            "model_id": self.model_id,
            "capability_ids": self.capability_ids,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "metadata": self.metadata,
        }
        values.update(changes)
        return AgentEntity(**values)
