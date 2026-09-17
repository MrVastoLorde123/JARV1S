"""M42: bounded world-model substrate over existing world observations.

The world model is a provider-neutral, immutable current-context representation.
It records observed/derived facts with explicit provenance without declaring
those facts authoritative truth, permission, intent, or execution authority.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any, Mapping

from .world_projection import WorldObservation


@dataclass(frozen=True)
class WorldModelFact:
    """One bounded world-model fact with explicit observation lineage."""

    fact_id: str
    subject_id: str
    domain: str
    value: Any
    source_observation_ids: tuple[str, ...]
    status: str = "OBSERVED"
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        for name in ("fact_id", "subject_id", "domain", "status"):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string")
        if not isinstance(self.source_observation_ids, tuple) or not self.source_observation_ids:
            raise ValueError("source_observation_ids must be a non-empty tuple")
        if len(set(self.source_observation_ids)) != len(self.source_observation_ids):
            raise ValueError("source_observation_ids must be unique")
        if any(not isinstance(item, str) or not item.strip() for item in self.source_observation_ids):
            raise ValueError("source_observation_ids must contain non-empty strings")
        if not isinstance(self.metadata, Mapping):
            raise TypeError("metadata must be a mapping")
        object.__setattr__(self, "metadata", MappingProxyType(dict(self.metadata)))

    def to_context(self) -> dict[str, Any]:
        return {
            "fact_id": self.fact_id,
            "subject_id": self.subject_id,
            "domain": self.domain,
            "value": self.value,
            "source_observation_ids": self.source_observation_ids,
            "status": self.status,
            "metadata": dict(self.metadata),
            "truth_established": False,
            "authority_granted": False,
        }


@dataclass(frozen=True)
class WorldModelSnapshot:
    """Immutable provider-neutral current-context snapshot."""

    model_id: str
    generated_at: str
    scope: str
    facts: tuple[WorldModelFact, ...] = ()
    source_observation_ids: tuple[str, ...] = ()
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        for name in ("model_id", "generated_at", "scope"):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string")
        if not isinstance(self.facts, tuple) or any(not isinstance(item, WorldModelFact) for item in self.facts):
            raise TypeError("facts must be a tuple of WorldModelFact values")
        fact_ids = tuple(item.fact_id for item in self.facts)
        if len(set(fact_ids)) != len(fact_ids):
            raise ValueError("world-model fact IDs must be unique")
        if not isinstance(self.source_observation_ids, tuple):
            raise TypeError("source_observation_ids must be a tuple")
        if len(set(self.source_observation_ids)) != len(self.source_observation_ids):
            raise ValueError("source_observation_ids must be unique")
        if not isinstance(self.metadata, Mapping):
            raise TypeError("metadata must be a mapping")
        object.__setattr__(self, "metadata", MappingProxyType(dict(self.metadata)))

    @property
    def fact_count(self) -> int:
        return len(self.facts)

    @property
    def subjects(self) -> tuple[str, ...]:
        return tuple(dict.fromkeys(fact.subject_id for fact in self.facts))

    def facts_for_subject(self, subject_id: str) -> tuple[WorldModelFact, ...]:
        if not isinstance(subject_id, str) or not subject_id.strip():
            raise ValueError("subject_id must be a non-empty string")
        return tuple(fact for fact in self.facts if fact.subject_id == subject_id.strip())

    def to_context(self) -> dict[str, Any]:
        return {
            "model_id": self.model_id,
            "generated_at": self.generated_at,
            "scope": self.scope,
            "facts": tuple(fact.to_context() for fact in self.facts),
            "source_observation_ids": self.source_observation_ids,
            "fact_count": self.fact_count,
            "subjects": self.subjects,
            "metadata": dict(self.metadata),
            "truth_established": False,
            "authority_granted": False,
            "permissions_granted": False,
        }


def build_world_model_snapshot(
    observation: WorldObservation,
    *,
    model_id: str,
    scope: str = "WORLD",
    metadata: Mapping[str, Any] | None = None,
) -> WorldModelSnapshot:
    """Project existing read-only world observations into bounded model facts."""
    if not isinstance(observation, WorldObservation):
        raise TypeError("observation must be a WorldObservation")
    if not isinstance(model_id, str) or not model_id.strip():
        raise ValueError("model_id must be a non-empty string")
    if not isinstance(scope, str) or not scope.strip():
        raise ValueError("scope must be a non-empty string")

    facts: list[WorldModelFact] = []
    observation_ids: list[str] = []
    for item in observation.agents:
        agent_id = item.agent.agent_id
        source_id = f"world-agent:{agent_id}:{observation.generated_at}"
        observation_ids.append(source_id)
        facts.extend(
            (
                WorldModelFact(f"{agent_id}:status", agent_id, "agent.status", item.agent.status.value, (source_id,)),
                WorldModelFact(f"{agent_id}:landscape", agent_id, "agent.landscape", item.agent.landscape.value, (source_id,)),
                WorldModelFact(f"{agent_id}:model", agent_id, "agent.model_id", item.agent.model_id, (source_id,)),
                WorldModelFact(f"{agent_id}:active", agent_id, "agent.active", item.active, (source_id,)),
            )
        )

    return WorldModelSnapshot(
        model_id=model_id.strip(),
        generated_at=observation.generated_at,
        scope=scope.strip(),
        facts=tuple(facts),
        source_observation_ids=tuple(observation_ids),
        metadata={"source": "M42", **dict(metadata or {})},
    )


__all__ = ["WorldModelFact", "WorldModelSnapshot", "build_world_model_snapshot"]
