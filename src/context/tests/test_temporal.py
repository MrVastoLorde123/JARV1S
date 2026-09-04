import json
import unittest

from src.context.temporal import (
    MAX_HISTORY_ITEMS,
    MAX_QUERY_RESULTS,
    TemporalContext,
    TemporalContextValidationError,
)
from src.context.world_state import ContextState


class TemporalContextTests(unittest.TestCase):
    def snapshot(self, context_id, observed_at, **state):
        return ContextState(
            context_id=context_id,
            state=state,
            source_refs=(f"source-{context_id}",),
            observed_at=observed_at,
        )

    def history(self):
        return TemporalContext(
            snapshots=(
                self.snapshot("ctx-1", "2026-01-01T10:00:00+00:00", status="old"),
                self.snapshot("ctx-2", "2026-01-02T10:00:00+00:00", status="middle"),
                self.snapshot("ctx-3", "2026-01-03T10:00:00+00:00", status="current"),
            )
        )

    def test_empty_history_is_valid(self):
        self.assertIsNone(TemporalContext().latest)

    def test_historical_snapshots_require_observed_at(self):
        snapshot = ContextState(context_id="ctx-1", state={})
        with self.assertRaises(TemporalContextValidationError):
            TemporalContext(snapshots=(snapshot,))

    def test_snapshots_must_be_ordered(self):
        first = self.snapshot("ctx-1", "2026-01-02T00:00:00+00:00")
        second = self.snapshot("ctx-2", "2026-01-01T00:00:00+00:00")
        with self.assertRaises(TemporalContextValidationError):
            TemporalContext(snapshots=(first, second))

    def test_duplicate_snapshot_ids_are_rejected(self):
        first = self.snapshot("ctx-1", "2026-01-01T00:00:00+00:00")
        second = self.snapshot("ctx-1", "2026-01-02T00:00:00+00:00")
        with self.assertRaises(TemporalContextValidationError):
            TemporalContext(snapshots=(first, second))

    def test_append_returns_new_history(self):
        history = self.history()
        snapshot = self.snapshot("ctx-4", "2026-01-04T00:00:00+00:00")
        updated = history.append(snapshot)
        self.assertEqual(len(history.snapshots), 3)
        self.assertEqual(len(updated.snapshots), 4)
        self.assertIs(updated.latest, snapshot)

    def test_between_is_inclusive_and_ordered(self):
        matches = self.history().between(
            "2026-01-02T00:00:00+00:00",
            "2026-01-03T10:00:00+00:00",
        )
        self.assertEqual(tuple(item.context_id for item in matches), ("ctx-2", "ctx-3"))

    def test_before_returns_recent_history_first(self):
        matches = self.history().before("2026-01-03T12:00:00+00:00", limit=2)
        self.assertEqual(tuple(item.context_id for item in matches), ("ctx-3", "ctx-2"))

    def test_after_returns_forward_history(self):
        matches = self.history().after("2026-01-01T12:00:00+00:00")
        self.assertEqual(tuple(item.context_id for item in matches), ("ctx-2", "ctx-3"))

    def test_invalid_time_range_is_rejected(self):
        with self.assertRaises(TemporalContextValidationError):
            self.history().between(
                "2026-01-03T00:00:00+00:00",
                "2026-01-02T00:00:00+00:00",
            )

    def test_query_limit_is_bounded(self):
        with self.assertRaises(ValueError):
            self.history().after("2026-01-01T00:00:00+00:00", limit=0)
        with self.assertRaises(ValueError):
            self.history().after(
                "2026-01-01T00:00:00+00:00",
                limit=MAX_QUERY_RESULTS + 1,
            )

    def test_history_size_is_bounded(self):
        snapshots = tuple(
            self.snapshot(
                f"ctx-{index}",
                f"2026-01-{(index % 28) + 1:02d}T00:00:00+00:00",
            )
            for index in range(MAX_HISTORY_ITEMS + 1)
        )
        snapshots = tuple(sorted(snapshots, key=lambda item: item.observed_at))
        with self.assertRaises(TemporalContextValidationError):
            TemporalContext(snapshots=snapshots)

    def test_latest_is_last_temporal_snapshot(self):
        self.assertEqual(self.history().latest.context_id, "ctx-3")

    def test_history_is_immutable(self):
        history = self.history()
        with self.assertRaises(AttributeError):
            history.snapshots = ()
        with self.assertRaises(TypeError):
            history.snapshots[0].state["new"] = "value"

    def test_serialization_is_deterministic_and_non_authoritative(self):
        history = self.history()
        first = history.to_json()
        second = history.to_json()
        self.assertEqual(first, second)
        payload = json.loads(first)
        self.assertFalse(payload["truth_guaranteed"])
        self.assertFalse(payload["fact_guaranteed"])
        self.assertFalse(payload["intent_guaranteed"])
        self.assertFalse(payload["authorization_granted"])
        self.assertFalse(payload["policy_authority"])
        self.assertFalse(payload["execution_requested"])
        self.assertEqual(len(payload["snapshots"]), 3)


if __name__ == "__main__":
    unittest.main()
