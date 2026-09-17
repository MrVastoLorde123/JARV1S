"""Repository-local M51 confirmation contract verification."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.agency.confirmation import ConfirmationDisposition, ConfirmationRequest, build_confirmation_result
from src.agency.scheduling_notification import (
    SchedulingNotificationKind,
    SchedulingNotificationProposal,
    SchedulingNotificationProposalSet,
)

proposals = SchedulingNotificationProposalSet(
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

result = build_confirmation_result(
    proposals,
    result_id="verify:result",
    requests=(
        ConfirmationRequest(
            "verify:confirmation",
            "verify:scheduling-set",
            "verify:schedule-proposal",
            "Confirm this proposal?",
            disposition=ConfirmationDisposition.CONFIRMED,
            response_text="yes",
            responded_at="2026-09-17T02:10:00+00:00",
        ),
    ),
)

payload = result.to_context()
assert payload["confirmed_ids"] == ("verify:confirmation",)
assert payload["authorization_granted"] is False
assert payload["execution_requested"] is False
print("M51 confirmation contract: PASS")
