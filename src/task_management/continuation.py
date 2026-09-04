"""M20.6 bounded continuation and next-step proposal boundary.

Continuation selects one bounded next-step proposal from an existing plan and
its current progress evidence. Selection is not authorization, scheduling, or
execution.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Iterable

from .dependencies import TaskDependencyGraph
from .planning import LongHorizonPlan, PlanStatus
from .progress import ProgressEvaluation, ProgressStatus
from .task import TaskState


class ContinuationError(ValueError):
    """Raised when a bounded continuation decision cannot be formed safely."""


class ContinuationStatus(str, Enum):
    PROPOSED = "PROPOSED"
    NEEDS_REVIEW = "NEEDS_REVIEW"
    NO_CONTINUATION = "NO_CONTINUATION"


@dataclass(frozen=True)
class NextStepProposal:
    """Immutable bounded recommendation for one plan task."""

    proposal_id: str
    plan_id: str
    task_id: str
    description: str
    reason: str
    evidence_ids: tuple[str, ...] = ()
    bounded: bool = True
    authorization_granted: bool = False
    execution_requested: bool = False

    def __post_init__(self) -> None:
        for name in ("proposal_id", "plan_id", "task_id", "description", "reason"):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string")
        if not isinstance(self.evidence_ids, tuple):
            raise TypeError("evidence_ids must be a tuple")
        if len(set(self.evidence_ids)) != len(self.evidence_ids):
            raise ValueError("evidence_ids must be unique")
        for evidence_id in self.evidence_ids:
            if not isinstance(evidence_id, str) or not evidence_id.strip():
                raise ValueError("evidence ids must be non-empty strings")
        if not isinstance(self.bounded, bool):
            raise TypeError("bounded must be a bool")
        if not isinstance(self.authorization_granted, bool):
            raise TypeError("authorization_granted must be a bool")
        if not isinstance(self.execution_requested, bool):
            raise TypeError("execution_requested must be a bool")
        if not self.bounded:
            raise ValueError("next-step proposals must remain bounded")
        if self.authorization_granted:
            raise ValueError("next-step proposals cannot grant authorization")
        if self.execution_requested:
            raise ValueError("next-step proposals cannot request execution")

    def to_context(self) -> dict[str, object]:
        return {
            "proposal_id": self.proposal_id,
            "plan_id": self.plan_id,
            "task_id": self.task_id,
            "description": self.description,
            "reason": self.reason,
            "evidence_ids": self.evidence_ids,
            "bounded": True,
            "authorization_granted": False,
            "execution_requested": False,
        }


@dataclass(frozen=True)
class ContinuationDecision:
    """Immutable bounded continuation outcome."""

    plan_id: str
    status: ContinuationStatus
    proposal: NextStepProposal | None = None
    reason: str = ""

    def __post_init__(self) -> None:
        if not isinstance(self.plan_id, str) or not self.plan_id.strip():
            raise ValueError("plan_id must be a non-empty string")
        if not isinstance(self.status, ContinuationStatus):
            try:
                object.__setattr__(self, "status", ContinuationStatus(self.status))
            except (TypeError, ValueError) as exc:
                raise TypeError("status must be a ContinuationStatus") from exc
        if self.proposal is not None:
            if not isinstance(self.proposal, NextStepProposal):
                raise TypeError("proposal must be a NextStepProposal")
            if self.proposal.plan_id != self.plan_id:
                raise ValueError("proposal/plan identity mismatch")
            if self.status is not ContinuationStatus.PROPOSED:
                raise ValueError("proposal requires PROPOSED status")
        elif self.status is ContinuationStatus.PROPOSED:
            raise ValueError("PROPOSED decision requires a proposal")
        if not isinstance(self.reason, str):
            raise TypeError("reason must be a string")
        if self.status is not ContinuationStatus.PROPOSED and not self.reason.strip():
            raise ValueError("non-proposed decision requires a reason")

    def to_context(self) -> dict[str, object]:
        return {
            "plan_id": self.plan_id,
            "status": self.status.value,
            "proposal": None if self.proposal is None else self.proposal.to_context(),
            "reason": self.reason,
            "authorization_granted": False,
            "execution_requested": False,
        }


class NextStepEngine:
    """Select one bounded next-step proposal from an existing plan."""

    _ACTIONABLE_STATES = {TaskState.READY.value, TaskState.IN_PROGRESS.value}
    _TERMINAL_OBSERVED_STATES = {
        TaskState.COMPLETED.value,
        TaskState.CANCELLED.value,
        TaskState.SUPERSEDED.value,
    }

    def __init__(
        self,
        plan: LongHorizonPlan,
        graph: TaskDependencyGraph,
        evaluations: Iterable[ProgressEvaluation],
    ) -> None:
        self._plan = plan
        self._graph = graph
        self._evaluations = {item.task_id: item for item in evaluations}
        plan_task_ids = tuple(step.task_id for step in plan.steps)
        if set(plan_task_ids) != set(graph.all_task_ids()):
            raise ContinuationError("plan task identities do not match graph")
        if set(plan_task_ids) != set(self._evaluations):
            raise ContinuationError("plan task identities do not match progress evaluations")

    def decide(self) -> ContinuationDecision:
        if self._plan.status is PlanStatus.NEEDS_REVIEW:
            return ContinuationDecision(
                self._plan.plan_id,
                ContinuationStatus.NEEDS_REVIEW,
                reason="plan contains conflicted progress and requires review",
            )

        ordered_steps = tuple(sorted(self._plan.steps, key=lambda step: step.ordinal))
        completed_ids = {
            task_id
            for task_id, evaluation in self._evaluations.items()
            if evaluation.observed_state.value == TaskState.COMPLETED.value
        }

        for step in ordered_steps:
            evaluation = self._evaluations[step.task_id]
            if evaluation.status is ProgressStatus.CONFLICTED:
                return ContinuationDecision(
                    self._plan.plan_id,
                    ContinuationStatus.NEEDS_REVIEW,
                    reason=f"task {step.task_id} has conflicted progress",
                )
            observed = evaluation.observed_state.value
            if observed in self._TERMINAL_OBSERVED_STATES:
                continue
            if observed not in self._ACTIONABLE_STATES:
                continue
            prerequisites = self._graph.prerequisites(step.task_id)
            if any(prerequisite_id not in completed_ids for prerequisite_id in prerequisites):
                continue
            proposal = NextStepProposal(
                proposal_id=f"{self._plan.plan_id}:next:{step.task_id}",
                plan_id=self._plan.plan_id,
                task_id=step.task_id,
                description=f"Continue work on task {step.task_id}",
                reason="earliest structurally available actionable task in plan order",
                evidence_ids=evaluation.evidence_ids,
            )
            return ContinuationDecision(
                self._plan.plan_id,
                ContinuationStatus.PROPOSED,
                proposal=proposal,
            )

        if ordered_steps and all(
            self._evaluations[step.task_id].observed_state.value in self._TERMINAL_OBSERVED_STATES
            for step in ordered_steps
        ):
            return ContinuationDecision(
                self._plan.plan_id,
                ContinuationStatus.NO_CONTINUATION,
                reason="all planned tasks are terminal according to observed progress",
            )

        return ContinuationDecision(
            self._plan.plan_id,
            ContinuationStatus.NO_CONTINUATION,
            reason="no unfinished actionable task is structurally available from current progress",
        )

    def select(self) -> NextStepProposal | None:
        """Return the proposal only; never authorize or execute it."""
        return self.decide().proposal
