"""M28.12 world observation projection for the interface boundary.

The world projection reads existing backend entities and exposes one coherent,
read-only observation for the frontend. It does not create work or grant
authority.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any, Iterable, Mapping

from src.agency.agent_entity import AgentEntity, AgentLandscape, AgentStatus
from src.agency.agent_runtime import AgentHandoff, AgentRoute, EvidenceBundle, WorkLineage


@dataclass(frozen=True)
class WorldAgentObservation:
    """Everything the world needs to render one active agent."""

    agent: AgentEntity
    route: AgentRoute | None = None
    lineage: WorkLineage | None = None
    evidence: EvidenceBundle | None = None
    handoff: AgentHandoff | None = None

    @property
    def active(self) -> bool:
        return self.agent.status is not AgentStatus.RETIRED

    def to_context(self) -> dict[str, Any]:
        return {
            "agent": self.agent.to_context(),
            "route": None if self.route is None else self.route.to_context(),
            "lineage": None if self.lineage is None else self.lineage.to_context(),
            "evidence": None if self.evidence is None else self.evidence.to_context(),
            "handoff": None if self.handoff is None else self.handoff.to_context(),
            "active": self.active,
        }


@dataclass(frozen=True)
class WorldObservation:
    """Read-only world state derived from JARVIS backend state."""

    generated_at: str
    agents: tuple[WorldAgentObservation, ...] = ()
    focused_agent_id: str | None = None
    current_landscape: AgentLandscape = AgentLandscape.OPERATIONS
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.generated_at, str) or not self.generated_at.strip():
            raise ValueError("generated_at must be a non-empty string")
        if not isinstance(self.agents, tuple) or any(not isinstance(item, WorldAgentObservation) for item in self.agents):
            raise TypeError("agents must be a tuple of WorldAgentObservation values")
        ids = [item.agent.agent_id for item in self.agents]
        if len(ids) != len(set(ids)):
            raise ValueError("world agents must have unique agent identities")
        if self.focused_agent_id is not None and self.focused_agent_id not in ids:
            raise ValueError("focused_agent_id must reference an observed agent")
        if not isinstance(self.current_landscape, AgentLandscape):
            raise TypeError("current_landscape must be an AgentLandscape")
        if not isinstance(self.metadata, Mapping):
            raise TypeError("metadata must be a mapping")
        object.__setattr__(self, "metadata", MappingProxyType(dict(self.metadata)))

    @property
    def active_agents(self) -> tuple[WorldAgentObservation, ...]:
        return tuple(item for item in self.agents if item.active)

    @property
    def landscape_agents(self) -> Mapping[AgentLandscape, tuple[WorldAgentObservation, ...]]:
        grouped: dict[AgentLandscape, list[WorldAgentObservation]] = {item: [] for item in AgentLandscape}
        for observation in self.active_agents:
            grouped[observation.agent.landscape].append(observation)
        return MappingProxyType({key: tuple(value) for key, value in grouped.items()})

    def agents_in(self, landscape: AgentLandscape) -> tuple[WorldAgentObservation, ...]:
        if not isinstance(landscape, AgentLandscape):
            raise TypeError("landscape must be an AgentLandscape")
        return self.landscape_agents[landscape]

    def to_context(self) -> dict[str, Any]:
        return {
            "generated_at": self.generated_at,
            "agents": tuple(item.to_context() for item in self.agents),
            "focused_agent_id": self.focused_agent_id,
            "current_landscape": self.current_landscape.value,
            "active_agent_count": len(self.active_agents),
            "landscape_counts": {
                landscape.value: len(items) for landscape, items in self.landscape_agents.items()
            },
            "metadata": dict(self.metadata),
            "authority_granted": False,
            "permissions_granted": False,
        }


class WorldObservationProjector:
    """Compose world observations without inventing backend state."""

    def project(
        self,
        agents: Iterable[AgentEntity],
        generated_at: str,
        *,
        routes: Mapping[str, AgentRoute] | None = None,
        lineages: Mapping[str, WorkLineage] | None = None,
        evidence: Mapping[str, EvidenceBundle] | None = None,
        handoffs: Mapping[str, AgentHandoff] | None = None,
        focused_agent_id: str | None = None,
        current_landscape: AgentLandscape = AgentLandscape.OPERATIONS,
        metadata: Mapping[str, Any] | None = None,
    ) -> WorldObservation:
        route_lookup = dict(routes or {})
        lineage_lookup = dict(lineages or {})
        evidence_lookup = dict(evidence or {})
        handoff_lookup = dict(handoffs or {})

        observations: list[WorldAgentObservation] = []
        for agent in tuple(agents):
            if not isinstance(agent, AgentEntity):
                raise TypeError("agents must contain AgentEntity values")
            if agent.agent_id in route_lookup and route_lookup[agent.agent_id].agent_id != agent.agent_id:
                raise ValueError("agent route identity does not match agent identity")
            if agent.agent_id in lineage_lookup:
                lineage = lineage_lookup[agent.agent_id]
                if lineage.agent_id is not None and lineage.agent_id != agent.agent_id:
                    raise ValueError("lineage identity does not match agent identity")
            bundle = evidence_lookup.get(agent.agent_id)
            if bundle is not None and bundle.agent_id != agent.agent_id:
                raise ValueError("evidence bundle identity does not match agent identity")
            handoff = handoff_lookup.get(agent.agent_id)
            if handoff is not None and handoff.agent_id != agent.agent_id:
                raise ValueError("handoff identity does not match agent identity")
            observations.append(
                WorldAgentObservation(
                    agent=agent,
                    route=route_lookup.get(agent.agent_id),
                    lineage=lineage_lookup.get(agent.agent_id),
                    evidence=bundle,
                    handoff=handoff,
                )
            )

        return WorldObservation(
            generated_at=generated_at,
            agents=tuple(observations),
            focused_agent_id=focused_agent_id,
            current_landscape=current_landscape,
            metadata=dict(metadata or {}),
        )
