"""M14.6 context relevance and prioritization boundary."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any

from .cross_domain import DomainReference


class ContextRelevanceValidationError(ValueError):
    """Raised when context relevance violates the M14.6 boundary."""


MAX_ITEMS = 256
MAX_REASON_LENGTH = 512
MAX_REASONS = 16
MAX_DOMAIN_LENGTH = 256


def _text(value: str, field_name: str, maximum: int) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ContextRelevanceValidationError(f"{field_name} must be a non-empty string")
    if len(value) > maximum:
        raise ContextRelevanceValidationError(f"{field_name} exceeds maximum length of {maximum}")
    return value


@dataclass(frozen=True)
class ContextRelevance:
    """Immutable bounded relevance judgment for one known context reference."""

    reference: DomainReference
    score: float
    reasons: tuple[str, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        if not isinstance(self.reference, DomainReference):
            raise ContextRelevanceValidationError("reference must be a DomainReference")
        if not isinstance(self.score, (int, float)) or isinstance(self.score, bool):
            raise ContextRelevanceValidationError("score must be a number")
        score = float(self.score)
        if score != score or score in (float("inf"), float("-inf")):
            raise ContextRelevanceValidationError("score must be finite")
        if not 0.0 <= score <= 1.0:
            raise ContextRelevanceValidationError("score must be between 0.0 and 1.0")
        object.__setattr__(self, "score", score)
        if not isinstance(self.reasons, tuple):
            raise ContextRelevanceValidationError("reasons must be a tuple")
        if len(self.reasons) > MAX_REASONS:
            raise ContextRelevanceValidationError(f"reasons exceeds maximum count of {MAX_REASONS}")
        if len(set(self.reasons)) != len(self.reasons):
            raise ContextRelevanceValidationError("reasons must be unique")
        for index, reason in enumerate(self.reasons):
            _text(reason, f"reasons[{index}]", MAX_REASON_LENGTH)

    @property
    def reference_key(self) -> tuple[str, str]:
        return (self.reference.domain.casefold(), self.reference.reference_id)

    def to_dict(self) -> dict[str, Any]:
        return {
            "reference": self.reference.to_dict(),
            "score": self.score,
            "reasons": list(self.reasons),
            "truth_guaranteed": False,
            "fact_guaranteed": False,
            "intent_guaranteed": False,
            "importance_guaranteed": False,
            "authorization_granted": False,
            "policy_authority": False,
            "execution_requested": False,
        }


@dataclass(frozen=True)
class ContextRelevanceRanking:
    """Immutable deterministic ranking of context by explicit relevance."""

    items: tuple[ContextRelevance, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        if not isinstance(self.items, tuple):
            raise ContextRelevanceValidationError("items must be a tuple")
        if len(self.items) > MAX_ITEMS:
            raise ContextRelevanceValidationError(f"items exceeds maximum count of {MAX_ITEMS}")
        if any(not isinstance(item, ContextRelevance) for item in self.items):
            raise ContextRelevanceValidationError("items must contain ContextRelevance values")
        keys = tuple(item.reference_key for item in self.items)
        if len(set(keys)) != len(keys):
            raise ContextRelevanceValidationError("reference keys must be unique")
        expected = tuple(sorted(self.items, key=_sort_key))
        if self.items != expected:
            raise ContextRelevanceValidationError(
                "items must be ordered by descending score with deterministic tie-breaking"
            )

    @property
    def top(self) -> ContextRelevance | None:
        return self.items[0] if self.items else None

    def for_domain(self, domain: str) -> tuple[ContextRelevance, ...]:
        _text(domain, "domain", MAX_DOMAIN_LENGTH)
        normalized = domain.casefold()
        return tuple(item for item in self.items if item.reference.domain.casefold() == normalized)

    def above(self, minimum_score: float) -> tuple[ContextRelevance, ...]:
        if not isinstance(minimum_score, (int, float)) or isinstance(minimum_score, bool):
            raise ContextRelevanceValidationError("minimum_score must be a number")
        threshold = float(minimum_score)
        if threshold != threshold or threshold in (float("inf"), float("-inf")):
            raise ContextRelevanceValidationError("minimum_score must be finite")
        if not 0.0 <= threshold <= 1.0:
            raise ContextRelevanceValidationError("minimum_score must be between 0.0 and 1.0")
        return tuple(item for item in self.items if item.score >= threshold)

    def to_dict(self) -> dict[str, Any]:
        return {
            "items": [item.to_dict() for item in self.items],
            "truth_guaranteed": False,
            "fact_guaranteed": False,
            "intent_guaranteed": False,
            "importance_guaranteed": False,
            "authorization_granted": False,
            "policy_authority": False,
            "execution_requested": False,
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), sort_keys=True, default=str)


def _sort_key(item: ContextRelevance) -> tuple[float, str, str]:
    return (-item.score, item.reference.domain.casefold(), item.reference.reference_id)


def rank_relevance(items: tuple[ContextRelevance, ...] | list[ContextRelevance]) -> ContextRelevanceRanking:
    """Return deterministic ordering without changing or inferring judgments."""
    if not isinstance(items, (tuple, list)):
        raise TypeError("items must be a tuple or list")
    return ContextRelevanceRanking(items=tuple(sorted(items, key=_sort_key)))
