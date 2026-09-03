"""M10.7 bounded intelligence integration boundary."""

from __future__ import annotations

from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any, Mapping

from src.learning.adaptation import AdaptationRecord, AdaptationState
from src.learning.consolidation import ConsolidatedMemory, ConsolidationState, MemoryStore, RetrievalResult
from src.learning.evaluation import Evaluation
from src.learning.reasoning_quality import FeedbackSignal, ReasoningFeedback
from src.learning.reliability import ReliabilityRecord, ReliabilityState


@dataclass(frozen=True)
class IntelligenceContext:
    """Immutable bounded context assembled from verified learning boundaries."""

    query: str
    memories: tuple[RetrievalResult, ...] = ()
    feedback: tuple[ReasoningFeedback, ...] = ()
    adaptations: tuple[AdaptationRecord, ...] = ()
    reliability: tuple[ReliabilityRecord, ...] = ()
    evaluations: tuple[Evaluation, ...] = ()
    provenance: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.query, str) or not self.query.strip():
            raise ValueError("query must be a non-empty string")
        for name, values, expected in (
            ("memories", self.memories, RetrievalResult),
            ("feedback", self.feedback, ReasoningFeedback),
            ("adaptations", self.adaptations, AdaptationRecord),
            ("reliability", self.reliability, ReliabilityRecord),
            ("evaluations", self.evaluations, Evaluation),
        ):
            if not isinstance(values, tuple):
                raise TypeError(f"{name} must be a tuple")
            if any(not isinstance(value, expected) for value in values):
                raise TypeError(f"{name} contains an invalid value")
        if not isinstance(self.provenance, Mapping):
            raise TypeError("provenance must be a mapping")
        object.__setattr__(self, "provenance", MappingProxyType(dict(self.provenance)))

    @property
    def active_reliability(self) -> tuple[ReliabilityRecord, ...]:
        return tuple(
            item for item in self.reliability
            if item.state not in {ReliabilityState.REVERSED, ReliabilityState.SUPERSEDED}
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "query": self.query,
            "memories": [item.to_dict() for item in self.memories],
            "feedback": [item.to_dict() for item in self.feedback],
            "adaptations": [item.to_dict() for item in self.adaptations],
            "reliability": [item.to_dict() for item in self.reliability],
            "evaluations": [item.to_dict() for item in self.evaluations],
            "provenance": dict(self.provenance),
            "truth_guaranteed": False,
            "authority_granted": False,
            "authorization_granted": False,
            "execution_requested": False,
            "policy_mutation": False,
        }


class IntelligenceIntegrator:
    """Assemble bounded learning signals into reasoning context."""

    def build_context(
        self,
        query: str,
        *,
        memory_results: tuple[RetrievalResult, ...] = (),
        feedback: tuple[ReasoningFeedback, ...] = (),
        adaptations: tuple[AdaptationRecord, ...] = (),
        reliability: tuple[ReliabilityRecord, ...] = (),
        evaluations: tuple[Evaluation, ...] = (),
        provenance: Mapping[str, Any] | None = None,
    ) -> IntelligenceContext:
        if not isinstance(query, str) or not query.strip():
            raise ValueError("query must be a non-empty string")
        if not isinstance(memory_results, tuple):
            raise TypeError("memory_results must be a tuple")
        filtered_memories = tuple(item for item in memory_results if item.score > 0.0)
        filtered_adaptations = tuple(
            item for item in adaptations if item.state == AdaptationState.ACCEPTED
        )
        filtered_reliability = tuple(
            item for item in reliability
            if item.state not in {ReliabilityState.REVERSED, ReliabilityState.SUPERSEDED}
        )
        merged_provenance = {
            "source": "m10.7",
            "memory_count": len(filtered_memories),
            "feedback_count": len(feedback),
            "accepted_adaptation_count": len(filtered_adaptations),
            "active_reliability_count": len(filtered_reliability),
            "evaluation_count": len(evaluations),
        }
        if provenance:
            merged_provenance.update(dict(provenance))
        return IntelligenceContext(
            query=query.strip(),
            memories=filtered_memories,
            feedback=feedback,
            adaptations=filtered_adaptations,
            reliability=filtered_reliability,
            evaluations=evaluations,
            provenance=merged_provenance,
        )

    @staticmethod
    def exclude_unreliable_memory(
        memories: tuple[RetrievalResult, ...],
        reliability: tuple[ReliabilityRecord, ...],
    ) -> tuple[RetrievalResult, ...]:
        blocked_ids = {
            record.artifact_id
            for record in reliability
            if record.state in {ReliabilityState.REVERSED, ReliabilityState.SUPERSEDED}
        }
        return tuple(result for result in memories if result.memory_id not in blocked_ids)
