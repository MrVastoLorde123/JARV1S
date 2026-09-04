"""M14.2 temporal and historical context boundary.

Historical context records bounded ContextState snapshots across time. A
historical observation describes what was recorded at a time; it is not a
truth claim, current-state guarantee, user intent, policy, authorization, or
execution permission.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime
from typing import Iterable

from .world_state import ContextState


class TemporalContextValidationError(ValueError):
    """Raised when temporal context violates the M14.2 boundary."""


MAX_HISTORY_ITEMS = 512
MAX_QUERY_RESULTS = 128


def _parse_timestamp(value: str) -> datetime:
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise TemporalContextValidationError("timestamp must be ISO-8601") from exc


@dataclass(frozen=True)
class TemporalContext:
    """Immutable bounded history of ContextState snapshots."""

    snapshots: tuple[ContextState, ...] = ()

    def __post_init__(self) -> None:
        if not isinstance(self.snapshots, tuple):
            raise TemporalContextValidationError("snapshots must be a tuple")
        if len(self.snapshots) > MAX_HISTORY_ITEMS:
            raise TemporalContextValidationError(
                f"snapshots exceeds maximum count of {MAX_HISTORY_ITEMS}"
            )
        if any(not isinstance(snapshot, ContextState) for snapshot in self.snapshots):
            raise TemporalContextValidationError(
                "snapshots must contain ContextState values"
            )

        seen_ids: set[str] = set()
        timestamps: list[datetime] = []
        for snapshot in self.snapshots:
            if snapshot.context_id in seen_ids:
                raise TemporalContextValidationError(
                    f"duplicate context snapshot id '{snapshot.context_id}'"
                )
            seen_ids.add(snapshot.context_id)
            if snapshot.observed_at is None:
                raise TemporalContextValidationError(
                    "historical snapshots require observed_at"
                )
            timestamps.append(_parse_timestamp(snapshot.observed_at))

        expected_order = tuple(
            snapshot.context_id
            for _, snapshot in sorted(
                zip(timestamps, self.snapshots),
                key=lambda item: (item[0], item[1].context_id),
            )
        )
        actual_order = tuple(snapshot.context_id for snapshot in self.snapshots)
        if actual_order != expected_order:
            raise TemporalContextValidationError(
                "snapshots must be ordered by observed_at, then context_id"
            )

    def append(self, snapshot: ContextState) -> "TemporalContext":
        if not isinstance(snapshot, ContextState):
            raise TypeError("snapshot must be a ContextState")
        return TemporalContext(self.snapshots + (snapshot,))

    def between(
        self,
        start: str,
        end: str,
        *,
        limit: int = MAX_QUERY_RESULTS,
    ) -> tuple[ContextState, ...]:
        start_time = _parse_timestamp(start)
        end_time = _parse_timestamp(end)
        if start_time > end_time:
            raise TemporalContextValidationError("start must not be after end")
        if not isinstance(limit, int) or isinstance(limit, bool):
            raise TypeError("limit must be an integer")
        if not 1 <= limit <= MAX_QUERY_RESULTS:
            raise ValueError(f"limit must be between 1 and {MAX_QUERY_RESULTS}")

        results = tuple(
            snapshot
            for snapshot in self.snapshots
            if start_time <= _parse_timestamp(snapshot.observed_at) <= end_time
        )
        return results[:limit]

    def before(
        self,
        timestamp: str,
        *,
        limit: int = MAX_QUERY_RESULTS,
    ) -> tuple[ContextState, ...]:
        cutoff = _parse_timestamp(timestamp)
        if not isinstance(limit, int) or isinstance(limit, bool):
            raise TypeError("limit must be an integer")
        if not 1 <= limit <= MAX_QUERY_RESULTS:
            raise ValueError(f"limit must be between 1 and {MAX_QUERY_RESULTS}")
        results = tuple(
            snapshot
            for snapshot in self.snapshots
            if _parse_timestamp(snapshot.observed_at) < cutoff
        )
        return results[-limit:]

    def after(
        self,
        timestamp: str,
        *,
        limit: int = MAX_QUERY_RESULTS,
    ) -> tuple[ContextState, ...]:
        cutoff = _parse_timestamp(timestamp)
        if not isinstance(limit, int) or isinstance(limit, bool):
            raise TypeError("limit must be an integer")
        if not 1 <= limit <= MAX_QUERY_RESULTS:
            raise ValueError(f"limit must be between 1 and {MAX_QUERY_RESULTS}")
        results = tuple(
            snapshot
            for snapshot in self.snapshots
            if _parse_timestamp(snapshot.observed_at) > cutoff
        )
        return results[:limit]

    @property
    def latest(self) -> ContextState | None:
        return self.snapshots[-1] if self.snapshots else None

    def to_dict(self) -> dict[str, object]:
        return {
            "snapshots": [snapshot.to_dict() for snapshot in self.snapshots],
            "truth_guaranteed": False,
            "fact_guaranteed": False,
            "intent_guaranteed": False,
            "authorization_granted": False,
            "policy_authority": False,
            "execution_requested": False,
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), sort_keys=True, default=str)
