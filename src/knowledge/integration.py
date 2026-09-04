"""M13.7 knowledge integration boundary.

Composes the existing personal-knowledge primitives without introducing a
second semantic engine. Entities remain persisted values; relationships and
associations remain explicit structured knowledge; retrieval remains read-only.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable

from .associations import EvidenceBackedAssociation
from .entities import Entity
from .persistence import EntityRepository
from .relationships import Relationship
from .retrieval import KnowledgeMatch, KnowledgeRetriever, KnowledgeSearchResult


class KnowledgeIntegrationError(RuntimeError):
    """Raised when integrated knowledge state violates its boundary."""


MAX_RELATIONSHIPS = 1024
MAX_ASSOCIATIONS = 1024


@dataclass(frozen=True)
class KnowledgeSnapshot:
    """Immutable projection of the integrated knowledge layer."""

    entities: tuple[Entity, ...]
    relationships: tuple[Relationship, ...] = ()
    associations: tuple[EvidenceBackedAssociation, ...] = ()

    def __post_init__(self) -> None:
        for name, values, maximum, expected in (
            ("entities", self.entities, 64 * 1024, Entity),
            ("relationships", self.relationships, MAX_RELATIONSHIPS, Relationship),
            ("associations", self.associations, MAX_ASSOCIATIONS, EvidenceBackedAssociation),
        ):
            if not isinstance(values, tuple):
                raise TypeError(f"{name} must be a tuple")
            if len(values) > maximum:
                raise KnowledgeIntegrationError(f"{name} exceed maximum count of {maximum}")
            if any(not isinstance(value, expected) for value in values):
                raise TypeError(f"{name} contains an invalid value")

    def to_dict(self) -> dict[str, object]:
        return {
            "entities": [entity.to_dict() for entity in self.entities],
            "relationships": [relationship.to_dict() for relationship in self.relationships],
            "associations": [association.to_dict() for association in self.associations],
            "truth_guaranteed": False,
            "fact_guaranteed": False,
            "intent_guaranteed": False,
            "authorization_granted": False,
            "policy_authority": False,
            "execution_requested": False,
        }


@dataclass(frozen=True)
class KnowledgeRuntime:
    """Application-facing composition of the M13 personal knowledge layer."""

    repository: EntityRepository
    relationships: tuple[Relationship, ...] = field(default_factory=tuple)
    associations: tuple[EvidenceBackedAssociation, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        if not isinstance(self.repository, EntityRepository):
            raise TypeError("repository must be an EntityRepository")
        if not isinstance(self.relationships, tuple):
            raise TypeError("relationships must be a tuple")
        if not isinstance(self.associations, tuple):
            raise TypeError("associations must be a tuple")
        if len(self.relationships) > MAX_RELATIONSHIPS:
            raise KnowledgeIntegrationError("relationships exceed maximum count")
        if len(self.associations) > MAX_ASSOCIATIONS:
            raise KnowledgeIntegrationError("associations exceed maximum count")
        if any(not isinstance(item, Relationship) for item in self.relationships):
            raise TypeError("relationships must contain Relationship values")
        if any(not isinstance(item, EvidenceBackedAssociation) for item in self.associations):
            raise TypeError("associations must contain EvidenceBackedAssociation values")

    @property
    def retriever(self) -> KnowledgeRetriever:
        return KnowledgeRetriever(self.repository)

    def get_entity(self, entity_id: str) -> Entity | None:
        return self.retriever.get(entity_id)

    def search_entities(self, query: str) -> KnowledgeSearchResult:
        return self.retriever.search(query)

    def relationships_for(self, entity_id: str) -> tuple[Relationship, ...]:
        if not isinstance(entity_id, str) or not entity_id.strip():
            raise KnowledgeIntegrationError("entity_id must be a non-empty string")
        return tuple(
            relationship
            for relationship in self.relationships
            if relationship.source_entity_id == entity_id or relationship.target_entity_id == entity_id
        )

    def associations_for(self, entity_id: str) -> tuple[EvidenceBackedAssociation, ...]:
        if not isinstance(entity_id, str) or not entity_id.strip():
            raise KnowledgeIntegrationError("entity_id must be a non-empty string")
        return tuple(
            association
            for association in self.associations
            if association.relationship.source_entity_id == entity_id
            or association.relationship.target_entity_id == entity_id
        )

    def snapshot(self) -> KnowledgeSnapshot:
        return KnowledgeSnapshot(
            entities=self.repository.list_all(),
            relationships=self.relationships,
            associations=self.associations,
        )

    def with_relationship(self, relationship: Relationship) -> "KnowledgeRuntime":
        if not isinstance(relationship, Relationship):
            raise TypeError("relationship must be a Relationship")
        if any(item.relationship_id == relationship.relationship_id for item in self.relationships):
            raise KnowledgeIntegrationError(
                f"relationship '{relationship.relationship_id}' already exists"
            )
        return KnowledgeRuntime(
            repository=self.repository,
            relationships=self.relationships + (relationship,),
            associations=self.associations,
        )

    def with_association(self, association: EvidenceBackedAssociation) -> "KnowledgeRuntime":
        if not isinstance(association, EvidenceBackedAssociation):
            raise TypeError("association must be an EvidenceBackedAssociation")
        if any(item.relationship_id == association.relationship_id for item in self.associations):
            raise KnowledgeIntegrationError(
                f"association for relationship '{association.relationship_id}' already exists"
            )
        if not any(
            relationship.relationship_id == association.relationship_id
            for relationship in self.relationships
        ):
            raise KnowledgeIntegrationError(
                "association relationship must already be present in the integrated runtime"
            )
        return KnowledgeRuntime(
            repository=self.repository,
            relationships=self.relationships,
            associations=self.associations + (association,),
        )

    def matching_entities(self, query: str) -> tuple[KnowledgeMatch, ...]:
        return self.search_entities(query).matches
