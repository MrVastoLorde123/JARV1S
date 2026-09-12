"""JARVIS-facing orchestration service for bounded coding-agent work."""

from __future__ import annotations

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
from src.agents.consequence_gate import (
    ConsequenceDecision,
    ConsequenceRequest,
    EvidenceGatedConsequencePolicy,
)
from src.agents.repository_context import RepositoryContextComposer
from src.agents.claim_evidence import ClaimEvaluation


class CodingAgentService:
    """Compose JARVIS context, planning, execution, evidence, eligibility, and authority handoff."""

    def __init__(
        self,
        planner,
        worker: CodingAgentWorker,
        context_composer=None,
        claim_evidence_adapter: CodingClaimEvidenceAdapter | None = None,
        consequence_policy: EvidenceGatedConsequencePolicy | None = None,
        authority_handoff_policy: AuthorityHandoffPolicy | None = None,
    ) -> None:
        self._planner = planner
        self._worker = worker
        self._context_composer = context_composer
        self._claim_evidence_adapter = claim_evidence_adapter or CodingClaimEvidenceAdapter()
        self._consequence_policy = consequence_policy or EvidenceGatedConsequencePolicy()
        self._authority_handoff_policy = authority_handoff_policy or AuthorityHandoffPolicy()

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
        """Apply deterministic repository verification policy after model planning.

        Agent-selected verification is advisory. For changes under the UI
        workspace, JARVIS owns the verification contract and requires the
        repository's canonical frontend build rather than an unconstrained
        unittest discovery invocation.
        """
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
    ) -> AuthorityHandoffRequest:
        """Prepare a non-authorizing handoff for the existing authority layer."""
        return self._authority_handoff_policy.handoff(
            decision,
            authority_target=authority_target,
        )


__all__ = ["CodingAgentService"]
