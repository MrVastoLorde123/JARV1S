"""Require durable authorization evidence before tool execution."""

from __future__ import annotations

from src.core.execution_plan_models import PlanStep
from src.core.tool_authorization import (
    ToolAuthorizationPolicy,
    require_authorization,
)
from src.core.tool_authorization_evidence_store import ToolAuthorizationEvidenceStore
from src.core.tool_authorization_policy import ToolAuthorizationEvidence
from src.core.tool_execution import ToolExecutionConfirmation, ToolPlanStepHandler, ToolInvoker


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
        self._handler = ToolPlanStepHandler(invoker)
        self._policy = policy
        self._evidence_store = evidence_store

    def __call__(
        self,
        step: PlanStep,
        confirmation: ToolExecutionConfirmation | None = None,
    ) -> object:
        request = ToolPlanStepHandler.build_request(step)
        authorization = self._policy.authorize(step, request)
        evidence = ToolAuthorizationEvidence.from_authorization(authorization)
        self._evidence_store.save(evidence)
        require_authorization(step, request, authorization)
        return self._handler(step, confirmation)
