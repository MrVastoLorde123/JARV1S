from datetime import datetime, timedelta, timezone
import unittest

from src.proactive.scheduling import (
    NotificationChannel,
    ProactiveScheduleProposal,
    SchedulingEvaluation,
    SchedulingStatus,
    propose_schedule,
    rank_schedule_proposals,
)


class SchedulingBoundaryTests(unittest.TestCase):
    def setUp(self) -> None:
        self.now = datetime(2026, 9, 5, 12, 0, tzinfo=timezone.utc)
        self.later = self.now + timedelta(hours=2)

    def test_bounded_schedule_is_proposed_without_side_effects(self) -> None:
        result = propose_schedule(
            "proposal-1",
            scheduled_for=self.later,
            reason="Review the proactive recommendation during the next work window.",
            notification_channel=NotificationChannel.OPERATOR,
            notification_message="Review proposal-1.",
        )
        self.assertIsInstance(result, SchedulingEvaluation)
        self.assertEqual(result.status, SchedulingStatus.PROPOSED)
        self.assertIsNotNone(result.schedule)
        context = result.to_context()
        self.assertFalse(context["scheduled"])
        self.assertFalse(context["notification_sent"])

    def test_schedule_requires_timezone_aware_datetime(self) -> None:
        with self.assertRaises(ValueError):
            propose_schedule(
                "proposal-1",
                scheduled_for=datetime(2026, 9, 5, 14, 0),
                reason="Review later.",
            )

    def test_expiry_cannot_precede_schedule(self) -> None:
        with self.assertRaises(ValueError):
            ProactiveScheduleProposal(
                proposal_id="proposal-1",
                scheduled_for=self.later,
                reason="Review later.",
                expires_at=self.now,
            )

    def test_notification_message_requires_channel(self) -> None:
        with self.assertRaises(ValueError):
            ProactiveScheduleProposal(
                proposal_id="proposal-1",
                scheduled_for=self.later,
                reason="Review later.",
                notification_message="Review proposal-1.",
            )

    def test_notification_channel_requires_message(self) -> None:
        with self.assertRaises(ValueError):
            ProactiveScheduleProposal(
                proposal_id="proposal-1",
                scheduled_for=self.later,
                reason="Review later.",
                notification_channel=NotificationChannel.MESSAGE,
            )

    def test_schedule_rejects_authority_and_execution(self) -> None:
        with self.assertRaises(SchedulingError):
            ProactiveScheduleProposal(
                proposal_id="proposal-1",
                scheduled_for=self.later,
                reason="Review later.",
                authorization_granted=True,
            )
        with self.assertRaises(SchedulingError):
            ProactiveScheduleProposal(
                proposal_id="proposal-1",
                scheduled_for=self.later,
                reason="Review later.",
                execution_requested=True,
            )

    def test_inactive_proposal_is_not_schedulable(self) -> None:
        result = propose_schedule(
            "proposal-1",
            scheduled_for=self.later,
            reason="Review later.",
            proposal_active=False,
        )
        self.assertEqual(result.status, SchedulingStatus.NOT_SCHEDULABLE)
        self.assertIsNone(result.schedule)

    def test_schedule_identity_must_match_evaluation(self) -> None:
        schedule = ProactiveScheduleProposal(
            proposal_id="proposal-2",
            scheduled_for=self.later,
            reason="Review later.",
        )
        with self.assertRaises(ValueError):
            SchedulingEvaluation(
                proposal_id="proposal-1",
                status=SchedulingStatus.PROPOSED,
                reason="test",
                schedule=schedule,
            )

    def test_ranking_is_deterministic_by_time_then_id(self) -> None:
        first = propose_schedule(
            "proposal-b",
            scheduled_for=self.later,
            reason="Later review.",
        )
        same_time = propose_schedule(
            "proposal-a",
            scheduled_for=self.later,
            reason="Later review.",
        )
        earlier = propose_schedule(
            "proposal-c",
            scheduled_for=self.now + timedelta(hours=1),
            reason="Earlier review.",
        )
        ranked = rank_schedule_proposals(
            {
                "proposal-b": first,
                "proposal-a": same_time,
                "proposal-c": earlier,
            }
        )
        self.assertEqual(
            tuple(item.proposal_id for item in ranked),
            ("proposal-c", "proposal-a", "proposal-b"),
        )


if __name__ == "__main__":
    unittest.main()
