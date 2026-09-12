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
from src.agents.consequence_feedback_evaluation import (
    ConsequenceFeedbackEvaluation,
    ConsequenceFeedbackEvaluationService,
)
from src.agents.consequence_learning_decision import (
    ConsequenceLearningDecision,
    ConsequenceLearningDecisionService,
)
from src.agents.consequence_learning_write_request import (
    ConsequenceLearningWriteRequest,
    ConsequenceLearningWriteRequestService,
)
from src.agents.consequence_learning_state_persistence import (
    ConsequenceLearningStatePersistenceReceipt,
    ConsequenceLearningStatePersistenceService,
    ConsequenceLearningStateWriter,
)
from src.agents.consequence_learning_state_persistence_verification import (
    ConsequenceLearningStatePersistenceVerification,
    ConsequenceLearningStatePersistenceVerificationService,
    ConsequenceLearningStateReader,
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
    """Compose JARVIS context, planning, execution, evidence, eligibility, handoff, authorization, preparation, attempt, outcome, feedback, evaluation, learning decision, learning-write request, persistence, and persistence verification."""

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
        consequence_feedback_evaluation_service: ConsequenceFeedbackEvaluationService | None = None,
        consequence_learning_decision_service: ConsequenceLearningDecisionService | None = None,
        consequence_learning_write_request_service: ConsequenceLearningWriteRequestService | None = None,
        consequence_learning_state_persistence_service: ConsequenceLearningStatePersistenceService | None = None,
        consequence_learning_state_persistence_verification_service: ConsequenceLearningStatePersistenceVerificationService | None = None,
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
        self._consequence_feedback_evaluation_service = consequence_feedback_evaluation_service
        self._consequence_learning_decision_service = consequence_learning_decision_service
        self._consequence_learning_write_request_service = consequence_learning_write_request_service
        self._consequence_learning_state_persistence_service = consequence_learning_state_persistence_service
        self._consequence_learning_state_persistence_verification_service = consequence_learning_state_persistence_verification_service

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
        self._consequence_execution_outcome_service = outcome_service or ConsequenceExecutionOutcomeService()

    def bind_consequence_execution_feedback(self, feedback_service: ConsequenceExecutionFeedbackService | None = None) -> None:
        self._consequence_execution_feedback_service = feedback_service or ConsequenceExecutionFeedbackService()

    def bind_consequence_feedback_evaluation(self, evaluation_service: ConsequenceFeedbackEvaluationService | None = None) -> None:
        self._consequence_feedback_evaluation_service = evaluation_service or ConsequenceFeedbackEvaluationService()

    def bind_consequence_learning_decision(self, decision_service: ConsequenceLearningDecisionService | None = None) -> None:
        self._consequence_learning_decision_service = decision_service or ConsequenceLearningDecisionService()

    def bind_consequence_learning_write_request(self, request_service: ConsequenceLearningWriteRequestService | None = None) -> None:
        self._consequence_learning_write_request_service = request_service or ConsequenceLearningWriteRequestService()

    def bind_consequence_learning_state_persistence(
        self,
        writer: ConsequenceLearningStateWriter | None = None,
        *,
        persistence_service: ConsequenceLearningStatePersistenceService | None = None,
    ) -> None:
        if writer is not None and persistence_service is not None:
            raise ValueError("provide either writer or persistence_service, not both")
        if persistence_service is not None:
            self._consequence_learning_state_persistence_service = persistence_service
            return
        if writer is None:
            raise ValueError("writer or persistence_service is required")
        self._consequence_learning_state_persistence_service = ConsequenceLearningStatePersistenceService(writer)

    def bind_consequence_learning_state_persistence_verification(
        self,
        reader: ConsequenceLearningStateReader | None = None,
        *,
        verification_service: ConsequenceLearningStatePersistenceVerificationService | None = None,
    ) -> None:
        if reader is not None and verification_service is not None:
            raise ValueError("provide either reader or verification_service, not both")
        if verification_service is not None:
            self._consequence_learning_state_persistence_verification_service = verification_service
            return
        if reader is None:
            raise ValueError("reader or verification_service is required")
        self._consequence_learning_state_persistence_verification_service = ConsequenceLearningStatePersistenceVerificationService(reader)

    def prepare_task(self, task: CodingAgentTask) -> CodingAgentTask:
        if not isinstance(task, CodingAgentTask):
            raise TypeError("task must be a CodingAgentTask")
        if self._context_composer is None or isinstance(task.metadata.get("repository_context"), str):
            return task
        repository_context = self._context_composer.compose()
        return CodingAgentTask(
            objective=task.objective,
            task_id=task.task_id,
            metadata={**dict(task.metadata), "repository_context": repository_context.render()},
        )

    @staticmethod
    def _apply_verification_authority(plan: CodingAgentPlan) -> CodingAgentPlan:
        if not any(edit.path == "ui" or edit.path.startswith("ui/") for edit in plan.edits):
            return plan
        if plan.verification.runner == "npm_build" and not plan.verification.arguments:
            return plan
        verification = CodingAgentVerification(runner="npm_build", arguments=(), timeout_seconds=plan.verification.timeout_seconds)
        return CodingAgentPlan(edits=plan.edits, verification=verification, rationale=plan.rationale)

    def plan(self, task: CodingAgentTask) -> CodingAgentPlan:
        return self._apply_verification_authority(self._worker.plan(self.prepare_task(task)))

    def execute(self, task: CodingAgentTask, plan: CodingAgentPlan) -> CodingAgentResult:
        if not isinstance(task, CodingAgentTask):
            raise TypeError("task must be a CodingAgentTask")
        if not isinstance(plan, CodingAgentPlan):
            raise TypeError("plan must be a CodingAgentPlan")
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
        if self._consequence_execution_outcome_service is None:
            raise RuntimeError("consequence execution-outcome service is not bound")
        return self._consequence_execution_outcome_service.evaluate(attempt)

    def evaluate_execution_feedback(self, outcome: ConsequenceExecutionOutcome) -> ConsequenceExecutionFeedback:
        if self._consequence_execution_feedback_service is None:
            raise RuntimeError("consequence execution-feedback service is not bound")
        return self._consequence_execution_feedback_service.evaluate(outcome)

    def evaluate_consequence_feedback(self, feedback: ConsequenceExecutionFeedback) -> ConsequenceFeedbackEvaluation:
        if self._consequence_feedback_evaluation_service is None:
            raise RuntimeError("consequence feedback-evaluation service is not bound")
        return self._consequence_feedback_evaluation_service.evaluate(feedback)

    def decide_consequence_learning(self, evaluation: ConsequenceFeedbackEvaluation) -> ConsequenceLearningDecision:
        if self._consequence_learning_decision_service is None:
            raise RuntimeError("consequence learning-decision service is not bound")
        return self._consequence_learning_decision_service.decide(evaluation)

    def create_consequence_learning_write_request(self, decision: ConsequenceLearningDecision) -> ConsequenceLearningWriteRequest:
        if self._consequence_learning_write_request_service is None:
            raise RuntimeError("consequence learning-write-request service is not bound")
        return self._consequence_learning_write_request_service.create(decision)

    def persist_consequence_learning_write_request(
        self,
        request: ConsequenceLearningWriteRequest,
    ) -> ConsequenceLearningStatePersistenceReceipt:
        if self._consequence_learning_state_persistence_service is None:
            raise RuntimeError("consequence learning-state persistence service is not bound")
        return self._consequence_learning_state_persistence_service.persist(request)

    def verify_consequence_learning_state_persistence(
        self,
        request: ConsequenceLearningWriteRequest,
        receipt: ConsequenceLearningStatePersistenceReceipt,
    ) -> ConsequenceLearningStatePersistenceVerification:
        if self._consequence_learning_state_persistence_verification_service is None:
            raise RuntimeError("consequence learning-state persistence-verification service is not bound")
        return self._consequence_learning_state_persistence_verification_service.verify(request, receipt)


__all__ = ["CodingAgentService"]
