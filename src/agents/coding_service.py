"""JARVIS-facing orchestration service for bounded coding-agent work."""

from __future__ import annotations

from typing import Mapping

from src.agents.ai_coding_planner import AICodingAgentPlanner
from src.agents.authority_handoff import AuthorityHandoffPolicy, AuthorityHandoffRequest
from src.agents.coding_claim_evidence import CodingClaimEvidenceAdapter, CodingClaimEvidenceResult
from src.agents.coding_worker import (
    CodingAgentPlan, CodingAgentResult, CodingAgentTask, CodingAgentVerification, CodingAgentWorker,
)
from src.agents.claim_evidence import ClaimEvaluation
from src.agents.consequence_authorization import ConsequenceAuthorizationDecision, ConsequenceAuthorizationService
from src.agents.consequence_execution_attempt import ConsequenceExecutionAttempt, ConsequenceExecutionAttemptService
from src.agents.consequence_execution_outcome import ConsequenceExecutionOutcome, ConsequenceExecutionOutcomeService
from src.agents.consequence_execution_preparation import ConsequenceExecutionPreparation, ConsequenceExecutionPreparationService
from src.agents.consequence_gate import ConsequenceDecision, ConsequenceRequest, EvidenceGatedConsequencePolicy
from src.agents.repository_context import RepositoryContextComposer
from src.tools.authorization import ExplicitAuthorizationService
from src.tools.execution_attempt import ToolExecutor
from src.tools.models import ToolDefinition, ToolRequest


