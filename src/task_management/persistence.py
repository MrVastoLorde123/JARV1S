"""M20.7 durable persistence and recovery boundary.

This module persists a validated long-horizon task-management snapshot and
recovers it without granting authority, inventing progress, or mutating the
live planning objects during serialization/deserialization.
"""

from __future__ import annotations

from dataclasses import dataclass
import json
from typing import Any, Mapping

from .dependencies import TaskDependencyGraph
from .goals import Goal, Objective, Provenance
from .planning import LongHorizonPlan, PlanStatus
from .progress import ProgressEvaluation, ProgressEvidence, ProgressStatus, ObservedState, TaskProgressEvaluator
from .task import Task, TaskState


class PersistenceError(ValueError):
    """Raised when a persistence snapshot cannot be safely stored or recovered."""


@dataclass(frozen=True)
class PersistenceSnapshot:
    """Immutable serialized boundary for one M20 long-horizon state."""

    snapshot_id: str
    plan_id: str
    goal: Goal
    objective: Objective
    tasks: tuple[Task, ...]
    dependencies: tuple[tuple[str, str], ...]
    evaluations: tuple[ProgressEvaluation, ...]
    plan_status: PlanStatus
    schema_version: int = 1

    def __post_init__(self) -> None:
        if not self.snapshot_id.strip():
            raise ValueError("snapshot_id must be non-empty")
        if not self.plan_id.strip():
            raise ValueError("plan_id must be non-empty")
        if self.schema_version != 1:
            raise ValueError("unsupported schema_version")

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "snapshot_id": self.snapshot_id,
            "plan_id": self.plan_id,
            "goal": _goal_to_dict(self.goal),
            "objective": _objective_to_dict(self.objective),
            "tasks": [_task_to_dict(task) for task in self.tasks],
            "dependencies": [list(edge) for edge in self.dependencies],
            "evaluations": [_evaluation_to_dict(evaluation) for evaluation in self.evaluations],
            "plan_status": self.plan_status.value,
            "authority": {
                "authority_granted": False,
                "authorization_granted": False,
                "execution_requested": False,
            },
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), sort_keys=True, separators=(",", ":"))


class PersistenceStore:
    """In-memory durable-shaped store with immutable snapshot replacement."""

    def __init__(self) -> None:
        self._snapshots: dict[str, PersistenceSnapshot] = {}

    def put(self, snapshot: PersistenceSnapshot) -> None:
        existing = self._snapshots.get(snapshot.snapshot_id)
        if existing is not None and existing != snapshot:
            raise PersistenceError("snapshot identity conflict")
        self._snapshots[snapshot.snapshot_id] = snapshot

    def get(self, snapshot_id: str) -> PersistenceSnapshot | None:
        return self._snapshots.get(snapshot_id)


def build_snapshot(
    snapshot_id: str,
    plan: LongHorizonPlan,
    goal: Goal,
    objective: Objective,
    tasks: tuple[Task, ...],
    graph: TaskDependencyGraph,
    evaluations: tuple[ProgressEvaluation, ...],
) -> PersistenceSnapshot:
    task_ids = tuple(task.task_id for task in tasks)
    if set(task_ids) != set(graph.all_task_ids()):
        raise PersistenceError("task and graph identities do not match")
    if set(task_ids) != {evaluation.task_id for evaluation in evaluations}:
        raise PersistenceError("task and evaluation identities do not match")
    if plan.plan_id == "":
        raise PersistenceError("plan identity is required")
    return PersistenceSnapshot(
        snapshot_id=snapshot_id,
        plan_id=plan.plan_id,
        goal=goal,
        objective=objective,
        tasks=tasks,
        dependencies=tuple(sorted(_dependencies(graph))),
        evaluations=tuple(sorted(evaluations, key=lambda item: item.task_id)),
        plan_status=plan.status,
    )


