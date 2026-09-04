"""M20.7 persistence and recovery boundary.

Persistence captures the current M20 long-horizon state without granting
authority, authorization, or execution. Recovery reconstructs equivalent
immutable domain objects and never invents missing progress or outcomes.
"""

from __future__ import annotations

from dataclasses import dataclass
import json
from typing import Any, Mapping

from .dependencies import TaskDependencyGraph
from .goals import Goal, GoalState, Objective, ObjectiveState, Provenance
from .planning import LongHorizonPlan, LongHorizonPlanner, PlanStatus
from .progress import (
    ObservedState,
    ProgressEvidence,
    ProgressEvaluation,
    ProgressStatus,
    TaskProgressEvaluator,
)
from .task import Task, TaskState


class PersistenceError(ValueError):
    """Raised when a persistence snapshot cannot be safely stored or recovered."""


@dataclass(frozen=True)
class PersistenceSnapshot:
    """Immutable serialized boundary for one long-horizon state."""

    snapshot_id: str
    plan_id: str
    goal: Goal
    objective: Objective
    tasks: tuple[Task, ...]
    dependencies: tuple[tuple[str, str], ...]
    evidence: tuple[ProgressEvidence, ...]
    evaluations: tuple[ProgressEvaluation, ...]
    plan_status: PlanStatus
    schema_version: int = 1

    def __post_init__(self) -> None:
        if not isinstance(self.snapshot_id, str) or not self.snapshot_id.strip():
            raise ValueError("snapshot_id must be non-empty")
        if not isinstance(self.plan_id, str) or not self.plan_id.strip():
            raise ValueError("plan_id must be non-empty")
        if self.schema_version != 1:
            raise ValueError("unsupported schema_version")
        task_ids = {task.task_id for task in self.tasks}
        if len(task_ids) != len(self.tasks):
            raise ValueError("duplicate task identity")
        if task_ids != {evaluation.task_id for evaluation in self.evaluations}:
            raise ValueError("task/evaluation identity mismatch")
        evidence_ids = {item.evidence_id for item in self.evidence}
        if len(evidence_ids) != len(self.evidence):
            raise ValueError("duplicate evidence identity")
        if not {item.task_id for item in self.evidence}.issubset(task_ids):
            raise ValueError("evidence references unknown task")
        if any(item not in evidence_ids for evaluation in self.evaluations for item in evaluation.evidence_ids):
            raise ValueError("evaluation references missing evidence")

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "snapshot_id": self.snapshot_id,
            "plan_id": self.plan_id,
            "goal": _goal_to_dict(self.goal),
            "objective": _objective_to_dict(self.objective),
            "tasks": [_task_to_dict(task) for task in self.tasks],
            "dependencies": [list(edge) for edge in self.dependencies],
            "evidence": [_evidence_to_dict(item) for item in self.evidence],
            "evaluations": [_evaluation_to_dict(item) for item in self.evaluations],
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
    """Conflict-aware immutable snapshot store."""

    def __init__(self) -> None:
        self._snapshots: dict[str, PersistenceSnapshot] = {}

    def put(self, snapshot: PersistenceSnapshot) -> None:
        if not isinstance(snapshot, PersistenceSnapshot):
            raise TypeError("snapshot must be a PersistenceSnapshot")
        existing = self._snapshots.get(snapshot.snapshot_id)
        if existing is not None and existing != snapshot:
            raise PersistenceError(f"snapshot identity conflict: {snapshot.snapshot_id}")
        self._snapshots[snapshot.snapshot_id] = snapshot

    def get(self, snapshot_id: str) -> PersistenceSnapshot | None:
        if not isinstance(snapshot_id, str) or not snapshot_id.strip():
            raise ValueError("snapshot_id must be non-empty")
        return self._snapshots.get(snapshot_id)

    def all_snapshots(self) -> tuple[PersistenceSnapshot, ...]:
        return tuple(sorted(self._snapshots.values(), key=lambda item: item.snapshot_id))


