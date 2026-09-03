"""M10.4 memory consolidation and deterministic retrieval boundary.

This module turns evaluated experience into bounded, inspectable memory
candidates and provides deterministic retrieval over those candidates.
It does not mutate the existing memory database, grant authority, authorize
work, or treat relevance as truth.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from enum import Enum
from types import MappingProxyType
from typing import Any, Mapping

from src.learning.adaptation import AdaptationRecord, AdaptationState
from src.learning.evaluation import Evaluation, EvaluationState
from src.learning.experience import Experience


class ConsolidationState(str, Enum):
    PROPOSED = "PROPOSED"
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"
    REVERSED = "REVERSED"


class ConsolidationConflictError(ValueError):
    """Raised when consolidated-memory identity conflicts with stored state."""


@dataclass(frozen=True)
class MemoryCandidate:
    """Immutable candidate for durable knowledge derived from evaluated experience."""

    candidate_id: str
    experience_id: str
    evaluation_id: str
    content: str
    source_kind: str
    confidence: float | None = None
    provenance: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        for name in (
            "candidate_id",
            "experience_id",
            "evaluation_id",
            "content",
            "source_kind",
        ):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string")
        if self.confidence is not None:
            if isinstance(self.confidence, bool) or not isinstance(self.confidence, (int, float)):
                raise TypeError("confidence must be a number or None")
            if not 0.0 <= float(self.confidence) <= 1.0:
                raise ValueError("confidence must be between 0.0 and 1.0")
        if not isinstance(self.provenance, Mapping):
            raise TypeError("provenance must be a mapping")
        object.__setattr__(self, "provenance", MappingProxyType(dict(self.provenance)))

    def to_dict(self) -> dict[str, Any]:
        return {
            "candidate_id": self.candidate_id,
            "experience_id": self.experience_id,
            "evaluation_id": self.evaluation_id,
            "content": self.content,
            "source_kind": self.source_kind,
            "confidence": self.confidence,
            "provenance": dict(self.provenance),
            "truth_guaranteed": False,
            "authority_granted": False,
            "authorization_granted": False,
            "execution_requested": False,
        }


@dataclass(frozen=True)
class ConsolidatedMemory:
    """Immutable durable-knowledge representation with explicit provenance."""

    memory_id: str
    candidate: MemoryCandidate
    state: ConsolidationState
    acceptance_reference: str | None = None
    reversal_reference: str | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.memory_id, str) or not self.memory_id.strip():
            raise ValueError("memory_id must be a non-empty string")
        if not isinstance(self.candidate, MemoryCandidate):
            raise TypeError("candidate must be a MemoryCandidate")
        if not isinstance(self.state, ConsolidationState):
            try:
                object.__setattr__(self, "state", ConsolidationState(self.state))
            except (TypeError, ValueError) as exc:
                raise TypeError("state must be a ConsolidationState") from exc
        if self.state == ConsolidationState.ACCEPTED:
            if not isinstance(self.acceptance_reference, str) or not self.acceptance_reference.strip():
                raise ValueError("accepted memories require an acceptance reference")
        if self.state == ConsolidationState.REVERSED:
            if not isinstance(self.reversal_reference, str) or not self.reversal_reference.strip():
                raise ValueError("reversed memories require a reversal reference")

    def to_dict(self) -> dict[str, Any]:
        return {
            "memory_id": self.memory_id,
            "candidate": self.candidate.to_dict(),
            "state": self.state.value,
            "acceptance_reference": self.acceptance_reference,
            "reversal_reference": self.reversal_reference,
            "truth_guaranteed": False,
            "authority_granted": False,
            "authorization_granted": False,
            "execution_requested": False,
            "policy_mutation": False,
        }


class MemoryConsolidator:
    """Create memory candidates from evaluated experiences without mutating storage."""

    def propose(
        self,
        experience: Experience,
        evaluation: Evaluation,
        *,
        content: str | None = None,
        confidence: float | None = None,
        provenance: Mapping[str, Any] | None = None,
        adaptation: AdaptationRecord | None = None,
    ) -> MemoryCandidate:
        if not isinstance(experience, Experience):
            raise TypeError("experience must be an Experience")
        if not isinstance(evaluation, Evaluation):
            raise TypeError("evaluation must be an Evaluation")
        if evaluation.experience_id != experience.experience_id:
            raise ValueError("evaluation must reference the supplied experience")
        if evaluation.state in {EvaluationState.INCOMPLETE, EvaluationState.INCONCLUSIVE}:
            raise ValueError("incomplete or inconclusive evaluations cannot be consolidated")
        if adaptation is not None:
            if not isinstance(adaptation, AdaptationRecord):
                raise TypeError("adaptation must be an AdaptationRecord")
            if adaptation.state != AdaptationState.ACCEPTED:
                raise ValueError("only accepted adaptations may be included as consolidation evidence")

        selected_content = content.strip() if isinstance(content, str) else ""
        if not selected_content:
            selected_content = experience.outcome.strip()
        if not selected_content:
            raise ValueError("consolidated memory content must be non-empty")

        source_kind = "EVALUATED_EXPERIENCE"
        if adaptation is not None:
            source_kind = "EVALUATED_EXPERIENCE_AND_ACCEPTED_ADAPTATION"

        inherited_confidence = confidence
        if inherited_confidence is None:
            inherited_confidence = evaluation.confidence
        if inherited_confidence is None:
            inherited_confidence = experience.confidence

        merged_provenance = {
            "source": "m10.4",
            "experience_id": experience.experience_id,
            "evaluation_id": evaluation.evaluation_id,
            "evaluation_state": evaluation.state.value,
        }
        if adaptation is not None:
            merged_provenance["adaptation_record_id"] = adaptation.record_id
        if provenance:
            merged_provenance.update(dict(provenance))

        return MemoryCandidate(
            candidate_id=f"{experience.experience_id}:{evaluation.evaluation_id}:memory",
            experience_id=experience.experience_id,
            evaluation_id=evaluation.evaluation_id,
            content=selected_content,
            source_kind=source_kind,
            confidence=inherited_confidence,
            provenance=merged_provenance,
        )

    def accept(self, candidate: MemoryCandidate, acceptance_reference: str) -> ConsolidatedMemory:
        if not isinstance(candidate, MemoryCandidate):
            raise TypeError("candidate must be a MemoryCandidate")
        if not isinstance(acceptance_reference, str) or not acceptance_reference.strip():
            raise ValueError("acceptance_reference must be a non-empty string")
        return ConsolidatedMemory(
            memory_id=candidate.candidate_id,
            candidate=candidate,
            state=ConsolidationState.ACCEPTED,
            acceptance_reference=acceptance_reference.strip(),
        )

    def reject(self, candidate: MemoryCandidate, rejection_reference: str) -> ConsolidatedMemory:
        if not isinstance(candidate, MemoryCandidate):
            raise TypeError("candidate must be a MemoryCandidate")
        if not isinstance(rejection_reference, str) or not rejection_reference.strip():
            raise ValueError("rejection_reference must be a non-empty string")
        return ConsolidatedMemory(
            memory_id=candidate.candidate_id,
            candidate=candidate,
            state=ConsolidationState.REJECTED,
            acceptance_reference=None,
        )

    def reverse(self, memory: ConsolidatedMemory, reversal_reference: str) -> ConsolidatedMemory:
        if not isinstance(memory, ConsolidatedMemory):
            raise TypeError("memory must be a ConsolidatedMemory")
        if memory.state != ConsolidationState.ACCEPTED:
            raise ValueError("only accepted memories can be reversed")
        if not isinstance(reversal_reference, str) or not reversal_reference.strip():
            raise ValueError("reversal_reference must be a non-empty string")
        return ConsolidatedMemory(
            memory_id=f"{memory.memory_id}:reversed",
            candidate=memory.candidate,
            state=ConsolidationState.REVERSED,
            acceptance_reference=memory.acceptance_reference,
            reversal_reference=reversal_reference.strip(),
        )


@dataclass(frozen=True)
class MemoryStore:
    """Immutable candidate-backed durable-memory view."""

    memories: tuple[ConsolidatedMemory, ...] = ()

    def __post_init__(self) -> None:
        if not isinstance(self.memories, tuple):
            raise TypeError("memories must be a tuple")
        seen: set[str] = set()
        for memory in self.memories:
            if not isinstance(memory, ConsolidatedMemory):
                raise TypeError("memories must contain ConsolidatedMemory values")
            if memory.memory_id in seen:
                raise ConsolidationConflictError(f"memory '{memory.memory_id}' is already stored")
            seen.add(memory.memory_id)

    def append(self, memory: ConsolidatedMemory) -> "MemoryStore":
        if not isinstance(memory, ConsolidatedMemory):
            raise TypeError("memory must be a ConsolidatedMemory")
        if any(item.memory_id == memory.memory_id for item in self.memories):
            raise ConsolidationConflictError(f"memory '{memory.memory_id}' is already stored")
        return MemoryStore(self.memories + (memory,))

    def list(self) -> tuple[ConsolidatedMemory, ...]:
        return self.memories


@dataclass(frozen=True)
class RetrievalResult:
    """One deterministic retrieval result with an inspectable relevance score."""

    memory_id: str
    score: float
    content: str
    provenance: Mapping[str, Any]

    def __post_init__(self) -> None:
        if not isinstance(self.memory_id, str) or not self.memory_id.strip():
            raise ValueError("memory_id must be a non-empty string")
        if isinstance(self.score, bool) or not isinstance(self.score, (int, float)):
            raise TypeError("score must be a number")
        if self.score < 0.0:
            raise ValueError("score must be non-negative")
        if not isinstance(self.content, str) or not self.content.strip():
            raise ValueError("content must be a non-empty string")
        if not isinstance(self.provenance, Mapping):
            raise TypeError("provenance must be a mapping")
        object.__setattr__(self, "provenance", MappingProxyType(dict(self.provenance)))

    def to_dict(self) -> dict[str, Any]:
        return {
            "memory_id": self.memory_id,
            "score": self.score,
            "content": self.content,
            "provenance": dict(self.provenance),
            "truth_guaranteed": False,
            "authority_granted": False,
            "authorization_granted": False,
            "execution_requested": False,
        }


class MemoryRetriever:
    """Deterministic lexical retrieval over accepted consolidated memories."""

    _TOKEN_RE = re.compile(r"[a-z0-9_]+")

    def retrieve(self, store: MemoryStore, query: str, *, limit: int = 5) -> tuple[RetrievalResult, ...]:
        if not isinstance(store, MemoryStore):
            raise TypeError("store must be a MemoryStore")
        if not isinstance(query, str) or not query.strip():
            raise ValueError("query must be a non-empty string")
        if not isinstance(limit, int) or isinstance(limit, bool) or limit <= 0:
            raise ValueError("limit must be a positive integer")

        query_tokens = set(self._TOKEN_RE.findall(query.lower()))
        results: list[RetrievalResult] = []
        for memory in store.memories:
            if memory.state != ConsolidationState.ACCEPTED:
                continue
            content_tokens = self._TOKEN_RE.findall(memory.candidate.content.lower())
            if not content_tokens:
                continue
            overlap = len(query_tokens.intersection(content_tokens))
            if overlap == 0:
                continue
            score = overlap / len(query_tokens)
            if memory.candidate.confidence is not None:
                score *= 0.5 + (0.5 * float(memory.candidate.confidence))
            results.append(
                RetrievalResult(
                    memory_id=memory.memory_id,
                    score=score,
                    content=memory.candidate.content,
                    provenance=memory.candidate.provenance,
                )
            )

        results.sort(key=lambda item: (-item.score, item.memory_id))
        return tuple(results[:limit])

    def to_json(self, results: tuple[RetrievalResult, ...]) -> str:
        return json.dumps(
            {"results": [item.to_dict() for item in results]},
            sort_keys=True,
            default=str,
        )
