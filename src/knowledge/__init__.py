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

__all__ = [
    "Entity",
    "EntityType",
    "EntityValidationError",
    "MAX_ENTITY_EVIDENCE_REFS",
    "MAX_ENTITY_ID_LENGTH",
    "MAX_ENTITY_METADATA_ITEMS",
    "MAX_ENTITY_NAME_LENGTH",
]