def recover_snapshot(payload: Mapping[str, Any]) -> PersistenceSnapshot:
    if int(payload.get("schema_version", -1)) != 1:
        raise PersistenceError("unsupported schema_version")
    authority = payload.get("authority", {})
    if any(bool(authority.get(key)) for key in ("authority_granted", "authorization_granted", "execution_requested")):
        raise PersistenceError("recovered snapshot cannot carry authority or execution state")

    try:
        goal = _goal_from_dict(payload["goal"])
        objective = _objective_from_dict(payload["objective"])
        tasks = tuple(_task_from_dict(item) for item in payload["tasks"])
        evaluations = tuple(_evaluation_from_dict(item) for item in payload["evaluations"])
        plan_status = PlanStatus(payload["plan_status"])
        dependencies = tuple(tuple(edge) for edge in payload["dependencies"])
    except (KeyError, TypeError, ValueError) as exc:
        raise PersistenceError("invalid persistence payload") from exc

    task_ids = {task.task_id for task in tasks}
    if len(task_ids) != len(tasks):
        raise PersistenceError("duplicate task identity")
    if task_ids != {evaluation.task_id for evaluation in evaluations}:
        raise PersistenceError("task/evaluation identity mismatch")
    for dependent, prerequisite in dependencies:
        if dependent == prerequisite:
            raise PersistenceError("self dependency is not recoverable")
        if dependent not in task_ids or prerequisite not in task_ids:
            raise PersistenceError("dependency references unknown task")

    return PersistenceSnapshot(
        snapshot_id=str(payload["snapshot_id"]),
        plan_id=str(payload["plan_id"]),
        goal=goal,
        objective=objective,
        tasks=tasks,
        dependencies=tuple(sorted(dependencies)),
        evaluations=tuple(sorted(evaluations, key=lambda item: item.task_id)),
        plan_status=plan_status,
    )


def _provenance_to_dict(value: Provenance) -> dict[str, str]:
    return {"source": value.source, "reference_id": value.reference_id}


def _provenance_from_dict(value: Mapping[str, Any]) -> Provenance:
    return Provenance(source=str(value["source"]), reference_id=str(value["reference_id"]))


def _goal_to_dict(value: Goal) -> dict[str, Any]:
    return {"goal_id": value.goal_id, "title": value.title, "description": value.description, "provenance": _provenance_to_dict(value.provenance), "state": value.state.value}


def _goal_from_dict(value: Mapping[str, Any]) -> Goal:
    from .goals import GoalState
    return Goal(str(value["goal_id"]), str(value["title"]), str(value["description"]), _provenance_from_dict(value["provenance"]), GoalState(value["state"]))


def _objective_to_dict(value: Objective) -> dict[str, Any]:
    return {"objective_id": value.objective_id, "goal_id": value.goal_id, "title": value.title, "description": value.description, "provenance": _provenance_to_dict(value.provenance), "state": value.state.value}


def _objective_from_dict(value: Mapping[str, Any]) -> Objective:
    from .goals import ObjectiveState
    return Objective(str(value["objective_id"]), str(value["goal_id"]), str(value["title"]), str(value["description"]), _provenance_from_dict(value["provenance"]), ObjectiveState(value["state"]))


def _task_to_dict(value: Task) -> dict[str, Any]:
    return {"task_id": value.task_id, "objective_id": value.objective_id, "title": value.title, "description": value.description, "provenance": _provenance_to_dict(value.provenance), "state": value.state.value}


def _task_from_dict(value: Mapping[str, Any]) -> Task:
    return Task(str(value["task_id"]), str(value["objective_id"]), str(value["title"]), str(value["description"]), _provenance_from_dict(value["provenance"]), TaskState(value["state"]))


def _evaluation_to_dict(value: ProgressEvaluation) -> dict[str, Any]:
    evidence = value.evidence
    evidence_items = [
        {
            "evidence_id": item.evidence_id,
            "task_id": item.task_id,
            "observed_state": item.observed_state.value,
            "source": item.source,
            "reference_id": item.reference_id,
            "observed_at": item.observed_at,
            "details": item.details,
        }
        for item in evidence
    ]
    return {
        "task_id": value.task_id,
        "recorded_state": value.recorded_state.value,
        "observed_state": value.observed_state.value,
        "status": value.status.value,
        "evidence_ids": list(value.evidence_ids),
        "evidence": evidence_items,
    }


def _evaluation_from_dict(value: Mapping[str, Any]) -> ProgressEvaluation:
    evidence = tuple(
        ProgressEvidence(
            str(item["evidence_id"]), str(item["task_id"]), ObservedState(item["observed_state"]), str(item["source"]), str(item["reference_id"]), item.get("observed_at"), str(item.get("details", ""))
        )
        for item in value.get("evidence", [])
    )
    return ProgressEvaluation(
        task_id=str(value["task_id"]),
        recorded_state=TaskState(value["recorded_state"]),
        observed_state=ObservedState(value["observed_state"]),
        status=ProgressStatus(value["status"]),
        evidence_ids=tuple(value.get("evidence_ids", [])),
        evidence=evidence,
    )


def _dependencies(graph: TaskDependencyGraph) -> tuple[tuple[str, str], ...]:
    edges: list[tuple[str, str]] = []
    for dependent in graph.all_task_ids():
        for prerequisite in graph.prerequisites(dependent):
            edges.append((dependent, prerequisite))
    return tuple(edges)
