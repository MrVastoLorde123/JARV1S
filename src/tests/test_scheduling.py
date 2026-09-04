import json
import unittest

from src.initiative import InitiativeCandidate
from src.evaluation import InitiativeEvaluation
from src.proposals import InitiativeProposal
from src.scheduling import (
    ProactiveSchedule,
    ProactiveScheduleValidationError,
    ScheduleStatus,
)


class ProactiveScheduleTests(unittest.TestCase):
    def setUp(self):
        candidate = InitiativeCandidate("init-1", "Review", "Review project")
        evaluation = InitiativeEvaluation("eval-1", candidate, 0.8, 0.5, 0.9, 0.2, 0.1)
        self.proposal = InitiativeProposal(
            "proposal-1", evaluation, "Review", "Review project", "Surface review"
        )

    def test_valid_schedule(self):
        item = ProactiveSchedule("sched-1", self.proposal, "2026-09-04T10:00:00+00:00")
        self.assertEqual(item.proposal_id, "proposal-1")
        self.assertEqual(item.status, ScheduleStatus.ACTIVE)

    def test_proposal_required(self):
        with self.assertRaises(ProactiveScheduleValidationError):
            ProactiveSchedule("sched-1", "bad", "2026-09-04T10:00:00+00:00")

    def test_timestamp_must_be_iso8601(self):
        with self.assertRaises(ProactiveScheduleValidationError):
            ProactiveSchedule("sched-1", self.proposal, "tomorrow")

    def test_interval_positive(self):
        with self.assertRaises(ProactiveScheduleValidationError):
            ProactiveSchedule("sched-1", self.proposal, "2026-09-04T10:00:00+00:00", interval_minutes=0)

    def test_functional_reschedule(self):
        item = ProactiveSchedule("sched-1", self.proposal, "2026-09-04T10:00:00+00:00")
        updated = item.reschedule("2026-09-05T10:00:00+00:00")
        self.assertEqual(item.next_at, "2026-09-04T10:00:00+00:00")
        self.assertEqual(updated.next_at, "2026-09-05T10:00:00+00:00")

    def test_functional_status_change(self):
        item = ProactiveSchedule("sched-1", self.proposal, "2026-09-04T10:00:00+00:00")
        updated = item.with_status(ScheduleStatus.PAUSED)
        self.assertEqual(item.status, ScheduleStatus.ACTIVE)
        self.assertEqual(updated.status, ScheduleStatus.PAUSED)

    def test_status_values(self):
        for status in ScheduleStatus:
            item = ProactiveSchedule("sched-1", self.proposal, "2026-09-04T10:00:00+00:00", status=status)
            self.assertEqual(item.status, status)

    def test_timezone_bounded(self):
        with self.assertRaises(ProactiveScheduleValidationError):
            ProactiveSchedule("sched-1", self.proposal, "2026-09-04T10:00:00+00:00", timezone="x" * 129)

    def test_metadata_frozen(self):
        item = ProactiveSchedule(
            "sched-1", self.proposal, "2026-09-04T10:00:00+00:00", metadata={"a": {"b": 1}}
        )
        with self.assertRaises(TypeError):
            item.metadata["a"]["b"] = 2

    def test_schedule_is_immutable(self):
        item = ProactiveSchedule("sched-1", self.proposal, "2026-09-04T10:00:00+00:00")
        with self.assertRaises(Exception):
            item.status = ScheduleStatus.PAUSED

    def test_serialization_is_non_authoritative(self):
        data = ProactiveSchedule("sched-1", self.proposal, "2026-09-04T10:00:00+00:00").to_dict()
        self.assertFalse(data["scheduling_is_authorization"])
        self.assertFalse(data["scheduling_is_confirmation"])
        self.assertFalse(data["authorization_granted"])
        self.assertFalse(data["policy_authority"])
        self.assertFalse(data["execution_requested"])

    def test_json_shape(self):
        data = json.loads(ProactiveSchedule("sched-1", self.proposal, "2026-09-04T10:00:00+00:00").to_json())
        self.assertEqual(data["schedule_id"], "sched-1")
        self.assertIsInstance(data, dict)

    def test_metadata_mapping_required(self):
        with self.assertRaises(ProactiveScheduleValidationError):
            ProactiveSchedule("sched-1", self.proposal, "2026-09-04T10:00:00+00:00", metadata="bad")

    def test_interval_integer_required(self):
        with self.assertRaises(ProactiveScheduleValidationError):
            ProactiveSchedule("sched-1", self.proposal, "2026-09-04T10:00:00+00:00", interval_minutes=True)

    def test_timezones_and_interval_preserved(self):
        item = ProactiveSchedule(
            "sched-1", self.proposal, "2026-09-04T10:00:00+00:00", "America/Paramaribo", 60
        )
        updated = item.with_status(ScheduleStatus.PAUSED)
        self.assertEqual(updated.timezone, "America/Paramaribo")
        self.assertEqual(updated.interval_minutes, 60)


if __name__ == "__main__":
    unittest.main()
