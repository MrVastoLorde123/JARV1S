"""SQLite persistence for exact coding-agent confirmation state."""
from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any

from src.agents.coding_confirmation_models import CodingConfirmationStatus, CodingPendingOperation
from src.agents.coding_worker import CodingAgentEdit, CodingAgentPlan, CodingAgentTask, CodingAgentVerification


class CodingConfirmationStore:
    """Persist exact coding confirmations and one-shot invocation consumption."""

    def __init__(self, database_path: str | Path) -> None:
        self._database_path = Path(database_path)
        self._database_path.parent.mkdir(parents=True, exist_ok=True)
        self.ensure_schema()

    @property
    def database_path(self) -> Path:
        return self._database_path

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self._database_path)

    def ensure_schema(self) -> None:
        connection = self._connect()
        try:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS coding_confirmation_operations (
                    operation_id TEXT PRIMARY KEY,
                    task_payload TEXT NOT NULL,
                    plan_payload TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    status TEXT NOT NULL,
                    metadata TEXT NOT NULL DEFAULT '{}'
                )
                """
            )
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS coding_confirmation_consumed_invocations (
                    operation_id TEXT NOT NULL,
                    invocation_id TEXT NOT NULL,
                    PRIMARY KEY (operation_id, invocation_id),
                    FOREIGN KEY (operation_id)
                        REFERENCES coding_confirmation_operations(operation_id)
                        ON DELETE CASCADE
                )
                """
            )
            connection.commit()
        finally:
            connection.close()

    @staticmethod
    def _task_payload(task: CodingAgentTask) -> dict[str, Any]:
        return {
            "objective": task.objective,
            "task_id": task.task_id,
            "metadata": dict(task.metadata),
        }

    @staticmethod
    def _plan_payload(plan: CodingAgentPlan) -> dict[str, Any]:
        return {
            "edits": [
                {
                    "path": edit.path,
                    "content": edit.content,
                    "overwrite": edit.overwrite,
                    "create_parents": edit.create_parents,
                }
                for edit in plan.edits
            ],
            "verification": {
                "runner": plan.verification.runner,
                "arguments": list(plan.verification.arguments),
                "timeout_seconds": plan.verification.timeout_seconds,
            },
            "rationale": plan.rationale,
        }

    def save(self, operation: CodingPendingOperation) -> None:
        if not isinstance(operation, CodingPendingOperation):
            raise TypeError("operation must be a CodingPendingOperation")
        connection = self._connect()
        try:
            connection.execute(
                """
                INSERT INTO coding_confirmation_operations (
                    operation_id, task_payload, plan_payload, created_at, status, metadata
                ) VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(operation_id) DO UPDATE SET
                    task_payload = excluded.task_payload,
                    plan_payload = excluded.plan_payload,
                    created_at = excluded.created_at,
                    status = excluded.status,
                    metadata = excluded.metadata
                """,
                (
                    operation.operation_id,
                    json.dumps(self._task_payload(operation.task), ensure_ascii=False, default=str),
                    json.dumps(self._plan_payload(operation.plan), ensure_ascii=False, default=str),
                    operation.created_at,
                    operation.status.value,
                    json.dumps(operation.metadata, ensure_ascii=False, default=str),
                ),
            )
            connection.commit()
        finally:
            connection.close()

    def mark_invocation_consumed(self, operation_id: str, invocation_id: str) -> None:
        connection = self._connect()
        try:
            connection.execute(
                """
                INSERT OR IGNORE INTO coding_confirmation_consumed_invocations (operation_id, invocation_id)
                VALUES (?, ?)
                """,
                (operation_id, invocation_id),
            )
            connection.commit()
        finally:
            connection.close()

    def clear(self) -> None:
        connection = self._connect()
        try:
            connection.execute("DELETE FROM coding_confirmation_consumed_invocations")
            connection.execute("DELETE FROM coding_confirmation_operations")
            connection.commit()
        finally:
            connection.close()

    def load_operations(self) -> tuple[CodingPendingOperation, ...]:
        connection = self._connect()
        try:
            rows = connection.execute(
                """
                SELECT operation_id, task_payload, plan_payload, created_at, status, metadata
                FROM coding_confirmation_operations
                ORDER BY created_at, operation_id
                """
            ).fetchall()
        finally:
            connection.close()

        operations: list[CodingPendingOperation] = []
        for row in rows:
            task_payload = json.loads(row[1])
            plan_payload = json.loads(row[2])
            metadata = json.loads(row[5])
            task = CodingAgentTask(
                objective=str(task_payload["objective"]),
                task_id=str(task_payload["task_id"]),
                metadata=dict(task_payload.get("metadata", {})),
            )
            edits = tuple(
                CodingAgentEdit(
                    path=str(edit["path"]),
                    content=str(edit["content"]),
                    overwrite=bool(edit.get("overwrite", False)),
                    create_parents=bool(edit.get("create_parents", False)),
                )
                for edit in plan_payload.get("edits", [])
            )
            verification_payload = plan_payload["verification"]
            plan = CodingAgentPlan(
                edits=edits,
                verification=CodingAgentVerification(
                    runner=str(verification_payload["runner"]),
                    arguments=tuple(str(item) for item in verification_payload.get("arguments", [])),
                    timeout_seconds=verification_payload.get("timeout_seconds"),
                ),
                rationale=str(plan_payload.get("rationale", "")),
            )
            operations.append(
                CodingPendingOperation(
                    operation_id=str(row[0]),
                    task=task,
                    plan=plan,
                    created_at=str(row[3]),
                    status=CodingConfirmationStatus(str(row[4])),
                    metadata=dict(metadata) if isinstance(metadata, dict) else {},
                )
            )
        return tuple(operations)

    def load_consumed_invocations(self) -> set[tuple[str, str]]:
        connection = self._connect()
        try:
            rows = connection.execute(
                """
                SELECT operation_id, invocation_id
                FROM coding_confirmation_consumed_invocations
                """
            ).fetchall()
        finally:
            connection.close()
        return {(str(operation_id), str(invocation_id)) for operation_id, invocation_id in rows}


__all__ = ["CodingConfirmationStore"]