def build_snapshot(
    snapshot_id: str,
    plan: LongHorizonPlan,
    goal: Goal,
    objective: Objective,
    tasks: tuple[Task, ...],
    graph: TaskDependencyGraph,
    evaluator: TaskProgressEvaluator,
) -> PersistenceSnapshot:
    task_ids = tuple(task.task_id for task in tasks)
    if objective.goal_id != goal.goal_id:
        raise PersistenceError("objective does not belong to goal")
    if set(task_ids) != set(graph.all_task_ids()):
        raise PersistenceError("task and graph identities do not match")
    evaluations = evaluator.evaluations()
    if set(task_ids) != {evaluation.task_id for evaluation in evaluations}:
        raise PersistenceError("task and evaluation identities do not match")
    if tuple(step.task_id for step in plan.steps) != graph.topological_order():
        raise PersistenceError("plan and graph ordering do not match")
    if plan.goal_id != goal.goal_id or plan.objective_id != objective.objective_id:
        raise PersistenceError("plan goal/objective identity mismatch")
    evidence = tuple(
        sorted(
            (item for task_id in sorted(task_ids) for item in evaluator.evidence_for(task_id)),
            key=lambda item: (item.task_id, item.observed_at, item.evidence_id),
        )
    )
    return PersistenceSnapshot(
        snapshot_id=snapshot_id,
        plan_id=plan.plan_id,
        goal=goal,
        objective=objective,
        tasks=tuple(sorted(tasks, key=lambda item: item.task_id)),
        dependencies=tuple(sorted(_dependencies(graph))),
        evidence=evidence,
        evaluations=tuple(sorted(evaluations, key=lambda item: item.task_id)),
        plan_status=plan.status,
    )


def recover_snapshot(payload: Mapping[str, Any] | str) -> PersistenceSnapshot:
    if isinstance(payload, str):
        try:
            payload = json.loads(payload)
        except json.JSONDecodeError as exc:
            raise PersistenceError("invalid JSON persistence payload") from exc
    if not isinstance(payload, Mapping):
        raise PersistenceError("persistence payload must be a mapping")
    if int(payload.get("schema_version", -1)) != 1:
        raise PersistenceError("unsupported schema_version")

    authority = payload.get("authority", {})
    if not isinstance(authority, Mapping):
        raise PersistenceError("invalid authority metadata")
    if any(bool(authority.get(key)) for key in ("authority_granted", "authorization_granted", "execution_requested")):
        raise PersistenceError("recovered state cannot carry authority or execution state")

    try:
        goal = _goal_from_dict(payload["goal"])
        objective = _objective_from_dict(payload["objective"])
        tasks = tuple(_task_from_dict(item) for item in payload["tasks"])
        dependencies = tuple(tuple(edge) for edge in payload["dependencies"])
        evidence = tuple(_evidence_from_dict(item) for item in payload["evidence"])
        evaluations = tuple(_evaluation_from_dict(item) for item in payload["evaluations"])
        plan_status = PlanStatus(payload["plan_status"])
        snapshot = PersistenceSnapshot(
            snapshot_id=str(payload["snapshot_id"]),
            plan_id=str(payload["plan_id"]),
            goal=goal,
            objective=objective,
            tasks=tuple(sorted(tasks, key=lambda item: item.task_id)),
            dependencies=tuple(sorted(dependencies)),
            evidence=tuple(sorted(evidence, key=lambda item: (item.task_id, item.observed_at, item.evidence_id))),
            evaluations=tuple(sorted(evaluations, key=lambda item: item.task_id)),
            plan_status=plan_status,
        )
    except (KeyError, TypeError, ValueError) as exc:
        raise PersistenceError("invalid persistence payload") from exc

    task_ids = {task.task_id for task in snapshot.tasks}
    graph = TaskDependencyGraph(task_ids)
    try:
        for dependent, prerequisite in snapshot.dependencies:
            graph.add_dependency(dependent, prerequisite)
    except (KeyError, ValueError, TypeError) as exc:
        raise PersistenceError("invalid dependency structure") from exc

    evaluator = TaskProgressEvaluator(snapshot.tasks)
    try:
        for item in snapshot.evidence:
            evaluator.add_evidence(item)
    except (TypeError, ValueError) as exc:
        raise PersistenceError("invalid evidence set") from exc
    recovered_evaluations = evaluator.evaluations()
    if recovered_evaluations != snapshot.evaluations:
        raise PersistenceError("recovered evaluations differ from persisted evaluations")

    try:
        recovered_plan = LongHorizonPlanner(
            snapshot.goal,
            snapshot.objective,
            snapshot.tasks,
            graph,
            evaluator,
        ).build(plan_id=snapshot.plan_id)
    except (TypeError, ValueError) as exc:
        raise PersistenceError("recovered plan could not be reconstructed") from exc
    if recovered_plan.status is not snapshot.plan_status:
        raise PersistenceError("recovered plan status differs from persisted status")

    return snapshot


