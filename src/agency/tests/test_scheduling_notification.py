from unittest import TestCase

from src.agency.proactive_proposal import ProactiveProposal, ProactiveProposalSet
from src.agency.scheduling_notification import (
    SchedulingNotificationKind,
    SchedulingNotificationProposal,
    build_scheduling_notification_proposal_set,
)


class M50SchedulingNotificationTests(TestCase):
    def _source(self) -> ProactiveProposalSet:
        return ProactiveProposalSet(
            "source:set",
            "eval:set",
            (
                ProactiveProposal(
                    "source:proposal",
                    "eval:set",
                    "Consider gathering evidence.",
                    "Could reduce uncertainty.",
                    candidate_id="candidate:1",
                    unresolved_uncertainties=("uncertainty:1",),
                ),
            ),
            ("uncertainty:1",),
        )

    def test_scheduling_proposal_is_not_execution(self) -> None:
        proposal = SchedulingNotificationProposal(
            "schedule:1",
            "source:set",
            "Consider scheduling evidence gathering.",
            SchedulingNotificationKind.SCHEDULE,
            "Bounded scheduling consideration.",
            scheduled_for="2026-09-18T12:00:00+00:00",
            candidate_id="candidate:1",
            unresolved_uncertainties=("uncertainty:1",),
        )
        payload = build_scheduling_notification_proposal_set(
            self._source(),
            proposal_set_id="schedule:set",
            proposals=(proposal,),
        ).to_context()
        self.assertEqual(payload["proposal_count"], 1)
        self.assertFalse(payload["scheduling_requested"])
        self.assertFalse(payload["notification_requested"])
        self.assertFalse(payload["authorization_requested"])
        self.assertFalse(payload["execution_requested"])

    def test_source_identity_must_match(self) -> None:
        proposal = SchedulingNotificationProposal(
            "schedule:1",
            "wrong:set",
            "Consider scheduling evidence gathering.",
            SchedulingNotificationKind.SCHEDULE,
            "Bounded scheduling consideration.",
        )
        with self.assertRaises(ValueError):
            build_scheduling_notification_proposal_set(
                self._source(), proposal_set_id="schedule:set", proposals=(proposal,)
            )

    def test_unknown_uncertainty_is_rejected(self) -> None:
        proposal = SchedulingNotificationProposal(
            "schedule:1",
            "source:set",
            "Consider notifying the user.",
            SchedulingNotificationKind.NOTIFY,
            "Bounded notification consideration.",
            unresolved_uncertainties=("unknown",),
        )
        with self.assertRaises(ValueError):
            build_scheduling_notification_proposal_set(
                self._source(), proposal_set_id="schedule:set", proposals=(proposal,)
            )

    def test_time_bounds_are_validated(self) -> None:
        with self.assertRaises(ValueError):
            SchedulingNotificationProposal(
                "schedule:1",
                "source:set",
                "Consider scheduling.",
                SchedulingNotificationKind.SCHEDULE,
                "Bounded scheduling consideration.",
                earliest_at="2026-09-20T12:00:00+00:00",
                latest_at="2026-09-19T12:00:00+00:00",
            )


if __name__ == "__main__":
    import unittest

    unittest.main()
