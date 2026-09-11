"""M12.7 canonical JARVIS runtime facade with M28 world composition.

The canonical runtime remains the application-facing composition root. M28.15
adds an optional world-facing agency composition that reuses the existing M9
worker runtime and exposes only immutable observation outward to the interface.
"""

from __future__ import annotations

from typing import Callable, Mapping

from src.agency.agent_entity import AgentEntity, AgentLandscape
from src.agency.world_projection import WorldObservation
from src.agency.world_runtime import AgentWorldRuntime
from src.agency.workforce import WorkerAssignment
from src.context.execution_semantics import ExecutionPreparation
from src.context.working_context import WorkingContext
from src.core.conversation_store import ConversationStore
from src.core.event_integrated_runtime import EventIntegratedRuntime
from src.core.recovery_integrated_runtime import RecoveryIntegratedResult, RecoveryIntegratedRuntime
from src.core.system_runtime import SystemRuntime
from src.interface.boundary import InterfaceChannel, InterfaceRequest, InterfaceResponse
from src.interface.events import InterfaceEventRuntime
from src.interface.reliability import InterfaceReliabilityRuntime


class JARVISRuntime:
    """Canonical application-facing entrypoint for the integrated JARVIS runtime."""

    def __init__(
        self,
        recovery_runtime: RecoveryIntegratedRuntime,
        *,
        world_runtime: AgentWorldRuntime | None = None,
    ) -> None:
        if not isinstance(recovery_runtime, RecoveryIntegratedRuntime):
            raise TypeError("recovery_runtime must be a RecoveryIntegratedRuntime")
        if world_runtime is not None and not isinstance(world_runtime, AgentWorldRuntime):
            raise TypeError("world_runtime must be an AgentWorldRuntime or None")
        self._recovery_runtime = recovery_runtime
        self._world_runtime = world_runtime

    @classmethod
    def from_processor(
        cls,
        processor,
        *,
        conversation_store: ConversationStore | None = None,
        durable_processor_factory=None,
        event_runtime: InterfaceEventRuntime | None = None,
        event_id_factory: Callable[[], str] | None = None,
        reliability_runtime: InterfaceReliabilityRuntime | None = None,
        recovery_id_factory: Callable[[], str] | None = None,
        world_runtime: AgentWorldRuntime | None = None,
    ) -> "JARVISRuntime":
        """Build the canonical runtime around one existing JARVIS processor."""
        system_runtime = SystemRuntime(
            processor,
            conversation_store=conversation_store,
            durable_processor_factory=durable_processor_factory,
        )
        event_integrated_runtime = EventIntegratedRuntime(
            system_runtime,
            event_runtime=event_runtime,
            event_id_factory=event_id_factory,
        )
        recovery_integrated_runtime = RecoveryIntegratedRuntime(
            event_integrated_runtime,
            reliability_runtime=reliability_runtime,
            recovery_id_factory=recovery_id_factory,
        )
        return cls(recovery_integrated_runtime, world_runtime=world_runtime)

    @property
    def recovery_runtime(self) -> RecoveryIntegratedRuntime:
        return self._recovery_runtime

    @property
    def event_integrated_runtime(self) -> EventIntegratedRuntime:
        return self._recovery_runtime.event_integrated_runtime

    @property
    def system_runtime(self) -> SystemRuntime:
        return self.event_integrated_runtime.system_runtime

    @property
    def world_runtime(self) -> AgentWorldRuntime | None:
        return self._world_runtime

    def observe_world(
        self,
        *,
        generated_at: str | None = None,
        focused_agent_id: str | None = None,
        current_landscape: AgentLandscape,
        metadata: Mapping[str, object] | None = None,
    ) -> WorldObservation:
        """Return the current runtime-owned world projection for transport/UI use."""
        if self._world_runtime is None:
            raise RuntimeError("JARVISRuntime has no AgentWorldRuntime configured")
        return self._world_runtime.observe(
            generated_at=generated_at,
            focused_agent_id=focused_agent_id,
            current_landscape=current_landscape,
            metadata=metadata,
        )

    def instantiate_world_agent(
        self,
        *,
        agent_id: str,
        display_name: str,
        assignment: WorkerAssignment,
        created_at: str | None = None,
        landscape: AgentLandscape = AgentLandscape.AGENTS,
        metadata: Mapping[str, object] | None = None,
    ) -> AgentEntity:
        """Create a concrete world agent through the existing M9 assignment boundary."""
        if self._world_runtime is None:
            raise RuntimeError("JARVISRuntime has no AgentWorldRuntime configured")
        return self._world_runtime.instantiate(
            agent_id=agent_id,
            display_name=display_name,
            assignment=assignment,
            created_at=created_at,
            landscape=landscape,
            metadata=metadata,
        )

    def run_world_agent(
        self,
        *,
        agent_id: str,
        working_context: WorkingContext,
        initial_preparation: ExecutionPreparation,
        next_step_provider=None,
    ):
        """Run one existing bounded M9 worker while updating its world lifecycle."""
        if self._world_runtime is None:
            raise RuntimeError("JARVISRuntime has no AgentWorldRuntime configured")
        return self._world_runtime.run(
            agent_id=agent_id,
            working_context=working_context,
            initial_preparation=initial_preparation,
            next_step_provider=next_step_provider,
        )

    def receive(
        self,
        *,
        request_id: str,
        channel: InterfaceChannel,
        content: str,
        session_id: str | None = None,
        metadata: dict[str, object] | None = None,
    ) -> RecoveryIntegratedResult:
        """Process interface traffic through the canonical integrated path."""
        return self._recovery_runtime.receive(
            request_id=request_id,
            channel=channel,
            content=content,
            session_id=session_id,
            metadata=metadata,
        )

    def process(self, request: InterfaceRequest) -> RecoveryIntegratedResult:
        """Process an existing interface request through the canonical path."""
        if not isinstance(request, InterfaceRequest):
            raise TypeError("request must be an InterfaceRequest")
        return self._recovery_runtime.process(request)

    def respond(self, result: RecoveryIntegratedResult) -> InterfaceResponse:
        """Project a canonical result back to the interface boundary."""
        if not isinstance(result, RecoveryIntegratedResult):
            raise TypeError("result must be a RecoveryIntegratedResult")
        return self._recovery_runtime.respond(result)


__all__ = ["JARVISRuntime"]
