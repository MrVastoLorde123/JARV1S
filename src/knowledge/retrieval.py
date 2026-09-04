"""M13.6 knowledge retrieval boundary.

Retrieval locates persisted Entity values. It does not resolve identity,
infer facts, establish truth, mutate knowledge, authorize actions, or execute.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Iterable

from .entities import Entity, EntityType
from .persistence import EntityRepository


class KnowledgeRetrievalError(RuntimeError):
    """Raised when a retrieval request violates the retrieval boundary."""


class RetrievalMatchField(str, Enum):
    ENTITY_ID = "entity_id"
    CANONICAL_NAME = "canonical_name"
    ENTITY_TYPE = "entity_type"
    METADATA = "metadata"
    EVIDENCE_REF = "evidence_ref"


MAX_QUERY_LENGTH = 256
MAX_RESULTS = 64


def _normalize_query(query: str) -> str:
    if not isinstance(query, str) or not query.strip():
        raise KnowledgeRetrievalError("query must be a non-empty string")
    query = query.strip()
    if len(query) > MAX_QUERY_LENGTH:
        raise KnowledgeRetrievalError(
            f"query exceeds maximum length of {MAX_QUERY_LENGTH}"
        )
    return query.casefold()


def _metadata_contains(entity: Entity, needle: str) -> bool:
    def walk(value: object) -> bool:
        if isinstance(value, dict):
            return any(walk(key) or walk(item) for key, item in value.items())
        if isinstance(value, (tuple, list)):
            return any(walk(item) for item in value)
        return needle in str(value).casefold()

    return walk(entity.metadata)


@dataclass(frozen=True)
class KnowledgeMatch:
    """One retrieved entity plus the fields that matched the query."""

    entity: Entity
    matched_fields: tuple[RetrievalMatchField, ...]

    def __post_init__(self) -> None:
        if not isinstance(self.entity, Entity):
            raise TypeError("entity must be an Entity")
        if not isinstance(self.matched_fields, tuple):
            raise TypeError("matched_fields must be a tuple")
        if not self.matched_fields:
            raise KnowledgeRetrievalError("a knowledge match requires matched fields")

    def to_dict(self) -> dict[str, object]:
        return {
            "entity": self.entity.to_dict(),
            "matched_fields": [field.value for field in self.matched_fields],
            "truth_guaranteed": False,
            "fact_guaranteed": False,
            "intent_guaranteed": False,
            "authorization_granted": False,
            "policy_authority": False,
            "execution_requested": False,
        }


@dataclass(frozen=True)
class KnowledgeSearchResult:
    """Immutable deterministic retrieval result."""

    query: str
    matches: tuple[KnowledgeMatch, ...]
    truncated: bool = False

    def __post_init__(self) -> None:
        if not isinstance(self.matches, tuple):
            raise TypeError("matches must be a tuple")
        if len(self.matches) > MAX_RESULTS:
            raise KnowledgeRetrievalError("matches exceed maximum result count")

    @property
    def entities(self) -> tuple[Entity, ...]:
        return tuple(match.entity for match in self.matches)

    def to_dict(self) -> dict[str, object]:
        return {
            "query": self.query,
            "matches": [match.to_dict() for match in self.matches],
            "truncated": self.truncated,
            "truth_guaranteed": False,
            "fact_guaranteed": False,
            "intent_guaranteed": False,
            "authorization_granted": False,
            "policy_authority": False,
            "execution_requested": False,
        }


@dataclass(frozen=True)
class KnowledgeRetriever:
    """Deterministic retrieval facade over persisted entities."""

    repository: EntityRepository
    max_results: int = MAX_RESULTS

    def __post_init__(self) -> None:
        if not isinstance(self.repository, EntityRepository):
            raise TypeError("repository must be an EntityRepository")
        if not isinstance(self.max_results, int) or isinstance(self.max_results, bool):
            raise TypeError("max_results must be an integer")
        if not 1 <= self.max_results <= MAX_RESULTS:
            raise ValueError(f"max_results must be between 1 and {MAX_RESULTS}")

    def get(self, entity_id: str) -> Entity | None:
        return self.repository.get(entity_id)

    def by_type(self, entity_type: EntityType) -> tuple[Entity, ...]:
        if not isinstance(entity_type, EntityType):
            try:
                entity_type = EntityType(entity_type)
            except (TypeError, ValueError) as exc:
                raise KnowledgeRetrievalError("entity_type must be supported") from exc
        return tuple(
            entity
            for entity in self.repository.list_all()
            if entity.entity_type is entity_type
        )

    def search(self, query: str) -> KnowledgeSearchResult:
        normalized = _normalize_query(query)
        matches: list[KnowledgeMatch] = []
        for entity in self.repository.list_all():
            fields: list[RetrievalMatchField] = []
            if normalized in entity.entity_id.casefold():
                fields.append(RetrievalMatchField.ENTITY_ID)
            if normalized in entity.canonical_name.casefold():
                fields.append(RetrievalMatchField.CANONICAL_NAME)
            if normalized in entity.entity_type.value.casefold():
                fields.append(RetrievalMatchField.ENTITY_TYPE)
            if _metadata_contains(entity, normalized):
                fields.append(RetrievalMatchField.METADATA)
            if any(normalized in ref.casefold() for ref in entity.evidence_refs):
                fields.append(RetrievalMatchField.EVIDENCE_REF)
            if fields:
                matches.append(KnowledgeMatch(entity=entity, matched_fields=tuple(fields)))

        truncated = len(matches) > self.max_results
        return KnowledgeSearchResult(
            query=query.strip(),
            matches=tuple(matches[: self.max_results]),
            truncated=truncated,
        )

    def all(self) -> tuple[Entity, ...]:
        return self.repository.list_all()
