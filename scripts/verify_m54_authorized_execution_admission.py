"""Repository-local M54 authorized execution admission contract verification."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.agency.authorization_decision import AuthorizationDecision, AuthorizationDisposition
from src.agency.authorization_execution_bridge import create_authorization_execution_bridge
from src.agency.authorized_execution_admission import create_authorized_execution_admission
from src.agency.execution_handoff import create_execution_handoff
from src.agency.work_dispatch import DispatchRequest, WorkDispatcher
from src.agency.work_planning import PlanStepKind, WorkPlanStep, build_work_plan
from src.agency.work_state import WorkRole, WorkStage, WorkState, WorkStatus
from src.agency.workforce import WorkerDefinition, WorkerRegistry
from src.context.authorization_integrity_semantics import AuthorizationIntegrity, AuthorizationIntegrityStatus
from src.context.authorization_semantics import AuthorizationDecision as LegacyAuthorizationDecision, AuthorizationStatus
from src.context.execution_semantics import ExecutionGate

work = WorkState(
    work_id="verify:m54",
    objective="admit authorized execution",
    stage=WorkStage.EXECUTING,
    status=WorkStatus.ACTIVE,
    role=WorkRole.TECHNICAL_LEAD,
)
plan = build_work_plan(
    work,
    (WorkPlanStep("verify:step", "deploy change", PlanStepKind.IMPLEMENT, WorkRole.TECHNICAL_LEAD),),
)
registry = WorkerRegistry()
registry.register(WorkerDefinition("verify:worker", "Worker", ("deploy",), 2))
dispatch = WorkDispatcher(registry).dispatch(
    DispatchRequest(plan, "verify:step", "verify:worker", input_scope=("repo",), output_scope=("result",))
)

legacy = LegacyAuthorizationDecision(
    request="deploy change",
    authorization_id="verify:auth",
    proposal_id="verify:proposal",
    validation_id="verify:validation",
    policy_decision_id="verify:policy",
    confirmation_id="verify:confirmation",
    status=AuthorizationStatus.AUTHORIZED,
    rationale="approved",
)
integrity = AuthorizationIntegrity(
    request="deploy change",
    authorization_id="verify:auth",
    proposal_id="verify:proposal",
    validation_id="verify:validation",
    policy_decision_id="verify:policy",
    confirmation_id="verify:confirmation",
    status=AuthorizationIntegrityStatus.VALID,
)
preparation = ExecutionGate().prepare(legacy, integrity, "verify:execution", "deploy")

agency_authorization = AuthorizationDecision(
    "verify:auth",
    "verify:confirmation-result",
    "verify:confirmation",
    AuthorizationDisposition.GRANTED,
    "explicitly granted",
)
bridge = create_authorization_execution_bridge(agency_authorization, preparation)
handoff = create_execution_handoff(dispatch, preparation)
admission = create_authorized_execution_admission(bridge, handoff)
payload = admission.to_context()

assert admission.authorization_id == agency_authorization.authorization_id
assert admission.execution_id == preparation.execution_id
assert payload["authorization_created"] is False
assert payload["execution_prepared"] is False
assert payload["execution_requested"] is False
assert payload["execution_performed"] is False
print("M54 authorized-execution-admission contract: PASS")
