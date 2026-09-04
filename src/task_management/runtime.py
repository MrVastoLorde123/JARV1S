"""M20.8 bounded end-to-end long-horizon runtime.

Composes the existing M20 goal/objective, task, dependency, progress,
planning, continuation, and persistence boundaries. This runtime coordinates
those components without introducing authority or execution rights.
"""

from __future__ import annotations

from dataclasses import dataclass
import json
from typing import Iterable, Mapping

from .continuation import ContinuationDecision, NextStepEngine
from .dependencies import TaskDependencyGraph
from .goals import Goal, Objective
from .persistence import PersistenceSnapshot, build_snapshot, recover_snapshot
from .planning import LongHorizonPlan, LongHorizonPlanner, PlanStatus, PlanStep
from .progress import ProgressEvaluation, ProgressStatus
from .task import Task


class LongHorizonRuntimeError(ValueError):
    """Raised when the integrated long-horizon runtime cannot form safely."""


@dataclass(frozen=True)
class RuntimeState:
    """Immutable runtime result containing only bounded planning state."""

    plan: LongHorizonPlan
    evaluations: tuple[ProgressEvaluation, ...]
    snapshot: PersistenceSnapshot
    decision: ContinuationDecision

    def to_context(self) -> dict[str, object]:
        return {
            "plan": self.plan.to_context(),
            "evaluations": tuple(item.to_context() for item in self.evaluations),
            "snapshot_id": self.snapshot.snapshot_id,
            "decision": self.decision.to_context(),
            "authority_granted": False,
            "authorization_granted": False,
            "execution_requested": False,
        }


class LongHorizonRuntime:
    """Build and recover one bounded M20 long-horizon state."""

    def __init__(
        self,
        goal: Goal,
        objective: Objective,
        tasks: Iterable[Task],
        graph: TaskDependencyGraph,
        evaluator: object,
    ) -> None:
        task_values = tuple(tasks)
        if objective.goal_id != goal.goal_id:
            raise LongHorizonRuntimeError("objective does not belong to goal")
        if {task.task_id for task in task_values} != set(graph.all_task_ids()):
            raise LongHorizonRuntimeError("task and graph identities do not match")
        self._goal = goal
        self._objective = objective
        self._tasks = tuple(sorted(task_values, key=lambda item: item.task_id))
        self._graph = graph
        self._evaluator = evaluator

    def build(self, *, plan_id: str, snapshot_id: str) -> RuntimeState:
        plan = LongHorizonPlanner(
            self._goal,
            self._objective,
            self._tasks,
            self._graph,
            self._evaluator,
        ).build(plan_id=plan_id)
        evaluations = self._evaluator.evaluations()
        snapshot = build_snapshot(
            snapshot_id,
            plan,
            self._goal,
            self._objective,
            self._tasks,
            self._graph,
            evaluations,
        )
        decision = NextStepEngine(plan, self._graph, evaluations).decide()
        return RuntimeState(plan, evaluations, snapshot, decision)

    @staticmethod
    def recover(snapshot_payload: str | Mapping[str, object]) -> PersistenceSnapshot:
        """Recover persisted state only; no continuation or execution occurs here."""
        payload = json.loads(snapshot_payload) if isinstance(snapshot_payload, str) else snapshot_payload
        recovered = recover_snapshot(payload)
        if recovered.plan_id != str(payload.get("plan_id")):
            raise LongHorizonRuntimeError("recovered plan identity mismatch")
        return recovered

    @staticmethod
    def _plan_from_snapshot(snapshot: PersistenceSnapshot, graph: TaskDependencyGraph) -> LongHorizonPlan:
        evaluations = {item.task_id: item for item in snapshot.evaluations}
        order = graph.topological_order()
        if set(order) != set(evaluations):
            raise LongHorizonRuntimeError("recovered plan/evaluation identity mismatch")
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
        status = PlanStatus.NEEDS_REVIEW if any(
            item.status is ProgressStatus.CONFLICTED for item in snapshot.evaluations
        ) else PlanStatus.READY
        evaluation_ids = tuple(
            f"{evaluation.task_id}:{','.join(evaluation.evidence_ids)}" if evaluation.evidence_ids else f"{evaluation.task_id}:none"
            for evaluation in (evaluations[task_id] for task_id in order)
        )
        return LongHorizonPlan(
            plan_id=snapshot.plan_id,
            goal_id=snapshot.goal.goal_id,
            objective_id=snapshot.objective.objective_id,
            title=snapshot.objective.title,
            status=status,
            steps=steps,
            evaluation_ids=evaluation_ids,
            source_references=(),
        )

    def rebuild_from_recovery(self, snapshot: PersistenceSnapshot) -> RuntimeState:
        if snapshot.goal.goal_id != snapshot.objective.goal_id:
            raise LongHorizonRuntimeError("recovered objective/goal identity mismatch")
        if any(task.objective_id != snapshot.objective.objective_id for task in snapshot.tasks):
            raise LongHorizonRuntimeError("recovered task/objective identity mismatch")

        graph = TaskDependencyGraph(task.task_id for task in snapshot.tasks)
        for dependent, prerequisite in snapshot.dependencies:
            graph.add_dependency(dependent, prerequisite)

        plan = self._plan_from_snapshot(snapshot, graph)
        if plan.status is not snapshot.plan_status:
            raise LongHorizonRuntimeError("recovered plan status does not match persisted plan status")

        evaluations = snapshot.evaluations
        decision = NextStepEngine(plan, graph, evaluations).decide()
        rebuilt = build_snapshot(
            snapshot.snapshot_id,
            plan,
            snapshot.goal,
            snapshot.objective,
            snapshot.tasks,
            graph,
            evaluations,
        )
        if rebuilt.to_json() != snapshot.to_json():
            raise LongHorizonRuntimeError("recovered state does not round-trip deterministically")
        return RuntimeState(plan, evaluations, rebuilt, decision)
