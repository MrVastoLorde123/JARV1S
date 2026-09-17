"""Post-execution learning bridge for the production coding path.

The coding worker already performs execution through the canonical tool gate.
This module observes that completed result exactly once, converts its evidence
into the existing immutable experience/evaluation contracts, and stores the
experience as a durable CANDIDATE episodic record. It never authorizes,
executes, retries, promotes, or mutates active memory.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import json
from typing import Any

from src.agents.coding_claim_evidence import CodingClaimEvidenceAdapter, CodingClaimEvidenceResult
from src.agents.coding_worker import CodingAgentPlan, CodingAgentResult, CodingAgentTask
from src.core.persistent_intelligence import PersistentMemoryRepository
from src.core.persistent_memory import MemoryLifecycle, PersistentMemoryKind, PersistentMemoryRecord
from src.core.memory_provenance import ProvenanceChain, ProvenanceRef, ProvenanceSourceKind
from src.learning.evaluation import Evidence as LearningEvidence
from src.learning.evaluation import Evaluation, OutcomeAssessment, OutcomeEvaluator
from src.learning.experience import Experience


@dataclass(frozen=True)
class CodingExecutionLearningRecord:
    """Durable learning evidence produced from one already-completed execution."""

    execution_id: str
    experience: Experience
    evaluation: Evaluation
    claim_evaluation_state: str
    memory_id: str
    persisted: bool
    persistence_error: str | None = None

    def __post_init__(self) -> None:
        for name in ("execution_id", "claim_evaluation_state", "memory_id"):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string")
        if not isinstance(self.experience, Experience):
            raise TypeError("experience must be an Experience")
        if not isinstance(self.evaluation, Evaluation):
            raise TypeError("evaluation must be an Evaluation")
        if not isinstance(self.persisted, bool):
            raise TypeError("persisted must be a bool")
        if self.persistence_error is not None and not isinstance(self.persistence_error, str):
            raise TypeError("persistence_error must be a string or None")

    def to_metadata(self) -> dict[str, object]:
        return {
            "learning_persisted": self.persisted,
            "learning_memory_id": self.memory_id,
            "learning_experience_id": self.experience.experience_id,
            "learning_evaluation_id": self.evaluation.evaluation_id,
            "learning_evaluation_state": self.evaluation.state.value,
            "claim_evaluation_state": self.claim_evaluation_state,
            "learning_persistence_error": self.persistence_error,
            "truth_established": False,
            "certainty_established": False,
            "authority_granted": False,
            "execution_requested": False,
        }


class CodingExecutionLearningService:
    """Observe one completed coding execution and durably record its evidence."""

    def __init__(
        self,
        repository: PersistentMemoryRepository | None = None,
        *,
        claim_evidence_adapter: CodingClaimEvidenceAdapter | None = None,
        outcome_evaluator: OutcomeEvaluator | None = None,
    ) -> None:
        self._repository = repository or PersistentMemoryRepository()
        if type(self._repository) is not PersistentMemoryRepository:
            raise TypeError("repository must be a PersistentMemoryRepository")
        self._claim_evidence_adapter = claim_evidence_adapter or CodingClaimEvidenceAdapter()
        self._outcome_evaluator = outcome_evaluator or OutcomeEvaluator()

    @property
    def repository(self) -> PersistentMemoryRepository:
        return self._repository

    def record(
        self,
        task: CodingAgentTask,
        plan: CodingAgentPlan,
        result: CodingAgentResult,
    ) -> CodingExecutionLearningRecord:
        """Record learning evidence after execution without performing another execution."""
        outcome = self._claim_evidence_adapter.evaluate(task, plan, result)
        execution_id = self._execution_id(outcome)
        experience = self._build_experience(task, result, outcome, execution_id)
        assessment = self._build_assessment(outcome)
        evaluation = self._outcome_evaluator.evaluate(
            experience,
            assessment,
            evaluation_id=f"{experience.experience_id}:evaluation",
            confidence=0.5,
            provenance={
                "source": "coding_execution_learning",
                "claim_id": outcome.claim.claim_id,
                "execution_id": execution_id,
            },
        )

        memory = self._build_memory_record(experience, evaluation, outcome)
        persistence_error: str | None = None
        persisted = False
        existing = self._repository.get(memory.memory_id)
        if existing is not None:
            self._validate_existing(existing, memory)
            persisted = False
        else:
            try:
                persisted = self._repository.persist(
                    memory,
                    ProvenanceChain(
                        refs=(
                            ProvenanceRef(
                                provenance_id=memory.provenance_ids[0],
                                source_kind=ProvenanceSourceKind.EXPERIENCE,
                                source_id=experience.experience_id,
                                summary="coding execution learning evidence",
                                observed_at=memory.created_at,
                                confidence=0.5,
                            ),
                        )
                    ),
                )
            except Exception as exc:  # persistence failure cannot retroactively change execution
                persistence_error = f"{type(exc).__name__}: {exc}"

        return CodingExecutionLearningRecord(
            execution_id=execution_id,
            experience=experience,
            evaluation=evaluation,
            claim_evaluation_state=outcome.evaluation.state.value,
            memory_id=memory.memory_id,
            persisted=persisted,
            persistence_error=persistence_error,
        )

    @staticmethod
    def _execution_id(outcome: CodingClaimEvidenceResult) -> str:
        payload = {
            "claim_id": outcome.claim.claim_id,
            "evidence_ids": outcome.evaluation.evidence_refs,
            "verification_refs": outcome.evaluation.verification_refs,
        }
        encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
        return f"coding-execution-{hashlib.sha256(encoded).hexdigest()[:24]}"

    @staticmethod
    def _experience_id(outcome: CodingClaimEvidenceResult) -> str:
        payload = {
            "claim_id": outcome.claim.claim_id,
            "evidence_ids": outcome.evaluation.evidence_refs,
        }
        encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
        return f"coding-experience-{hashlib.sha256(encoded).hexdigest()[:24]}"

    def _build_experience(
        self,
        task: CodingAgentTask,
        result: CodingAgentResult,
        outcome: CodingClaimEvidenceResult,
        execution_id: str,
    ) -> Experience:
        return Experience(
            experience_id=self._experience_id(outcome),
            source="coding_execution",
            objective_id=task.task_id,
            action_reference=execution_id,
            decision_reference=task.metadata.get("coding_operation_id"),
            observations=tuple(outcome.evaluation.evidence_refs),
            outcome=f"{result.status}: {result.message}",
            evaluation=outcome.evaluation.state.value,
            confidence=0.5,
            provenance={
                "task_id": task.task_id,
                "claim_id": outcome.claim.claim_id,
                "operation_id": task.metadata.get("coding_operation_id"),
                "verification_refs": outcome.evaluation.verification_refs,
                "authority_granted": False,
                "execution_repeated": False,
            },
        )

    @staticmethod
    def _build_assessment(outcome: CodingClaimEvidenceResult) -> OutcomeAssessment:
        evidence: list[LearningEvidence] = []
        for item in outcome.evidence:
            supports_success: bool | None = None
            if item.source_type.value == "CONTRADICTION":
                supports_success = False
            elif item.source_type.value in {"TEST_RESULT", "BUILD_RESULT"}:
                value = item.payload.get("passed")
                if isinstance(value, bool):
                    supports_success = value
            elif item.source_type.value == "FILESYSTEM_OBSERVATION":
                value = item.payload.get("success")
                if isinstance(value, bool):
                    supports_success = value
            evidence.append(
                LearningEvidence(
                    evidence_id=item.evidence_id,
                    signal=item.source_type.value,
                    supports_success=supports_success,
                    provenance=dict(item.provenance),
                )
            )
        return OutcomeAssessment(
            outcome=outcome.claim.payload.get("status", ""),
            evidence=tuple(evidence),
            complete=True,
        )

    @staticmethod
    def _build_memory_record(
        experience: Experience,
        evaluation: Evaluation,
        outcome: CodingClaimEvidenceResult,
    ) -> PersistentMemoryRecord:
        payload = {
            "experience": experience.to_dict(),
            "evaluation": evaluation.to_dict(),
            "claim_evaluation": {
                "state": outcome.evaluation.state.value,
                "evidence_refs": outcome.evaluation.evidence_refs,
                "verification_refs": outcome.evaluation.verification_refs,
            },
        }
        content = json.dumps(payload, sort_keys=True, default=str)
        encoded = content.encode("utf-8")
        memory_digest = hashlib.sha256(encoded).hexdigest()[:24]
        provenance_digest = hashlib.sha256(
            json.dumps(
                {"experience_id": experience.experience_id, "memory_digest": memory_digest},
                sort_keys=True,
                separators=(",", ":"),
            ).encode("utf-8")
        ).hexdigest()[:24]
        now = datetime.now(timezone.utc).isoformat()
        return PersistentMemoryRecord(
            memory_id=f"coding-learning-{memory_digest}",
            subject_id=experience.objective_id or experience.experience_id,
            kind=PersistentMemoryKind.EPISODIC,
            content=content,
            confidence=0.5,
            importance=0.5,
            status=MemoryLifecycle.CANDIDATE,
            created_at=now,
            updated_at=now,
            provenance_ids=(f"coding-experience-provenance-{provenance_digest}",),
            tags=("coding", "execution", "learning", "candidate"),
            metadata={
                "experience_id": experience.experience_id,
                "evaluation_id": evaluation.evaluation_id,
                "evaluation_state": evaluation.state.value,
                "claim_evaluation_state": outcome.evaluation.state.value,
            },
        )

    @staticmethod
    def _validate_existing(existing: PersistentMemoryRecord, incoming: PersistentMemoryRecord) -> None:
        if existing.content != incoming.content:
            raise ValueError(f"learning memory id conflict: {incoming.memory_id}")
        if existing.provenance_ids != incoming.provenance_ids:
            raise ValueError(f"learning memory provenance conflict: {incoming.memory_id}")
        if existing.kind is not PersistentMemoryKind.EPISODIC:
            raise ValueError(f"learning memory kind conflict: {incoming.memory_id}")
        if existing.status is not MemoryLifecycle.CANDIDATE:
            raise ValueError(f"learning memory lifecycle conflict: {incoming.memory_id}")


__all__ = ["CodingExecutionLearningRecord", "CodingExecutionLearningService"]
