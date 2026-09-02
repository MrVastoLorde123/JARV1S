"""Semantic boundary between WorkingContext and downstream reasoning.

M7.1 deliberately does not invoke a model, perform reasoning, authorize an
action, or execute anything. It classifies existing WorkingContext information
so a reasoning system can distinguish observation, evidence, persisted claims,
and current state without treating every input as equally authoritative.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Mapping

from src.context.models import (
    EVIDENCE,
    HISTORY,
    MEMORY,
    OBSERVATION,
    STATE,
    ContextItem,
)
from src.context.working_context import WorkingContext


class EpistemicRole(str, Enum):
    """Semantic role of information at the reasoning boundary."""

    OBSERVED = "observed"
    EVIDENCE = "evidence"
    PERSISTED_CLAIM = "persisted_claim"
    CURRENT_STATE = "current_state"
    DERIVED = "derived"
    PROPOSED = "proposed"


class Freshness(str, Enum):
    """Explicit freshness state carried into reasoning."""

    FRESH = "fresh"
    STALE = "stale"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class ReasoningInput:
    """One semantically classified input available to a reasoning system."""

    content: Any
    source_type: str
    provenance: Mapping[str, Any] = field(default_factory=dict)
    relevance_score: float | None = None
    confidence: float | None = None
    importance: float | None = None
    freshness: Freshness = Freshness.UNKNOWN
    epistemic_role: EpistemicRole = EpistemicRole.PERSISTED_CLAIM

    def __post_init__(self):
        if not isinstance(self.source_type, str) or not self.source_type.strip():
            raise ValueError("source_type must be a non-empty string.")
        if not isinstance(self.provenance, Mapping):
            raise TypeError("provenance must be a mapping.")
        if self.relevance_score is not None and not 0.0 <= self.relevance_score <= 1.0:
            raise ValueError("relevance_score must be between 0.0 and 1.0.")
        if self.confidence is not None and not 0.0 <= self.confidence <= 1.0:
            raise ValueError("confidence must be between 0.0 and 1.0.")
        if self.importance is not None and not 0.0 <= self.importance <= 1.0:
            raise ValueError("importance must be between 0.0 and 1.0.")
        if not isinstance(self.freshness, Freshness):
            raise TypeError("freshness must be a Freshness value.")
        if not isinstance(self.epistemic_role, EpistemicRole):
            raise TypeError("epistemic_role must be an EpistemicRole value.")

        if self.epistemic_role in {EpistemicRole.DERIVED, EpistemicRole.PROPOSED}:
            raise ValueError(
                "DERIVED and PROPOSED are reasoning-output roles and cannot be "
                "used as reasoning inputs."
            )


@dataclass(frozen=True)
class ReasoningContext:
    """Provider-neutral semantic projection of one WorkingContext."""

    request: str
    inputs: tuple[ReasoningInput, ...]
    current_state: Mapping[str, Any] | None = None
    observations: tuple[ReasoningInput, ...] = ()
    constraints: tuple[str, ...] = ()
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if not isinstance(self.request, str) or not self.request.strip():
            raise ValueError("request must be a non-empty string.")
        if not isinstance(self.inputs, tuple):
            raise TypeError("inputs must be a tuple.")
        if any(not isinstance(item, ReasoningInput) for item in self.inputs):
            raise TypeError("inputs must contain ReasoningInput values.")
        if not isinstance(self.observations, tuple):
            raise TypeError("observations must be a tuple.")
        if any(not isinstance(item, ReasoningInput) for item in self.observations):
            raise TypeError("observations must contain ReasoningInput values.")
        if not isinstance(self.constraints, tuple):
            raise TypeError("constraints must be a tuple.")
        if any(not isinstance(item, str) or not item.strip() for item in self.constraints):
            raise ValueError("constraints must contain non-empty strings.")
        if self.current_state is not None and not isinstance(self.current_state, Mapping):
            raise TypeError("current_state must be a mapping or None.")
        if not isinstance(self.metadata, Mapping):
            raise TypeError("metadata must be a mapping.")

        observation_ids = {id(item) for item in self.observations}
        if any(item.epistemic_role is not EpistemicRole.OBSERVED for item in self.observations):
            raise ValueError("observations must contain only OBSERVED reasoning inputs.")
        if any(id(item) in observation_ids for item in self.inputs):
            raise ValueError("observations must not be duplicated in inputs.")

    def to_context(self) -> dict[str, Any]:
        """Return a provider-neutral representation for a reasoning provider."""
        return {
            "request": self.request,
            "inputs": tuple(_input_to_context(item) for item in self.inputs),
            "current_state": None if self.current_state is None else dict(self.current_state),
            "observations": tuple(_input_to_context(item) for item in self.observations),
            "constraints": self.constraints,
            "metadata": dict(self.metadata),
        }


class ReasoningContextProjector:
    """Project canonical WorkingContext data into reasoning semantics."""

    _ROLE_BY_SOURCE_TYPE = {
        MEMORY: EpistemicRole.PERSISTED_CLAIM,
        HISTORY: EpistemicRole.PERSISTED_CLAIM,
        EVIDENCE: EpistemicRole.EVIDENCE,
        STATE: EpistemicRole.CURRENT_STATE,
        OBSERVATION: EpistemicRole.OBSERVED,
    }

    def project(self, working_context: WorkingContext) -> ReasoningContext:
        """Build reasoning inputs without retrieving, mutating, or validating truth."""
        if not isinstance(working_context, WorkingContext):
            raise TypeError("working_context must be a WorkingContext.")

        source_decisions = {
            decision.source_id: decision
            for decision in (
                ()
                if working_context.source_selection is None
                else working_context.source_selection.selected
            )
        }

        inputs = []
        for item in working_context.context_package.items:
            if item.source_type == OBSERVATION:
                continue
            inputs.append(
                self._from_item(
                    item,
                    source_decisions=source_decisions,
                )
            )

        observations = tuple(
            self._from_observation(item)
            for item in working_context.observations
        )

        current_state = None
        if working_context.conversation_state is not None:
            current_state = {
                "conversation_id": working_context.conversation_state.conversation_id,
                "active_topic": working_context.conversation_state.active_topic,
                "active_task": working_context.conversation_state.active_task,
                "turn_count": len(working_context.conversation_state.turns),
            }

        constraints = tuple(working_context.context_package.instructions)
        metadata = {
            **working_context.context_package.metadata,
            **working_context.metadata,
            "reasoning_semantics": "m7.1",
        }

        return ReasoningContext(
            request=working_context.request,
            inputs=tuple(inputs),
            current_state=current_state,
            observations=observations,
            constraints=constraints,
            metadata=metadata,
        )

    def _from_item(
        self,
        item: ContextItem,
        *,
        source_decisions: Mapping[str, Any],
    ) -> ReasoningInput:
        role = self._ROLE_BY_SOURCE_TYPE.get(
            item.source_type,
            EpistemicRole.PERSISTED_CLAIM,
        )
        freshness = self._freshness_for_item(item, source_decisions=source_decisions)
        return ReasoningInput(
            content=item.content,
            source_type=item.source_type,
            provenance=dict(item.provenance),
            relevance_score=item.relevance_score,
            confidence=item.confidence,
            importance=item.importance,
            freshness=freshness,
            epistemic_role=role,
        )

    @staticmethod
    def _from_observation(item: ContextItem) -> ReasoningInput:
        return ReasoningInput(
            content=item.content,
            source_type=item.source_type,
            provenance=dict(item.provenance),
            relevance_score=item.relevance_score,
            confidence=item.confidence,
            importance=item.importance,
            freshness=Freshness.FRESH,
            epistemic_role=EpistemicRole.OBSERVED,
        )

    @staticmethod
    def _freshness_for_item(
        item: ContextItem,
        *,
        source_decisions: Mapping[str, Any],
    ) -> Freshness:
        source_id = item.provenance.get("source_id")
        if source_id is not None:
            decision = source_decisions.get(str(source_id))
            if decision is not None and decision.refresh_required:
                return Freshness.STALE

        raw_freshness = item.provenance.get("freshness")
        if raw_freshness in {value.value for value in Freshness}:
            return Freshness(raw_freshness)
        return Freshness.UNKNOWN


def _input_to_context(item: ReasoningInput) -> dict[str, Any]:
    return {
        "content": item.content,
        "source_type": item.source_type,
        "provenance": dict(item.provenance),
        "relevance_score": item.relevance_score,
        "confidence": item.confidence,
        "importance": item.importance,
        "freshness": item.freshness.value,
        "epistemic_role": item.epistemic_role.value,
    }
