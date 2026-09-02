"""M8.5 bounded multi-step agency orchestration.

M8.5 coordinates multiple individually authorized execution handoffs. The
coordinator owns sequencing and bounds, but it never creates authority,
selects a capability, invokes a plugin directly, or turns one observation
into permission for another action.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Callable, Protocol

from src.agency.execution_lifecycle import ExecutionLifecycle
from src.agency.execution_runtime import ExecutionObservation, ExecutionRuntime
from src.agency.observation_integration import ExecutionObservationContextIntegrator
from src.context.execution_semantics import ExecutionPreparation, ExecutionPreparationStatus
from src.context.working_context import WorkingContext


class AgencyStopReason(str, Enum):
    """Deterministic reason a bounded agency run stopped."""

    COMPLETED = "completed"
    STEP_LIMIT_REACHED = "step_limit_reached"
    INITIAL_PREPARATION_BLOCKED = "initial_preparation_blocked"
    NEXT_PREPARATION_BLOCKED = "next_preparation_blocked"
    INVALID_PREPARATION = "invalid_preparation"
    DUPLICATE_EXECUTION_ID = "duplicate_execution_id"
    EXECUTION_FAILED = "execution_failed"
    NO_NEXT_STEP = "no_next_step"
    STEP_PROVIDER_ERROR = "step_provider_error"


class AgencyStepProvider(Protocol):
    """Provider of the next already-authorized execution preparation."""

    def next_preparation(
        self,
        working_context: WorkingContext,
        previous_observation: ExecutionObservation,
    ) -> ExecutionPreparation | None:
        """Return the next M7 preparation, or None to stop."""
        ...


@dataclass(frozen=True)
class ControlledAgencyResult:
    """Immutable record of one bounded multi-step agency run."""

    observations: tuple[ExecutionObservation, ...]
    lifecycles: tuple[ExecutionLifecycle, ...]
    working_context: WorkingContext
    stop_reason: AgencyStopReason

    @property
    def steps_executed(self) -> int:
        return len(self.observations)

    @property
    def succeeded(self) -> bool:
        return self.stop_reason is AgencyStopReason.COMPLETED

    def to_context(self) -> dict[str, object]:
        """Serialize the run without manufacturing an authority grant."""
        return {
            "steps_executed": self.steps_executed,
            "stop_reason": self.stop_reason.value,
            "observations": tuple(item.to_context() for item in self.observations),
            "lifecycles": tuple(item.to_context() for item in self.lifecycles),
            "working_context": self.working_context.to_context(),
        }


class ControlledAgency:
    """Run a finite sequence of independently authorized execution handoffs."""

    def __init__(
        self,
        runtime: ExecutionRuntime,
        observation_integrator: ExecutionObservationContextIntegrator,
        max_steps: int,
        next_step_provider: AgencyStepProvider | None = None,
    ) -> None:
        if not isinstance(runtime, ExecutionRuntime):
            raise TypeError("runtime must be an ExecutionRuntime.")
        if not isinstance(observation_integrator, ExecutionObservationContextIntegrator):
            raise TypeError("observation_integrator must be an ExecutionObservationContextIntegrator.")
        if not isinstance(max_steps, int) or isinstance(max_steps, bool) or max_steps <= 0:
            raise ValueError("max_steps must be a positive integer.")
        if next_step_provider is not None and not callable(getattr(next_step_provider, "next_preparation", None)):
            raise TypeError("next_step_provider must expose next_preparation(working_context, previous_observation).")

        self._runtime = runtime
        self._integrator = observation_integrator
        self._max_steps = max_steps
        self._next_step_provider = next_step_provider

    def run(
        self,
        working_context: WorkingContext,
        initial_preparation: ExecutionPreparation,
    ) -> ControlledAgencyResult:
        """Execute bounded steps; every step must be a distinct M7 READY handoff."""
        if not isinstance(working_context, WorkingContext):
            raise TypeError("working_context must be a WorkingContext.")
        if not isinstance(initial_preparation, ExecutionPreparation):
            raise TypeError("initial_preparation must be an ExecutionPreparation.")

        if initial_preparation.status is not ExecutionPreparationStatus.READY:
            return ControlledAgencyResult(
                observations=(),
                lifecycles=(),
                working_context=working_context,
                stop_reason=AgencyStopReason.INITIAL_PREPARATION_BLOCKED,
            )

        observations: list[ExecutionObservation] = []
        lifecycles: list[ExecutionLifecycle] = []
        seen_execution_ids: set[str] = set()
        context = working_context
        preparation: ExecutionPreparation | None = initial_preparation

        while preparation is not None:
            if len(observations) >= self._max_steps:
                return ControlledAgencyResult(
                    observations=tuple(observations),
                    lifecycles=tuple(lifecycles),
                    working_context=context,
                    stop_reason=AgencyStopReason.STEP_LIMIT_REACHED,
                )

            if not isinstance(preparation, ExecutionPreparation):
                return ControlledAgencyResult(
                    observations=tuple(observations),
                    lifecycles=tuple(lifecycles),
                    working_context=context,
                    stop_reason=AgencyStopReason.INVALID_PREPARATION,
                )

            if preparation.status is not ExecutionPreparationStatus.READY:
                reason = (
                    AgencyStopReason.INITIAL_PREPARATION_BLOCKED
                    if not observations
                    else AgencyStopReason.NEXT_PREPARATION_BLOCKED
                )
                return ControlledAgencyResult(
                    observations=tuple(observations),
                    lifecycles=tuple(lifecycles),
                    working_context=context,
                    stop_reason=reason,
                )

            if preparation.execution_id in seen_execution_ids:
                return ControlledAgencyResult(
                    observations=tuple(observations),
                    lifecycles=tuple(lifecycles),
                    working_context=context,
                    stop_reason=AgencyStopReason.DUPLICATE_EXECUTION_ID,
                )

            seen_execution_ids.add(preparation.execution_id)
            lifecycle = ExecutionLifecycle.start(preparation.execution_id).start_running()
            observation = self._runtime.execute(preparation)
            lifecycle = lifecycle.apply_observation(observation)
            observations.append(observation)
            lifecycles.append(lifecycle)
            context = self._integrator.integrate(context, (observation,))

            if len(observations) >= self._max_steps:
                return ControlledAgencyResult(
                    observations=tuple(observations),
                    lifecycles=tuple(lifecycles),
                    working_context=context,
                    stop_reason=AgencyStopReason.STEP_LIMIT_REACHED,
                )

            provider = self._next_step_provider
            if provider is None:
                stop_reason = (
                    AgencyStopReason.COMPLETED
                    if observation.succeeded
                    else AgencyStopReason.EXECUTION_FAILED
                )
                return ControlledAgencyResult(
                    observations=tuple(observations),
                    lifecycles=tuple(lifecycles),
                    working_context=context,
                    stop_reason=stop_reason,
                )

            try:
                preparation = provider.next_preparation(context, observation)
            except Exception:
                return ControlledAgencyResult(
                    observations=tuple(observations),
                    lifecycles=tuple(lifecycles),
                    working_context=context,
                    stop_reason=AgencyStopReason.STEP_PROVIDER_ERROR,
                )

            if preparation is None:
                stop_reason = (
                    AgencyStopReason.COMPLETED
                    if observation.succeeded
                    else AgencyStopReason.EXECUTION_FAILED
                )
                return ControlledAgencyResult(
                    observations=tuple(observations),
                    lifecycles=tuple(lifecycles),
                    working_context=context,
                    stop_reason=stop_reason,
                )

        return ControlledAgencyResult(
            observations=tuple(observations),
            lifecycles=tuple(lifecycles),
            working_context=context,
            stop_reason=AgencyStopReason.NO_NEXT_STEP,
        )
