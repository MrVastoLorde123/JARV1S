"""OPS-08 durable fenced scheduler state."""
from __future__ import annotations

from src.database import get_connection
from src.runtime.autonomous_runtime_scheduler import (
    AutonomousRuntimeSchedule,
    AutonomousRuntimeScheduleStore,
    scheduler_claim_token,
    scheduler_lease_expired,
)


class SQLiteAutonomousRuntimeScheduleStore(AutonomousRuntimeScheduleStore):
    """SQLite-backed scheduler store with lease and completion fencing."""

    _TABLE_SQL = """
        CREATE TABLE IF NOT EXISTS autonomous_runtime_schedules (
            job_id TEXT PRIMARY KEY,
            next_due REAL NOT NULL,
            interval REAL NOT NULL,
            claim_token TEXT,
            lease_until REAL,
            failure_count INTEGER NOT NULL DEFAULT 0,
            last_failure TEXT,
            last_failure_at REAL,
            CHECK ((claim_token IS NULL) = (lease_until IS NULL)),
            CHECK ((last_failure IS NULL) = (last_failure_at IS NULL))
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

    @staticmethod
    def _row_to_schedule(row) -> AutonomousRuntimeSchedule:
        return AutonomousRuntimeSchedule(
            job_id=row[0],
            next_due=row[1],
            interval=row[2],
            claim_token=row[3],
            lease_until=row[4],
            failure_count=row[5],
            last_failure=row[6],
            last_failure_at=row[7],
        )

    def save(self, schedule: AutonomousRuntimeSchedule) -> None:
        if not isinstance(schedule, AutonomousRuntimeSchedule):
            raise TypeError("schedule must be an AutonomousRuntimeSchedule")
        connection = self._connection_factory()
        try:
            connection.execute(
                """
                INSERT INTO autonomous_runtime_schedules
                    (job_id, next_due, interval, claim_token, lease_until,
                     failure_count, last_failure, last_failure_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(job_id) DO UPDATE SET
                    next_due = excluded.next_due,
                    interval = excluded.interval,
                    claim_token = excluded.claim_token,
                    lease_until = excluded.lease_until,
                    failure_count = excluded.failure_count,
                    last_failure = excluded.last_failure,
                    last_failure_at = excluded.last_failure_at
                """,
                (
                    schedule.job_id,
                    schedule.next_due,
                    schedule.interval,
                    schedule.claim_token,
                    schedule.lease_until,
                    schedule.failure_count,
                    schedule.last_failure,
                    schedule.last_failure_at,
                ),
            )
            connection.commit()
        finally:
            connection.close()

    def list_all(self, *, limit: int = 500) -> tuple[AutonomousRuntimeSchedule, ...]:
        if isinstance(limit, bool) or not isinstance(limit, int) or not 1 <= limit <= 500:
            raise ValueError("limit must be an integer from 1 to 500")
        connection = self._connection_factory()
        try:
            rows = connection.execute(
                """
                SELECT job_id, next_due, interval, claim_token, lease_until,
                       failure_count, last_failure, last_failure_at
                FROM autonomous_runtime_schedules
                ORDER BY next_due ASC, job_id ASC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()
            return tuple(self._row_to_schedule(row) for row in rows)
        finally:
            connection.close()

    def delete(self, job_id: str) -> bool:
        if not isinstance(job_id, str) or not job_id.strip():
            raise ValueError("job_id must be a non-empty string")
        connection = self._connection_factory()
        try:
            cursor = connection.execute(
                "DELETE FROM autonomous_runtime_schedules WHERE job_id = ?",
                (job_id,),
            )
            connection.commit()
            return cursor.rowcount == 1
        finally:
            connection.close()

    def load_due(self, now: float) -> list[AutonomousRuntimeSchedule]:
        connection = self._connection_factory()
        try:
            rows = connection.execute(
                """
                SELECT job_id, next_due, interval, claim_token, lease_until,
                       failure_count, last_failure, last_failure_at
                FROM autonomous_runtime_schedules
                WHERE next_due <= ?
                ORDER BY next_due ASC, job_id ASC
                """,
                (now,),
            ).fetchall()
            return [self._row_to_schedule(row) for row in rows]
        finally:
            connection.close()

    def claim(
        self,
        schedule: AutonomousRuntimeSchedule,
        now: float,
        lease_seconds: float,
    ) -> str | None:
        if not isinstance(schedule, AutonomousRuntimeSchedule):
            raise TypeError("schedule must be an AutonomousRuntimeSchedule")
        connection = self._connection_factory()
        token = scheduler_claim_token(schedule.job_id, now, lease_seconds)
        lease_until = now + lease_seconds
        try:
            connection.execute("BEGIN IMMEDIATE")
            row = connection.execute(
                "SELECT claim_token, lease_until FROM autonomous_runtime_schedules WHERE job_id = ?",
                (schedule.job_id,),
            ).fetchone()
            if row is None:
                connection.rollback()
                return None
            active_token, active_lease_until = row
            if active_token is not None and not scheduler_lease_expired(active_lease_until, now):
                connection.rollback()
                return None
            connection.execute(
                """
                UPDATE autonomous_runtime_schedules
                SET claim_token = ?, lease_until = ?
                WHERE job_id = ?
                """,
                (token, lease_until, schedule.job_id),
            )
            connection.commit()
            return token
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    def complete_claim(
        self,
        schedule: AutonomousRuntimeSchedule,
        claim_token: str,
        replacement: AutonomousRuntimeSchedule | None,
    ) -> bool:
        if not isinstance(schedule, AutonomousRuntimeSchedule):
            raise TypeError("schedule must be an AutonomousRuntimeSchedule")
        if not isinstance(claim_token, str) or not claim_token.strip():
            raise ValueError("claim_token must be a non-empty string")
        if replacement is not None and not isinstance(replacement, AutonomousRuntimeSchedule):
            raise TypeError("replacement must be an AutonomousRuntimeSchedule or None")

        connection = self._connection_factory()
        try:
            connection.execute("BEGIN IMMEDIATE")
            if replacement is None:
                cursor = connection.execute(
                    "DELETE FROM autonomous_runtime_schedules WHERE job_id = ? AND claim_token = ?",
                    (schedule.job_id, claim_token),
                )
            else:
                cursor = connection.execute(
                    """
                    UPDATE autonomous_runtime_schedules
                    SET next_due = ?, interval = ?, claim_token = ?, lease_until = ?,
                        failure_count = ?, last_failure = ?, last_failure_at = ?
                    WHERE job_id = ? AND claim_token = ?
                    """,
                    (
                        replacement.next_due,
                        replacement.interval,
                        replacement.claim_token,
                        replacement.lease_until,
                        replacement.failure_count,
                        replacement.last_failure,
                        replacement.last_failure_at,
                        schedule.job_id,
                        claim_token,
                    ),
                )
            success = cursor.rowcount == 1
            if success:
                connection.commit()
            else:
                connection.rollback()
            return success
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()


__all__ = ["SQLiteAutonomousRuntimeScheduleStore"]
