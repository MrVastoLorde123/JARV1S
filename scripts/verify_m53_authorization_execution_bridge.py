"""Repository-local M53 authorization-execution bridge contract verification."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.agency.authorization_decision import AuthorizationDecision, AuthorizationDisposition
from src.agency.authorization_execution_bridge import create_authorization_execution_bridge
from src.context.execution_semantics import ExecutionPreparation, ExecutionPreparationStatus, ExecutionRequest

authorization = AuthorizationDecision(
    "verify:authorization",
    "verify:confirmation-result",
    "verify:confirmation",
    AuthorizationDisposition.GRANTED,
    "explicit grant",
)

request = ExecutionRequest(
    execution_id="verify:execution",
    request="Perform approved operation",
    proposal_id="verify:proposal",
    validation_id="verify:validation",
    policy_decision_id="verify:policy",
    confirmation_id="verify:confirmation",
    authorization_id="verify:authorization",
    operation="approved_operation",
)
preparation = ExecutionPreparation(
    request="Perform approved operation",
    execution_id="verify:execution",
    status=ExecutionPreparationStatus.READY,
    execution_request=request,
)

bridge = create_authorization_execution_bridge(authorization, preparation)
payload = bridge.to_context()
assert payload["authorization_id"] == "verify:authorization"
assert payload["execution_id"] == "verify:execution"
assert payload["authorization_created"] is False
assert payload["execution_prepared"] is False
assert payload["execution_requested"] is False
assert payload["execution_performed"] is False

print("M53 authorization-execution bridge contract: PASS")
