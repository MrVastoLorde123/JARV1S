"""M92-M99: provider-neutral world-model and current-context boundary.

The world model is a derived view over observations. Observations are evidence;
they are not truth. Reconciliation selects a bounded current view for context
while retaining conflicting candidates as explicit uncertainty.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Mapping


class WorldEntityType(str, Enum):
    USER = "USER"
    PERSON = "PERSON"
    PROJECT = "PROJECT"
    DEVICE = "DEVICE"
    LOCATION = "LOCATION"
    ORGANIZATION = "ORGANIZATION"
    RESOURCE = "RESOURCE"
    CONCEPT = "CONCEPT"
    SYSTEM = "SYSTEM"
    OTHER = "OTHER"


class WorldObservationAction(str, Enum):
    ASSERT = "ASSERT"
    RETRACT = "RETRACT"


def _parse_timestamp(value: str) -> datetime:
    if not isinstance(value, str) or not value.strip():
        raise ValueError("timestamp must be a non-empty string")
    normalized = value.strip().replace("Z", "+00:00")
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError as exc:
        raise ValueError(f"invalid ISO-8601 timestamp: {value!r}") from exc
    if parsed.tzinfo is None:
        raise ValueError("timestamp must include a timezone offset")
    return parsed


def _canonical(value: object) -> object:
    if isinstance(value, Mapping):
        return {str(key): _canonical(item) for key, item in sorted(value.items(), key=lambda pair: str(pair[0]))}
    if isinstance(value, (tuple, list)):
        return [_canonical(item) for item in value]
    if isinstance(value, Enum):
        return value.value
    return value


def _digest(payload: object) -> str:
    encoded = json.dumps(_canonical(payload), sort_keys=True, separators=(",", ":"), default=str).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _validate_mapping(name: str, value: Mapping[str, object]) -> None:
    if not isinstance(value, Mapping):
        raise TypeError(f"{name} must be a mapping")


@dataclass(frozen=True)
class ValidityWindow:
    """Explicit temporal bounds for a world-state assertion."""

    observed_at: str
    valid_from: str
    valid_until: str | None = None

    def __post_init__(self) -> None:
        observed = _parse_timestamp(self.observed_at)
        start = _parse_timestamp(self.valid_from)
        if self.valid_until is not None:
            end = _parse_timestamp(self.valid_until)
            if end <= start:
                raise ValueError("valid_until must be later than valid_from")
        if observed < start:
            raise ValueError("observed_at cannot precede valid_from")

    def is_active(self, at: str) -> bool:
        moment = _parse_timestamp(at)
        start = _parse_timestamp(self.valid_from)
        if moment < start:
            return False
        if self.valid_until is None:
            return True
        return moment < _parse_timestamp(self.valid_until)

    def to_context(self) -> dict[str, object]:
        return {
            "observed_at": self.observed_at,
            "valid_from": self.valid_from,
            "valid_until": self.valid_until,
        }


@dataclass(frozen=True)
class WorldEntity:
    """Immutable entity-state candidate derived from one observation."""

    entity_id: str
    entity_type: WorldEntityType
    label: str
    attributes: Mapping[str, object] = field(default_factory=dict)
    confidence: float = 0.5
    provenance_ids: tuple[str, ...] = ()
    validity: ValidityWindow = field(
        default_factory=lambda: ValidityWindow(
            observed_at="1970-01-01T00:00:00+00:00",
            valid_from="1970-01-01T00:00:00+00:00",
        )
    )

    def __post_init__(self) -> None:
        for name in ("entity_id", "label"):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string")
        if not isinstance(self.entity_type, WorldEntityType):
            raise TypeError("entity_type must be a WorldEntityType")
        _validate_mapping("attributes", self.attributes)
        if not isinstance(self.confidence, (int, float)) or isinstance(self.confidence, bool):
            raise TypeError("confidence must be numeric")
        if not 0.0 <= float(self.confidence) <= 1.0:
            raise ValueError("confidence must be between 0 and 1")
        if not isinstance(self.provenance_ids, tuple) or any(
            not isinstance(item, str) or not item.strip() for item in self.provenance_ids
        ):
            raise TypeError("provenance_ids must be a tuple of non-empty strings")
        if len(set(self.provenance_ids)) != len(self.provenance_ids):
            raise ValueError("provenance_ids must not contain duplicates")
        if not isinstance(self.validity, ValidityWindow):
            raise TypeError("validity must be a ValidityWindow")

    @property
    def fingerprint(self) -> str:
        return _digest(self.to_context(include_identity=False))

    def to_context(self, *, include_identity: bool = True) -> dict[str, object]:
        payload: dict[str, object] = {
            "entity_type": self.entity_type.value,
            "label": self.label,
            "attributes": dict(self.attributes),
            "confidence": float(self.confidence),
            "provenance_ids": tuple(self.provenance_ids),
            "validity": self.validity.to_context(),
            "truth_established": False,
            "authority_granted": False,
            "execution_requested": False,
        }
        if include_identity:
            payload["entity_id"] = self.entity_id
        return payload


@dataclass(frozen=True)
class WorldRelation:
    """Immutable relationship-state candidate between two world entities."""

    relation_id: str
    source_entity_id: str
    target_entity_id: str
    predicate: str
    confidence: float = 0.5
    provenance_ids: tuple[str, ...] = ()
    validity: ValidityWindow = field(
        default_factory=lambda: ValidityWindow(
            observed_at="1970-01-01T00:00:00+00:00",
            valid_from="1970-01-01T00:00:00+00:00",
        )
    )
    metadata: Mapping[str, object] = field(default_factory=dict)

    def __post_init__(self) -> None:
        for name in ("relation_id", "source_entity_id", "target_entity_id", "predicate"):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string")
        _validate_mapping("metadata", self.metadata)
        if not isinstance(self.confidence, (int, float)) or isinstance(self.confidence, bool):
            raise TypeError("confidence must be numeric")
        if not 0.0 <= float(self.confidence) <= 1.0:
            raise ValueError("confidence must be between 0 and 1")
        if not isinstance(self.provenance_ids, tuple) or any(
            not isinstance(item, str) or not item.strip() for item in self.provenance_ids
        ):
            raise TypeError("provenance_ids must be a tuple of non-empty strings")
        if len(set(self.provenance_ids)) != len(self.provenance_ids):
            raise ValueError("provenance_ids must not contain duplicates")
        if not isinstance(self.validity, ValidityWindow):
            raise TypeError("validity must be a ValidityWindow")

    @property
    def fingerprint(self) -> str:
        return _digest(self.to_context(include_identity=False))

    def to_context(self, *, include_identity: bool = True) -> dict[str, object]:
        payload: dict[str, object] = {
            "source_entity_id": self.source_entity_id,
            "target_entity_id": self.target_entity_id,
            "predicate": self.predicate,
            "confidence": float(self.confidence),
            "provenance_ids": tuple(self.provenance_ids),
            "validity": self.validity.to_context(),
            "metadata": dict(self.metadata),
            "truth_established": False,
            "authority_granted": False,
            "execution_requested": False,
        }
        if include_identity:
            payload["relation_id"] = self.relation_id
        return payload


@dataclass(frozen=True)
class WorldObservation:
    """Evidence packet from which a world-state candidate is derived."""

    observation_id: str
    observed_at: str
    provenance_ids: tuple[str, ...]
    entity: WorldEntity | None = None
    relation: WorldRelation | None = None
    action: WorldObservationAction = WorldObservationAction.ASSERT
    retracts_observation_id: str | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.observation_id, str) or not self.observation_id.strip():
            raise ValueError("observation_id must be a non-empty string")
        _parse_timestamp(self.observed_at)
        if not isinstance(self.provenance_ids, tuple) or any(
            not isinstance(item, str) or not item.strip() for item in self.provenance_ids
        ):
            raise TypeError("provenance_ids must be a tuple of non-empty strings")
        if not self.provenance_ids:
            raise ValueError("world observations require at least one provenance id")
        if len(set(self.provenance_ids)) != len(self.provenance_ids):
            raise ValueError("provenance_ids must not contain duplicates")
        if not isinstance(self.action, WorldObservationAction):
            raise TypeError("action must be a WorldObservationAction")
        if self.action is WorldObservationAction.ASSERT:
            if (self.entity is None) == (self.relation is None):
                raise ValueError("ASSERT observations require exactly one entity or relation")
            if self.retracts_observation_id is not None:
                raise ValueError("ASSERT observations cannot target a retraction")
        else:
            if self.entity is not None or self.relation is not None:
                raise ValueError("RETRACT observations cannot contain entity or relation payloads")
            if not isinstance(self.retracts_observation_id, str) or not self.retracts_observation_id.strip():
                raise ValueError("RETRACT observations require retracts_observation_id")

    @property
    def target_id(self) -> str:
        if self.entity is not None:
            return self.entity.entity_id
        if self.relation is not None:
            return self.relation.relation_id
        return self.retracts_observation_id or ""

    @property
    def fingerprint(self) -> str:
        payload = {
            "observation_id": self.observation_id,
            "observed_at": self.observed_at,
            "provenance_ids": self.provenance_ids,
            "entity": self.entity.to_context() if self.entity else None,
            "relation": self.relation.to_context() if self.relation else None,
            "action": self.action.value,
            "retracts_observation_id": self.retracts_observation_id,
        }
        return _digest(payload)

    def to_context(self) -> dict[str, object]:
        return {
            "observation_id": self.observation_id,
            "observed_at": self.observed_at,
            "provenance_ids": tuple(self.provenance_ids),
            "entity": self.entity.to_context() if self.entity else None,
            "relation": self.relation.to_context() if self.relation else None,
            "action": self.action.value,
            "retracts_observation_id": self.retracts_observation_id,
            "truth_established": False,
            "authority_granted": False,
            "execution_requested": False,
        }


@dataclass(frozen=True)
class WorldConflict:
    """Explicit ambiguity retained when active state candidates disagree."""

    conflict_id: str
    subject_id: str
    subject_kind: str
    candidate_fingerprints: tuple[str, ...]
    selected_fingerprint: str
    observation_ids: tuple[str, ...]
    reason: str = "multiple active candidates disagree"

    def __post_init__(self) -> None:
        for value in (self.conflict_id, self.subject_id, self.subject_kind, self.selected_fingerprint, self.reason):
            if not isinstance(value, str) or not value.strip():
                raise ValueError("conflict identity and reason must be non-empty strings")
        if not self.candidate_fingerprints:
            raise ValueError("conflict must contain candidate fingerprints")
        if not self.observation_ids:
            raise ValueError("conflict must contain observation ids")

    def to_context(self) -> dict[str, object]:
        return {
            "conflict_id": self.conflict_id,
            "subject_id": self.subject_id,
            "subject_kind": self.subject_kind,
            "candidate_fingerprints": tuple(self.candidate_fingerprints),
            "selected_fingerprint": self.selected_fingerprint,
            "observation_ids": tuple(self.observation_ids),
            "reason": self.reason,
            "truth_established": False,
            "authority_granted": False,
            "execution_requested": False,
        }


@dataclass(frozen=True)
class WorldSnapshot:
    """Immutable bounded current-world projection for downstream reasoning."""

    snapshot_id: str
    version: int
    generated_at: str
    entities: tuple[WorldEntity, ...]
    relations: tuple[WorldRelation, ...]
    conflicts: tuple[WorldConflict, ...]
    observation_ids: tuple[str, ...]

    def __post_init__(self) -> None:
        _parse_timestamp(self.generated_at)
        if not isinstance(self.version, int) or self.version < 0:
            raise ValueError("version must be a non-negative integer")
        if not isinstance(self.entities, tuple) or any(not isinstance(item, WorldEntity) for item in self.entities):
            raise TypeError("entities must be a tuple of WorldEntity")
        if not isinstance(self.relations, tuple) or any(not isinstance(item, WorldRelation) for item in self.relations):
            raise TypeError("relations must be a tuple of WorldRelation")
        if not isinstance(self.conflicts, tuple) or any(not isinstance(item, WorldConflict) for item in self.conflicts):
            raise TypeError("conflicts must be a tuple of WorldConflict")
        if not isinstance(self.observation_ids, tuple) or any(not isinstance(item, str) or not item.strip() for item in self.observation_ids):
            raise TypeError("observation_ids must be a tuple of non-empty strings")

    @property
    def is_ambiguous(self) -> bool:
        return bool(self.conflicts)

    def to_context(self) -> dict[str, object]:
        return {
            "snapshot_id": self.snapshot_id,
            "version": self.version,
            "generated_at": self.generated_at,
            "entities": tuple(item.to_context() for item in self.entities),
            "relations": tuple(item.to_context() for item in self.relations),
            "conflicts": tuple(item.to_context() for item in self.conflicts),
            "observation_ids": tuple(self.observation_ids),
            "ambiguous": self.is_ambiguous,
            "truth_established": False,
            "authority_granted": False,
            "execution_requested": False,
        }


class WorldModelSystem:
    """In-memory derived world model over provenance-backed observations."""

    def __init__(self) -> None:
        self._observations: dict[str, WorldObservation] = {}
        self._retracted: set[str] = set()
        self._version = 0

    def observe(self, observation: WorldObservation) -> bool:
        if not isinstance(observation, WorldObservation):
            raise TypeError("observation must be a WorldObservation")
        existing = self._observations.get(observation.observation_id)
        if existing is not None:
            if existing.fingerprint != observation.fingerprint:
                raise ValueError(f"observation id already exists with different content: {observation.observation_id}")
            return False
        if observation.action is WorldObservationAction.RETRACT:
            target = observation.retracts_observation_id
            if target not in self._observations:
                raise ValueError(f"cannot retract unknown observation: {target}")
            self._retracted.add(target)
        self._observations[observation.observation_id] = observation
        self._version += 1
        return True

    def observations(self) -> tuple[WorldObservation, ...]:
        return tuple(self._observations[key] for key in sorted(self._observations))

    @staticmethod
    def _candidate_sort_key(
        observation: WorldObservation,
        payload: WorldEntity | WorldRelation,
    ) -> tuple[float, datetime, str]:
        return (float(payload.confidence), _parse_timestamp(observation.observed_at), observation.observation_id)

    def _select_entity(
        self,
        subject_id: str,
        candidates: list[tuple[WorldObservation, WorldEntity]],
    ) -> tuple[tuple[WorldObservation, WorldEntity], WorldConflict | None]:
        ordered = sorted(candidates, key=lambda pair: self._candidate_sort_key(pair[0], pair[1]), reverse=True)
        selected = ordered[0]
        fingerprints = tuple(sorted({payload.fingerprint for _, payload in ordered}))
        if len(fingerprints) <= 1:
            return selected, None
        observation_ids = tuple(item.observation_id for item, _ in ordered)
        conflict_id = _digest({"subject_id": subject_id, "fingerprints": fingerprints, "observation_ids": observation_ids})
        return selected, WorldConflict(
            conflict_id=conflict_id,
            subject_id=subject_id,
            subject_kind="ENTITY",
            candidate_fingerprints=fingerprints,
            selected_fingerprint=selected[1].fingerprint,
            observation_ids=observation_ids,
        )

    def _select_relation(
        self,
        subject_id: str,
        candidates: list[tuple[WorldObservation, WorldRelation]],
    ) -> tuple[tuple[WorldObservation, WorldRelation], WorldConflict | None]:
        ordered = sorted(candidates, key=lambda pair: self._candidate_sort_key(pair[0], pair[1]), reverse=True)
        selected = ordered[0]
        fingerprints = tuple(sorted({payload.fingerprint for _, payload in ordered}))
        if len(fingerprints) <= 1:
            return selected, None
        observation_ids = tuple(item.observation_id for item, _ in ordered)
        conflict_id = _digest({"subject_id": subject_id, "fingerprints": fingerprints, "observation_ids": observation_ids})
        return selected, WorldConflict(
            conflict_id=conflict_id,
            subject_id=subject_id,
            subject_kind="RELATION",
            candidate_fingerprints=fingerprints,
            selected_fingerprint=selected[1].fingerprint,
            observation_ids=observation_ids,
        )

    def snapshot(self, *, generated_at: str) -> WorldSnapshot:
        _parse_timestamp(generated_at)
        active = [
            observation
            for observation in self._observations.values()
            if observation.action is WorldObservationAction.ASSERT
            and observation.observation_id not in self._retracted
            and (
                (observation.entity is not None and observation.entity.validity.is_active(generated_at))
                or (observation.relation is not None and observation.relation.validity.is_active(generated_at))
            )
        ]

        entity_candidates: dict[str, list[tuple[WorldObservation, WorldEntity]]] = {}
        relation_candidates: dict[str, list[tuple[WorldObservation, WorldRelation]]] = {}
        for observation in active:
            if observation.entity is not None:
                entity_candidates.setdefault(observation.entity.entity_id, []).append((observation, observation.entity))
            if observation.relation is not None:
                relation_candidates.setdefault(observation.relation.relation_id, []).append((observation, observation.relation))

        entities: list[WorldEntity] = []
        relations: list[WorldRelation] = []
        conflicts: list[WorldConflict] = []
        used_observation_ids: list[str] = []

        for subject_id in sorted(entity_candidates):
            candidates = entity_candidates[subject_id]
            selected, conflict = self._select_entity(subject_id, candidates)
            entities.append(selected[1])
            used_observation_ids.extend(item.observation_id for item, _ in candidates)
            if conflict is not None:
                conflicts.append(conflict)

        for relation_id in sorted(relation_candidates):
            candidates = relation_candidates[relation_id]
            selected, conflict = self._select_relation(relation_id, candidates)
            relations.append(selected[1])
            used_observation_ids.extend(item.observation_id for item, _ in candidates)
            if conflict is not None:
                conflicts.append(conflict)

        observation_ids = tuple(sorted(set(used_observation_ids)))
        snapshot_payload = {
            "version": self._version,
            "generated_at": generated_at,
            "entities": tuple(item.to_context() for item in entities),
            "relations": tuple(item.to_context() for item in relations),
            "conflicts": tuple(item.to_context() for item in conflicts),
            "observation_ids": observation_ids,
        }
        snapshot_id = _digest(snapshot_payload)
        return WorldSnapshot(
            snapshot_id=snapshot_id,
            version=self._version,
            generated_at=generated_at,
            entities=tuple(entities),
            relations=tuple(relations),
            conflicts=tuple(conflicts),
            observation_ids=observation_ids,
        )

    def summary(self) -> Mapping[str, object]:
        return {
            "observation_count": len(self._observations),
            "retracted_count": len(self._retracted),
            "version": self._version,
            "truth_established": False,
            "authority_granted": False,
            "execution_requested": False,
            "provider_selected": False,
        }

    def to_context(self, *, generated_at: str) -> Mapping[str, object]:
        snapshot = self.snapshot(generated_at=generated_at)
        return {
            "summary": dict(self.summary()),
            "snapshot": snapshot.to_context(),
            "truth_established": False,
            "authority_granted": False,
            "execution_requested": False,
        }

    @property
    def authorizes_execution(self) -> bool:
        return False

    @property
    def executes_capability(self) -> bool:
        return False

    @property
    def mutates_external_state(self) -> bool:
        return False

    @property
    def persists_state(self) -> bool:
        return False

    @property
    def establishes_truth(self) -> bool:
        return False

    @property
    def establishes_certainty(self) -> bool:
        return False

    @property
    def selects_provider(self) -> bool:
        return False


__all__ = [
    "ValidityWindow",
    "WorldConflict",
    "WorldEntity",
    "WorldEntityType",
    "WorldModelSystem",
    "WorldObservation",
    "WorldObservationAction",
    "WorldRelation",
    "WorldSnapshot",
]
