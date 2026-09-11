"""M28.11 composition of world-facing agents over the existing M9 workforce.

This module does not replace workforce, delegation, execution, or reporting.
It creates the world-facing projection of those existing contracts so the UI
can observe a real agent moving through JARVIS's environments.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any, Mapping

from src.agency.agent_entity import AgentEntity, AgentLandscape, AgentStatus
from src.agency.workforce import WorkerAssignment, WorkerDefinition, WorkerRegistry, WorkerReport


@dataclass(frozen=True)
class AgentRoute:
    """Ordered landscape movement for one concrete agent instance."""

    agent_id: str
    landmarks: tuple[AgentLandscape, ...]
    current_index: int = 0
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.agent_id, str) or not self.agent_id.strip():
            raise ValueError("agent_id must be a non-empty string")
        if not isinstance(self.landmarks, tuple) or not self.landmarks:
            raise ValueError("landmarks must be a non-empty tuple")
        if any(not isinstance(item, AgentLandscape) for item in self.landmarks):
            raise TypeError("landmarks must contain AgentLandscape values")
        if len(set(self.landmarks)) != len(self.landmarks):
            raise ValueError("landmarks must not contain duplicates")
        if not isinstance(self.current_index, int) or isinstance(self.current_index, bool):
            raise TypeError("current_index must be an integer")
        if self.current_index < 0 or self.current_index >= len(self.landmarks):
            raise ValueError("current_index is outside the route")
        if not isinstance(self.metadata, Mapping):
            raise TypeError("metadata must be a mapping")
        object.__setattr__(self, "metadata", MappingProxyType(dict(self.metadata)))

    @property
    def current(self) -> AgentLandscape:
        return self.landmarks[self.current_index]

    @property
    def destination(self) -> AgentLandscape | None:
        next_index = self.current_index + 1
        return self.landmarks[next_index] if next_index < len(self.landmarks) else None

    @property
    def complete(self) -> bool:
        return self.current_index == len(self.landmarks) - 1

    def advance(self) -> "AgentRoute":
        if self.complete:
            raise ValueError("agent route is already complete")
        return AgentRoute(
            agent_id=self.agent_id,
            landmarks=self.landmarks,
            current_index=self.current_index + 1,
            metadata=self.metadata,
        )

    def to_context(self) -> dict[str, Any]:
        return {
            "agent_id": self.agent_id,
            "landmarks": tuple(item.value for item in self.landmarks),
            "current": self.current.value,
            "destination": None if self.destination is None else self.destination.value,
            "current_index": self.current_index,
            "complete": self.complete,
            "metadata": dict(self.metadata),
            "authority_granted": False,
        }


@dataclass(frozen=True)
class WorkLineage:
    """Trace from user intent through bounded delegation to result handoff."""

    lineage_id: str
    request: str
    plan_id: str | None = None
    assignment_id: str | None = None
    agent_id: str | None = None
    execution_ids: tuple[str, ...] = ()
    evidence_ids: tuple[str, ...] = ()
    handoff_id: str | None = None
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        for name in ("lineage_id", "request"):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string")
        for name in ("plan_id", "assignment_id", "agent_id", "handoff_id"):
            value = getattr(self, name)
            if value is not None and (not isinstance(value, str) or not value.strip()):
                raise ValueError(f"{name} must be a non-empty string or None")
        for name in ("execution_ids", "evidence_ids"):
            values = getattr(self, name)
            if not isinstance(values, tuple) or any(not isinstance(item, str) or not item.strip() for item in values):
                raise TypeError(f"{name} must be a tuple of non-empty strings")
            if len(set(values)) != len(values):
                raise ValueError(f"{name} must not contain duplicates")
        if not isinstance(self.metadata, Mapping):
            raise TypeError("metadata must be a mapping")
        object.__setattr__(self, "metadata", MappingProxyType(dict(self.metadata)))

    def to_context(self) -> dict[str, Any]:
        return {
            "lineage_id": self.lineage_id,
            "request": self.request,
            "plan_id": self.plan_id,
            "assignment_id": self.assignment_id,
            "agent_id": self.agent_id,
            "execution_ids": self.execution_ids,
            "evidence_ids": self.evidence_ids,
            "handoff_id": self.handoff_id,
            "metadata": dict(self.metadata),
            "authority_granted": False,
            "truth_guaranteed": False,
        }


@dataclass(frozen=True)
class EvidenceReference:
    """A provenance-bearing reference to evidence produced by delegated work."""

    evidence_id: str
    source_id: str
    title: str
    locator: str = ""
    excerpt: str = ""
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        for name in ("evidence_id", "source_id", "title"):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string")
        for name in ("locator", "excerpt"):
            if not isinstance(getattr(self, name), str):
                raise TypeError(f"{name} must be a string")
        if not isinstance(self.metadata, Mapping):
            raise TypeError("metadata must be a mapping")
        object.__setattr__(self, "metadata", MappingProxyType(dict(self.metadata)))

    def to_context(self) -> dict[str, Any]:
        return {
            "evidence_id": self.evidence_id,
            "source_id": self.source_id,
            "title": self.title,
            "locator": self.locator,
            "excerpt": self.excerpt,
            "metadata": dict(self.metadata),
            "truth_guaranteed": False,
        }


@dataclass(frozen=True)
class EvidenceBundle:
    """Immutable evidence collection attached to an agent's assignment."""

    bundle_id: str
    agent_id: str
    assignment_id: str
    references: tuple[EvidenceReference, ...] = ()
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        for name in ("bundle_id", "agent_id", "assignment_id"):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string")
        if not isinstance(self.references, tuple) or any(not isinstance(item, EvidenceReference) for item in self.references):
            raise TypeError("references must be a tuple of EvidenceReference values")
        ids = [item.evidence_id for item in self.references]
        if len(ids) != len(set(ids)):
            raise ValueError("evidence references must have unique identities")
        if not isinstance(self.metadata, Mapping):
            raise TypeError("metadata must be a mapping")
        object.__setattr__(self, "metadata", MappingProxyType(dict(self.metadata)))

    def to_context(self) -> dict[str, Any]:
        return {
            "bundle_id": self.bundle_id,
            "agent_id": self.agent_id,
            "assignment_id": self.assignment_id,
            "references": tuple(item.to_context() for item in self.references),
            "metadata": dict(self.metadata),
            "truth_guaranteed": False,
        }


