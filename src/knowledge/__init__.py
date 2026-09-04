"""M13 personal knowledge boundaries."""

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

__all__ = [
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
]
