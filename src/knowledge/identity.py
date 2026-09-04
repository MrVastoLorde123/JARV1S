"""M13.2 deterministic entity identity and resolution boundary."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from enum import Enum
from typing import Any, Iterable

from src.knowledge.entities import Entity, EntityType, MAX_ENTITY_ID_LENGTH, MAX_ENTITY_NAME_LENGTH


class IdentityResolutionStatus(str, Enum):
    """Outcome of comparing a reference against a candidate entity."""

    EXACT_MATCH = "EXACT_MATCH"
    POSSIBLE_MATCH = "POSSIBLE_MATCH"
    NO_MATCH = "NO_MATCH"
    CONFLICT = "CONFLICT"


class IdentityResolutionError(ValueError):
    """Raised when identity-resolution inputs violate the boundary."""


MAX_REFERENCE_LENGTH = MAX_ENTITY_NAME_LENGTH
MAX_CANDIDATES = 256
MAX_REASON_LENGTH = 512


def normalize_identity_reference(value: str) -> str:
    """Normalize presentation differences without asserting identity or truth."""
    if not isinstance(value, str) or not value.strip():
        raise IdentityResolutionError("reference must be a non-empty string")
    value = value.strip().casefold()
    value = re.sub(r"\s+", " ", value)
    return value


@dataclass(frozen=True)
class IdentityResolution:
    """Immutable, non-authoritative result of identity comparison."""

    reference: str
    entity_id: str | None
    entity_type: EntityType | None
    status: IdentityResolutionStatus
    score: float
    reasons: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not isinstance(self.reference, str) or not self.reference.strip():
            raise IdentityResolutionError("reference must be a non-empty string")
        if len(self.reference) > MAX_REFERENCE_LENGTH:
            raise IdentityResolutionError(
                f"reference exceeds maximum length of {MAX_REFERENCE_LENGTH}"
            )
        if self.entity_id is not None:
            if not isinstance(self.entity_id, str) or not self.entity_id.strip():
                raise IdentityResolutionError("entity_id must be None or a non-empty string")
            if len(self.entity_id) > MAX_ENTITY_ID_LENGTH:
                raise IdentityResolutionError(
                    f"entity_id exceeds maximum length of {MAX_ENTITY_ID_LENGTH}"
                )
        if self.entity_type is not None and not isinstance(self.entity_type, EntityType):
            raise IdentityResolutionError("entity_type must be an EntityType or None")
        if not isinstance(self.status, IdentityResolutionStatus):
            try:
                object.__setattr__(self, "status", IdentityResolutionStatus(self.status))
            except (TypeError, ValueError) as exc:
                raise IdentityResolutionError("status must be an IdentityResolutionStatus") from exc
        if isinstance(self.score, bool) or not isinstance(self.score, (int, float)):
            raise IdentityResolutionError("score must be a number")
        if not 0.0 <= float(self.score) <= 1.0:
            raise IdentityResolutionError("score must be between 0.0 and 1.0")
        if not isinstance(self.reasons, tuple):
            raise IdentityResolutionError("reasons must be a tuple")
        for index, reason in enumerate(self.reasons):
            if not isinstance(reason, str) or not reason.strip():
                raise IdentityResolutionError(f"reasons[{index}] must be a non-empty string")
            if len(reason) > MAX_REASON_LENGTH:
                raise IdentityResolutionError(
                    f"reasons[{index}] exceeds maximum length of {MAX_REASON_LENGTH}"
                )

    def to_dict(self) -> dict[str, Any]:
        return {
            "reference": self.reference,
            "entity_id": self.entity_id,
            "entity_type": None if self.entity_type is None else self.entity_type.value,
            "status": self.status.value,
            "score": float(self.score),
            "reasons": list(self.reasons),
            "identity_guaranteed": False,
            "truth_guaranteed": False,
            "authorization_granted": False,
            "policy_authority": False,
            "execution_requested": False,
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), sort_keys=True)


@dataclass(frozen=True)
class EntityIdentityResolver:
    """Deterministic resolver using only explicit entity fields.

    The resolver ranks candidates; it never mutates entities, merges records,
    declares truth, grants authority, or performs persistence.
    """

    exact_threshold: float = 1.0
    possible_threshold: float = 0.75

    def __post_init__(self) -> None:
        if not 0.0 <= self.possible_threshold <= self.exact_threshold <= 1.0:
            raise IdentityResolutionError(
                "thresholds must satisfy 0.0 <= possible_threshold <= exact_threshold <= 1.0"
            )

    def resolve(
        self,
        reference: str,
        candidates: Iterable[Entity],
        *,
        expected_type: EntityType | None = None,
    ) -> IdentityResolution:
        """Return the best bounded identity judgment for a reference."""
        normalized_reference = normalize_identity_reference(reference)
        candidate_list = tuple(candidates)
        if len(candidate_list) > MAX_CANDIDATES:
            raise IdentityResolutionError(
                f"candidates exceeds maximum count of {MAX_CANDIDATES}"
            )
        for index, entity in enumerate(candidate_list):
            if not isinstance(entity, Entity):
                raise IdentityResolutionError(f"candidates[{index}] must be an Entity")
        if expected_type is not None and not isinstance(expected_type, EntityType):
            raise IdentityResolutionError("expected_type must be an EntityType or None")

        scored: list[tuple[float, Entity, tuple[str, ...]]] = []
        for entity in candidate_list:
            normalized_name = normalize_identity_reference(entity.canonical_name)
            score = 0.0
            reasons: list[str] = []

            if normalized_reference == normalized_name:
                score += 0.8
                reasons.append("canonical_name_exact")
            elif normalized_reference in normalized_name or normalized_name in normalized_reference:
                score += 0.45
                reasons.append("canonical_name_containment")

            if expected_type is not None:
                if entity.entity_type == expected_type:
                    score += 0.2
                    reasons.append("entity_type_matches")
                else:
                    score = 0.0
                    reasons.append("entity_type_conflict")

            alias_values = entity.metadata.get("aliases", ())
            if isinstance(alias_values, (tuple, list)):
                normalized_aliases = {normalize_identity_reference(str(alias)) for alias in alias_values if str(alias).strip()}
                if normalized_reference in normalized_aliases:
                    score = max(score, 0.9 if expected_type is None else min(1.0, 0.9 + (0.2 if entity.entity_type == expected_type else 0.0)))
                    reasons.append("metadata_alias_exact")

            scored.append((min(1.0, score), entity, tuple(reasons)))

        if not scored:
            return IdentityResolution(
                reference=reference,
                entity_id=None,
                entity_type=None,
                status=IdentityResolutionStatus.NO_MATCH,
                score=0.0,
                reasons=("no_candidates",),
            )

        scored.sort(key=lambda item: (-item[0], item[1].entity_id))
        best_score, best_entity, best_reasons = scored[0]
        if best_score >= self.exact_threshold:
            status = IdentityResolutionStatus.EXACT_MATCH
        elif best_score >= self.possible_threshold:
            if len(scored) > 1 and scored[1][0] >= best_score and scored[1][1].entity_id != best_entity.entity_id:
                return IdentityResolution(
                    reference=reference,
                    entity_id=None,
                    entity_type=None,
                    status=IdentityResolutionStatus.CONFLICT,
                    score=best_score,
                    reasons=("multiple_candidates_share_top_score",),
                )
            status = IdentityResolutionStatus.POSSIBLE_MATCH
        else:
            status = IdentityResolutionStatus.NO_MATCH

        return IdentityResolution(
            reference=reference,
            entity_id=best_entity.entity_id if status != IdentityResolutionStatus.NO_MATCH else None,
            entity_type=best_entity.entity_type if status != IdentityResolutionStatus.NO_MATCH else None,
            status=status,
            score=best_score,
            reasons=best_reasons or ("no_identity_signal",),
        )
