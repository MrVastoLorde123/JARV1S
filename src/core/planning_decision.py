"""M109-M116: bounded goals, planning, and decision-support boundary.

Planning consumes bounded world context and reasoning outputs and produces
candidate plans, feasibility assessments, deterministic advisory ranking, and
an inspectable planning result. It does not authorize or execute a plan.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Mapping

from src.core.reasoning import ReasoningResult
from src.core.world_model import WorldSnapshot


class PlanningValidationError(ValueError):
    """Raised when planning contracts are structurally invalid."""


class GoalStatus(str, Enum):
    ACTIVE = "ACTIVE"
    PAUSED = "PAUSED"
    COMPLETED = "COMPLETED"
    ABANDONED = "ABANDONED"


class PlanFeasibility(str, Enum):
    FEASIBLE = "FEASIBLE"
    BLOCKED = "BLOCKED"
    REVIEW = "REVIEW"


def _parse_timestamp(value: str) -> datetime:
    if not isinstance(value, str) or not value.strip():
        raise PlanningValidationError("timestamp must be a non-empty string")
    try:
        parsed = datetime.fromisoformat(value.strip().replace("Z", "+00:00"))
    except ValueError as exc:
        raise PlanningValidationError(f"invalid ISO-8601 timestamp: {value!r}") from exc
    if parsed.tzinfo is None:
        raise PlanningValidationError("timestamp must include a timezone offset")
    return parsed


def _score(value: float, field_name: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise PlanningValidationError(f"{field_name} must be numeric")
    value = float(value)
    if not 0.0 <= value <= 1.0:
        raise PlanningValidationError(f"{field_name} must be between 0 and 1")
    return value


@dataclass(frozen=True)
class Goal:
    """Immutable desired outcome representation used by planning."""

    goal_id: str
    title: str
    desired_outcome: str
    priority: float = 0.5
    status: GoalStatus = GoalStatus.ACTIVE
    horizon_start: str | None = None
    horizon_end: str | None = None
    constraints: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        for name in ("goal_id", "title", "desired_outcome"):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise PlanningValidationError(f"{name} must be a non-empty string")
        object.__setattr__(self, "priority", _score(self.priority, "priority"))
        if not isinstance(self.status, GoalStatus):
            raise TypeError("status must be a GoalStatus")
        if self.horizon_start is not None:
            _parse_timestamp(self.horizon_start)
        if self.horizon_end is not None:
            _parse_timestamp(self.horizon_end)
        if self.horizon_start and self.horizon_end:
            if _parse_timestamp(self.horizon_end) <= _parse_timestamp(self.horizon_start):
                raise PlanningValidationError("horizon_end must be later than horizon_start")
        if not isinstance(self.constraints, tuple):
            raise TypeError("constraints must be a tuple")
        if any(not isinstance(item, str) or not item.strip() for item in self.constraints):
            raise PlanningValidationError("constraints must contain non-empty strings")

    def to_context(self) -> dict[str, object]:
        return {
            "goal_id": self.goal_id,
            "title": self.title,
            "desired_outcome": self.desired_outcome,
            "priority": float(self.priority),
            "status": self.status.value,
            "horizon_start": self.horizon_start,
            "horizon_end": self.horizon_end,
            "constraints": tuple(self.constraints),
            "authorization_granted": False,
            "execution_requested": False,
        }


@dataclass(frozen=True)
class PlannedStep:
    """Provider-neutral intended step; this is not executable work."""

    step_id: str
    description: str
    prerequisite_ids: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not isinstance(self.step_id, str) or not self.step_id.strip():
            raise PlanningValidationError("step_id must be a non-empty string")
        if not isinstance(self.description, str) or not self.description.strip():
            raise PlanningValidationError("description must be a non-empty string")
        if not isinstance(self.prerequisite_ids, tuple):
            raise TypeError("prerequisite_ids must be a tuple")
        if len(set(self.prerequisite_ids)) != len(self.prerequisite_ids):
            raise PlanningValidationError("prerequisite_ids must be unique")


@dataclass(frozen=True)
class PlanningContext:
    """Immutable bounded planning input assembled from world and reasoning."""

    context_id: str
    created_at: str
    world_snapshot: WorldSnapshot
    reasoning_result: ReasoningResult
    goal: Goal
    additional_constraints: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not isinstance(self.context_id, str) or not self.context_id.strip():
            raise PlanningValidationError("context_id must be a non-empty string")
        _parse_timestamp(self.created_at)
        if not isinstance(self.world_snapshot, WorldSnapshot):
            raise TypeError("world_snapshot must be a WorldSnapshot")
        if not isinstance(self.reasoning_result, ReasoningResult):
            raise TypeError("reasoning_result must be a ReasoningResult")
        if not isinstance(self.goal, Goal):
            raise TypeError("goal must be a Goal")
        if not isinstance(self.additional_constraints, tuple):
            raise TypeError("additional_constraints must be a tuple")
        if any(not isinstance(item, str) or not item.strip() for item in self.additional_constraints):
            raise PlanningValidationError("additional_constraints must contain non-empty strings")

    def to_context(self) -> dict[str, object]:
        return {
            "context_id": self.context_id,
            "created_at": self.created_at,
            "world_snapshot_id": self.world_snapshot.snapshot_id,
            "world_version": self.world_snapshot.version,
            "reasoning_result_id": self.reasoning_result.context.request_id,
            "goal": self.goal.to_context(),
            "additional_constraints": tuple(self.additional_constraints),
            "authorization_granted": False,
            "execution_requested": False,
        }


@dataclass(frozen=True)
class CandidatePlan:
    """Immutable candidate plan for advisory comparison."""

    plan_id: str
    goal_id: str
    steps: tuple[PlannedStep, ...]
    expected_benefit: float
    effort: float
    risk: float
    confidence: float
    assumptions: tuple[str, ...] = ()
    blockers: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not isinstance(self.plan_id, str) or not self.plan_id.strip():
            raise PlanningValidationError("plan_id must be a non-empty string")
        if not isinstance(self.goal_id, str) or not self.goal_id.strip():
            raise PlanningValidationError("goal_id must be a non-empty string")
        if not isinstance(self.steps, tuple) or not self.steps:
            raise PlanningValidationError("steps must be a non-empty tuple")
        if any(not isinstance(item, PlannedStep) for item in self.steps):
            raise TypeError("steps must contain PlannedStep values")
        ids = tuple(item.step_id for item in self.steps)
        if len(set(ids)) != len(ids):
            raise PlanningValidationError("step ids must be unique")
        known = set(ids)
        for step in self.steps:
            unknown = set(step.prerequisite_ids) - known
            if unknown:
                raise PlanningValidationError(f"unknown step prerequisites: {sorted(unknown)}")
        for name in ("expected_benefit", "effort", "risk", "confidence"):
            object.__setattr__(self, name, _score(getattr(self, name), name))
        for name, values in (("assumptions", self.assumptions), ("blockers", self.blockers)):
            if not isinstance(values, tuple):
                raise TypeError(f"{name} must be a tuple")
            if any(not isinstance(item, str) or not item.strip() for item in values):
                raise PlanningValidationError(f"{name} must contain non-empty strings")

    @property
    def advisory_score(self) -> float:
        """Bounded comparison signal; never permission or authorization."""
        raw = (
            (0.50 * self.expected_benefit)
            + (0.20 * self.confidence)
            + (0.20 * (1.0 - self.effort))
            + (0.10 * (1.0 - self.risk))
        )
        return max(0.0, min(1.0, raw))

    def to_context(self) -> dict[str, object]:
        return {
            "plan_id": self.plan_id,
            "goal_id": self.goal_id,
            "steps": tuple({
                "step_id": item.step_id,
                "description": item.description,
                "prerequisite_ids": tuple(item.prerequisite_ids),
            } for item in self.steps),
            "expected_benefit": float(self.expected_benefit),
            "effort": float(self.effort),
            "risk": float(self.risk),
            "confidence": float(self.confidence),
            "advisory_score": self.advisory_score,
            "assumptions": tuple(self.assumptions),
            "blockers": tuple(self.blockers),
            "authorization_granted": False,
            "execution_requested": False,
        }


@dataclass(frozen=True)
class PlanEvaluation:
    """Immutable feasibility and utility evaluation of one candidate."""

    plan_id: str
    feasibility: PlanFeasibility
    blockers: tuple[str, ...]
    advisory_score: float
    rationale: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not isinstance(self.plan_id, str) or not self.plan_id.strip():
            raise PlanningValidationError("plan_id must be a non-empty string")
        if not isinstance(self.feasibility, PlanFeasibility):
            raise TypeError("feasibility must be a PlanFeasibility")
        if not isinstance(self.blockers, tuple) or not isinstance(self.rationale, tuple):
            raise TypeError("blockers and rationale must be tuples")
        if any(not isinstance(item, str) or not item.strip() for item in self.blockers + self.rationale):
            raise PlanningValidationError("blockers and rationale must contain non-empty strings")
        object.__setattr__(self, "advisory_score", _score(self.advisory_score, "advisory_score"))

    def to_context(self) -> dict[str, object]:
        return {
            "plan_id": self.plan_id,
            "feasibility": self.feasibility.value,
            "blockers": tuple(self.blockers),
            "advisory_score": float(self.advisory_score),
            "rationale": tuple(self.rationale),
            "selection_is_authorization": False,
            "authorization_granted": False,
            "execution_requested": False,
        }


@dataclass(frozen=True)
class PlanRanking:
    """Deterministic advisory ordering over evaluated plans."""

    ordered_plan_ids: tuple[str, ...]
    scores: Mapping[str, float]
    advisory_selected_plan_id: str | None

    def __post_init__(self) -> None:
        if not isinstance(self.ordered_plan_ids, tuple):
            raise TypeError("ordered_plan_ids must be a tuple")
        if len(set(self.ordered_plan_ids)) != len(self.ordered_plan_ids):
            raise PlanningValidationError("ordered_plan_ids must be unique")
        if not isinstance(self.scores, Mapping):
            raise TypeError("scores must be a mapping")
        object.__setattr__(self, "scores", dict(self.scores))
        if self.advisory_selected_plan_id is not None and self.advisory_selected_plan_id not in self.ordered_plan_ids:
            raise PlanningValidationError("selected plan must be present in ordered_plan_ids")

    def to_context(self) -> dict[str, object]:
        return {
            "ordered_plan_ids": tuple(self.ordered_plan_ids),
            "scores": dict(self.scores),
            "advisory_selected_plan_id": self.advisory_selected_plan_id,
            "selection_is_authorization": False,
            "authorization_granted": False,
            "execution_requested": False,
        }


@dataclass(frozen=True)
class PlanningResult:
    """Complete inspectable planning output."""

    context: PlanningContext
    evaluations: tuple[PlanEvaluation, ...]
    ranking: PlanRanking

    @property
    def is_ambiguous(self) -> bool:
        return any(item.feasibility is PlanFeasibility.REVIEW for item in self.evaluations)

    def to_context(self) -> dict[str, object]:
        return {
            "context": self.context.to_context(),
            "evaluations": tuple(item.to_context() for item in self.evaluations),
            "ranking": self.ranking.to_context(),
            "ambiguous": self.is_ambiguous,
            "selection_is_authorization": False,
            "authorization_granted": False,
            "execution_requested": False,
        }


class PlanningDecisionSystem:
    """Provider-neutral planning and advisory decision-support boundary."""

    def evaluate(self, context: PlanningContext, plan: CandidatePlan) -> PlanEvaluation:
        if not isinstance(context, PlanningContext):
            raise TypeError("context must be a PlanningContext")
        if not isinstance(plan, CandidatePlan):
            raise TypeError("plan must be a CandidatePlan")
        if plan.goal_id != context.goal.goal_id:
            raise PlanningValidationError("candidate plan must target the planning goal")
        blockers = tuple(plan.blockers)
        if context.goal.status is not GoalStatus.ACTIVE:
            blockers = blockers + (f"goal status is {context.goal.status.value}",)
        if blockers:
            feasibility = PlanFeasibility.BLOCKED
            rationale = ("candidate contains unresolved blockers",)
        elif context.world_snapshot.is_ambiguous or context.reasoning_result.is_ambiguous:
            feasibility = PlanFeasibility.REVIEW
            rationale = ("current world or reasoning result remains ambiguous",)
        else:
            feasibility = PlanFeasibility.FEASIBLE
            rationale = ("candidate satisfies structural planning boundary",)
        return PlanEvaluation(
            plan_id=plan.plan_id,
            feasibility=feasibility,
            blockers=blockers,
            advisory_score=plan.advisory_score,
            rationale=rationale,
        )

    def rank(self, evaluations: tuple[PlanEvaluation, ...]) -> PlanRanking:
        if not isinstance(evaluations, tuple) or any(not isinstance(item, PlanEvaluation) for item in evaluations):
            raise TypeError("evaluations must be a tuple of PlanEvaluation")
        if len({item.plan_id for item in evaluations}) != len(evaluations):
            raise PlanningValidationError("plan ids must be unique")
        priority = {
            PlanFeasibility.FEASIBLE: 2,
            PlanFeasibility.REVIEW: 1,
            PlanFeasibility.BLOCKED: 0,
        }
        ordered = tuple(
            sorted(
                evaluations,
                key=lambda item: (
                    -priority[item.feasibility],
                    -float(item.advisory_score),
                    item.plan_id,
                ),
            )
        )
        ordered_ids = tuple(item.plan_id for item in ordered)
        scores = {item.plan_id: float(item.advisory_score) for item in ordered}
        selected = next(
            (item.plan_id for item in ordered if item.feasibility is PlanFeasibility.FEASIBLE),
            None,
        )
        return PlanRanking(
            ordered_plan_ids=ordered_ids,
            scores=scores,
            advisory_selected_plan_id=selected,
        )

    def plan(
        self,
        context: PlanningContext,
        candidates: tuple[CandidatePlan, ...],
    ) -> PlanningResult:
        if not isinstance(context, PlanningContext):
            raise TypeError("context must be a PlanningContext")
        if not isinstance(candidates, tuple) or any(not isinstance(item, CandidatePlan) for item in candidates):
            raise TypeError("candidates must be a tuple of CandidatePlan")
        if len({item.plan_id for item in candidates}) != len(candidates):
            raise PlanningValidationError("candidate plan ids must be unique")
        evaluations = tuple(self.evaluate(context, candidate) for candidate in candidates)
        ranking = self.rank(evaluations)
        return PlanningResult(context=context, evaluations=evaluations, ranking=ranking)

    def summary(self) -> Mapping[str, object]:
        return {
            "planning_kind": "GOALS_AND_DECISION_SUPPORT",
            "authorizes_execution": False,
            "executes_capability": False,
            "mutates_external_state": False,
            "persists_state": False,
            "establishes_truth": False,
            "establishes_certainty": False,
            "selection_is_authorization": False,
        }

    @property
    def authorizes_execution(self) -> bool:
        return False

    @property
    def executes_capability(self) -> bool:
        return False

    @property
    def mutates_external_state(self) -> bool:
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
    "CandidatePlan",
    "Goal",
    "GoalStatus",
    "PlanEvaluation",
    "PlanFeasibility",
    "PlanRanking",
    "PlannedStep",
    "PlanningContext",
    "PlanningDecisionSystem",
    "PlanningResult",
    "PlanningValidationError",
]
