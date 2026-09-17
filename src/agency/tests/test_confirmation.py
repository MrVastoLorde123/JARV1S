from unittest import TestCase

from src.agency.confirmation import (
    ConfirmationDisposition,
    ConfirmationRequest,
    build_confirmation_result,
)
from src.agency.scheduling_notification import (
    SchedulingNotificationKind,
    SchedulingNotificationProposal,
    SchedulingNotificationProposalSet,
)


class M51ConfirmationTests(TestCase):
    def _proposals(self):
        return SchedulingNotificationProposalSet(
            "verify:scheduling-set",
            "verify:proactive-set",
            (
                SchedulingNotificationProposal(
                    "verify:schedule-proposal",
                    "verify:proactive-set",
                    "Consider scheduling the task.",
                    SchedulingNotificationKind.SCHEDULE,
                    "bounded confirmation candidate",
                ),
            ),
            ("verify:uncertainty",),
        )

    def test_confirmation_must_reference_supplied_proposal(self):
        with self.assertRaises(ValueError):
            build_confirmation_result(
                self._proposals(),
                result_id="verify:result",
                requests=(
                    ConfirmationRequest(
                        "verify:confirmation",
                        "verify:scheduling-set",
                        "unknown",
                        "Confirm?",
                    ),
                ),
            )

    def test_pending_confirmation_cannot_claim_response(self):
        with self.assertRaises(ValueError):
            build_confirmation_result(
                self._proposals(),
                result_id="verify:result",
                requests=(
                    ConfirmationRequest(
                        "verify:confirmation",
                        "verify:scheduling-set",
                        "verify:schedule-proposal",
                        "Confirm?",
                        response_text="yes",
                    ),
                ),
            )

    def test_confirmed_result_is_still_not_authorization(self):
        result = build_confirmation_result(
            self._proposals(),
            result_id="verify:result",
            requests=(
                ConfirmationRequest(
                    "verify:confirmation",
                    "verify:scheduling-set",
                    "verify:schedule-proposal",
                    "Confirm?",
                    disposition=ConfirmationDisposition.CONFIRMED,
                    response_text="yes",
                    responded_at="2026-09-17T02:10:00+00:00",
                ),
            ),
        )
        payload = result.to_context()
        self.assertEqual(payload["confirmed_ids"], ("verify:confirmation",))
        self.assertFalse(payload["authorization_granted"])
        self.assertFalse(payload["execution_requested"])

    def test_source_identity_must_match(self):
        with self.assertRaises(ValueError):
            build_confirmation_result(
                self._proposals(),
                result_id="verify:result",
                requests=(
                    ConfirmationRequest(
                        "verify:confirmation",
                        "other-set",
                        "verify:schedule-proposal",
                        "Confirm?",
                    ),
                ),
            )
