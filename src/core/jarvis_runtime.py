"""M12.7 canonical JARVIS runtime facade with M28 world composition.

The canonical runtime remains the application-facing composition root. M28.15
adds an optional world-facing agency composition that reuses the existing M9
worker/delegation runtime and exposes only immutable observation outward to the
interface.
"""

from __future__ import annotations

from typing import Callable, Mapping

from src.agency.agent_entity import AgentEntity, AgentLandscape
from src.agency.delegation import DelegationPlan, DelegationResult
from src.agency.world_projection import WorldObservation
from src.agency.world_runtime import AgentWorldRuntime
from src.agency.workforce import WorkerAssignment
from src.context.execution_semantics import ExecutionPreparation
from src.context.working_context import WorkingContext
from src.core.conversation_store import ConversationStore
from src.core.event_integrated_runtime import EventIntegratedRuntime
from src.core.operational_control_plane import OperationalControlPlane
from src.core.recovery_integrated_runtime import RecoveryIntegratedResult, RecoveryIntegratedRuntime
from src.core.system_runtime import SystemRuntime
from src.runtime.operational_continuous_runtime import OperationalContinuousRuntime
from src.interface.boundary import InterfaceChannel, InterfaceRequest, InterfaceResponse
from src.interface.boundary import InterfaceChannel, InterfaceRequest, InterfaceResponse
from src.core.interface_backend import InterfaceResponseStatus
from src.interface.events import InterfaceEventRuntime
from src.interface.reliability import InterfaceReliabilityRuntime


class JARVISRuntime:
    """Canonical application-facing entrypoint for the integrated JARVIS runtime."""

    def __init__(
        self,
        recovery_runtime: RecoveryIntegratedRuntime,
        *,
        world_runtime: AgentWorldRuntime | None = None,
        operational_runtime: OperationalContinuousRuntime | None = None,
    ) -> None:
        if not isinstance(recovery_runtime, RecoveryIntegratedRuntime):
            raise TypeError("recovery_runtime must be a RecoveryIntegratedRuntime")
        if world_runtime is not None and not isinstance(world_runtime, AgentWorldRuntime):
            raise TypeError("world_runtime must be an AgentWorldRuntime or None")
        self._recovery_runtime = recovery_runtime
        self._world_runtime = world_runtime
        self._control_plane = OperationalControlPlane()
        if operational_runtime is not None and not isinstance(
            operational_runtime,
            OperationalContinuousRuntime,
        ):
            raise TypeError(
                "operational_runtime must be an OperationalContinuousRuntime or None"
            )
        self._operational_runtime = operational_runtime

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
        operational_runtime: OperationalContinuousRuntime | None = None,
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
        return cls(
            recovery_integrated_runtime,
            world_runtime=world_runtime,
            operational_runtime=operational_runtime,
        )

    @property
    def control_plane(self) -> OperationalControlPlane:
        return self._control_plane

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

    @property
    def operational_runtime(self) -> OperationalContinuousRuntime | None:
        return self._operational_runtime

    def submit_autonomous(self, goal: str, **kwargs):
        if self._operational_runtime is None:
            raise RuntimeError("JARVISRuntime has no operational autonomous runtime configured")
        return self._operational_runtime.submit(goal, **kwargs)

    def inspect_autonomous(self, job_id: str):
        if self._operational_runtime is None:
            raise RuntimeError("JARVISRuntime has no operational autonomous runtime configured")
        return self._operational_runtime.inspect(job_id)

    def resume_autonomous(self, job_id: str, **kwargs):
        if self._operational_runtime is None:
            raise RuntimeError("JARVISRuntime has no operational autonomous runtime configured")
        return self._operational_runtime.resume(job_id, **kwargs)

    def reconcile_autonomous(self, job_id: str, **kwargs):
        if self._operational_runtime is None:
            raise RuntimeError("JARVISRuntime has no operational autonomous runtime configured")
        return self._operational_runtime.reconcile_ambiguous_execution(job_id, **kwargs)

    def cancel_autonomous(self, job_id: str, reason: str = "Autonomous job cancelled"):
        if self._operational_runtime is None:
            raise RuntimeError("JARVISRuntime has no operational autonomous runtime configured")
        return self._operational_runtime.cancel(job_id, reason)

    def tick_autonomous(self, *args, **kwargs):
        if self._operational_runtime is None:
            raise RuntimeError("JARVISRuntime has no operational autonomous runtime configured")
        return self._operational_runtime.tick(*args, **kwargs)

    def start_autonomous_runtime(self) -> None:
        if self._operational_runtime is None:
            raise RuntimeError("JARVISRuntime has no operational autonomous runtime configured")
        self._operational_runtime.start()

    def stop_autonomous_runtime(self) -> None:
        if self._operational_runtime is not None:
            self._operational_runtime.stop()


    def coordinate_world_delegation(self, plan: DelegationPlan) -> DelegationResult:
        """Validate and order a real M9.5 delegation plan before world instantiation."""
        if self._world_runtime is None:
            raise RuntimeError("JARVISRuntime has no AgentWorldRuntime configured")
        return self._world_runtime.coordinate_delegation(plan)

    def instantiate_world_agents(
        self,
        plan: DelegationPlan,
        *,
        agent_id_factory: Callable[[WorkerAssignment, int], str],
        display_name_factory: Callable[[WorkerAssignment, int], str],
        created_at: str | None = None,
        landscape: AgentLandscape = AgentLandscape.AGENTS,
        metadata: Mapping[str, object] | None = None,
    ) -> tuple[AgentEntity, ...]:
        """Instantiate agents from deterministic M9.5 assignment order."""
        if self._world_runtime is None:
            raise RuntimeError("JARVISRuntime has no AgentWorldRuntime configured")
        return self._world_runtime.instantiate_delegated_agents(
            plan,
            agent_id_factory=agent_id_factory,
            display_name_factory=display_name_factory,
            created_at=created_at,
            landscape=landscape,
            metadata=metadata,
        )

    def observe_world(
        self,
        *,
        generated_at: str | None = None,
        focused_agent_id: str | None = None,
        current_landscape: AgentLandscape = AgentLandscape.OPERATIONS,
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
        request = InterfaceRequest(
            request_id=request_id,
            channel=channel,
            content=content,
            session_id=session_id,
            metadata={} if metadata is None else metadata,
        )
        return self.process(request)

    def process(self, request: InterfaceRequest) -> RecoveryIntegratedResult:
        """Process an existing interface request and project operational state."""
        if not isinstance(request, InterfaceRequest):
            raise TypeError("request must be an InterfaceRequest")

        self._control_plane.record_request(request)
        try:
            result = self._recovery_runtime.process(request)
            response = self._recovery_runtime.respond(result)
            self._control_plane.record_response(request, response)
            if self._operational_runtime is not None:
                self._operational_runtime.reconcile_confirmation(response.metadata)
            return result
        except Exception as exc:
            # Preserve the original control-flow/authority semantics while still
            # making failures visible to the observational control plane.
            self._control_plane.record_failure(request, exc)
            raise

    def respond(self, result: RecoveryIntegratedResult) -> InterfaceResponse:
        """Project a canonical result back to the interface boundary."""
        if not isinstance(result, RecoveryIntegratedResult):
            raise TypeError("result must be a RecoveryIntegratedResult")
        return self._recovery_runtime.respond(result)


__all__ = ["JARVISRuntime"]
