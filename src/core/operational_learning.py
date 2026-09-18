"""OPS-07: bounded operational experience, learning, and future-behavior hints."""
from __future__ import annotations

import hashlib
import json
import re
import uuid
from dataclasses import dataclass
from enum import Enum
from typing import Any, Mapping

from src.core.execution_executor_models import (
    PlanExecutionResult,
    PlanExecutionStatus,
)
from src.core.execution_plan_models import ExecutionPlan


class OperationalOutcomeStatus(str, Enum):
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    BLOCKED = "BLOCKED"


class OperationalLearningEvaluationStatus(str, Enum):
    SUCCESS_PATTERN = "SUCCESS_PATTERN"
    FAILURE_PATTERN = "FAILURE_PATTERN"
    BOUNDED_BLOCK = "BOUNDED_BLOCK"


class OperationalAdaptationHintStatus(str, Enum):
    REINFORCE_PATTERN = "REINFORCE_PATTERN"
    CORRECT_PATTERN = "CORRECT_PATTERN"
    PRESERVE_BOUNDARY = "PRESERVE_BOUNDARY"


def _tokens(text: str) -> set[str]:
    return {
        token
        for token in re.findall(r"\b[a-zA-Z0-9][a-zA-Z0-9_-]*\b", text.casefold())
        if token
        not in {
            "a", "an", "and", "for", "in", "is", "it", "of", "on", "the", "to",
            "with", "current", "please", "task",
        }
    }


def _fingerprint(payload: Mapping[str, Any]) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class OperationalExperience:
    """Immutable evidence of one real execution observation."""

    experience_id: str
    plan_id: str
    task_description: str
    outcome_status: OperationalOutcomeStatus
    completed_step_ids: tuple[str, ...]
    failed_step_ids: tuple[str, ...]
    actions: tuple[str, ...]
    failure_reason: str | None
    result_fingerprint: str
    capability: str | None
    evidence_kind: str = "DIRECT_EXECUTION_RESULT"

    @property
    def is_advisory_only(self) -> bool:
        return True

    @property
    def establishes_truth(self) -> bool:
        return False

    @property
    def grants_authority(self) -> bool:
        return False

    @property
    def authorizes_retry(self) -> bool:
        return False

    @property
    def mutates_policy(self) -> bool:
        return False

    @property
    def executes(self) -> bool:
        return False


@dataclass(frozen=True)
class OperationalLearningEvaluation:
    """Immutable deterministic evaluation of one operational experience."""

    evaluation_id: str
    experience_id: str
    status: OperationalLearningEvaluationStatus
    basis: str
    evidence_kind: str = "DIRECT_EXECUTION_RESULT"

    @property
    def is_advisory_only(self) -> bool:
        return True

    @property
    def creates_truth(self) -> bool:
        return False

    @property
    def creates_authority(self) -> bool:
        return False

    @property
    def authorizes_retry(self) -> bool:
        return False

    @property
    def schedules_work(self) -> bool:
        return False

    @property
    def mutates_policy(self) -> bool:
        return False


@dataclass(frozen=True)
class OperationalAdaptationHint:
    """Immutable, non-authoritative future-behavior guidance derived from learning."""

    hint_id: str
    evaluation_id: str
    status: OperationalAdaptationHintStatus
    task_shape: str
    guidance: str

    @property
    def is_advisory_only(self) -> bool:
        return True

    @property
    def changes_authority(self) -> bool:
        return False

    @property
    def changes_policy(self) -> bool:
        return False

    @property
    def authorizes_retry(self) -> bool:
        return False

    @property
    def executes(self) -> bool:
        return False


@dataclass(frozen=True)
class OperationalLearningRecord:
    """Complete immutable experience → learning → adaptation lineage."""

    experience: OperationalExperience
    evaluation: OperationalLearningEvaluation
    adaptation_hint: OperationalAdaptationHint


