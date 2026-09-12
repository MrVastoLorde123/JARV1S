"""JARVIS-facing orchestration service for bounded coding-agent work."""

from __future__ import annotations

from typing import Mapping

from src.agents.ai_coding_planner import AICodingAgentPlanner
from src.agents.authority_handoff import (
    AuthorityHandoffPolicy,
    AuthorityHandoffRequest,
)
from src.agents.coding_claim_evidence import (
    CodingClaimEvidenceAdapter,
    CodingClaimEvidenceResult,
)
from src.agents.coding_worker import (
    CodingAgentPlan,
    CodingAgentResult,
    CodingAgentTask,
    CodingAgentWorker,
    CodingAgentVerification,
)
from src.agents.claim_evidence import ClaimEvaluation
from src.agents.consequence_authorization import (
    ConsequenceAuthorizationDecision,
    ConsequenceAuthorizationService,
)
from src.agents.consequence_execution_attempt import (
    ConsequenceExecutionAttempt,
    ConsequenceExecutionAttemptService,
)
from src.agents.consequence_execution_feedback import (
    ConsequenceExecutionFeedback,
    ConsequenceExecutionFeedbackService,
)
from src.agents.consequence_execution_outcome import (
    ConsequenceExecutionOutcome,
    ConsequenceExecutionOutcomeService,
)
from src.agents.consequence_execution_preparation import (
    ConsequenceExecutionPreparation,
    ConsequenceExecutionPreparationService,
)
from src.agents.consequence_gate import (
    ConsequenceDecision,
    ConsequenceRequest,
    EvidenceGatedConsequencePolicy,
)
from src.agents.repository_context import RepositoryContextComposer
from src.tools.authorization import ExplicitAuthorizationService
from src.tools.models import ToolDefinition, ToolRequest
from src.tools.execution_attempt import ToolExecutor


