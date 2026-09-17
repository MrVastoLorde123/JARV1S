"""M91: persistent-intelligence composition root.

This subsystem owns durable memory state and its evidence lineage. It does not
grant authority, execute capabilities, select providers, or establish truth.
"""

from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

from src.core.memory_episodic import EpisodicMemory
from src.core.memory_lifecycle import (
    ConsolidationProposal,
    MemoryTransition,
    propose_semantic_consolidation,
    validate_transition,
)
from src.core.memory_provenance import ProvenanceChain, ProvenanceRef, validate_provenance
from src.core.memory_working import WorkingMemorySnapshot
from src.core.personal_model import PersonalModel, PersonalModelEntry
from src.core.persistent_memory import (
    MemoryLifecycle,
    PersistentMemoryKind,
    PersistentMemoryRecord,
)


@dataclass(frozen=True)
class PersistentIntelligenceCoverage:
    persistent_record_count: int
    episodic_count: int
    semantic_count: int
    procedural_count: int
    provenance_ref_count: int
    active_count: int
    superseded_count: int

    def to_context(self) -> dict[str, object]:
        return {
            "persistent_record_count": self.persistent_record_count,
            "episodic_count": self.episodic_count,
            "semantic_count": self.semantic_count,
            "procedural_count": self.procedural_count,
            "provenance_ref_count": self.provenance_ref_count,
            "active_count": self.active_count,
            "superseded_count": self.superseded_count,
            "truth_established": False,
            "authority_granted": False,
            "execution_requested": False,
        }


