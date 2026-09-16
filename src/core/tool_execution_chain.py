"""Compose planning-bound tool execution into explicit authority stages.

The chain is deliberately an orchestrator, not an authority source. It
materializes a request, obtains and persists authorization evidence, enforces
confirmation, executes once, verifies the resulting observation, and persists
verification evidence. Each stage remains independently replaceable.
"""

from __future__ import annotations

from dataclasses import dataclass

from src.core.execution_plan_models import PlanStep
from src.core.tool_authorization import (
    ToolAuthorizationPolicy,
    ToolExecutionAuthorization,
    require_authorization,
)
from src.core.tool_authorization_evidence_store import (
    StoredToolAuthorizationEvidence,
    ToolAuthorizationEvidenceStore,
)
from src.core.tool_authorization_policy import ToolAuthorizationEvidence
from src.core.tool_execution import ToolExecutionConfirmation, ToolPlanStepHandler, ToolInvoker
from src.core.tool_execution_verification import ToolExecutionVerification, ToolExecutionVerifier
from src.core.tool_execution_verification_evidence_store import (
    StoredToolExecutionVerification,
    ToolExecutionVerificationEvidenceStore,
)
from src.core.tool_execution_verification_service import ToolExecutionVerificationService
from src.tools.models import ToolRequest, ToolResult


@dataclass(frozen=True)
class ToolExecutionChainTrace:
    """Immutable trace of one completed or failed authority chain."""

    step: PlanStep
    request: ToolRequest
    authorization: ToolExecutionAuthorization
    authorization_evidence: StoredToolAuthorizationEvidence
    result: ToolResult
    verification: ToolExecutionVerification
    verification_evidence: StoredToolExecutionVerification


class ToolExecutionChain:
    """Run the complete authorization → execution → verification chain."""

    def __init__(
        self,
        invoker: ToolInvoker,
        policy: ToolAuthorizationPolicy,
        authorization_store: ToolAuthorizationEvidenceStore,
        verifier: ToolExecutionVerifier,
        verification_store: ToolExecutionVerificationEvidenceStore,
    ) -> None:
        if not isinstance(invoker, ToolInvoker):
            raise TypeError("invoker must implement ToolInvoker")
        if not isinstance(policy, ToolAuthorizationPolicy):
            raise TypeError("policy must implement ToolAuthorizationPolicy")
        if not isinstance(authorization_store, ToolAuthorizationEvidenceStore):
            raise TypeError(
                "authorization_store must be a ToolAuthorizationEvidenceStore"
            )
        if not isinstance(verifier, ToolExecutionVerifier):
            raise TypeError("verifier must implement ToolExecutionVerifier")
        if not isinstance(
            verification_store,
            ToolExecutionVerificationEvidenceStore,
        ):
            raise TypeError(
                "verification_store must be a ToolExecutionVerificationEvidenceStore"
            )

        self._execution = ToolPlanStepHandler(invoker)
        self._policy = policy
        self._authorization_store = authorization_store
        self._verification_service = ToolExecutionVerificationService(verifier)
        self._verification_store = verification_store

    def execute(
        self,
        step: PlanStep,
        confirmation: ToolExecutionConfirmation | None = None,
    ) -> ToolExecutionChainTrace:
        request = ToolPlanStepHandler.build_request(step)

        authorization = self._policy.authorize(step, request)
        authorization_evidence = ToolAuthorizationEvidence.from_authorization(
            authorization
        )
        stored_authorization = self._authorization_store.save(authorization_evidence)
        require_authorization(step, request, authorization)

        observed_request, result = self._execution.invoke(step, confirmation)
        if observed_request != request:
            raise RuntimeError(
                "execution adapter materialized a request different from the authorized request"
            )

        verification = self._verification_service.verify(observed_request, result)
        stored_verification = self._verification_store.save(verification)

        return ToolExecutionChainTrace(
            step=step,
            request=request,
            authorization=authorization,
            authorization_evidence=stored_authorization,
            result=result,
            verification=verification,
            verification_evidence=stored_verification,
        )
