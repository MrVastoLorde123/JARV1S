"""Semantic contract for interpretations derived from a ReasoningContext.

M7.2 defines what a reasoning system is allowed to conclude without turning
those conclusions into authoritative facts. Interpretations remain derived,
retain explicit support references, and expose uncertainty, conflict, and
missing information as first-class outputs.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Mapping

from src.context.reasoning_semantics import EpistemicRole, ReasoningContext


class InterpretationStatus(str, Enum):
    SUPPORTED = "supported"
    UNCERTAIN = "uncertain"
    CONFLICTED = "conflicted"
    INCOMPLETE = "incomplete"


@dataclass(frozen=True)
class SupportReference:
    """Reference to one input in a ReasoningContext."""

    input_index: int
    relationship: str = "supports"

    def __post_init__(self):
        if not isinstance(self.input_index, int) or isinstance(self.input_index, bool):
            raise TypeError("input_index must be an integer.")
        if self.input_index < 0:
            raise ValueError("input_index cannot be negative.")
        if not isinstance(self.relationship, str) or not self.relationship.strip():
            raise ValueError("relationship must be a non-empty string.")


@dataclass(frozen=True)
class DerivedClaim:
    """A non-authoritative conclusion derived from one or more inputs."""

    claim: str
    support: tuple[SupportReference, ...]
    confidence: float | None = None
    status: InterpretationStatus = InterpretationStatus.SUPPORTED
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if not isinstance(self.claim, str) or not self.claim.strip():
            raise ValueError("claim must be a non-empty string.")
        if not isinstance(self.support, tuple):
            raise TypeError("support must be a tuple.")
        if any(not isinstance(item, SupportReference) for item in self.support):
            raise TypeError("support must contain SupportReference values.")
        if self.confidence is not None and not 0.0 <= self.confidence <= 1.0:
            raise ValueError("confidence must be between 0.0 and 1.0.")
        if not isinstance(self.status, InterpretationStatus):
            raise TypeError("status must be an InterpretationStatus value.")


@dataclass(frozen=True)
class Uncertainty:
    """A reason the reasoning system should avoid treating a conclusion as settled."""

    description: str
    support: tuple[SupportReference, ...] = ()
    severity: float | None = None

    def __post_init__(self):
        if not isinstance(self.description, str) or not self.description.strip():
            raise ValueError("description must be a non-empty string.")
        if not isinstance(self.support, tuple):
            raise TypeError("support must be a tuple.")
        if any(not isinstance(item, SupportReference) for item in self.support):
            raise TypeError("support must contain SupportReference values.")
        if self.severity is not None and not 0.0 <= self.severity <= 1.0:
            raise ValueError("severity must be between 0.0 and 1.0.")


@dataclass(frozen=True)
class InterpretationConflict:
    """Explicit representation of incompatible or tensioning inputs."""

    description: str
    support: tuple[SupportReference, ...]

    def __post_init__(self):
        if not isinstance(self.description, str) or not self.description.strip():
            raise ValueError("description must be a non-empty string.")
        if not isinstance(self.support, tuple) or not self.support:
            raise ValueError("conflict support must be a non-empty tuple.")
        if any(not isinstance(item, SupportReference) for item in self.support):
            raise TypeError("support must contain SupportReference values.")


@dataclass(frozen=True)
class MissingInformation:
    """Information explicitly identified as necessary but unavailable."""

    description: str
    importance: float | None = None

    def __post_init__(self):
        if not isinstance(self.description, str) or not self.description.strip():
            raise ValueError("description must be a non-empty string.")
        if self.importance is not None and not 0.0 <= self.importance <= 1.0:
            raise ValueError("importance must be between 0.0 and 1.0.")


@dataclass(frozen=True)
class Interpretation:
    """Complete non-authoritative interpretation result for one request."""

    request: str
    claims: tuple[DerivedClaim, ...] = ()
    uncertainties: tuple[Uncertainty, ...] = ()
    conflicts: tuple[InterpretationConflict, ...] = ()
    missing_information: tuple[MissingInformation, ...] = ()
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if not isinstance(self.request, str) or not self.request.strip():
            raise ValueError("request must be a non-empty string.")
        if not isinstance(self.claims, tuple):
            raise TypeError("claims must be a tuple.")
        if any(not isinstance(item, DerivedClaim) for item in self.claims):
            raise TypeError("claims must contain DerivedClaim values.")
        if not isinstance(self.uncertainties, tuple):
            raise TypeError("uncertainties must be a tuple.")
        if any(not isinstance(item, Uncertainty) for item in self.uncertainties):
            raise TypeError("uncertainties must contain Uncertainty values.")
        if not isinstance(self.conflicts, tuple):
            raise TypeError("conflicts must be a tuple.")
        if any(not isinstance(item, InterpretationConflict) for item in self.conflicts):
            raise TypeError("conflicts must contain InterpretationConflict values.")
        if not isinstance(self.missing_information, tuple):
            raise TypeError("missing_information must be a tuple.")
        if any(not isinstance(item, MissingInformation) for item in self.missing_information):
            raise TypeError("missing_information must contain MissingInformation values.")
        if not isinstance(self.metadata, Mapping):
            raise TypeError("metadata must be a mapping.")

    def to_context(self) -> dict[str, Any]:
        return {
            "request": self.request,
            "claims": tuple(
                {
                    "claim": claim.claim,
                    "support": tuple(
                        {"input_index": ref.input_index, "relationship": ref.relationship}
                        for ref in claim.support
                    ),
                    "confidence": claim.confidence,
                    "status": claim.status.value,
                    "metadata": dict(claim.metadata),
                    "epistemic_role": EpistemicRole.DERIVED.value,
                }
                for claim in self.claims
            ),
            "uncertainties": tuple(
                {
                    "description": uncertainty.description,
                    "support": tuple(
                        {"input_index": ref.input_index, "relationship": ref.relationship}
                        for ref in uncertainty.support
                    ),
                    "severity": uncertainty.severity,
                }
                for uncertainty in self.uncertainties
            ),
            "conflicts": tuple(
                {
                    "description": conflict.description,
                    "support": tuple(
                        {"input_index": ref.input_index, "relationship": ref.relationship}
                        for ref in conflict.support
                    ),
                }
                for conflict in self.conflicts
            ),
            "missing_information": tuple(
                {
                    "description": item.description,
                    "importance": item.importance,
                }
                for item in self.missing_information
            ),
            "metadata": dict(self.metadata),
        }


class InterpretationValidator:
    """Validate interpretation structure and support references deterministically."""

    def validate(self, reasoning_context: ReasoningContext, interpretation: Interpretation) -> None:
        if not isinstance(reasoning_context, ReasoningContext):
            raise TypeError("reasoning_context must be a ReasoningContext.")
        if not isinstance(interpretation, Interpretation):
            raise TypeError("interpretation must be an Interpretation.")
        if interpretation.request != reasoning_context.request:
            raise ValueError("interpretation request must match reasoning context request.")

        input_count = len(reasoning_context.inputs) + len(reasoning_context.observations)
        references = self._references(interpretation)
        for reference in references:
            if reference.input_index >= input_count:
                raise ValueError("interpretation support reference points outside the reasoning context.")

        for claim in interpretation.claims:
            if claim.status is InterpretationStatus.SUPPORTED and not claim.support:
                raise ValueError("supported derived claims require at least one support reference.")
            if claim.status is InterpretationStatus.CONFLICTED and not claim.support:
                raise ValueError("conflicted derived claims require support references.")

    @staticmethod
    def _references(interpretation: Interpretation) -> tuple[SupportReference, ...]:
        references = []
        for claim in interpretation.claims:
            references.extend(claim.support)
        for uncertainty in interpretation.uncertainties:
            references.extend(uncertainty.support)
        for conflict in interpretation.conflicts:
            references.extend(conflict.support)
        return tuple(references)