class PersistentMemoryRepository:
    """SQLite-backed canonical repository for persistent memory records."""

    def __init__(self, database_path: str | Path = "data/processed/jarvis.db") -> None:
        self._database_path = Path(database_path)
        self._database_path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    @property
    def database_path(self) -> Path:
        return self._database_path

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self._database_path)
        connection.execute("PRAGMA foreign_keys = ON")
        return connection

    def _initialize(self) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS persistent_memory_records (
                    memory_id TEXT PRIMARY KEY,
                    subject_id TEXT NOT NULL,
                    kind TEXT NOT NULL,
                    content TEXT NOT NULL,
                    confidence REAL NOT NULL,
                    importance REAL NOT NULL,
                    status TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    supersedes_memory_id TEXT,
                    provenance_json TEXT NOT NULL,
                    tags_json TEXT NOT NULL,
                    metadata_json TEXT NOT NULL
                )
                """
            )
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS persistent_memory_provenance (
                    provenance_id TEXT PRIMARY KEY,
                    source_kind TEXT NOT NULL,
                    source_id TEXT NOT NULL,
                    summary TEXT NOT NULL,
                    observed_at TEXT,
                    confidence REAL
                )
                """
            )

    def persist(
        self,
        record: PersistentMemoryRecord,
        provenance: ProvenanceChain,
    ) -> bool:
        if not isinstance(record, PersistentMemoryRecord):
            raise TypeError("record must be a PersistentMemoryRecord")
        if not isinstance(provenance, ProvenanceChain):
            raise TypeError("provenance must be a ProvenanceChain")
        if record.kind is PersistentMemoryKind.WORKING:
            raise ValueError("working memory is contextual and must not enter durable storage")
        errors = validate_provenance(record, provenance)
        if errors:
            raise ValueError("; ".join(errors))
        if not record.provenance_ids:
            raise ValueError("persistent records require at least one provenance reference")
        if not record.created_at or not record.updated_at:
            raise ValueError("persistent records require created_at and updated_at")

        with self._connect() as connection:
            existing = connection.execute(
                "SELECT kind, subject_id, content, confidence, importance, status, created_at, updated_at, supersedes_memory_id, provenance_json, tags_json, metadata_json FROM persistent_memory_records WHERE memory_id = ?",
                (record.memory_id,),
            ).fetchone()
            if existing is not None:
                existing_payload = {
                    "kind": existing[0],
                    "subject_id": existing[1],
                    "content": existing[2],
                    "confidence": existing[3],
                    "importance": existing[4],
                    "status": existing[5],
                    "created_at": existing[6],
                    "updated_at": existing[7],
                    "supersedes_memory_id": existing[8],
                    "provenance_ids": tuple(json.loads(existing[9])),
                    "tags": tuple(json.loads(existing[10])),
                    "metadata": json.loads(existing[11]),
                }
                incoming_payload = {
                    "kind": record.kind.value,
                    "subject_id": record.subject_id,
                    "content": record.content,
                    "confidence": float(record.confidence),
                    "importance": float(record.importance),
                    "status": record.status.value,
                    "created_at": record.created_at,
                    "updated_at": record.updated_at,
                    "supersedes_memory_id": record.supersedes_memory_id,
                    "provenance_ids": tuple(record.provenance_ids),
                    "tags": tuple(record.tags),
                    "metadata": dict(record.metadata),
                }
                if existing_payload != incoming_payload:
                    raise ValueError(f"memory id already exists with different content: {record.memory_id}")
                return False

            for reference in provenance.refs:
                existing_ref = connection.execute(
                    "SELECT source_kind, source_id, summary, observed_at, confidence FROM persistent_memory_provenance WHERE provenance_id = ?",
                    (reference.provenance_id,),
                ).fetchone()
                incoming_ref = (
                    reference.source_kind.value,
                    reference.source_id,
                    reference.summary,
                    reference.observed_at,
                    reference.confidence,
                )
                if existing_ref is not None and tuple(existing_ref) != incoming_ref:
                    raise ValueError(
                        f"provenance id already exists with different content: {reference.provenance_id}"
                    )
                if existing_ref is None:
                    connection.execute(
                        "INSERT INTO persistent_memory_provenance (provenance_id, source_kind, source_id, summary, observed_at, confidence) VALUES (?, ?, ?, ?, ?, ?)",
                        (reference.provenance_id, *incoming_ref),
                    )

            connection.execute(
                "INSERT INTO persistent_memory_records (memory_id, subject_id, kind, content, confidence, importance, status, created_at, updated_at, supersedes_memory_id, provenance_json, tags_json, metadata_json) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    record.memory_id,
                    record.subject_id,
                    record.kind.value,
                    record.content,
                    float(record.confidence),
                    float(record.importance),
                    record.status.value,
                    record.created_at,
                    record.updated_at,
                    record.supersedes_memory_id,
                    json.dumps(record.provenance_ids),
                    json.dumps(record.tags),
                    json.dumps(dict(record.metadata), sort_keys=True),
                ),
            )
        return True

    def get(self, memory_id: str) -> PersistentMemoryRecord | None:
        if not isinstance(memory_id, str) or not memory_id.strip():
            raise ValueError("memory_id must be a non-empty string")
        with self._connect() as connection:
            row = connection.execute(
                "SELECT memory_id, subject_id, kind, content, confidence, importance, status, created_at, updated_at, supersedes_memory_id, provenance_json, tags_json, metadata_json FROM persistent_memory_records WHERE memory_id = ?",
                (memory_id,),
            ).fetchone()
        if row is None:
            return None
        return self._record_from_row(row)

    def list_records(
        self,
        *,
        kind: PersistentMemoryKind | None = None,
        subject_id: str | None = None,
        status: MemoryLifecycle | None = None,
    ) -> tuple[PersistentMemoryRecord, ...]:
        clauses: list[str] = []
        values: list[object] = []
        if kind is not None:
            if not isinstance(kind, PersistentMemoryKind):
                raise TypeError("kind must be a PersistentMemoryKind")
            clauses.append("kind = ?")
            values.append(kind.value)
        if subject_id is not None:
            if not isinstance(subject_id, str) or not subject_id.strip():
                raise ValueError("subject_id must be non-empty when provided")
            clauses.append("subject_id = ?")
            values.append(subject_id)
        if status is not None:
            if not isinstance(status, MemoryLifecycle):
                raise TypeError("status must be a MemoryLifecycle")
            clauses.append("status = ?")
            values.append(status.value)
        where = " WHERE " + " AND ".join(clauses) if clauses else ""
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT memory_id, subject_id, kind, content, confidence, importance, status, created_at, updated_at, supersedes_memory_id, provenance_json, tags_json, metadata_json FROM persistent_memory_records"
                + where
                + " ORDER BY created_at, memory_id",
                tuple(values),
            ).fetchall()
        return tuple(self._record_from_row(row) for row in rows)

    @staticmethod
    def _record_from_row(row: tuple[Any, ...]) -> PersistentMemoryRecord:
        return PersistentMemoryRecord(
            memory_id=row[0],
            subject_id=row[1],
            kind=PersistentMemoryKind(row[2]),
            content=row[3],
            confidence=float(row[4]),
            importance=float(row[5]),
            status=MemoryLifecycle(row[6]),
            created_at=row[7],
            updated_at=row[8],
            supersedes_memory_id=row[9],
            provenance_ids=tuple(json.loads(row[10])),
            tags=tuple(json.loads(row[11])),
            metadata=json.loads(row[12]),
        )

    def apply_transition(self, transition: MemoryTransition, *, updated_at: str) -> PersistentMemoryRecord:
        if not isinstance(transition, MemoryTransition):
            raise TypeError("transition must be a MemoryTransition")
        if not isinstance(updated_at, str) or not updated_at.strip():
            raise ValueError("updated_at must be non-empty")
        record = self.get(transition.memory_id)
        if record is None:
            raise ValueError(f"unknown memory id: {transition.memory_id}")
        errors = validate_transition(record, transition)
        if errors:
            raise ValueError("; ".join(errors))
        with self._connect() as connection:
            connection.execute(
                "UPDATE persistent_memory_records SET status = ?, updated_at = ? WHERE memory_id = ?",
                (transition.to_status.value, updated_at, transition.memory_id),
            )
        updated = self.get(transition.memory_id)
        if updated is None:
            raise RuntimeError("memory disappeared after lifecycle update")
        return updated

    def provenance_for(self, memory_id: str) -> ProvenanceChain:
        record = self.get(memory_id)
        if record is None:
            raise ValueError(f"unknown memory id: {memory_id}")
        placeholders = ",".join("?" for _ in record.provenance_ids)
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT provenance_id, source_kind, source_id, summary, observed_at, confidence FROM persistent_memory_provenance WHERE provenance_id IN ("
                + placeholders
                + ")",
                tuple(record.provenance_ids),
            ).fetchall()
        by_id = {row[0]: row for row in rows}
        refs = tuple(
            ProvenanceRef(
                provenance_id=provenance_id,
                source_kind=__import__(
                    "src.core.memory_provenance", fromlist=["ProvenanceSourceKind"]
                ).ProvenanceSourceKind(row[1]),
                source_id=row[2],
                summary=row[3],
                observed_at=row[4],
                confidence=row[5],
            )
            for provenance_id, row in ((item, by_id[item]) for item in record.provenance_ids if item in by_id)
        )
        chain = ProvenanceChain(refs=refs)
        errors = validate_provenance(record, chain)
        if errors:
            raise ValueError("; ".join(errors))
        return chain


