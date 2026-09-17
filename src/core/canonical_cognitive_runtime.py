"""CS1 canonical cognitive runtime composition.

This module composes existing Phase 6-9 advisory boundaries into the live
request path without creating a new authority or execution system.

The runtime performs:

    context -> world model -> reasoning -> planning decision support
    -> proactive initiative / proposal

It does not confirm, authorize, execute, schedule delivery, persist learning,
establish truth, or establish certainty.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Callable, Mapping

from src.core.planning_decision import (
    CandidatePlan,
    Goal,
    PlannedStep,
    PlanningContext,
    PlanningDecisionSystem,
    PlanningResult,
)
from src.core.proactive_initiative import (
    ProactiveInitiativeContext,
    ProactiveInitiativeResult,
    ProactiveInitiativeSystem,
)
from src.core.reasoning import (
    Hypothesis,
    ReasoningContext,
    ReasoningResult,
    ReasoningSystem,
)
from src.core.world_model import WorldModelSystem, WorldSnapshot


class CanonicalCognitiveRuntimeError(RuntimeError):
    """Raised when the canonical advisory cognition chain cannot complete."""


@dataclass(frozen=True)
class CanonicalCognitiveRequest:
    """Bounded request envelope for one canonical cognition pass."""

    request_id: str
    query: str
    created_at: str
    context_ids: tuple[str, ...] = ()
    memory_ids: tuple[str, ...] = ()
    metadata: Mapping[str, object] = None  # type: ignore[assignment]

    def __post_init__(self) -> None:
        for name in ("request_id", "query", "created_at"):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string")
        try:
            parsed = datetime.fromisoformat(self.created_at.replace("Z", "+00:00"))
        except ValueError as exc:
            raise ValueError("created_at must be ISO-8601") from exc
        if parsed.tzinfo is None:
            raise ValueError("created_at must include a timezone offset")
        for name in ("context_ids", "memory_ids"):
            values = getattr(self, name)
            if not isinstance(values, tuple) or any(
                not isinstance(item, str) or not item.strip() for item in values
            ):
                raise TypeError(f"{name} must be a tuple of non-empty strings")
            if len(set(values)) != len(values):
                raise ValueError(f"{name} must not contain duplicates")
        metadata = {} if self.metadata is None else self.metadata
        if not isinstance(metadata, Mapping):
            raise TypeError("metadata must be mapping-compatible")
        object.__setattr__(self, "metadata", dict(metadata))


@dataclass(frozen=True)
class CanonicalCognitiveResult:
    """Inspectable result of the Phase 6-9 canonical cognition chain."""

    request: CanonicalCognitiveRequest
    world_snapshot: WorldSnapshot
    reasoning: ReasoningResult
    planning: PlanningResult
    initiative: ProactiveInitiativeResult
    stage_sequence: tuple[str, ...]
    lineage: Mapping[str, str | None]

    def __post_init__(self) -> None:
        if not isinstance(self.request, CanonicalCognitiveRequest):
            raise TypeError("request must be a CanonicalCognitiveRequest")
        if not isinstance(self.world_snapshot, WorldSnapshot):
            raise TypeError("world_snapshot must be a WorldSnapshot")
        if not isinstance(self.reasoning, ReasoningResult):
            raise TypeError("reasoning must be a ReasoningResult")
        if not isinstance(self.planning, PlanningResult):
            raise TypeError("planning must be a PlanningResult")
        if not isinstance(self.initiative, ProactiveInitiativeResult):
            raise TypeError("initiative must be a ProactiveInitiativeResult")
        expected = ("context", "world_model", "reasoning", "planning", "initiative")
        if self.stage_sequence != expected:
            raise ValueError("stage_sequence must preserve the canonical cognition order")
        if not isinstance(self.lineage, Mapping):
            raise TypeError("lineage must be mapping-compatible")
        object.__setattr__(self, "lineage", dict(self.lineage))

    @property
    def proposal_id(self) -> str | None:
        proposal = self.initiative.proposal
        return None if proposal is None else proposal.proposal_id

    @property
    def ready_for_downstream_validation(self) -> bool:
        return self.initiative.is_ready_for_downstream_validation

    def to_context(self) -> dict[str, object]:
        return {
            "request_id": self.request.request_id,
            "stage_sequence": self.stage_sequence,
            "lineage": dict(self.lineage),
            "world_snapshot_id": self.world_snapshot.snapshot_id,
            "reasoning_result_id": self.reasoning.context.request_id,
            "planning_context_id": self.planning.context.context_id,
            "proposal_id": self.proposal_id,
            "ready_for_downstream_validation": self.ready_for_downstream_validation,
            "authority_granted": False,
            "authorization_granted": False,
            "execution_requested": False,
            "execution_performed": False,
            "truth_established": False,
            "certainty_established": False,
        }


class CanonicalCognitiveRuntime:
    """Thin composition root for the existing advisory Phase 6-9 boundaries."""

    STAGE_SEQUENCE = ("context", "world_model", "reasoning", "planning", "initiative")

    def __init__(
        self,
        *,
        world_model: WorldModelSystem | None = None,
        reasoning: ReasoningSystem | None = None,
        planning: PlanningDecisionSystem | None = None,
        initiative: ProactiveInitiativeSystem | None = None,
        clock: Callable[[], datetime] | None = None,
    ) -> None:
        self.world_model = world_model or WorldModelSystem()
        self.reasoning = reasoning or ReasoningSystem()
        self.planning = planning or PlanningDecisionSystem()
        self.initiative = initiative or ProactiveInitiativeSystem()
        self.clock = clock or (lambda: datetime.now(timezone.utc))

        for name, value, expected in (
            ("world_model", self.world_model, WorldModelSystem),
            ("reasoning", self.reasoning, ReasoningSystem),
            ("planning", self.planning, PlanningDecisionSystem),
            ("initiative", self.initiative, ProactiveInitiativeSystem),
        ):
            if not isinstance(value, expected):
                raise TypeError(f"{name} must be a {expected.__name__}")
        if not callable(self.clock):
            raise TypeError("clock must be callable")

    @staticmethod
    def _request_id(query: str, created_at: str) -> str:
        payload = f"{created_at}\n{query}".encode("utf-8")
        return hashlib.sha256(payload).hexdigest()

    @staticmethod
    def _goal(query: str, request_id: str) -> Goal:
        return Goal(
            goal_id=f"goal-{request_id}",
            title="Advisory handling of the current request",
            desired_outcome=query,
            priority=0.5,
        )

    @staticmethod
    def _candidate(goal: Goal, query: str, request_id: str) -> CandidatePlan:
        return CandidatePlan(
            plan_id=f"plan-{request_id}",
            goal_id=goal.goal_id,
            steps=(
                PlannedStep(
                    step_id=f"step-{request_id}",
                    description=f"Review the request and prepare a safe next step: {query}",
                ),
            ),
            expected_benefit=0.5,
            effort=0.2,
            risk=0.1,
            confidence=0.5,
            assumptions=("The request remains subject to downstream validation and authorization.",),
        )

    def run(
        self,
        query: str,
        *,
        request_id: str | None = None,
        created_at: str | None = None,
        context_ids: tuple[str, ...] = (),
        memory_ids: tuple[str, ...] = (),
        metadata: Mapping[str, object] | None = None,
    ) -> CanonicalCognitiveResult:
        if not isinstance(query, str) or not query.strip():
            raise ValueError("query must be a non-empty string")
        now = created_at or self.clock().isoformat()
        request_identity = request_id or self._request_id(query.strip(), now)
        request = CanonicalCognitiveRequest(
            request_id=request_identity,
            query=query.strip(),
            created_at=now,
            context_ids=context_ids,
            memory_ids=memory_ids,
            metadata=metadata or {},
        )

        try:
            world_snapshot = self.world_model.snapshot(generated_at=now)

            reasoning_context = ReasoningContext(
                request_id=request.request_id,
                created_at=request.created_at,
                question=request.query,
                world_snapshot_id=world_snapshot.snapshot_id,
                world_version=world_snapshot.version,
                world_observation_ids=world_snapshot.observation_ids,
                memory_ids=request.memory_ids,
                assumptions=("World state is evidence-derived and not established truth.",),
                metadata={
                    **dict(request.metadata),
                    "context_ids": request.context_ids,
                },
            )
            hypothesis = Hypothesis(
                hypothesis_id=f"hypothesis-{request.request_id}",
                statement="The current request can be represented as an advisory planning objective.",
                prior=0.5,
                context=reasoning_context,
            )
            reasoning_result = self.reasoning.reason(
                reasoning_context,
                (hypothesis,),
                (),
            )

            goal = self._goal(request.query, request.request_id)
            candidate = self._candidate(goal, request.query, request.request_id)
            planning_context = PlanningContext(
                context_id=f"planning-{request.request_id}",
                created_at=request.created_at,
                world_snapshot=world_snapshot,
                reasoning_result=reasoning_result,
                goal=goal,
            )
            planning_result = self.planning.plan(planning_context, (candidate,))

            initiative_context = ProactiveInitiativeContext(
                planning_result=planning_result,
                candidate_plans={candidate.plan_id: candidate},
            )
            initiative_result = self.initiative.compose(initiative_context)
        except (TypeError, ValueError, RuntimeError) as exc:
            raise CanonicalCognitiveRuntimeError(
                f"canonical cognition failed closed for request {request.request_id}: {exc}"
            ) from exc

        lineage = {
            "request_id": request.request_id,
            "world_snapshot_id": world_snapshot.snapshot_id,
            "reasoning_result_id": reasoning_result.context.request_id,
            "planning_context_id": planning_result.context.context_id,
            "goal_id": planning_result.context.goal.goal_id,
            "selected_plan_id": planning_result.ranking.advisory_selected_plan_id,
            "proposal_id": initiative_result.proposal.proposal_id if initiative_result.proposal else None,
        }
        return CanonicalCognitiveResult(
            request=request,
            world_snapshot=world_snapshot,
            reasoning=reasoning_result,
            planning=planning_result,
            initiative=initiative_result,
            stage_sequence=self.STAGE_SEQUENCE,
            lineage=lineage,
        )

    @property
    def authorizes_execution(self) -> bool:
        return False

    @property
    def executes_capability(self) -> bool:
        return False

    @property
    def persists_state(self) -> bool:
        return False

    @property
    def establishes_truth(self) -> bool:
        return False

    @property
    def establishes_certainty(self) -> bool:
        return False


__all__ = [
    "CanonicalCognitiveRequest",
    "CanonicalCognitiveResult",
    "CanonicalCognitiveRuntime",
    "CanonicalCognitiveRuntimeError",
]
