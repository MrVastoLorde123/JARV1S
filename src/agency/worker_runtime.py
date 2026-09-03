"""M9.2 bounded worker runtime.

Workers operate inside explicit M9.1 assignments, but they do not own
authority. Each executable action must already arrive as a READY M7
ExecutionPreparation and is consumed through the existing M8 ExecutionRuntime.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from src.agency.controlled_agency import AgencyStopReason, ControlledAgency
from src.agency.execution_lifecycle import ExecutionLifecycle
from src.agency.execution_runtime import ExecutionObservation, ExecutionRuntime
from src.agency.observation_integration import ExecutionObservationContextIntegrator
from src.agency.workforce import WorkerAssignment, WorkerDefinition, WorkerRegistry, WorkerReport, WorkerReportStatus
from src.context.execution_semantics import ExecutionPreparation, ExecutionPreparationStatus
from src.context.working_context import WorkingContext


class WorkerStepProvider(Protocol):
    """Provider of already-authorized M7 preparations for one worker assignment."""

    def next_preparation(
        self,
        worker_context: WorkingContext,
        previous_observation: ExecutionObservation | None,
    ) -> ExecutionPreparation | None:
        """Return the next already-authorized preparation or stop."""
        ...


@dataclass(frozen=True)
class WorkerRuntimeResult:
    """Immutable result of one bounded worker run."""

    worker: WorkerDefinition
    assignment: WorkerAssignment
    observations: tuple[ExecutionObservation, ...]
    lifecycles: tuple[ExecutionLifecycle, ...]
    working_context: WorkingContext
    report: WorkerReport
    stop_reason: AgencyStopReason

    @property
    def succeeded(self) -> bool:
        return self.report.status is WorkerReportStatus.COMPLETED


class BoundedWorkerRuntime:
    """Run a worker only within its registered bounds and M7/M8 execution path."""

    def __init__(
        self,
        registry: WorkerRegistry,
        execution_runtime: ExecutionRuntime,
        observation_integrator: ExecutionObservationContextIntegrator,
    ) -> None:
        if not isinstance(registry, WorkerRegistry):
            raise TypeError("registry must be a WorkerRegistry.")
        if not isinstance(execution_runtime, ExecutionRuntime):
            raise TypeError("execution_runtime must be an ExecutionRuntime.")
        if not isinstance(observation_integrator, ExecutionObservationContextIntegrator):
            raise TypeError("observation_integrator must be an ExecutionObservationContextIntegrator.")
        self._registry = registry
        self._execution_runtime = execution_runtime
        self._observation_integrator = observation_integrator

    def run(
        self,
        assignment: WorkerAssignment,
        working_context: WorkingContext,
        initial_preparation: ExecutionPreparation | None = None,
        next_step_provider: WorkerStepProvider | None = None,
    ) -> WorkerRuntimeResult:
        """Execute a bounded worker assignment through M8; authority stays upstream."""
        if not isinstance(assignment, WorkerAssignment):
            raise TypeError("assignment must be a WorkerAssignment.")
        if not isinstance(working_context, WorkingContext):
            raise TypeError("working_context must be a WorkingContext.")
        worker = self._registry.validate_assignment(assignment)

        if initial_preparation is None:
            report = WorkerReport(
                assignment_id=assignment.assignment_id,
                worker_id=assignment.worker_id,
                status=WorkerReportStatus.BLOCKED,
                summary="worker run requires an initial M7 execution preparation",
            )
            return WorkerRuntimeResult(
                worker=worker,
                assignment=assignment,
                observations=(),
                lifecycles=(),
                working_context=working_context,
                report=report,
                stop_reason=AgencyStopReason.INITIAL_PREPARATION_BLOCKED,
            )

        if initial_preparation.status is not ExecutionPreparationStatus.READY:
            report = WorkerReport(
                assignment_id=assignment.assignment_id,
                worker_id=assignment.worker_id,
                status=WorkerReportStatus.BLOCKED,
                summary="initial worker execution preparation is not READY",
            )
            return WorkerRuntimeResult(
                worker=worker,
                assignment=assignment,
                observations=(),
                lifecycles=(),
                working_context=working_context,
                report=report,
                stop_reason=AgencyStopReason.INITIAL_PREPARATION_BLOCKED,
            )

        if initial_preparation.execution_request is None:
            raise ValueError("READY initial_preparation must contain an execution request.")
        if initial_preparation.execution_request.operation not in assignment.allowed_capabilities:
            raise ValueError("initial execution operation exceeds worker assignment capability bounds.")

        provider = _BoundedWorkerStepProvider(next_step_provider, assignment)
        agency = ControlledAgency(
            runtime=self._execution_runtime,
            observation_integrator=self._observation_integrator,
            max_steps=min(worker.max_steps, assignment.max_steps),
            next_step_provider=provider if next_step_provider is not None else None,
        )
        result = agency.run(working_context, initial_preparation)

        if result.stop_reason is AgencyStopReason.COMPLETED:
            report_status = WorkerReportStatus.COMPLETED
        elif result.observations:
            report_status = (
                WorkerReportStatus.PARTIAL
                if result.observations[-1].succeeded
                else WorkerReportStatus.FAILED
            )
        else:
            report_status = WorkerReportStatus.BLOCKED

        report = WorkerReport(
            assignment_id=assignment.assignment_id,
            worker_id=worker.worker_id,
            status=report_status,
            outputs={
                "steps_executed": result.steps_executed,
                "stop_reason": result.stop_reason.value,
            },
            summary=f"worker run stopped: {result.stop_reason.value}",
            metadata={"worker_runtime": "m9.2"},
        )
        return WorkerRuntimeResult(
            worker=worker,
            assignment=assignment,
            observations=result.observations,
            lifecycles=result.lifecycles,
            working_context=result.working_context,
            report=report,
            stop_reason=result.stop_reason,
        )


class _BoundedWorkerStepProvider:
    """Validate every subsequent preparation against the same worker assignment."""

    def __init__(self, provider: WorkerStepProvider, assignment: WorkerAssignment) -> None:
        self._provider = provider
        self._assignment = assignment

    def next_preparation(
        self,
        working_context: WorkingContext,
        previous_observation: ExecutionObservation,
    ) -> ExecutionPreparation | None:
        preparation = self._provider.next_preparation(working_context, previous_observation)
        if preparation is None:
            return None
        if not isinstance(preparation, ExecutionPreparation):
            return preparation
        if preparation.status is ExecutionPreparationStatus.READY:
            request = preparation.execution_request
            if request is not None and request.operation not in self._assignment.allowed_capabilities:
                raise ValueError("next execution operation exceeds worker assignment capability bounds.")
        return preparation
