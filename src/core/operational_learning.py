"""OPS-07: bounded operational experience, learning, and future-behavior hints."""
from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Mapping

from src.core.memory_provenance import ProvenanceChain, ProvenanceRef, ProvenanceSourceKind
from src.core.persistent_intelligence import PersistentMemoryRepository
from src.core.persistent_memory import MemoryLifecycle, PersistentMemoryKind, PersistentMemoryRecord

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
    REVIEW_REQUIRED = "REVIEW_REQUIRED"


class OperationalAdaptationHintStatus(str, Enum):
    REINFORCE_PATTERN = "REINFORCE_PATTERN"
    CORRECT_PATTERN = "CORRECT_PATTERN"
    PRESERVE_BOUNDARY = "PRESERVE_BOUNDARY"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"


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
    persisted: bool = False
    persistence_error: str | None = None


class OperationalLearningRuntime:
    """Bounded session/runtime learning loop for completed executions."""

    def __init__(
        self,
        *,
        max_history: int = 32,
        repository: PersistentMemoryRepository | None = None,
        subject_id: str = "jarvis-operational-learning",
    ) -> None:
        if not isinstance(max_history, int):
            raise TypeError("max_history must be an integer")
        if max_history <= 0:
            raise ValueError("max_history must be positive")
        if repository is not None and type(repository) is not PersistentMemoryRepository:
            raise TypeError("repository must be a PersistentMemoryRepository or None")
        if not isinstance(subject_id, str) or not subject_id.strip():
            raise ValueError("subject_id must be a non-empty string")
        self._max_history = max_history
        self._repository = repository
        self._subject_id = subject_id.strip()
        self._records: list[OperationalLearningRecord] = []
        self._persistence_error: str | None = None
        self._hydrate_persisted()

    @property
    def records(self) -> tuple[OperationalLearningRecord, ...]:
        return tuple(self._records)

    @property
    def repository(self) -> PersistentMemoryRepository | None:
        return self._repository

    @property
    def persistence_error(self) -> str | None:
        return self._persistence_error

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
            experience_id=f"experience-{fingerprint[:24]}",
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

        tool_outcomes = tuple(
            step.metadata.get("tool_outcome")
            for step in execution.steps
            if isinstance(step.metadata, Mapping)
            and isinstance(step.metadata.get("tool_outcome"), Mapping)
        )
        externally_verified = bool(tool_outcomes) and all(
            str(outcome.get("verification_state", "")).upper() == "VERIFIED"
            for outcome in tool_outcomes
        )

        if execution.status is PlanExecutionStatus.COMPLETED and tool_outcomes and not externally_verified:
            evaluation_status = OperationalLearningEvaluationStatus.REVIEW_REQUIRED
            basis = (
                "execution completed successfully, but the tool outcome is not externally verified; "
                "retain the execution evidence without reinforcing it as a verified success"
            )
        else:
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
            evaluation_id=f"learning-evaluation-{experience.experience_id.removeprefix('experience-')}",
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
            OperationalLearningEvaluationStatus.REVIEW_REQUIRED: (
                OperationalAdaptationHintStatus.REVIEW_REQUIRED,
                "A similar future task should treat this execution as unverified evidence; do not reinforce it as externally verified success.",
            ),
        }[evaluation.status]

        hint = OperationalAdaptationHint(
            hint_id=f"adaptation-hint-{experience.experience_id.removeprefix('experience-')}",
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
        persisted, persistence_error = self._persist_record(record)
        record = OperationalLearningRecord(
            experience=record.experience,
            evaluation=record.evaluation,
            adaptation_hint=record.adaptation_hint,
            persisted=persisted,
            persistence_error=persistence_error,
        )
        self._records.append(record)
        if len(self._records) > self._max_history:
            del self._records[: len(self._records) - self._max_history]
        return record

    def _persist_record(
        self,
        record: OperationalLearningRecord,
    ) -> tuple[bool, str | None]:
        if self._repository is None:
            return False, None

        payload = {
            "experience": {
                "experience_id": record.experience.experience_id,
                "plan_id": record.experience.plan_id,
                "task_description": record.experience.task_description,
                "outcome_status": record.experience.outcome_status.value,
                "completed_step_ids": record.experience.completed_step_ids,
                "failed_step_ids": record.experience.failed_step_ids,
                "actions": record.experience.actions,
                "failure_reason": record.experience.failure_reason,
                "result_fingerprint": record.experience.result_fingerprint,
                "capability": record.experience.capability,
                "evidence_kind": record.experience.evidence_kind,
            },
            "evaluation": {
                "evaluation_id": record.evaluation.evaluation_id,
                "experience_id": record.evaluation.experience_id,
                "status": record.evaluation.status.value,
                "basis": record.evaluation.basis,
                "evidence_kind": record.evaluation.evidence_kind,
            },
            "adaptation_hint": {
                "hint_id": record.adaptation_hint.hint_id,
                "evaluation_id": record.adaptation_hint.evaluation_id,
                "status": record.adaptation_hint.status.value,
                "task_shape": record.adaptation_hint.task_shape,
                "guidance": record.adaptation_hint.guidance,
            },
        }
        content = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
        memory_id = f"operational-learning-{record.experience.experience_id.removeprefix('experience-')}"
        provenance_id = f"operational-learning-provenance-{record.experience.result_fingerprint[:24]}"
        now = datetime.now(timezone.utc).isoformat()
        persistent_record = PersistentMemoryRecord(
            memory_id=memory_id,
            subject_id=self._subject_id,
            kind=PersistentMemoryKind.EPISODIC,
            content=content,
            confidence=0.5,
            importance=0.5,
            status=MemoryLifecycle.CANDIDATE,
            created_at=now,
            updated_at=now,
            provenance_ids=(provenance_id,),
            tags=("operational_learning", "candidate", record.evaluation.status.value),
            metadata={
                "source": "operational_learning",
                "experience_id": record.experience.experience_id,
                "evaluation_id": record.evaluation.evaluation_id,
                "adaptation_hint_id": record.adaptation_hint.hint_id,
                "authority_granted": False,
                "execution_requested": False,
                "truth_established": False,
            },
        )
        try:
            persisted = self._repository.persist(
                persistent_record,
                ProvenanceChain(
                    refs=(
                        ProvenanceRef(
                            provenance_id=provenance_id,
                            source_kind=ProvenanceSourceKind.EXPERIENCE,
                            source_id=record.experience.experience_id,
                            summary="operational execution learning evidence",
                            observed_at=now,
                            confidence=0.5,
                        ),
                    )
                ),
            )
            return True, None if persisted else None
        except Exception as exc:
            error = f"{type(exc).__name__}: {exc}"
            self._persistence_error = error
            return False, error

    def _hydrate_persisted(self) -> None:
        if self._repository is None:
            return
        try:
            records = self._repository.list_records(
                kind=PersistentMemoryKind.EPISODIC,
                subject_id=self._subject_id,
                status=MemoryLifecycle.CANDIDATE,
            )
            hydrated: list[OperationalLearningRecord] = []
            for stored in records:
                if stored.metadata.get("source") != "operational_learning":
                    continue
                try:
                    payload = json.loads(stored.content)
                    experience_payload = payload["experience"]
                    evaluation_payload = payload["evaluation"]
                    hint_payload = payload["adaptation_hint"]
                    hydrated.append(
                        OperationalLearningRecord(
                            experience=OperationalExperience(
                                experience_id=experience_payload["experience_id"],
                                plan_id=experience_payload["plan_id"],
                                task_description=experience_payload["task_description"],
                                outcome_status=OperationalOutcomeStatus(experience_payload["outcome_status"]),
                                completed_step_ids=tuple(experience_payload["completed_step_ids"]),
                                failed_step_ids=tuple(experience_payload["failed_step_ids"]),
                                actions=tuple(experience_payload["actions"]),
                                failure_reason=experience_payload["failure_reason"],
                                result_fingerprint=experience_payload["result_fingerprint"],
                                capability=experience_payload["capability"],
                                evidence_kind=experience_payload["evidence_kind"],
                            ),
                            evaluation=OperationalLearningEvaluation(
                                evaluation_id=evaluation_payload["evaluation_id"],
                                experience_id=evaluation_payload["experience_id"],
                                status=OperationalLearningEvaluationStatus(evaluation_payload["status"]),
                                basis=evaluation_payload["basis"],
                                evidence_kind=evaluation_payload["evidence_kind"],
                            ),
                            adaptation_hint=OperationalAdaptationHint(
                                hint_id=hint_payload["hint_id"],
                                evaluation_id=hint_payload["evaluation_id"],
                                status=OperationalAdaptationHintStatus(hint_payload["status"]),
                                task_shape=hint_payload["task_shape"],
                                guidance=hint_payload["guidance"],
                            ),
                            persisted=True,
                        )
                    )
                except (KeyError, TypeError, ValueError, json.JSONDecodeError):
                    continue
            self._records = hydrated[-self._max_history :]
        except Exception as exc:
            self._persistence_error = f"{type(exc).__name__}: {exc}"

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
            "persistence_available": self._repository is not None,
            "persistence_error": self._persistence_error,
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
                    "persisted": record.persisted,
                    "persistence_error": record.persistence_error,
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