class PersistentIntelligenceSystem:
    """Provider-neutral persistent-memory control plane."""

    def __init__(self, repository: PersistentMemoryRepository) -> None:
        if type(repository) is not PersistentMemoryRepository:
            raise TypeError("repository must be a PersistentMemoryRepository")
        self._repository = repository

    @property
    def repository(self) -> PersistentMemoryRepository:
        return self._repository

    def remember(
        self,
        record: PersistentMemoryRecord,
        provenance: ProvenanceChain,
    ) -> bool:
        return self._repository.persist(record, provenance)

    def recall(
        self,
        *,
        kind: PersistentMemoryKind | None = None,
        subject_id: str | None = None,
        status: MemoryLifecycle | None = None,
    ) -> tuple[PersistentMemoryRecord, ...]:
        return self._repository.list_records(kind=kind, subject_id=subject_id, status=status)

    def provenance(self, memory_id: str) -> ProvenanceChain:
        return self._repository.provenance_for(memory_id)

    def transition(self, transition: MemoryTransition, *, updated_at: str) -> PersistentMemoryRecord:
        return self._repository.apply_transition(transition, updated_at=updated_at)

    def consolidate(
        self,
        episodes: tuple[EpisodicMemory, ...],
    ) -> tuple[ConsolidationProposal, ...]:
        return propose_semantic_consolidation(episodes)

    def project_personal_model(
        self,
        subject_id: str,
        entries: tuple[PersonalModelEntry, ...],
        *,
        model_version: int = 1,
    ) -> PersonalModel:
        if any(entry.active and entry.source_memory_id is None for entry in entries):
            raise ValueError("active personal-model entries require a source memory id")
        return PersonalModel(subject_id=subject_id, entries=entries, model_version=model_version)

    def build_working_memory(self, snapshot: WorkingMemorySnapshot) -> Mapping[str, object]:
        if not isinstance(snapshot, WorkingMemorySnapshot):
            raise TypeError("snapshot must be a WorkingMemorySnapshot")
        return snapshot.to_context()

    def coverage(self) -> PersistentIntelligenceCoverage:
        records = self._repository.list_records()
        provenance_count = len({item for record in records for item in record.provenance_ids})
        return PersistentIntelligenceCoverage(
            persistent_record_count=len(records),
            episodic_count=sum(item.kind is PersistentMemoryKind.EPISODIC for item in records),
            semantic_count=sum(item.kind is PersistentMemoryKind.SEMANTIC for item in records),
            procedural_count=sum(item.kind is PersistentMemoryKind.PROCEDURAL for item in records),
            provenance_ref_count=provenance_count,
            active_count=sum(item.status is MemoryLifecycle.ACTIVE for item in records),
            superseded_count=sum(item.status is MemoryLifecycle.SUPERSEDED for item in records),
        )

    def summary(self) -> Mapping[str, object]:
        coverage = self.coverage()
        return {
            "coverage": coverage.to_context(),
            "repository_path": str(self._repository.database_path),
            "truth_established": False,
            "authority_granted": False,
            "execution_requested": False,
            "capability_invocation_performed": False,
            "provider_selected": False,
        }

    def to_context(self) -> dict[str, object]:
        return {
            "summary": dict(self.summary()),
            "coverage": self.coverage().to_context(),
            "authority_granted": False,
            "execution_requested": False,
        }


__all__ = [
    "PersistentIntelligenceCoverage",
    "PersistentIntelligenceSystem",
    "PersistentMemoryRepository",
]