class CodingAgentService:
    """Compose JARVIS context, planning, execution, evidence, eligibility, handoff, authorization, preparation, attempt, outcome, and feedback."""

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
        consequence_execution_feedback_service: ConsequenceExecutionFeedbackService | None = None,
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
        self._consequence_execution_feedback_service = consequence_execution_feedback_service

    @classmethod
    def from_ai_service(cls, ai_service, tool_invoker, *, provider_name: str | None = None):
        planner = AICodingAgentPlanner(
            ai_service,
            provider_name=provider_name,
        )
        worker = CodingAgentWorker(
            planner,
            tool_invoker,
        )
        context_composer = RepositoryContextComposer(tool_invoker)
        return cls(planner, worker, context_composer)

    def bind_consequence_authorization(
        self,
        authorization_service: ExplicitAuthorizationService,
        *,
        authority_target: str = "coding_confirmation",
    ) -> None:
        """Bind the existing M22.8 authorizer to the M31→M32 consequence seam."""
        self._consequence_authorization_service = ConsequenceAuthorizationService(
            authorization_service,
            authority_target=authority_target,
        )

    def bind_consequence_execution_preparation(
        self,
        preparation_service: ConsequenceExecutionPreparationService | None = None,
    ) -> None:
        """Bind the M33 consequence authorization → execution-preparation seam."""
        self._consequence_execution_preparation_service = (
            preparation_service or ConsequenceExecutionPreparationService()
        )

    def bind_consequence_execution_attempt(
        self,
        executor: ToolExecutor | None = None,
        *,
        attempt_service: ConsequenceExecutionAttemptService | None = None,
    ) -> None:
        """Bind the M34 consequence preparation → existing attempt seam."""
        if attempt_service is not None and executor is not None:
            raise ValueError("provide either executor or attempt_service, not both")
        if attempt_service is not None:
            self._consequence_execution_attempt_service = attempt_service
            return
        if executor is None:
            raise ValueError("executor or attempt_service is required")
        self._consequence_execution_attempt_service = ConsequenceExecutionAttemptService(executor)

    def bind_consequence_execution_outcome(
        self,
        outcome_service: ConsequenceExecutionOutcomeService | None = None,
    ) -> None:
        """Bind the M35 execution-attempt → observed-outcome seam."""
        self._consequence_execution_outcome_service = outcome_service or ConsequenceExecutionOutcomeService()

    def bind_consequence_execution_feedback(
        self,
        feedback_service: ConsequenceExecutionFeedbackService | None = None,
    ) -> None:
        """Bind the M36 observed-outcome → inert-feedback seam."""
        self._consequence_execution_feedback_service = (
            feedback_service or ConsequenceExecutionFeedbackService()
        )

    def prepare_task(self, task: CodingAgentTask) -> CodingAgentTask:
        """Attach JARVIS-observed environment context to a task before planning."""
        if not isinstance(task, CodingAgentTask):
            raise TypeError("task must be a CodingAgentTask")
        if self._context_composer is None:
            return task
        if isinstance(task.metadata.get("repository_context"), str):
            return task

        repository_context = self._context_composer.compose()
        return CodingAgentTask(
            objective=task.objective,
            task_id=task.task_id,
            metadata={
                **dict(task.metadata),
                "repository_context": repository_context.render(),
            },
        )

    @staticmethod
    def _apply_verification_authority(plan: CodingAgentPlan) -> CodingAgentPlan:
        """Apply deterministic repository verification policy after model planning."""
        if not any(edit.path == "ui" or edit.path.startswith("ui/") for edit in plan.edits):
            return plan
        if plan.verification.runner == "npm_build" and not plan.verification.arguments:
            return plan

        verification = CodingAgentVerification(
            runner="npm_build",
            arguments=(),
            timeout_seconds=plan.verification.timeout_seconds,
        )
        return CodingAgentPlan(
            edits=plan.edits,
            verification=verification,
            rationale=plan.rationale,
        )

    def plan(self, task: CodingAgentTask) -> CodingAgentPlan:
        """Compose observed environment context before generating a proposal."""
        prepared_task = self.prepare_task(task)
        proposed_plan = self._worker.plan(prepared_task)
        return self._apply_verification_authority(proposed_plan)

    def execute(self, task: CodingAgentTask, plan: CodingAgentPlan) -> CodingAgentResult:
        """Execute exactly the supplied plan through the worker authority boundary."""
        if not isinstance(task, CodingAgentTask):
            raise TypeError("task must be a CodingAgentTask")
        if not isinstance(plan, CodingAgentPlan):
            raise TypeError("plan must be a CodingAgentPlan")
        return self._worker.execute(task, plan)

    def execute_and_evaluate(
        self,
        task: CodingAgentTask,
        plan: CodingAgentPlan,
    ) -> CodingClaimEvidenceResult:
        """Execute through M28 authority, then deterministically evaluate M29 evidence."""
        result = self.execute(task, plan)
        return self._claim_evidence_adapter.evaluate(task, plan, result)

    def decide_consequence(
        self,
        evaluation: ClaimEvaluation,
        consequence: ConsequenceRequest,
    ) -> ConsequenceDecision:
        """Consume an M29 evaluation through the M30 consequence boundary."""
        return self._consequence_policy.decide(evaluation, consequence)

    def prepare_authority_handoff(
        self,
        decision: ConsequenceDecision,
        *,
        authority_target: str = "existing_authority",
        authority_context: Mapping[str, object] | None = None,
    ) -> AuthorityHandoffRequest:
        """Prepare a non-authorizing handoff for the existing authority layer."""
        return self._authority_handoff_policy.handoff(
            decision,
            authority_target=authority_target,
            authority_context=authority_context,
        )

    def authorize_consequence(
        self,
        handoff: AuthorityHandoffRequest,
        definition: ToolDefinition,
        request: ToolRequest,
        *,
        authorization_id: str,
    ) -> ConsequenceAuthorizationDecision:
        """Authorize one M31 handoff through the existing explicit authorizer."""
        if self._consequence_authorization_service is None:
            raise RuntimeError("consequence authorization service is not bound")
        return self._consequence_authorization_service.authorize(
            handoff,
            definition,
            request,
            authorization_id=authorization_id,
        )

    def prepare_authorized_consequence(
        self,
        authorization: ConsequenceAuthorizationDecision,
        definition: ToolDefinition,
        request: ToolRequest,
    ) -> ConsequenceExecutionPreparation:
        """Prepare one M32-authorized consequence through M22.9/M30 execution walls."""
        if self._consequence_execution_preparation_service is None:
            raise RuntimeError("consequence execution-preparation service is not bound")
        return self._consequence_execution_preparation_service.prepare(
            authorization,
            definition,
            request,
        )

    def attempt_prepared_consequence(
        self,
        preparation: ConsequenceExecutionPreparation,
    ) -> ConsequenceExecutionAttempt:
        """Start one M33-prepared consequence through the existing execution-attempt boundary."""
        if self._consequence_execution_attempt_service is None:
            raise RuntimeError("consequence execution-attempt service is not bound")
        return self._consequence_execution_attempt_service.attempt(preparation)

    def evaluate_execution_outcome(
        self,
        attempt: ConsequenceExecutionAttempt,
    ) -> ConsequenceExecutionOutcome:
        """Interpret one M34 execution attempt as an observed M35 outcome."""
        if self._consequence_execution_outcome_service is None:
            raise RuntimeError("consequence execution-outcome service is not bound")
        return self._consequence_execution_outcome_service.evaluate(attempt)

    def evaluate_execution_feedback(
        self,
        outcome: ConsequenceExecutionOutcome,
    ) -> ConsequenceExecutionFeedback:
        """Convert one M35 observed outcome into inert M36 consequence feedback."""
        if self._consequence_execution_feedback_service is None:
            raise RuntimeError("consequence execution-feedback service is not bound")
        return self._consequence_execution_feedback_service.evaluate(outcome)


__all__ = ["CodingAgentService"]
