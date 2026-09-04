"""M20 long-horizon task management primitives."""

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
from .progress import (
    ObservedState,
    ProgressEvidence,
    ProgressEvaluation,
    ProgressEvaluationError,
    ProgressStatus,
    TaskProgressEvaluator,
)
from .task import Task, TaskState, TaskStore, TaskTransitionError

__all__ = [
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
    "ObservedState",
    "ProgressEvidence",
    "ProgressEvaluation",
    "ProgressEvaluationError",
    "ProgressStatus",
    "TaskProgressEvaluator",
    "Task",
    "TaskState",
    "TaskStore",
    "TaskTransitionError",
]
