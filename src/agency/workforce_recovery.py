"""M9.6 bounded workforce reliability and recovery."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from types import MappingProxyType
from typing import Any, Mapping, Optional

from src.agency.delegation import DelegationPlan
from src.agency.workforce import WorkerAssignment


class WorkerRecoveryState(str, Enum):
    RETRYABLE = "RETRYABLE"
    BLOCKED = "BLOCKED"
    PARTIAL = "PARTIAL"
    INTERRUPTED = "INTERRUPTED"
    RECONCILE = "RECONCILE"
    TERMINAL = "TERMINAL"
    COMPLETED = "COMPLETED"


class WorkforceRecoveryConflictError(ValueError):
    """Raised when recovery identities or evidence conflict."""


@dataclass(frozen=True)
class WorkerRecoveryAssessment:
    plan_id: str
    assignment_id: str
    worker_id: str
    state: WorkerRecoveryState
    attempt_count: int = 0
    retryable: bool = False
    evidence: Mapping[str, Any] = field(default_factory=dict)
    execution_id: Optional[str] = None
    result_id: Optional[str] = None

    def __post_init__(self) -> None:
        for field_name in ("plan_id", "assignment_id", "worker_id"):
            value = getattr(self, field_name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{field_name} must be a non-empty string")
        if not isinstance(self.state, WorkerRecoveryState):
            try:
                object.__setattr__(self, "state", WorkerRecoveryState(self.state))
            except (TypeError, ValueError) as exc:
                raise TypeError("state must be a WorkerRecoveryState") from exc
        if not isinstance(self.attempt_count, int) or isinstance(self.attempt_count, bool) or self.attempt_count < 0:
            raise ValueError("attempt_count must be a non-negative integer")
        if not isinstance(self.retryable, bool):
            raise TypeError("retryable must be a bool")
        if self.state != WorkerRecoveryState.RETRYABLE and self.retryable:
            raise ValueError("only RETRYABLE assessments may be retryable")
        for field_name in ("execution_id", "result_id"):
            value = getattr(self, field_name)
            if value is not None and (not isinstance(value, str) or not value.strip()):
                raise ValueError(f"{field_name} must be None or a non-empty string")
        if not isinstance(self.evidence, Mapping):
            raise TypeError("evidence must be a mapping")
        object.__setattr__(self, "evidence", MappingProxyType(dict(self.evidence)))

    def to_context(self) -> dict[str, Any]:
        return {
            "plan_id": self.plan_id,
            "assignment_id": self.assignment_id,
            "worker_id": self.worker_id,
            "state": self.state.value,
            "attempt_count": self.attempt_count,
            "retryable": self.retryable,
            "evidence": dict(self.evidence),
            "execution_id": self.execution_id,
            "result_id": self.result_id,
            "authorization_granted": False,
            "capability_escalation": False,
            "global_context_access": False,
        }


@dataclass(frozen=True)
class WorkerRecoveryIntent:
    assessment: WorkerRecoveryAssessment
    max_retries: int = 0
    fresh_authorization_required: bool = True
    preserve_assignment_scope: bool = True

    def __post_init__(self) -> None:
        if not isinstance(self.assessment, WorkerRecoveryAssessment):
            raise TypeError("assessment must be a WorkerRecoveryAssessment")
        if not isinstance(self.max_retries, int) or isinstance(self.max_retries, bool) or self.max_retries < 0:
            raise ValueError("max_retries must be a non-negative integer")
        if not isinstance(self.fresh_authorization_required, bool):
            raise TypeError("fresh_authorization_required must be a bool")
        if not isinstance(self.preserve_assignment_scope, bool):
            raise TypeError("preserve_assignment_scope must be a bool")
        if self.assessment.retryable and self.max_retries <= 0:
            raise ValueError("retryable recovery requires a positive retry bound")
        if self.max_retries > 0 and not self.assessment.retryable:
            raise ValueError("non-retryable recovery cannot request retries")
        if self.assessment.retryable and not self.fresh_authorization_required:
            raise ValueError("retry recovery requires fresh authorization")
        if not self.preserve_assignment_scope:
            raise ValueError("recovery cannot relax assignment scope")

    @property
    def should_retry(self) -> bool:
        return self.assessment.retryable and self.assessment.attempt_count < self.max_retries

    def to_context(self) -> dict[str, Any]:
        return {
            "plan_id": self.assessment.plan_id,
            "assignment_id": self.assessment.assignment_id,
            "worker_id": self.assessment.worker_id,
            "state": self.assessment.state.value,
            "attempt_count": self.assessment.attempt_count,
            "max_retries": self.max_retries,
            "should_retry": self.should_retry,
            "fresh_authorization_required": self.fresh_authorization_required,
            "preserve_assignment_scope": self.preserve_assignment_scope,
            "authorization_granted": False,
            "capability_escalation": False,
            "execution_performed": False,
        }


class WorkerRecoveryStore:
    def __init__(self) -> None:
        self._records: dict[tuple[str, str, str], WorkerRecoveryAssessment] = {}

    def record(self, assessment: WorkerRecoveryAssessment) -> WorkerRecoveryAssessment:
        if not isinstance(assessment, WorkerRecoveryAssessment):
            raise TypeError("assessment must be a WorkerRecoveryAssessment")
        key = (assessment.plan_id, assessment.assignment_id, assessment.worker_id)
        existing = self._records.get(key)
        if existing is not None and existing != assessment:
            raise WorkforceRecoveryConflictError(
                f"conflicting recovery assessment: {assessment.plan_id}/{assessment.assignment_id}/{assessment.worker_id}"
            )
        self._records[key] = assessment
        return existing if existing is not None else assessment

    def get(self, plan_id: str, assignment_id: str, worker_id: str) -> WorkerRecoveryAssessment | None:
        return self._records.get((plan_id, assignment_id, worker_id))

    def snapshot(self) -> tuple[WorkerRecoveryAssessment, ...]:
        return tuple(self._records[key] for key in sorted(self._records))


class WorkforceRecoveryPlanner:
    def __init__(self, *, default_max_retries: int = 0) -> None:
        if not isinstance(default_max_retries, int) or isinstance(default_max_retries, bool) or default_max_retries < 0:
            raise ValueError("default_max_retries must be a non-negative integer")
        self._default_max_retries = default_max_retries

    def assess(
        self,
        plan: DelegationPlan,
        assignment: WorkerAssignment,
        *,
        state: WorkerRecoveryState,
        attempt_count: int = 0,
        retryable: bool = False,
        evidence: Mapping[str, Any] | None = None,
        execution_id: str | None = None,
        result_id: str | None = None,
    ) -> WorkerRecoveryAssessment:
        if not isinstance(plan, DelegationPlan):
            raise TypeError("plan must be a DelegationPlan")
        if not isinstance(assignment, WorkerAssignment):
            raise TypeError("assignment must be a WorkerAssignment")
        assignment_ids = {item.assignment_id for item in plan.assignments}
        if assignment.assignment_id not in assignment_ids:
            raise ValueError("assignment is not part of the delegation plan")
        return WorkerRecoveryAssessment(
            plan_id=plan.plan_id,
            assignment_id=assignment.assignment_id,
            worker_id=assignment.worker_id,
            state=state,
            attempt_count=attempt_count,
            retryable=retryable,
            evidence={} if evidence is None else evidence,
            execution_id=execution_id,
            result_id=result_id,
        )

    def plan_retry(self, assessment: WorkerRecoveryAssessment, *, max_retries: int | None = None) -> WorkerRecoveryIntent:
        bound = self._default_max_retries if max_retries is None else max_retries
        return WorkerRecoveryIntent(assessment=assessment, max_retries=bound)

    def ensure_dependency_ready(
        self,
        plan: DelegationPlan,
        assignment_id: str,
        completed_assignment_ids: set[str] | frozenset[str],
    ) -> None:
        if not isinstance(plan, DelegationPlan):
            raise TypeError("plan must be a DelegationPlan")
        assignment_ids = {item.assignment_id for item in plan.assignments}
        if assignment_id not in assignment_ids:
            raise ValueError(f"unknown assignment: {assignment_id}")
        completed = set(completed_assignment_ids)
        required = set(plan.dependencies.get(assignment_id, ()))
        if not required.issubset(completed):
            raise WorkforceRecoveryConflictError(
                f"cannot recover assignment {assignment_id}; dependencies incomplete: {sorted(required - completed)}"
            )
