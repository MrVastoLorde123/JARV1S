"""M118-M126: bounded planning-to-proactive-initiative integration.

This module bridges the verified Phase 8 planning boundary into the existing
M15 proactive initiative artifacts. The bridge remains advisory: it never
creates confirmation, authorization, execution, scheduling delivery, policy
authority, or user-intent guarantees.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Mapping

from src.core.planning_decision import (
    CandidatePlan,
    PlanEvaluation,
    PlanFeasibility,
    PlanningResult,
)
from src.core.world_model import WorldSnapshot
from src.core.reasoning import ReasoningResult
from src.evaluation import InitiativeEvaluation
from src.initiative import InitiativeCandidate
from src.initiative_runtime import InitiativeRuntime
from src.initiative_safety import InitiativeSafetyResult, check_initiative_safety
from src.opportunities import DetectionType, OpportunityDetection, OpportunityDetectionSet
from src.proposals import InitiativeProposal
from src.scheduling import ProactiveSchedule


class ProactiveInitiativeValidationError(ValueError):
    """Raised when proactive integration inputs violate the boundary."""


@dataclass(frozen=True)
class ProactiveInitiativeContext:
    """Immutable bridge context binding planning, world, and reasoning identity."""

    planning_result: PlanningResult
    candidate_plans: Mapping[str, CandidatePlan]

    def __post_init__(self) -> None:
        if not isinstance(self.planning_result, PlanningResult):
            raise TypeError("planning_result must be a PlanningResult")
        if not isinstance(self.candidate_plans, Mapping):
            raise TypeError("candidate_plans must be a mapping")
        frozen = dict(self.candidate_plans)
        if any(not isinstance(key, str) or not key.strip() for key in frozen):
            raise ProactiveInitiativeValidationError("candidate plan keys must be non-empty strings")
        if any(not isinstance(value, CandidatePlan) for value in frozen.values()):
            raise TypeError("candidate_plans must contain CandidatePlan values")
        object.__setattr__(self, "candidate_plans", frozen)
        if self.planning_result.context.goal.goal_id not in {
            item.goal_id for item in frozen.values()
        }:
            raise ProactiveInitiativeValidationError("candidate plans must target the planning goal")

    @property
    def world_snapshot(self) -> WorldSnapshot:
        return self.planning_result.context.world_snapshot

    @property
    def reasoning_result(self) -> ReasoningResult:
        return self.planning_result.context.reasoning_result

    @property
    def selected_plan_id(self) -> str | None:
        return self.planning_result.ranking.advisory_selected_plan_id

    @property
    def selected_plan(self) -> CandidatePlan | None:
        if self.selected_plan_id is None:
            return None
        return self.candidate_plans.get(self.selected_plan_id)

    def to_context(self) -> dict[str, object]:
        return {
            "planning_context_id": self.planning_result.context.context_id,
            "world_snapshot_id": self.world_snapshot.snapshot_id,
            "world_version": self.world_snapshot.version,
            "reasoning_result_id": self.reasoning_result.context.request_id,
            "goal_id": self.planning_result.context.goal.goal_id,
            "selected_plan_id": self.selected_plan_id,
            "authorization_granted": False,
            "execution_requested": False,
        }


@dataclass(frozen=True)
class ProactiveInitiativeResult:
    """Immutable inspectable proactive integration result."""

    context: ProactiveInitiativeContext
    detections: OpportunityDetectionSet
    initiative_runtime: InitiativeRuntime
    safety: InitiativeSafetyResult | None
    schedule: ProactiveSchedule | None
    planning_selection_available: bool

    @property
    def proposal(self) -> InitiativeProposal | None:
        return self.initiative_runtime.proposal

    @property
    def is_ready_for_downstream_validation(self) -> bool:
        return (
            self.safety is not None
            and self.safety.safe_for_downstream_validation
            and self.proposal is not None
        )

    def to_context(self) -> dict[str, object]:
        return {
            "context": self.context.to_context(),
            "detections": self.detections.to_dict(),
            "initiative_runtime": self.initiative_runtime.to_dict(),
            "safety": None if self.safety is None else self.safety.to_dict(),
            "schedule": None if self.schedule is None else self.schedule.to_dict(),
            "planning_selection_available": self.planning_selection_available,
            "ready_for_downstream_validation": self.is_ready_for_downstream_validation,
            "authority_granted": False,
            "execution_requested": False,
        }


class ProactiveInitiativeSystem:
    """Bridge verified planning outputs into the existing bounded initiative stack."""

    def detect(self, context: ProactiveInitiativeContext) -> OpportunityDetectionSet:
        if not isinstance(context, ProactiveInitiativeContext):
            raise TypeError("context must be a ProactiveInitiativeContext")
        detections: list[OpportunityDetection] = []
        for evaluation in context.planning_result.evaluations:
            if evaluation.feasibility is PlanFeasibility.BLOCKED:
                detection_type = DetectionType.GAP
                title = f"Blocked plan: {evaluation.plan_id}"
            elif evaluation.feasibility is PlanFeasibility.REVIEW:
                detection_type = DetectionType.CHANGE
                title = f"Review plan: {evaluation.plan_id}"
            else:
                detection_type = DetectionType.OPPORTUNITY
                title = f"Feasible plan: {evaluation.plan_id}"
            detections.append(
                OpportunityDetection(
                    detection_id=f"plan-{evaluation.plan_id}",
                    detection_type=detection_type,
                    title=title,
                    description=(
                        f"Planning evaluation for goal {context.planning_result.context.goal.goal_id} "
                        f"is {evaluation.feasibility.value}."
                    ),
                    context_refs=(
                        context.planning_result.context.context_id,
                        context.world_snapshot.snapshot_id,
                        context.reasoning_result.context.request_id,
                        evaluation.plan_id,
                    ),
                    metadata={
                        "advisory_score": evaluation.advisory_score,
                        "feasibility": evaluation.feasibility.value,
                        "truth_guaranteed": False,
                        "authorization_granted": False,
                        "execution_requested": False,
                    },
                )
            )
        return OpportunityDetectionSet(tuple(detections))

    def _require_selected(
        self,
        context: ProactiveInitiativeContext,
    ) -> tuple[CandidatePlan, PlanEvaluation]:
        selected_id = context.selected_plan_id
        if selected_id is None:
            raise ProactiveInitiativeValidationError("planning produced no advisory selection")
        plan = context.selected_plan
        if plan is None:
            raise ProactiveInitiativeValidationError("selected plan is missing from candidate plan map")
        evaluation = next(
            (item for item in context.planning_result.evaluations if item.plan_id == selected_id),
            None,
        )
        if evaluation is None:
            raise ProactiveInitiativeValidationError("selected plan has no evaluation")
        if evaluation.feasibility is not PlanFeasibility.FEASIBLE:
            raise ProactiveInitiativeValidationError("only FEASIBLE plans may become proactive initiative proposals")
        return plan, evaluation

    def build_candidate(self, context: ProactiveInitiativeContext) -> InitiativeCandidate:
        plan, evaluation = self._require_selected(context)
        goal = context.planning_result.context.goal
        return InitiativeCandidate(
            initiative_id=f"initiative-{plan.plan_id}",
            title=goal.title,
            description=goal.desired_outcome,
            context_refs=(
                context.planning_result.context.context_id,
                context.world_snapshot.snapshot_id,
                context.reasoning_result.context.request_id,
                plan.plan_id,
            ),
            tags=("planned", "proactive"),
            metadata={
                "goal_id": goal.goal_id,
                "plan_id": plan.plan_id,
                "planning_score": evaluation.advisory_score,
                "selection_is_authorization": False,
                "authorization_granted": False,
                "execution_requested": False,
            },
        )

    def build_evaluation(
        self,
        context: ProactiveInitiativeContext,
        candidate: InitiativeCandidate,
    ) -> InitiativeEvaluation:
        plan, evaluation = self._require_selected(context)
        return InitiativeEvaluation(
            evaluation_id=f"evaluation-{plan.plan_id}",
            candidate=candidate,
            value_score=plan.expected_benefit,
            urgency_score=context.planning_result.context.goal.priority,
            confidence_score=plan.confidence,
            effort_score=plan.effort,
            risk_score=plan.risk,
            reasons=(
                f"planning feasibility: {evaluation.feasibility.value}",
                f"advisory score: {evaluation.advisory_score:.6f}",
            ),
            metadata={
                "planning_context_id": context.planning_result.context.context_id,
                "planning_selection_is_authorization": False,
            },
        )

    def build_proposal(
        self,
        context: ProactiveInitiativeContext,
        candidate: InitiativeCandidate,
        evaluation: InitiativeEvaluation,
    ) -> InitiativeProposal:
        plan = context.selected_plan
        if plan is None:
            raise ProactiveInitiativeValidationError("selected plan is required for proposal")
        step_text = "; ".join(step.description for step in plan.steps)
        return InitiativeProposal(
            proposal_id=f"proposal-{plan.plan_id}",
            evaluation=evaluation,
            title=candidate.title,
            description=candidate.description,
            proposed_action=step_text,
            reasons=evaluation.reasons,
            metadata={
                "goal_id": context.planning_result.context.goal.goal_id,
                "plan_id": plan.plan_id,
                "world_snapshot_id": context.world_snapshot.snapshot_id,
                "reasoning_result_id": context.reasoning_result.context.request_id,
                "confirmation_required": True,
                "authorization_granted": False,
                "execution_requested": False,
            },
        )

    def safety_check(self, proposal: InitiativeProposal) -> InitiativeSafetyResult:
        return check_initiative_safety(proposal)

    def compose(
        self,
        context: ProactiveInitiativeContext,
        *,
        next_at: str | None = None,
        timezone: str = "UTC",
    ) -> ProactiveInitiativeResult:
        if not isinstance(context, ProactiveInitiativeContext):
            raise TypeError("context must be a ProactiveInitiativeContext")
        detections = self.detect(context)
        selected_available = context.selected_plan is not None
        if not selected_available:
            return ProactiveInitiativeResult(
                context=context,
                detections=detections,
                initiative_runtime=InitiativeRuntime(detections=detections),
                safety=None,
                schedule=None,
                planning_selection_available=False,
            )

        candidate = self.build_candidate(context)
        evaluation = self.build_evaluation(context, candidate)
        proposal = self.build_proposal(context, candidate, evaluation)
        safety = self.safety_check(proposal)
        schedule = None
        if next_at is not None:
            schedule = ProactiveSchedule(
                schedule_id=f"schedule-{proposal.proposal_id}",
                proposal=proposal,
                next_at=next_at,
                timezone=timezone,
            )
        runtime = InitiativeRuntime(
            detections=detections,
            candidate=candidate,
            evaluation=evaluation,
            proposal=proposal,
            schedule=schedule,
            safety=safety,
        )
        return ProactiveInitiativeResult(
            context=context,
            detections=detections,
            initiative_runtime=runtime,
            safety=safety,
            schedule=schedule,
            planning_selection_available=True,
        )

    @property
    def authorizes_execution(self) -> bool:
        return False

    @property
    def executes_capability(self) -> bool:
        return False

    @property
    def mutates_state(self) -> bool:
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

    @property
    def selects_provider(self) -> bool:
        return False


__all__ = [
    "ProactiveInitiativeContext",
    "ProactiveInitiativeResult",
    "ProactiveInitiativeSystem",
    "ProactiveInitiativeValidationError",
]
