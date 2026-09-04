"""M20.8 bounded end-to-end long-horizon runtime.

Composes the existing M20 goal/objective, task, dependency, progress,
planning, continuation, and persistence boundaries. This runtime coordinates
those components without introducing authority or execution rights.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from .continuation import ContinuationDecision, NextStepEngine
from .dependencies import TaskDependencyGraph
from .goals import Goal, Objective
from .persistence import PersistenceSnapshot, build_snapshot, recover_snapshot
from .planning import LongHorizonPlan, LongHorizonPlanner
from .progress import ProgressEvaluation, TaskProgressEvaluator
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
        evaluator: TaskProgressEvaluator,
    ) -> None:
        task_values = tuple(tasks)
        if objective.goal_id != goal.goal_id:
            raise LongHorizonRuntimeError("objective does not belong to goal")
        if set(task.task_id for task in task_values) != set(graph.all_task_ids()):
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
    def recover(snapshot_payload: str | dict[str, object]) -> PersistenceSnapshot:
        """Recover persisted state only; no continuation or execution occurs here."""
        import json

        payload = json.loads(snapshot_payload) if isinstance(snapshot_payload, str) else snapshot_payload
        recovered = recover_snapshot(payload)
        if recovered.plan_id != str(payload.get("plan_id")):
            raise LongHorizonRuntimeError("recovered plan identity mismatch")
        return recovered

    def rebuild_from_recovery(self, snapshot: PersistenceSnapshot) -> RuntimeState:
        task_map = {task.task_id: task for task in snapshot.tasks}
        graph = TaskDependencyGraph(task_map)
        for dependent, prerequisite in snapshot.dependencies:
            graph.add_dependency(dependent, prerequisite)

        evaluator = TaskProgressEvaluator(snapshot.tasks)
        from .persistence import _evaluation_to_dict
        from .progress import ProgressEvidence, ObservedState

        for evaluation in snapshot.evaluations:
            raw = _evaluation_to_dict(evaluation)
            for item in raw.get("evidence", ()):
                evaluator.add_evidence(
                    ProgressEvidence(
                        str(item["evidence_id"]),
                        str(item["task_id"]),
                        ObservedState(item["observed_state"]),
                        str(item["source"]),
                        str(item["reference_id"]),
                        str(item["observed_at"]),
                        str(item.get("details", "")),
                    )
                )

        plan = LongHorizonPlanner(
            snapshot.goal,
            snapshot.objective,
            snapshot.tasks,
            graph,
            evaluator,
        ).build(plan_id=snapshot.plan_id)
        if plan.status is not snapshot.plan_status:
            raise LongHorizonRuntimeError("recovered plan status does not match persisted plan status")
        evaluations = evaluator.evaluations()
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
