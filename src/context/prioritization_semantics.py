"""Semantic contract for prioritizing attention after interpretation.

M7.3 defines attention as a non-authoritative ordering decision. It ranks
context and interpretation targets for the current request without granting
authority, selecting tools, authorizing actions, executing anything, or
mutating state.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Mapping

from src.context.interpretation_semantics import Interpretation, InterpretationStatus
from src.context.reasoning_semantics import ReasoningContext


class PriorityKind(str, Enum):
    INPUT = "input"
    OBSERVATION = "observation"
    CLAIM = "claim"
    UNCERTAINTY = "uncertainty"
    CONFLICT = "conflict"
    MISSING_INFORMATION = "missing_information"
    EXECUTION_STATE = "execution_state"


@dataclass(frozen=True)
class PrioritySignal:
    relevance: float = 0.0
    urgency: float = 0.0
    importance: float = 0.0
    user_intent: float = 0.0
    unresolved: float = 0.0
    conflict: float = 0.0
    execution: float = 0.0

    def __post_init__(self):
        for name in (
            "relevance", "urgency", "importance", "user_intent",
            "unresolved", "conflict", "execution",
        ):
            value = getattr(self, name)
            if not isinstance(value, (int, float)) or isinstance(value, bool):
                raise TypeError(f"{name} must be a number.")
            if not 0.0 <= value <= 1.0:
                raise ValueError(f"{name} must be between 0.0 and 1.0.")

    @property
    def score(self) -> float:
        return (
            self.relevance * 0.25
            + self.urgency * 0.15
            + self.importance * 0.15
            + self.user_intent * 0.15
            + self.unresolved * 0.10
            + self.conflict * 0.10
            + self.execution * 0.10
        )


@dataclass(frozen=True)
class PriorityTarget:
    target_id: str
    kind: PriorityKind
    description: str
    signal: PrioritySignal
    rank: int
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if not isinstance(self.target_id, str) or not self.target_id.strip():
            raise ValueError("target_id must be a non-empty string.")
        if not isinstance(self.kind, PriorityKind):
            raise TypeError("kind must be a PriorityKind value.")
        if not isinstance(self.description, str) or not self.description.strip():
            raise ValueError("description must be a non-empty string.")
        if not isinstance(self.signal, PrioritySignal):
            raise TypeError("signal must be a PrioritySignal.")
        if not isinstance(self.rank, int) or isinstance(self.rank, bool) or self.rank < 0:
            raise ValueError("rank must be a non-negative integer.")
        if not isinstance(self.metadata, Mapping):
            raise TypeError("metadata must be a mapping.")


@dataclass(frozen=True)
class Prioritization:
    request: str
    targets: tuple[PriorityTarget, ...] = ()
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if not isinstance(self.request, str) or not self.request.strip():
            raise ValueError("request must be a non-empty string.")
        if not isinstance(self.targets, tuple):
            raise TypeError("targets must be a tuple.")
        if any(not isinstance(target, PriorityTarget) for target in self.targets):
            raise TypeError("targets must contain PriorityTarget values.")
        ranks = tuple(target.rank for target in self.targets)
        if ranks != tuple(range(len(self.targets))):
            raise ValueError("target ranks must be contiguous starting at zero.")
        if not isinstance(self.metadata, Mapping):
            raise TypeError("metadata must be a mapping.")

    def to_context(self) -> dict[str, Any]:
        return {
            "request": self.request,
            "targets": tuple(
                {
                    "target_id": target.target_id,
                    "kind": target.kind.value,
                    "description": target.description,
                    "signal": {
                        "relevance": target.signal.relevance,
                        "urgency": target.signal.urgency,
                        "importance": target.signal.importance,
                        "user_intent": target.signal.user_intent,
                        "unresolved": target.signal.unresolved,
                        "conflict": target.signal.conflict,
                        "execution": target.signal.execution,
                        "score": target.signal.score,
                    },
                    "rank": target.rank,
                    "metadata": dict(target.metadata),
                }
                for target in self.targets
            ),
            "metadata": dict(self.metadata),
        }


class PrioritizationProjector:
    """Project reasoning and interpretation into non-authoritative attention targets."""

    def project(
        self,
        reasoning_context: ReasoningContext,
        interpretation: Interpretation | None = None,
    ) -> Prioritization:
        if not isinstance(reasoning_context, ReasoningContext):
            raise TypeError("reasoning_context must be a ReasoningContext.")
        if interpretation is not None and not isinstance(interpretation, Interpretation):
            raise TypeError("interpretation must be an Interpretation or None.")
        if interpretation is not None and interpretation.request != reasoning_context.request:
            raise ValueError("interpretation request must match reasoning context request.")

        candidates = []
        for index, item in enumerate(reasoning_context.inputs):
            candidates.append((
                f"input:{index}", PriorityKind.INPUT, str(item.content),
                PrioritySignal(
                    relevance=item.relevance_score or 0.0,
                    importance=item.importance or 0.0,
                    user_intent=1.0 if index == 0 else 0.0,
                ),
            ))

        for index, item in enumerate(reasoning_context.observations):
            candidates.append((
                f"observation:{index}", PriorityKind.OBSERVATION, str(item.content),
                PrioritySignal(
                    relevance=item.relevance_score or 0.0,
                    importance=item.importance or 0.0,
                    urgency=0.5,
                ),
            ))

        if interpretation is not None:
            for index, claim in enumerate(interpretation.claims):
                candidates.append((
                    f"claim:{index}", PriorityKind.CLAIM, claim.claim,
                    PrioritySignal(
                        relevance=claim.confidence or 0.0,
                        unresolved=1.0 if claim.status is not InterpretationStatus.SUPPORTED else 0.0,
                        conflict=1.0 if claim.status is InterpretationStatus.CONFLICTED else 0.0,
                    ),
                ))
            for index, uncertainty in enumerate(interpretation.uncertainties):
                candidates.append((
                    f"uncertainty:{index}", PriorityKind.UNCERTAINTY, uncertainty.description,
                    PrioritySignal(urgency=uncertainty.severity or 0.0, unresolved=1.0),
                ))
            for index, conflict in enumerate(interpretation.conflicts):
                candidates.append((
                    f"conflict:{index}", PriorityKind.CONFLICT, conflict.description,
                    PrioritySignal(urgency=0.75, unresolved=1.0, conflict=1.0),
                ))
            for index, missing in enumerate(interpretation.missing_information):
                candidates.append((
                    f"missing:{index}", PriorityKind.MISSING_INFORMATION, missing.description,
                    PrioritySignal(importance=missing.importance or 0.0, unresolved=1.0),
                ))

        execution = (
            reasoning_context.current_state.get("execution_state")
            if reasoning_context.current_state is not None
            else None
        )
        if execution is not None:
            candidates.append((
                "execution_state", PriorityKind.EXECUTION_STATE,
                str(execution.get("status", "unknown")),
                PrioritySignal(execution=1.0, urgency=0.5, unresolved=0.5),
            ))

        ordered = sorted(candidates, key=lambda value: (-value[3].score, value[0]))
        targets = tuple(
            PriorityTarget(target_id, kind, description, signal, rank)
            for rank, (target_id, kind, description, signal) in enumerate(ordered)
        )
        return Prioritization(
            request=reasoning_context.request,
            targets=targets,
            metadata={"prioritization_semantics": "m7.3"},
        )


class PrioritizationValidator:
    """Validate attention ordering without granting execution authority."""

    def validate(self, reasoning_context: ReasoningContext, prioritization: Prioritization) -> None:
        if not isinstance(reasoning_context, ReasoningContext):
            raise TypeError("reasoning_context must be a ReasoningContext.")
        if not isinstance(prioritization, Prioritization):
            raise TypeError("prioritization must be a Prioritization.")
        if prioritization.request != reasoning_context.request:
            raise ValueError("prioritization request must match reasoning context request.")
        scores = tuple(target.signal.score for target in prioritization.targets)
        if scores != tuple(sorted(scores, reverse=True)):
            raise ValueError("priority targets must be ordered by descending attention score.")
        if len({target.target_id for target in prioritization.targets}) != len(prioritization.targets):
            raise ValueError("priority target IDs must be unique.")
