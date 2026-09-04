"""M20 long-horizon task management primitives."""

from .continuation import (
    ContinuationError,
    ContinuationDecision,
    ContinuationStatus,
    NextStepEngine,
    NextStepProposal,
)
from .dependencies import DependencyError, TaskDependency, TaskDependencyGraph
from .goals import (
    Goal,
    GoalObjectiveStore,
    GoalState,
    Objective,
    ObjectiveState,
    ObjectiveTransitionError,
    Provenance,
)
from .planning import LongHorizonPlan, LongHorizonPlanner, PlanStatus, PlanStep, PlanningError
from .progress import (
    ObservedState,
    ProgressEvidence,
    ProgressEvaluation,
    ProgressEvaluationError,
    ProgressStatus,
    TaskProgressEvaluator,
)
from .persistence import PersistenceError, PersistenceSnapshot, PersistenceStore, build_snapshot, recover_snapshot
from .runtime import LongHorizonRuntime, LongHorizonRuntimeError, RuntimeState
from .task import Task, TaskState, TaskStore, TaskTransitionError

__all__ = [
    "ContinuationError",
    "ContinuationDecision",
    "ContinuationStatus",
    "NextStepEngine",
    "NextStepProposal",
    "DependencyError",
    "TaskDependency",
    "TaskDependencyGraph",
    "Goal",
    "GoalObjectiveStore",
    "GoalState",
    "Objective",
    "ObjectiveState",
    "ObjectiveTransitionError",
    "Provenance",
    "LongHorizonPlan",
    "LongHorizonPlanner",
    "PlanStatus",
    "PlanStep",
    "PlanningError",
    "ObservedState",
    "ProgressEvidence",
    "ProgressEvaluation",
    "ProgressEvaluationError",
    "ProgressStatus",
    "TaskProgressEvaluator",
    "PersistenceError",
    "PersistenceSnapshot",
    "PersistenceStore",
    "build_snapshot",
    "recover_snapshot",
    "LongHorizonRuntime",
    "LongHorizonRuntimeError",
    "RuntimeState",
    "Task",
    "TaskState",
    "TaskStore",
    "TaskTransitionError",
]