def _provenance_from_dict(value: Mapping[str, Any]) -> Provenance:
    return Provenance(source=str(value["source"]), reference_id=str(value["reference_id"]))


def _goal_to_dict(value: Goal) -> dict[str, Any]:
    return {
        "goal_id": value.goal_id,
        "title": value.title,
        "description": value.description,
        "provenance": value.provenance.to_dict(),
        "state": value.state.value,
        "created_at": value.created_at,
        "metadata": dict(value.metadata),
    }


def _goal_from_dict(value: Mapping[str, Any]) -> Goal:
    return Goal(
        goal_id=str(value["goal_id"]),
        title=str(value["title"]),
        description=str(value["description"]),
        provenance=_provenance_from_dict(value["provenance"]),
        state=GoalState(value["state"]),
        created_at=str(value["created_at"]),
        metadata=dict(value.get("metadata", {})),
    )


def _objective_to_dict(value: Objective) -> dict[str, Any]:
    return {
        "objective_id": value.objective_id,
        "goal_id": value.goal_id,
        "title": value.title,
        "description": value.description,
        "provenance": value.provenance.to_dict(),
        "state": value.state.value,
        "priority": value.priority,
        "created_at": value.created_at,
        "updated_at": value.updated_at,
        "metadata": dict(value.metadata),
    }


def _objective_from_dict(value: Mapping[str, Any]) -> Objective:
    return Objective(
        objective_id=str(value["objective_id"]),
        goal_id=str(value["goal_id"]),
        title=str(value["title"]),
        description=str(value["description"]),
        provenance=_provenance_from_dict(value["provenance"]),
        state=ObjectiveState(value["state"]),
        priority=int(value["priority"]),
        created_at=str(value["created_at"]),
        updated_at=str(value["updated_at"]),
        metadata=dict(value.get("metadata", {})),
    )


def _task_to_dict(value: Task) -> dict[str, Any]:
    return {
        "task_id": value.task_id,
        "objective_id": value.objective_id,
        "title": value.title,
        "description": value.description,
        "provenance": value.provenance.to_dict(),
        "state": value.state.value,
        "priority": value.priority,
        "created_at": value.created_at,
        "updated_at": value.updated_at,
        "metadata": dict(value.metadata),
    }


def _task_from_dict(value: Mapping[str, Any]) -> Task:
    return Task(
        task_id=str(value["task_id"]),
        objective_id=str(value["objective_id"]),
        title=str(value["title"]),
        description=str(value["description"]),
        provenance=_provenance_from_dict(value["provenance"]),
        state=TaskState(value["state"]),
        priority=int(value["priority"]),
        created_at=str(value["created_at"]),
        updated_at=str(value["updated_at"]),
        metadata=dict(value.get("metadata", {})),
    )


def _evidence_to_dict(value: ProgressEvidence) -> dict[str, Any]:
    return {
        "evidence_id": value.evidence_id,
        "task_id": value.task_id,
        "observed_state": value.observed_state.value,
        "source": value.source,
        "reference_id": value.reference_id,
        "observed_at": value.observed_at,
        "details": value.details,
    }


def _evidence_from_dict(value: Mapping[str, Any]) -> ProgressEvidence:
    return ProgressEvidence(
        evidence_id=str(value["evidence_id"]),
        task_id=str(value["task_id"]),
        observed_state=ObservedState(value["observed_state"]),
        source=str(value["source"]),
        reference_id=str(value["reference_id"]),
        observed_at=str(value["observed_at"]),
        details=str(value.get("details", "")),
    )


def _evaluation_to_dict(value: ProgressEvaluation) -> dict[str, Any]:
    return {
        "task_id": value.task_id,
        "recorded_state": value.recorded_state.value,
        "observed_state": value.observed_state.value,
        "status": value.status.value,
        "evidence_ids": list(value.evidence_ids),
    }


def _evaluation_from_dict(value: Mapping[str, Any]) -> ProgressEvaluation:
    return ProgressEvaluation(
        task_id=str(value["task_id"]),
        recorded_state=TaskState(value["recorded_state"]),
        observed_state=ObservedState(value["observed_state"]),
        status=ProgressStatus(value["status"]),
        evidence_ids=tuple(value.get("evidence_ids", [])),
    )


def _dependencies(graph: TaskDependencyGraph) -> tuple[tuple[str, str], ...]:
    return tuple(
        (dependent, prerequisite)
        for dependent in graph.all_task_ids()
        for prerequisite in graph.prerequisites(dependent)
    )
