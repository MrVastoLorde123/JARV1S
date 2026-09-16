"""Durable storage for post-execution verification evidence.

The store persists verification decisions as evidence only. It does not
execute tools, authorize requests, confirm intent, or independently decide
whether a result is verified. Integrity is content-addressed so tampering is
rejected instead of silently becoming trusted state.
"""

from __future__ import annotations

import hashlib
import json
import sqlite3
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterator, Mapping

from src.core.tool_execution_verification import (
    ToolExecutionVerification,
    ToolVerificationStatus,
)
from src.tools.models import ToolError, ToolRequest, ToolResult


_SCHEMA = """
CREATE TABLE IF NOT EXISTS tool_execution_verification_evidence (
    evidence_id TEXT PRIMARY KEY,
    tool_name TEXT NOT NULL,
    invocation_id TEXT,
    status TEXT NOT NULL,
    evidence TEXT NOT NULL,
    reason TEXT NOT NULL,
    request_json TEXT NOT NULL,
    result_json TEXT NOT NULL,
    UNIQUE (evidence_id)
)
"""


@dataclass(frozen=True)
class StoredToolExecutionVerification:
    """Verification plus its stable persistence identifier."""

    evidence_id: str
    verification: ToolExecutionVerification


def _json_native(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {str(key): _json_native(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_native(item) for item in value]
    if isinstance(value, set | frozenset):
        return sorted(_json_native(item) for item in value)
    if isinstance(value, ToolError):
        return {
            "code": value.code,
            "message": value.message,
            "details": _json_native(value.details),
        }
    if isinstance(value, ToolVerificationStatus):
        return value.value
    return value


def _request_record(request: ToolRequest) -> dict[str, Any]:
    return {
        "tool_name": request.tool_name,
        "arguments": _json_native(request.arguments),
        "metadata": _json_native(request.metadata),
        "invocation_id": request.invocation_id,
    }


def _result_record(result: ToolResult) -> dict[str, Any]:
    return {
        "success": result.success,
        "tool_name": result.tool_name,
        "content": _json_native(result.content),
        "metadata": _json_native(result.metadata),
        "error": _json_native(result.error),
        "invocation_id": result.invocation_id,
    }


def _canonical_json(value: Any) -> str:
    return json.dumps(
        _json_native(value),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )


class ToolExecutionVerificationEvidenceStore:
    """Persist and retrieve immutable verification evidence snapshots."""

    def __init__(self, database_path: str | Path = "data/processed/jarvis.db") -> None:
        self._database_path = Path(database_path)
        self._database_path.parent.mkdir(parents=True, exist_ok=True)
        with self._connection() as connection:
            connection.execute(_SCHEMA)

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self._database_path)
        connection.execute("PRAGMA foreign_keys = ON")
        return connection

    @contextmanager
    def _connection(self) -> Iterator[sqlite3.Connection]:
        connection = self._connect()
        try:
            yield connection
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    @staticmethod
    def _payload(verification: ToolExecutionVerification) -> dict[str, Any]:
        request = _request_record(verification.request)
        result = _result_record(verification.result)
        return {
            "tool_name": verification.request.tool_name,
            "invocation_id": verification.request.invocation_id,
            "status": verification.status.value,
            "evidence": verification.evidence,
            "reason": verification.reason,
            "request": request,
            "result": result,
        }

    @classmethod
    def _evidence_id(cls, verification: ToolExecutionVerification) -> str:
        payload = _canonical_json(cls._payload(verification))
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    @classmethod
    def _row_to_stored(cls, row: tuple[object, ...]) -> StoredToolExecutionVerification:
        request_record = json.loads(row[6])
        result_record = json.loads(row[7])
        error = result_record.get("error")
        tool_error = (
            ToolError(
                code=error["code"],
                message=error["message"],
                details=error.get("details", {}),
            )
            if error is not None
            else None
        )
        request = ToolRequest(
            tool_name=request_record["tool_name"],
            arguments=request_record.get("arguments", {}),
            metadata=request_record.get("metadata", {}),
            invocation_id=request_record.get("invocation_id"),
        )
        result = ToolResult(
            success=result_record["success"],
            tool_name=result_record["tool_name"],
            content=result_record.get("content"),
            metadata=result_record.get("metadata", {}),
            error=tool_error,
            invocation_id=result_record.get("invocation_id"),
        )
        verification = ToolExecutionVerification(
            request=request,
            result=result,
            status=ToolVerificationStatus(row[3]),
            evidence=row[4],
            reason=row[5],
        )
        stored = StoredToolExecutionVerification(row[0], verification)
        cls._validate_integrity(stored.evidence_id, stored.verification)
        return stored

    @classmethod
    def _validate_integrity(
        cls,
        evidence_id: str,
        verification: ToolExecutionVerification,
    ) -> None:
        expected = cls._evidence_id(verification)
        if evidence_id != expected:
            raise ValueError(
                "stored tool execution verification failed integrity validation"
            )

    def save(
        self,
        verification: ToolExecutionVerification,
    ) -> StoredToolExecutionVerification:
        if not isinstance(verification, ToolExecutionVerification):
            raise TypeError("verification must be a ToolExecutionVerification")

        evidence_id = self._evidence_id(verification)
        payload = self._payload(verification)
        request_json = _canonical_json(payload["request"])
        result_json = _canonical_json(payload["result"])

        with self._connection() as connection:
            connection.execute(
                """
                INSERT OR IGNORE INTO tool_execution_verification_evidence (
                    evidence_id, tool_name, invocation_id, status, evidence,
                    reason, request_json, result_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    evidence_id,
                    payload["tool_name"],
                    payload["invocation_id"],
                    payload["status"],
                    payload["evidence"],
                    payload["reason"],
                    request_json,
                    result_json,
                ),
            )

        return StoredToolExecutionVerification(evidence_id, verification)

    def get(self, evidence_id: str) -> StoredToolExecutionVerification | None:
        if not isinstance(evidence_id, str) or not evidence_id.strip():
            raise ValueError("evidence_id must be a non-empty string")
        with self._connection() as connection:
            row = connection.execute(
                """
                SELECT evidence_id, tool_name, invocation_id, status, evidence,
                       reason, request_json, result_json
                FROM tool_execution_verification_evidence
                WHERE evidence_id = ?
                """,
                (evidence_id,),
            ).fetchone()
        if row is None:
            return None
        return self._row_to_stored(row)

    def list_for_invocation(
        self,
        invocation_id: str,
    ) -> tuple[StoredToolExecutionVerification, ...]:
        if not isinstance(invocation_id, str) or not invocation_id.strip():
            raise ValueError("invocation_id must be a non-empty string")
        with self._connection() as connection:
            rows = connection.execute(
                """
                SELECT evidence_id, tool_name, invocation_id, status, evidence,
                       reason, request_json, result_json
                FROM tool_execution_verification_evidence
                WHERE invocation_id = ?
                ORDER BY evidence_id
                """,
                (invocation_id,),
            ).fetchall()
        return tuple(self._row_to_stored(row) for row in rows)

    def all(self) -> tuple[StoredToolExecutionVerification, ...]:
        with self._connection() as connection:
            rows = connection.execute(
                """
                SELECT evidence_id, tool_name, invocation_id, status, evidence,
                       reason, request_json, result_json
                FROM tool_execution_verification_evidence
                ORDER BY evidence_id
                """
            ).fetchall()
        return tuple(self._row_to_stored(row) for row in rows)
