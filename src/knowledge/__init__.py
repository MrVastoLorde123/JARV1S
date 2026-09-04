"""M13 personal knowledge boundaries."""

from .associations import (
    AssociationEvidence,
    AssociationEvidenceValidationError,
    EvidenceBackedAssociation,
    MAX_ASSOCIATION_EVIDENCE_REFS,
    MAX_EVIDENCE_REF_LENGTH,
    MAX_SOURCE_LENGTH,
)
from .entities import (
    Entity,
    EntityType,
    EntityValidationError,
    MAX_ENTITY_EVIDENCE_REFS,
    MAX_ENTITY_METADATA_ITEMS,
    MAX_ENTITY_ID_LENGTH,
    MAX_ENTITY_NAME_LENGTH,
)
from .identity import (
    EntityIdentityResolver,
    IdentityResolution,
    IdentityResolutionError,
    IdentityResolutionStatus,
    MAX_CANDIDATES,
    MAX_REASON_LENGTH,
    MAX_REFERENCE_LENGTH,
    normalize_identity_reference,
)
from .persistence import (
    EntityAlreadyExistsError,
    EntityNotFoundError,
    EntityPersistenceError,
    EntityRepository,
)
from .relationships import (
    Relationship,
    RelationshipType,
    RelationshipValidationError,
    MAX_RELATIONSHIP_EVIDENCE_REFS,
    MAX_RELATIONSHIP_METADATA_ITEMS,
    MAX_RELATIONSHIP_ID_LENGTH,
)

__all__ = [
    "AssociationEvidence",
    "AssociationEvidenceValidationError",
    "EvidenceBackedAssociation",
    "MAX_ASSOCIATION_EVIDENCE_REFS",
    "MAX_EVIDENCE_REF_LENGTH",
    "MAX_SOURCE_LENGTH",
    "Entity",
    "EntityType",
    "EntityValidationError",
    "MAX_ENTITY_EVIDENCE_REFS",
    "MAX_ENTITY_METADATA_ITEMS",
    "MAX_ENTITY_ID_LENGTH",
    "MAX_ENTITY_NAME_LENGTH",
    "EntityIdentityResolver",
    "IdentityResolution",
    "IdentityResolutionError",
    "IdentityResolutionStatus",
    "MAX_CANDIDATES",
    "MAX_REASON_LENGTH",
    "MAX_REFERENCE_LENGTH",
    "normalize_identity_reference",
    "EntityAlreadyExistsError",
    "EntityNotFoundError",
    "EntityPersistenceError",
    "EntityRepository",
    "Relationship",
    "RelationshipType",
    "RelationshipValidationError",
    "MAX_RELATIONSHIP_EVIDENCE_REFS",
    "MAX_RELATIONSHIP_METADATA_ITEMS",
    "MAX_RELATIONSHIP_ID_LENGTH",
]
