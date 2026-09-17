from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.agency.authorization_decision import AuthorizationDecision, AuthorizationDisposition, build_authorization_decision_set
from src.agency.confirmation import ConfirmationDisposition, ConfirmationRequest, ConfirmationResult

confirmation = ConfirmationResult(
    "verify:result",
    "verify:proposals",
    (
        ConfirmationRequest(
            "verify:confirmation",
            "verify:proposals",
            "verify:proposal",
            "Confirm this proposal.",
            disposition=ConfirmationDisposition.CONFIRMED,
            response_text="confirmed",
        ),
    ),
)

decision = AuthorizationDecision(
    "verify:authorization",
    "verify:result",
    "verify:confirmation",
    AuthorizationDisposition.GRANTED,
    "explicit confirmation received",
    constraints=("execute only the confirmed operation",),
)

result = build_authorization_decision_set(
    confirmation,
    decision_set_id="verify:decisions",
    decisions=(decision,),
)

payload = result.to_context()
assert payload["authority_granted"] is True
assert payload["permissions_granted"] is True
assert payload["execution_requested"] is False
assert payload["execution_performed"] is False
assert payload["truth_established"] is False
print("M52 authorization contract: PASS")
