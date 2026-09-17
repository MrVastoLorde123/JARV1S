"""Repository-local M50 scheduling-notification contract verification."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.agency.proactive_proposal import ProactiveProposal, ProactiveProposalSet
from src.agency.scheduling_notification import (
    SchedulingNotificationKind,
    SchedulingNotificationProposal,
    build_scheduling_notification_proposal_set,
)


source = ProactiveProposalSet(
    "verify:source",
    "verify:eval",
    (
        ProactiveProposal(
            "verify:proposal",
            "verify:eval",
            "Consider gathering evidence.",
            "Could reduce uncertainty.",
            candidate_id="verify:candidate",
            unresolved_uncertainties=("verify:uncertainty",),
        ),
    ),
    ("verify:uncertainty",),
)

result = build_scheduling_notification_proposal_set(
    source,
    proposal_set_id="verify:scheduling",
    proposals=(
        SchedulingNotificationProposal(
            "verify:schedule",
            "verify:source",
            "Consider scheduling evidence gathering.",
            SchedulingNotificationKind.SCHEDULE,
            "Bounded scheduling consideration.",
            scheduled_for="2026-09-18T12:00:00+00:00",
            candidate_id="verify:candidate",
            unresolved_uncertainties=("verify:uncertainty",),
        ),
    ),
)

payload = result.to_context()
assert payload["proposal_count"] == 1
assert payload["truth_established"] is False
assert payload["intent_established"] is False
assert payload["authority_granted"] is False
assert payload["scheduling_requested"] is False
assert payload["notification_requested"] is False
assert payload["authorization_requested"] is False
assert payload["execution_requested"] is False
print("M50 scheduling-notification contract: PASS")
