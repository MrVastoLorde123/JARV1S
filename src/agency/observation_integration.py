"""M8.3 integration of execution observations into JARVIS context/state."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from src.agency.execution_runtime import ExecutionObservation
from src.context.models import ContextItem, OBSERVATION, PRIVATE
from src.context.working_context import WorkingContext


class ObservationConflictError(ValueError):
    """Raised when an execution observation identity conflicts with stored state."""


@dataclass(frozen=True)
class ExecutionObservationStore:
    """Immutable deterministic store for execution observations."""

    observations: tuple[ExecutionObservation, ...] = ()

    def __post_init__(self) -> None:
        if not isinstance(self.observations, tuple):
            raise TypeError("observations must be a tuple")
        seen: set[str] = set()
        for observation in self.observations:
            if not isinstance(observation, ExecutionObservation):
                raise TypeError("observations must contain ExecutionObservation values")
            if observation.execution_id in seen:
                raise ObservationConflictError(
                    f"execution observation '{observation.execution_id}' is already stored"
                )
            seen.add(observation.execution_id)

    def append(self, observation: ExecutionObservation) -> "ExecutionObservationStore":
        if not isinstance(observation, ExecutionObservation):
            raise TypeError("observation must be an ExecutionObservation")
        if any(item.execution_id == observation.execution_id for item in self.observations):
            raise ObservationConflictError(
                f"execution observation '{observation.execution_id}' is already stored"
            )
        return ExecutionObservationStore(self.observations + (observation,))

    def get(self, execution_id: str) -> ExecutionObservation | None:
        normalized = execution_id.strip() if isinstance(execution_id, str) else ""
        for observation in self.observations:
            if observation.execution_id == normalized:
                return observation
        return None

    def list(self) -> tuple[ExecutionObservation, ...]:
        return self.observations


class ExecutionObservationContextIntegrator:
    """Project execution observations into the existing WorkingContext model."""

    SOURCE_TYPE = OBSERVATION

    def __init__(self, store: ExecutionObservationStore | None = None) -> None:
        self._store = store or ExecutionObservationStore()

    @property
    def store(self) -> ExecutionObservationStore:
        return self._store

    def record(self, observation: ExecutionObservation) -> ContextItem:
        """Store one observation and return its context-safe projection."""
        self._store = self._store.append(observation)
        return self.to_context_item(observation)

    @classmethod
    def to_context_item(cls, observation: ExecutionObservation) -> ContextItem:
        if not isinstance(observation, ExecutionObservation):
            raise TypeError("observation must be an ExecutionObservation")

        context = observation.to_context()
        return ContextItem(
            source_type=cls.SOURCE_TYPE,
            content=str(context),
            relevance_score=1.0,
            confidence=1.0,
            importance=1.0,
            privacy_level=PRIVATE,
            provenance={
                "source_id": observation.execution_id,
                "execution_id": observation.execution_id,
                "operation": observation.operation,
                "status": observation.status.value,
                "observation_type": "execution_observation",
            },
        )

    def integrate(
        self,
        working_context: WorkingContext,
        observations: Iterable[ExecutionObservation] = (),
    ) -> WorkingContext:
        """Return a new context containing projections of recorded observations."""
        if not isinstance(working_context, WorkingContext):
            raise TypeError("working_context must be a WorkingContext")

        projected = list(working_context.observations)
        for observation in observations:
            self.record(observation)
            projected.append(self.to_context_item(observation))

        return WorkingContext(
            request=working_context.request,
            context_package=working_context.context_package,
            conversation_state=working_context.conversation_state,
            task=working_context.task,
            execution_state=working_context.execution_state,
            execution_progress=working_context.execution_progress,
            observations=tuple(projected),
            source_selection=working_context.source_selection,
            metadata={
                **dict(working_context.metadata),
                "execution_observation_integration": "m8.3",
            },
        )