class CodingAgentService:
    """Compose JARVIS context, planning, execution, evidence, eligibility, authority, and outcome boundaries."""

    def __init__(
        self,
        planner,
        worker: CodingAgentWorker,
        context_composer=None,
        claim_evidence_adapter: CodingClaimEvidenceAdapter | None = None,
        consequence_policy: EvidenceGatedConsequencePolicy | None = None,
        authority_handoff_policy: AuthorityHandoffPolicy | None = None,
        consequence_authorization_service: ConsequenceAuthorizationService | None = None,
        consequence_execution_preparation_service: ConsequenceExecutionPreparationService | None = None,
        consequence_execution_attempt_service: ConsequenceExecutionAttemptService | None = None,
        consequence_execution_outcome_service: ConsequenceExecutionOutcomeService | None = None,
    ) -> None:
        self._planner = planner
        self._worker = worker
        self._context_composer = context_composer
        self._claim_evidence_adapter = claim_evidence_adapter or CodingClaimEvidenceAdapter()
        self._consequence_policy = consequence_policy or EvidenceGatedConsequencePolicy()
        self._authority_handoff_policy = authority_handoff_policy or AuthorityHandoffPolicy()
        self._consequence_authorization_service = consequence_authorization_service
        self._consequence_execution_preparation_service = consequence_execution_preparation_service
        self._consequence_execution_attempt_service = consequence_execution_attempt_service
        self._consequence_execution_outcome_service = consequence_execution_outcome_service

    @classmethod
    def from_ai_service(cls, ai_service, tool_invoker, *, provider_name: str | None = None):
        planner = AICodingAgentPlanner(ai_service, provider_name=provider_name)
        worker = CodingAgentWorker(planner, tool_invoker)
        context_composer = RepositoryContextComposer(tool_invoker)
        return cls(planner, worker, context_composer)

    def bind_consequence_authorization(self, authorization_service: ExplicitAuthorizationService, *, authority_target: str = "coding_confirmation") -> None:
        self._consequence_authorization_service = ConsequenceAuthorizationService(authorization_service, authority_target=authority_target)

    def bind_consequence_execution_preparation(self, preparation_service: ConsequenceExecutionPreparationService | None = None) -> None:
        self._consequence_execution_preparation_service = preparation_service or ConsequenceExecutionPreparationService()

    def bind_consequence_execution_attempt(self, executor: ToolExecutor | None = None, *, attempt_service: ConsequenceExecutionAttemptService | None = None) -> None:
        if attempt_service is not None and executor is not None:
            raise ValueError("provide either executor or attempt_service, not both")
        if attempt_service is not None:
            self._consequence_execution_attempt_service = attempt_service
            return
        if executor is None:
            raise ValueError("executor or attempt_service is required")
        self._consequence_execution_attempt_service = ConsequenceExecutionAttemptService(executor)

    def bind_consequence_execution_outcome(self, outcome_service: ConsequenceExecutionOutcomeService | None = None) -> None:
        """Bind the M35 execution-attempt → consequence-outcome seam."""
        self._consequence_execution_outcome_service = outcome_service or ConsequenceExecutionOutcomeService()

    def prepare_task(self, task: CodingAgentTask) -> CodingAgentTask:
        if not isinstance(task, CodingAgentTask):
            raise TypeError("task must be a CodingAgentTask")
        if self._context_composer is None or isinstance(task.metadata.get("repository_context"), str):
            return task
        repository_context = self._context_composer.compose()
        return CodingAgentTask(objective=task.objective, task_id=task.task_id, metadata={**dict(task.metadata), "repository_context": repository_context.render()})

    @staticmethod
    def _apply_verification_authority(plan: CodingAgentPlan) -> CodingAgentPlan:
        if not any(edit.path == "ui" or edit.path.startswith("ui/") for edit in plan.edits):
            return plan
        if plan.verification.runner == "npm_build" and not plan.verification.arguments:
            return plan
        return CodingAgentPlan(edits=plan.edits, verification=CodingAgentVerification(runner="npm_build", arguments=(), timeout_seconds=plan.verification.timeout_seconds), rationale=plan.rationale)

    def plan(self, task: CodingAgentTask) -> CodingAgentPlan:
        return self._apply_verification_authority(self._worker.plan(self.prepare_task(task)))

    def execute(self, task: CodingAgentTask, plan: CodingAgentPlan) -> CodingAgentResult:
        if not isinstance(task, CodingAgentTask) or not isinstance(plan, CodingAgentPlan):
            raise TypeError("task and plan must be CodingAgentTask and CodingAgentPlan")
        return self._worker.execute(task, plan)

    def execute_and_evaluate(self, task: CodingAgentTask, plan: CodingAgentPlan) -> CodingClaimEvidenceResult:
        return self._claim_evidence_adapter.evaluate(task, plan, self.execute(task, plan))

    def decide_consequence(self, evaluation: ClaimEvaluation, consequence: ConsequenceRequest) -> ConsequenceDecision:
        return self._consequence_policy.decide(evaluation, consequence)

    def prepare_authority_handoff(self, decision: ConsequenceDecision, *, authority_target: str = "existing_authority", authority_context: Mapping[str, object] | None = None) -> AuthorityHandoffRequest:
        return self._authority_handoff_policy.handoff(decision, authority_target=authority_target, authority_context=authority_context)

    def authorize_consequence(self, handoff: AuthorityHandoffRequest, definition: ToolDefinition, request: ToolRequest, *, authorization_id: str) -> ConsequenceAuthorizationDecision:
        if self._consequence_authorization_service is None:
            raise RuntimeError("consequence authorization service is not bound")
        return self._consequence_authorization_service.authorize(handoff, definition, request, authorization_id=authorization_id)

    def prepare_authorized_consequence(self, authorization: ConsequenceAuthorizationDecision, definition: ToolDefinition, request: ToolRequest) -> ConsequenceExecutionPreparation:
        if self._consequence_execution_preparation_service is None:
            raise RuntimeError("consequence execution-preparation service is not bound")
        return self._consequence_execution_preparation_service.prepare(authorization, definition, request)

    def attempt_prepared_consequence(self, preparation: ConsequenceExecutionPreparation) -> ConsequenceExecutionAttempt:
        if self._consequence_execution_attempt_service is None:
            raise RuntimeError("consequence execution-attempt service is not bound")
        return self._consequence_execution_attempt_service.attempt(preparation)

    def evaluate_execution_outcome(self, attempt: ConsequenceExecutionAttempt) -> ConsequenceExecutionOutcome:
        """Interpret one M34 attempt as an observed M35 consequence outcome."""
        if self._consequence_execution_outcome_service is None:
            raise RuntimeError("consequence execution-outcome service is not bound")
        return self._consequence_execution_outcome_service.evaluate(attempt)


__all__ = ["CodingAgentService"]
