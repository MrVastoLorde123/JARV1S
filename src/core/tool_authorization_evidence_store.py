"""Durable storage for tool-authorization evidence.

The store persists authorization decisions as evidence only. It does not
execute tools, authorize requests, confirm intent, or report execution
success. Persistence is intentionally separated from the authorization
policy and execution adapters.
"""

from __future__ import annotations

import hashlib
import json
import sqlite3
from dataclasses import dataclass
from pathlib import Path

from src.core.tool_authorization_policy import ToolAuthorizationEvidence


_SCHEMA = """
CREATE TABLE IF NOT EXISTS tool_authorization_evidence (
    evidence_id TEXT PRIMARY KEY,
    step_id TEXT NOT NULL,
    invocation_id TEXT,
    tool_name TEXT NOT NULL,
    scope TEXT NOT NULL,
    capability_class TEXT NOT NULL,
    authorized INTEGER NOT NULL CHECK (authorized IN (0, 1)),
    policy_id TEXT NOT NULL,
    reason TEXT NOT NULL,
    UNIQUE (evidence_id)
)
"""


@dataclass(frozen=True)
class StoredToolAuthorizationEvidence:
    """Evidence plus its stable persistence identifier."""

    evidence_id: str
    evidence: ToolAuthorizationEvidence


class ToolAuthorizationEvidenceStore:
    """Persist and retrieve immutable authorization evidence snapshots."""

    def __init__(self, database_path: str | Path = "data/processed/jarvis.db") -> None:
        self._database_path = Path(database_path)
        self._database_path.parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as connection:
            connection.execute(_SCHEMA)

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self._database_path)
        connection.execute("PRAGMA foreign_keys = ON")
        return connection

    @staticmethod
    def _evidence_id(evidence: ToolAuthorizationEvidence) -> str:
        payload = json.dumps(
            evidence.to_record(),
            sort_keys=True,
            separators=(",", ":"),
        )
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    def save(self, evidence: ToolAuthorizationEvidence) -> StoredToolAuthorizationEvidence:
        if not isinstance(evidence, ToolAuthorizationEvidence):
            raise TypeError("evidence must be a ToolAuthorizationEvidence")

        evidence_id = self._evidence_id(evidence)
        record = evidence.to_record()

        with self._connect() as connection:
            connection.execute(
                """
                INSERT OR IGNORE INTO tool_authorization_evidence (
                    evidence_id, step_id, invocation_id, tool_name, scope,
                    capability_class, authorized, policy_id, reason
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    evidence_id,
                    record["step_id"],
                    record["invocation_id"],
                    record["tool_name"],
                    record["scope"],
                    record["capability_class"],
                    int(record["authorized"]),
                    record["policy_id"],
                    record["reason"],
                ),
            )

        return StoredToolAuthorizationEvidence(evidence_id, evidence)

    def get(self, evidence_id: str) -> StoredToolAuthorizationEvidence | None:
        if not isinstance(evidence_id, str) or not evidence_id.strip():
            raise ValueError("evidence_id must be a non-empty string")

        with self._connect() as connection:
            row = connection.execute(
                """
                SELECT evidence_id, step_id, invocation_id, tool_name, scope,
                       capability_class, authorized, policy_id, reason
                FROM tool_authorization_evidence
                WHERE evidence_id = ?
                """,
                (evidence_id,),
            ).fetchone()

        if row is None:
            return None

        evidence = ToolAuthorizationEvidence(
            step_id=row[1],
            invocation_id=row[2],
            tool_name=row[3],
            scope=row[4],
            capability_class=row[5],
            authorized=bool(row[6]),
            policy_id=row[7],
            reason=row[8],
        )
        return StoredToolAuthorizationEvidence(row[0], evidence)

    def list_for_step(self, step_id: str) -> tuple[StoredToolAuthorizationEvidence, ...]:
        if not isinstance(step_id, str) or not step_id.strip():
            raise ValueError("step_id must be a non-empty string")

        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT evidence_id, step_id, invocation_id, tool_name, scope,
                       capability_class, authorized, policy_id, reason
                FROM tool_authorization_evidence
                WHERE step_id = ?
                ORDER BY evidence_id
                """,
                (step_id,),
            ).fetchall()

        return tuple(
            StoredToolAuthorizationEvidence(
                row[0],
                ToolAuthorizationEvidence(
                    step_id=row[1],
                    invocation_id=row[2],
                    tool_name=row[3],
                    scope=row[4],
                    capability_class=row[5],
                    authorized=bool(row[6]),
                    policy_id=row[7],
                    reason=row[8],
                ),
            )
            for row in rows
        )

    def all(self) -> tuple[StoredToolAuthorizationEvidence, ...]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT evidence_id, step_id, invocation_id, tool_name, scope,
                       capability_class, authorized, policy_id, reason
                FROM tool_authorization_evidence
                ORDER BY evidence_id
                """
            ).fetchall()

        return tuple(
            StoredToolAuthorizationEvidence(
                row[0],
                ToolAuthorizationEvidence(
                    step_id=row[1],
                    invocation_id=row[2],
                    tool_name=row[3],
                    scope=row[4],
                    capability_class=row[5],
                    authorized=bool(row[6]),
                    policy_id=row[7],
                    reason=row[8],
                ),
            )
            for row in rows
        )