@dataclass(frozen=True)
class AgentHandoff:
    """Explicit result handoff from a worker instance back into JARVIS."""

    handoff_id: str
    agent_id: str
    assignment_id: str
    destination: str
    summary: str
    report_status: str
    evidence_bundle_id: str | None = None
    accepted: bool = False
    completed_at: str = ""
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        for name in ("handoff_id", "agent_id", "assignment_id", "destination", "summary", "report_status", "completed_at"):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string")
        if self.evidence_bundle_id is not None and (not isinstance(self.evidence_bundle_id, str) or not self.evidence_bundle_id.strip()):
            raise ValueError("evidence_bundle_id must be a non-empty string or None")
        if not isinstance(self.accepted, bool):
            raise TypeError("accepted must be a bool")
        if not isinstance(self.metadata, Mapping):
            raise TypeError("metadata must be a mapping")
        object.__setattr__(self, "metadata", MappingProxyType(dict(self.metadata)))

    def to_context(self) -> dict[str, Any]:
        return {
            "handoff_id": self.handoff_id,
            "agent_id": self.agent_id,
            "assignment_id": self.assignment_id,
            "destination": self.destination,
            "summary": self.summary,
            "report_status": self.report_status,
            "evidence_bundle_id": self.evidence_bundle_id,
            "accepted": self.accepted,
            "completed_at": self.completed_at,
            "metadata": dict(self.metadata),
            "authority_granted": False,
            "acceptance_is_not_truth": True,
        }


class AgentRuntime:
    """Compose WorkerRegistry + WorkerAssignment into an observable AgentEntity."""

    def __init__(self, registry: WorkerRegistry) -> None:
        if not isinstance(registry, WorkerRegistry):
            raise TypeError("registry must be a WorkerRegistry")
        self._registry = registry

    def instantiate(
        self,
        agent_id: str,
        display_name: str,
        assignment: WorkerAssignment,
        created_at: str,
        landscape: AgentLandscape = AgentLandscape.AGENTS,
        metadata: Mapping[str, Any] | None = None,
    ) -> AgentEntity:
        """Create an agent only after the existing worker boundary accepts the assignment."""
        worker = self._registry.validate_assignment(assignment)
        return AgentEntity(
            agent_id=agent_id,
            display_name=display_name,
            archetype=worker.worker_id,
            assignment_id=assignment.assignment_id,
            status=AgentStatus.ASSIGNED,
            landscape=landscape,
            capability_ids=assignment.allowed_capabilities,
            created_at=created_at,
            updated_at=created_at,
            metadata={
                "worker_id": worker.worker_id,
                "worker_name": worker.name,
                **dict(metadata or {}),
            },
        )

    def move(self, agent: AgentEntity, destination: AgentLandscape, updated_at: str) -> AgentEntity:
        self._require_agent(agent)
        return agent.move_to(destination, updated_at)

    def arrive(self, agent: AgentEntity, landscape: AgentLandscape, updated_at: str) -> AgentEntity:
        self._require_agent(agent)
        if agent.destination is not None and agent.destination is not landscape:
            raise ValueError("agent arrived at a landscape different from its declared destination")
        return agent.arrive(landscape, updated_at)

    def begin_return(self, agent: AgentEntity, updated_at: str) -> AgentEntity:
        self._require_agent(agent)
        if agent.status is not AgentStatus.EXECUTING:
            raise ValueError("only an executing agent may begin its return")
        return agent.with_status(AgentStatus.RETURNING, updated_at)

    def begin_handoff(self, agent: AgentEntity, updated_at: str) -> AgentEntity:
        self._require_agent(agent)
        if agent.status is not AgentStatus.RETURNING:
            raise ValueError("only a returning agent may enter handoff")
        return agent.with_status(AgentStatus.HANDOFF, updated_at)

    def retire(self, agent: AgentEntity, updated_at: str) -> AgentEntity:
        self._require_agent(agent)
        if agent.status is not AgentStatus.HANDOFF:
            raise ValueError("only a handoff agent may retire")
        return agent.with_status(AgentStatus.RETIRED, updated_at)

    def validate_report(self, agent: AgentEntity, assignment: WorkerAssignment, report: WorkerReport) -> None:
        self._require_agent(agent)
        if assignment.assignment_id != agent.assignment_id or assignment.worker_id != str(agent.metadata.get("worker_id", assignment.worker_id)):
            raise ValueError("agent, assignment, and worker identities do not compose")
        if report.assignment_id != assignment.assignment_id or report.worker_id != assignment.worker_id:
            raise ValueError("worker report does not belong to the agent assignment")

    @staticmethod
    def _require_agent(agent: AgentEntity) -> None:
        if not isinstance(agent, AgentEntity):
            raise TypeError("agent must be an AgentEntity")
