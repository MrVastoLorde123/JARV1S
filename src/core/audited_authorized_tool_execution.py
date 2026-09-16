"""Require durable authorization evidence before tool execution."""

from __future__ import annotations

from src.core.authorized_tool_execution import AuthorizedToolPlanStepHandler
from src.core.execution_plan_models import PlanStep
from src.core.tool_authorization import ToolExecutionAuthorization
from src.core.tool_authorization_evidence_store import ToolAuthorizationEvidenceStore
from src.core.tool_authorization_policy import ToolAuthorizationEvidence, ToolAuthorizationPolicy
from src.core.tool_execution import ToolExecutionConfirmation, ToolInvoker


class AuditedAuthorizedToolPlanStepHandler:
    """Authorize, persist evidence, then delegate to the execution adapter."""

    def __init__(
        self,
        invoker: ToolInvoker,
        policy: ToolAuthorizationPolicy,
        evidence_store: ToolAuthorizationEvidenceStore,
    ) -> None:
        if not isinstance(invoker, ToolInvoker):
            raise TypeError("invoker must implement ToolInvoker")
        if not isinstance(policy, ToolAuthorizationPolicy):
            raise TypeError("policy must implement ToolAuthorizationPolicy")
        if not isinstance(evidence_store, ToolAuthorizationEvidenceStore):
            raise TypeError("evidence_store must be a ToolAuthorizationEvidenceStore")
        self._invoker = invoker
        self._policy = policy
        self._evidence_store = evidence_store
        self._authorized_handler = AuthorizedToolPlanStepHandler(invoker, policy)

    def __call__(
        self,
        step: PlanStep,
        confirmation: ToolExecutionConfirmation | None = None,
    ) -> object:
        request = self._authorized_handler._handler.build_request(step)
        authorization = self._policy.authorize(step, request)
        evidence = ToolAuthorizationEvidence.from_authorization(authorization)
        self._evidence_store.save(evidence)
        return self._authorized_handler(step, confirmation)
