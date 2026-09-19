"""OPS-08 durable SQLite persistence for autonomous job snapshots."""
from __future__ import annotations

import hashlib
import json

from src.database import get_connection
from src.runtime.autonomous_job import (
    AutonomousJob,
    AutonomousJobEvent,
    AutonomousJobEventKind,
    AutonomousJobStatus,
    AutonomousJobStep,
    AutonomousJobValidationError,
)
from src.runtime.autonomous_job_persistence import AutonomousJobStore


class SQLiteAutonomousJobStore(AutonomousJobStore):
    """Persist complete autonomous-job snapshots with revision integrity."""

    _TABLE_SQL = """
        CREATE TABLE IF NOT EXISTS autonomous_jobs (
            job_id TEXT PRIMARY KEY,
            snapshot_json TEXT NOT NULL,
            revision TEXT NOT NULL
        )
    """

    def __init__(self, connection_factory=get_connection) -> None:
        if not callable(connection_factory):
            raise TypeError("connection_factory must be callable")
        self._connection_factory = connection_factory
        self._ensure_schema()

    def _ensure_schema(self) -> None:
        connection = self._connection_factory()
        try:
            connection.execute(self._TABLE_SQL)
            connection.commit()
        finally:
            connection.close()

    def save(self, job: AutonomousJob) -> str:
        if not isinstance(job, AutonomousJob):
            raise TypeError("job must be an AutonomousJob")
        snapshot_json = json.dumps(job.to_dict(), sort_keys=True, separators=(",", ":"))
        revision = self._revision(snapshot_json)
        connection = self._connection_factory()
        try:
            connection.execute(
                """
                INSERT INTO autonomous_jobs (job_id, snapshot_json, revision)
                VALUES (?, ?, ?)
                ON CONFLICT(job_id) DO UPDATE SET
                    snapshot_json = excluded.snapshot_json,
                    revision = excluded.revision
                """,
                (job.job_id, snapshot_json, revision),
            )
            connection.commit()
            return revision
        finally:
            connection.close()

    def list_jobs(self, *, limit: int = 100) -> tuple[AutonomousJob, ...]:
        if isinstance(limit, bool) or not isinstance(limit, int) or not 1 <= limit <= 500:
            raise ValueError("limit must be an integer from 1 to 500")
        connection = self._connection_factory()
        try:
            rows = connection.execute(
                """
                SELECT snapshot_json, revision
                FROM autonomous_jobs
                ORDER BY rowid DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()
        finally:
            connection.close()

        jobs: list[AutonomousJob] = []
        for snapshot_json, revision in rows:
            if revision != self._revision(snapshot_json):
                raise AutonomousJobValidationError(
                    "stored autonomous-job revision does not match snapshot"
                )
            try:
                snapshot = json.loads(snapshot_json)
                job = self._from_dict(snapshot)
            except (KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
                raise AutonomousJobValidationError(
                    "stored autonomous-job snapshot is invalid"
                ) from exc
            jobs.append(job)
        return tuple(jobs)

    def load(self, job_id: str) -> AutonomousJob | None:
        if not isinstance(job_id, str) or not job_id.strip():
            raise ValueError("job_id must be a non-empty string")
        connection = self._connection_factory()
        try:
            row = connection.execute(
                "SELECT snapshot_json, revision FROM autonomous_jobs WHERE job_id = ?",
                (job_id,),
            ).fetchone()
        finally:
            connection.close()
        if row is None:
            return None
        snapshot_json, revision = row
        if revision != self._revision(snapshot_json):
            raise AutonomousJobValidationError(
                "stored autonomous-job revision does not match snapshot"
            )
        try:
            snapshot = json.loads(snapshot_json)
            job = self._from_dict(snapshot)
        except (KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
            raise AutonomousJobValidationError(
                "stored autonomous-job snapshot is invalid"
            ) from exc
        if job.job_id != job_id:
            raise AutonomousJobValidationError(
                "stored autonomous-job snapshot has a different identity"
            )
        return job

    @staticmethod
    def _revision(snapshot_json: str) -> str:
        digest = hashlib.sha256(snapshot_json.encode("utf-8")).hexdigest()[:24]
        return f"autonomous-job-revision-{digest}"

    @staticmethod
    def _from_dict(snapshot: object) -> AutonomousJob:
        if not isinstance(snapshot, dict):
            raise AutonomousJobValidationError("stored autonomous-job snapshot must be an object")
        raw_steps = snapshot.get("steps", [])
        raw_events = snapshot.get("events", [])
        if not isinstance(raw_steps, list) or not isinstance(raw_events, list):
            raise AutonomousJobValidationError("stored autonomous-job steps/events must be arrays")

        steps = tuple(
            AutonomousJobStep(
                step_id=item["step_id"],
                job_id=item["job_id"],
                sequence=item["sequence"],
                phase=item["phase"],
                summary=item["summary"],
                observation=item.get("observation", ""),
                context_delta=item.get("context_delta", {}),
            )
            for item in raw_steps
            if isinstance(item, dict)
        )
        if len(steps) != len(raw_steps):
            raise AutonomousJobValidationError("stored autonomous-job steps contain an invalid entry")

        events = tuple(
            AutonomousJobEvent(
                event_id=item["event_id"],
                job_id=item["job_id"],
                sequence=item["sequence"],
                kind=AutonomousJobEventKind(item["kind"]),
                summary=item["summary"],
                metadata=item.get("metadata", {}),
            )
            for item in raw_events
            if isinstance(item, dict)
        )
        if len(events) != len(raw_events):
            raise AutonomousJobValidationError("stored autonomous-job events contain an invalid entry")

        return AutonomousJob(
            job_id=snapshot["job_id"],
            goal=snapshot["goal"],
            status=AutonomousJobStatus(snapshot["status"]),
            step_count=snapshot["step_count"],
            max_steps=snapshot["max_steps"],
            steps=steps,
            events=events,
            working_context=snapshot.get("working_context", {}),
            waiting_reason=snapshot.get("waiting_reason"),
            result=snapshot.get("result"),
            failure_reason=snapshot.get("failure_reason"),
        )


__all__ = ["SQLiteAutonomousJobStore"]