class OperationalLearningRuntime:
    """Bounded session/runtime learning loop for completed executions."""

    def __init__(self, *, max_history: int = 32) -> None:
        if not isinstance(max_history, int):
            raise TypeError("max_history must be an integer")
        if max_history <= 0:
            raise ValueError("max_history must be positive")
        self._max_history = max_history
        self._records: list[OperationalLearningRecord] = []

    @property
    def records(self) -> tuple[OperationalLearningRecord, ...]:
        return tuple(self._records)

    def record_execution(
        self,
        execution: PlanExecutionResult,
        plan: ExecutionPlan,
        *,
        capability: str | None = None,
    ) -> OperationalLearningRecord:
        if type(execution) is not PlanExecutionResult:
            raise TypeError("execution must be a PlanExecutionResult")
        if type(plan) is not ExecutionPlan:
            raise TypeError("plan must be an ExecutionPlan")
        if execution.plan_id != plan.plan_id:
            raise ValueError("execution and plan identities must match")
        if capability is not None and (not isinstance(capability, str) or not capability.strip()):
            raise ValueError("capability must be None or a non-empty string")

        outcome_status = OperationalOutcomeStatus(execution.status.value)
        failed_steps = tuple(step.step_id for step in execution.failed_steps)
        completed_steps = tuple(
            step.step_id
            for step in execution.steps
            if step.status.value == "COMPLETED"
        )
        actions = tuple(step.action for step in execution.steps)
        failure_reason = execution.error
        if failure_reason is None and failed_steps:
            failure_reason = next(
                (step.error for step in execution.failed_steps if step.error),
                None,
            )

        fingerprint = _fingerprint(
            {
                "plan_id": execution.plan_id,
                "task_description": plan.task_description,
                "status": execution.status.value,
                "steps": [
                    {
                        "step_id": step.step_id,
                        "action": step.action,
                        "status": step.status.value,
                        "error": step.error,
                    }
                    for step in execution.steps
                ],
                "error": execution.error,
            }
        )
        experience = OperationalExperience(
            experience_id=f"experience-{uuid.uuid4()}",
            plan_id=plan.plan_id,
            task_description=plan.task_description,
            outcome_status=outcome_status,
            completed_step_ids=completed_steps,
            failed_step_ids=failed_steps,
            actions=actions,
            failure_reason=failure_reason,
            result_fingerprint=fingerprint,
            capability=capability,
        )

        evaluation_status, basis = {
            PlanExecutionStatus.COMPLETED: (
                OperationalLearningEvaluationStatus.SUCCESS_PATTERN,
                "execution completed successfully; retain the observed task pattern as advisory evidence",
            ),
            PlanExecutionStatus.FAILED: (
                OperationalLearningEvaluationStatus.FAILURE_PATTERN,
                "execution failed; future similar work should consider correction before repetition",
            ),
            PlanExecutionStatus.BLOCKED: (
                OperationalLearningEvaluationStatus.BOUNDED_BLOCK,
                "execution was blocked; preserve existing policy, confirmation, and authorization boundaries",
            ),
        }[execution.status]

        evaluation = OperationalLearningEvaluation(
            evaluation_id=f"learning-evaluation-{uuid.uuid4()}",
            experience_id=experience.experience_id,
            status=evaluation_status,
            basis=basis,
        )
        hint_status, guidance = {
            OperationalLearningEvaluationStatus.SUCCESS_PATTERN: (
                OperationalAdaptationHintStatus.REINFORCE_PATTERN,
                "A similar future task may reuse this successful execution pattern as advisory context.",
            ),
            OperationalLearningEvaluationStatus.FAILURE_PATTERN: (
                OperationalAdaptationHintStatus.CORRECT_PATTERN,
                "A similar future task should treat this prior failure as evidence to consider correction before repeating.",
            ),
            OperationalLearningEvaluationStatus.BOUNDED_BLOCK: (
                OperationalAdaptationHintStatus.PRESERVE_BOUNDARY,
                "A similar future task should preserve the existing policy/confirmation boundary; prior attempts do not create permission.",
            ),
        }[evaluation.status]

        hint = OperationalAdaptationHint(
            hint_id=f"adaptation-hint-{uuid.uuid4()}",
            evaluation_id=evaluation.evaluation_id,
            status=hint_status,
            task_shape=plan.task_description,
            guidance=guidance,
        )
        record = OperationalLearningRecord(
            experience=experience,
            evaluation=evaluation,
            adaptation_hint=hint,
        )
        self._records.append(record)
        if len(self._records) > self._max_history:
            del self._records[: len(self._records) - self._max_history]
        return record

    def context_for(self, request: str, *, max_matches: int = 5) -> Mapping[str, Any]:
        if not isinstance(request, str):
            raise TypeError("request must be a string")
        if not isinstance(max_matches, int) or max_matches < 0:
            raise ValueError("max_matches must be a non-negative integer")

        query_tokens = _tokens(request)
        scored: list[tuple[int, int, OperationalLearningRecord]] = []
        for index, record in enumerate(self._records):
            overlap = len(query_tokens & _tokens(record.experience.task_description))
            scored.append((overlap, index, record))

        scored.sort(key=lambda item: (item[0], item[1]), reverse=True)
        selected = [
            item[2]
            for item in scored
            if item[0] > 0
        ][:max_matches]

        if not selected and self._records and max_matches > 0:
            selected = list(self._records[-max_matches:])

        return {
            "available": bool(self._records),
            "authority_granted": False,
            "execution_requested": False,
            "truth_established": False,
            "matches": tuple(
                {
                    "experience_id": record.experience.experience_id,
                    "plan_id": record.experience.plan_id,
                    "task_shape": record.experience.task_description,
                    "outcome_status": record.experience.outcome_status.value,
                    "failure_reason": record.experience.failure_reason,
                    "result_fingerprint": record.experience.result_fingerprint,
                    "evaluation_id": record.evaluation.evaluation_id,
                    "learning_status": record.evaluation.status.value,
                    "adaptation_hint_id": record.adaptation_hint.hint_id,
                    "adaptation_hint_status": record.adaptation_hint.status.value,
                    "guidance": record.adaptation_hint.guidance,
                }
                for record in selected
            ),
        }


__all__ = [
    "OperationalOutcomeStatus",
    "OperationalLearningEvaluationStatus",
    "OperationalAdaptationHintStatus",
    "OperationalExperience",
    "OperationalLearningEvaluation",
    "OperationalAdaptationHint",
    "OperationalLearningRecord",
    "OperationalLearningRuntime",
]
