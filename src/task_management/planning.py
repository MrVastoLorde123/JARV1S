"""M20.5 long-horizon planning boundary.

Planning assembles an explicit plan from existing goals, objectives, task
structure, dependencies, and progress evaluations. It does not select a next
step, schedule work, authorize work, or execute work.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Iterable, Mapping

from .dependencies import TaskDependencyGraph
from .goals import Goal, Objective
from .progress import ProgressEvaluation, ProgressStatus, TaskProgressEvaluator
from .task import Task


class PlanningError(ValueError):
    """Raised when a long-horizon plan cannot be constructed safely."""


class PlanStatus(str, Enum):
    READY = "READY"
    NEEDS_REVIEW = "NEEDS_REVIEW"


@dataclass(frozen=True)
class PlanStep:
    """A structural task reference inside a plan; not a next-step command."""

    task_id: str
    ordinal: int
    progress_status: ProgressStatus
    recorded_state: str
    observed_state: str

    def to_dict(self) -> dict[str, object]:
        return {
            "task_id": self.task_id,
            "ordinal": self.ordinal,
            "progress_status": self.progress_status.value,
            "recorded_state": self.recorded_state,
            "observed_state": self.observed_state,
        }


@dataclass(frozen=True)
class LongHorizonPlan:
    """Immutable structural plan assembled from current task reality."""

    plan_id: str
    goal_id: str
    objective_id: str
    title: str
    status: PlanStatus
    steps: tuple[PlanStep, ...]
    evaluation_ids: tuple[str, ...]
    source_references: tuple[str, ...]

    def to_context(self) -> dict[str, object]:
        return {
            "plan_id": self.plan_id,
            "goal_id": self.goal_id,
            "objective_id": self.objective_id,
            "title": self.title,
            "status": self.status.value,
            "steps": tuple(step.to_dict() for step in self.steps),
            "evaluation_ids": self.evaluation_ids,
            "source_references": self.source_references,
            "authority_granted": False,
            "authorization_granted": False,
            "execution_requested": False,
            "next_step_selected": False,
            "schedule_created": False,
        }


class LongHorizonPlanner:
    """Build a deterministic plan snapshot without making execution decisions."""

    def __init__(
        self,
        goal: Goal,
        objective: Objective,
        tasks: Iterable[Task],
        graph: TaskDependencyGraph,
        evaluator: TaskProgressEvaluator,
    ) -> None:
        if objective.goal_id != goal.goal_id:
            raise PlanningError("objective does not belong to goal")
        task_values = tuple(sorted(tasks, key=lambda item: item.task_id))
        task_map: dict[str, Task] = {}
        for task in task_values:
            if task.objective_id != objective.objective_id:
                raise PlanningError("task does not belong to objective")
            if task.task_id in task_map and task_map[task.task_id] != task:
                raise PlanningError(f"task identity conflict: {task.task_id}")
            task_map[task.task_id] = task
        graph_ids = set(graph.all_task_ids())
        if graph_ids != set(task_map):
            raise PlanningError("graph task identities do not match supplied tasks")
        self._goal = goal
        self._objective = objective
        self._tasks = task_map
        self._graph = graph
        self._evaluator = evaluator

    def build(self, *, plan_id: str, source_references: Iterable[str] = ()) -> LongHorizonPlan:
        if not isinstance(plan_id, str) or not plan_id.strip():
            raise ValueError("plan_id must be a non-empty string")
        references = tuple(sorted({ref for ref in source_references if isinstance(ref, str) and ref.strip()}))
        order = self._graph.topological_order()
        evaluations = {evaluation.task_id: evaluation for evaluation in self._evaluator.evaluations()}
        missing = set(self._tasks) - set(evaluations)
        if missing:
            raise PlanningError(f"missing progress evaluation for tasks: {', '.join(sorted(missing))}")

        steps = tuple(
            PlanStep(
                task_id=task_id,
                ordinal=index,
                progress_status=evaluations[task_id].status,
                recorded_state=evaluations[task_id].recorded_state.value,
                observed_state=evaluations[task_id].observed_state.value,
            )
            for index, task_id in enumerate(order, start=1)
        )
        evaluation_ids = tuple(
            f"{evaluation.task_id}:{','.join(evaluation.evidence_ids)}" if evaluation.evidence_ids else f"{evaluation.task_id}:none"
            for evaluation in (evaluations[task_id] for task_id in order)
        )
        needs_review = any(item.progress_status is ProgressStatus.CONFLICTED for item in steps)
        return LongHorizonPlan(
            plan_id=plan_id,
            goal_id=self._goal.goal_id,
            objective_id=self._objective.objective_id,
            title=self._objective.title,
            status=PlanStatus.NEEDS_REVIEW if needs_review else PlanStatus.READY,
            steps=steps,
            evaluation_ids=evaluation_ids,
            source_references=references,
        )

    def summarize(self) -> Mapping[str, object]:
        order = self._graph.topological_order()
        evaluations = {evaluation.task_id: evaluation for evaluation in self._evaluator.evaluations()}
        return {
            "goal_id": self._goal.goal_id,
            "objective_id": self._objective.objective_id,
            "task_count": len(order),
            "ordered_task_ids": order,
            "aligned_count": sum(item.status is ProgressStatus.ALIGNED for item in evaluations.values()),
            "conflicted_count": sum(item.status is ProgressStatus.CONFLICTED for item in evaluations.values()),
            "unverified_count": sum(item.status is ProgressStatus.UNVERIFIED for item in evaluations.values()),
            "next_step_selected": False,
            "schedule_created": False,
            "execution_requested": False,
        }
