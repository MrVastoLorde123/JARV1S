"""M28.15 runtime-owned composition of M9 worker execution into the JARVIS world.

This module does not replace M9 workforce or M8 execution. It owns the
lifetime of concrete AgentEntity projections for work that the canonical
runtime explicitly runs through the existing BoundedWorkerRuntime.

The retained state is the runtime's current world-facing projection, not a
second source of execution truth or an independent persistence store.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Mapping

from src.agency.agent_entity import AgentEntity, AgentLandscape, AgentStatus
from src.agency.agent_runtime import AgentRuntime
from src.agency.world_projection import WorldObservation, WorldObservationProjector
from src.agency.worker_runtime import BoundedWorkerRuntime, WorkerRuntimeResult
from src.agency.workforce import WorkerAssignment, WorkerRegistry
from src.context.execution_semantics import ExecutionPreparation
from src.context.working_context import WorkingContext


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


class AgentWorldRuntime:
    """Runtime-owned bridge from bounded worker execution to world observation."""

    def __init__(
        self,
        registry: WorkerRegistry,
        worker_runtime: BoundedWorkerRuntime,
        *,
        agent_runtime: AgentRuntime | None = None,
        projector: WorldObservationProjector | None = None,
    ) -> None:
        if not isinstance(registry, WorkerRegistry):
            raise TypeError("registry must be a WorkerRegistry")
        if not isinstance(worker_runtime, BoundedWorkerRuntime):
            raise TypeError("worker_runtime must be a BoundedWorkerRuntime")
        self._registry = registry
        self._worker_runtime = worker_runtime
        self._agent_runtime = agent_runtime or AgentRuntime(registry)
        self._projector = projector or WorldObservationProjector()
        self._agents: dict[str, AgentEntity] = {}

    @property
    def agents(self) -> tuple[AgentEntity, ...]:
        return tuple(self._agents.values())

    def instantiate(
        self,
        *,
        agent_id: str,
        display_name: str,
        assignment: WorkerAssignment,
        created_at: str | None = None,
        landscape: AgentLandscape = AgentLandscape.AGENTS,
        metadata: Mapping[str, Any] | None = None,
    ) -> AgentEntity:
        """Instantiate one concrete world agent after normal M9 assignment validation."""
        entity = self._agent_runtime.instantiate(
            agent_id=agent_id,
            display_name=display_name,
            assignment=assignment,
            created_at=created_at or _now(),
            landscape=landscape,
            metadata=metadata,
        )
        if entity.agent_id in self._agents:
            raise ValueError(f"agent_id '{entity.agent_id}' is already active in the runtime")
        self._agents[entity.agent_id] = entity
        return entity

    def begin_execution(self, agent_id: str, updated_at: str | None = None) -> AgentEntity:
        """Move an assigned agent into executing state immediately before M9 run."""
        agent = self._require_agent(agent_id)
        if agent.status is not AgentStatus.ASSIGNED:
            raise ValueError("only an assigned agent may begin execution")
        updated = agent.with_status(AgentStatus.EXECUTING, updated_at or _now())
        self._agents[agent_id] = updated
        return updated

    def run(
        self,
        *,
        agent_id: str,
        working_context: WorkingContext,
        initial_preparation: ExecutionPreparation,
        next_step_provider=None,
    ) -> WorkerRuntimeResult:
        """Execute the real M9 worker assignment while reflecting its lifecycle in the world."""
        agent = self._require_agent(agent_id)
        assignment = self._assignment_for(agent)
        if agent.status is not AgentStatus.ASSIGNED:
            raise ValueError("agent must be ASSIGNED before a worker run")

        self.begin_execution(agent_id)
        result = self._worker_runtime.run(
            assignment=assignment,
            working_context=working_context,
            initial_preparation=initial_preparation,
            next_step_provider=next_step_provider,
        )

        current = self._agents[agent_id]
        if result.succeeded:
            current = current.with_status(AgentStatus.RETURNING, _now())
            current = current.with_status(AgentStatus.HANDOFF, _now())
            current = current.with_status(AgentStatus.RETIRED, _now())
        elif result.observations:
            current = current.with_status(AgentStatus.RETURNING, _now())
            current = current.with_status(AgentStatus.HANDOFF, _now())
        else:
            current = current.with_status(AgentStatus.HANDOFF, _now())

        self._agents[agent_id] = current
        return result

    def observe(
        self,
        *,
        generated_at: str | None = None,
        focused_agent_id: str | None = None,
        current_landscape: AgentLandscape = AgentLandscape.OPERATIONS,
        metadata: Mapping[str, Any] | None = None,
    ) -> WorldObservation:
        """Project the runtime's current concrete agent entities into world state."""
        return self._projector.project(
            self._agents.values(),
            generated_at or _now(),
            focused_agent_id=focused_agent_id,
            current_landscape=current_landscape,
            metadata=metadata,
        )

    def get_agent(self, agent_id: str) -> AgentEntity:
        return self._require_agent(agent_id)

    def _require_agent(self, agent_id: str) -> AgentEntity:
        if not isinstance(agent_id, str) or not agent_id.strip():
            raise ValueError("agent_id must be a non-empty string")
        try:
            return self._agents[agent_id.strip()]
        except KeyError as exc:
            raise KeyError(f"unknown runtime agent: {agent_id}") from exc

    def _assignment_for(self, agent: AgentEntity) -> WorkerAssignment:
        worker_id = str(agent.metadata.get("worker_id", "")).strip()
        if not worker_id:
            raise ValueError("agent metadata does not contain worker_id")
        assignment = self._registry.get_assignment(agent.assignment_id)
        if assignment.worker_id != worker_id:
            raise ValueError("agent worker identity does not match assignment")
        return assignment


__all__ = ["AgentWorldRuntime"]
