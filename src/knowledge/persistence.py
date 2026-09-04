"""M13.5 entity persistence boundary.

Persistence stores and retrieves immutable Entity values. Storage does not
upgrade an entity into truth, fact, intent, policy, authorization, or
execution authority.
"""

from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass
from typing import Callable, Iterable

from .entities import Entity, EntityType


class EntityPersistenceError(RuntimeError):
    """Base error for entity persistence operations."""


class EntityAlreadyExistsError(EntityPersistenceError):
    """Raised when a persistence write would overwrite an existing entity."""


class EntityNotFoundError(EntityPersistenceError):
    """Raised when a required entity does not exist."""


ConnectionFactory = Callable[[], sqlite3.Connection]


@dataclass(frozen=True)
class EntityRepository:
    """SQLite repository for immutable Entity values."""

    connection_factory: ConnectionFactory

    def initialize(self) -> None:
        with self.connection_factory() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS knowledge_entities (
                    entity_id TEXT PRIMARY KEY,
                    entity_type TEXT NOT NULL,
                    canonical_name TEXT NOT NULL,
                    metadata_json TEXT NOT NULL,
                    evidence_refs_json TEXT NOT NULL
                )
                """
            )

    def save(self, entity: Entity) -> None:
        if not isinstance(entity, Entity):
            raise TypeError("entity must be an Entity")
        self.initialize()
        try:
            with self.connection_factory() as connection:
                connection.execute(
                    """
                    INSERT INTO knowledge_entities
                    (entity_id, entity_type, canonical_name, metadata_json, evidence_refs_json)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (
                        entity.entity_id,
                        entity.entity_type.value,
                        entity.canonical_name,
                        json.dumps(entity.to_dict()["metadata"], sort_keys=True),
                        json.dumps(list(entity.evidence_refs), sort_keys=True),
                    ),
                )
        except sqlite3.IntegrityError as exc:
            raise EntityAlreadyExistsError(
                f"entity '{entity.entity_id}' already exists"
            ) from exc

    def get(self, entity_id: str) -> Entity | None:
        if not isinstance(entity_id, str) or not entity_id.strip():
            raise ValueError("entity_id must be a non-empty string")
        self.initialize()
        with self.connection_factory() as connection:
            row = connection.execute(
                """
                SELECT entity_id, entity_type, canonical_name,
                       metadata_json, evidence_refs_json
                FROM knowledge_entities
                WHERE entity_id = ?
                """,
                (entity_id,),
            ).fetchone()
        if row is None:
            return None
        return self._from_row(row)

    def require(self, entity_id: str) -> Entity:
        entity = self.get(entity_id)
        if entity is None:
            raise EntityNotFoundError(f"entity '{entity_id}' does not exist")
        return entity

    def list_all(self) -> tuple[Entity, ...]:
        self.initialize()
        with self.connection_factory() as connection:
            rows = connection.execute(
                """
                SELECT entity_id, entity_type, canonical_name,
                       metadata_json, evidence_refs_json
                FROM knowledge_entities
                ORDER BY entity_id
                """
            ).fetchall()
        return tuple(self._from_row(row) for row in rows)

    def delete(self, entity_id: str) -> bool:
        if not isinstance(entity_id, str) or not entity_id.strip():
            raise ValueError("entity_id must be a non-empty string")
        self.initialize()
        with self.connection_factory() as connection:
            cursor = connection.execute(
                "DELETE FROM knowledge_entities WHERE entity_id = ?",
                (entity_id,),
            )
            return cursor.rowcount == 1

    @staticmethod
    def _from_row(row: Iterable[object]) -> Entity:
        entity_id, entity_type, canonical_name, metadata_json, evidence_refs_json = row
        try:
            metadata = json.loads(str(metadata_json))
            evidence_refs = tuple(json.loads(str(evidence_refs_json)))
            return Entity(
                entity_id=str(entity_id),
                entity_type=EntityType(str(entity_type)),
                canonical_name=str(canonical_name),
                metadata=metadata,
                evidence_refs=evidence_refs,
            )
        except (TypeError, ValueError, json.JSONDecodeError) as exc:
            raise EntityPersistenceError("stored entity data is invalid") from exc
