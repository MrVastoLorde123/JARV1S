"""M25.2: orchestrate interface requests across the bounded M24 lifecycle."""
from __future__ import annotations

from typing import Any, Mapping, Protocol

from src.core.continuous_self_improvement_candidate import (
    ContinuousSelfImprovementCandidate,
    ContinuousSelfImprovementCandidateService,
)
from src.core.improvement_application import (
    ImprovementApplication,
    ImprovementApplicationService,
)
from src.core.improvement_decision import (
    ImprovementDecision,
    ImprovementDecisionService,
)
from src.core.improvement_evaluation import (
    ImprovementEvaluation,
    ImprovementEvaluationService,
)
from src.core.improvement_verification import (
    ImprovementVerification,
    ImprovementVerificationService,
)
from src.core.interface_backend import (
    InterfaceOperation,
    InterfaceOrchestrationPort,
    InterfaceRequest,
    InterfaceResponse,
    InterfaceResponseStatus,
)
from src.core.learning_state_execution_learning_state_validation_integrity_consumption import (
    LearningStateExecutionLearningStateValidationIntegrityConsumption,
)


class SelfImprovementOrchestrationError(RuntimeError):
    """Raised when an interface request cannot be safely orchestrated."""


class ImprovementStageService(Protocol):
    """Marker protocol for an injected bounded M24 service."""


class SelfImprovementOrchestration(InterfaceOrchestrationPort):
    """Dispatch interface operations to injected M24 services without owning their semantics."""

    def __init__(
        self,
        *,
        candidate_service: ContinuousSelfImprovementCandidateService,
        evaluation_service: ImprovementEvaluationService,
        decision_service: ImprovementDecisionService,
        application_service: ImprovementApplicationService,
        verification_service: ImprovementVerificationService,
    ) -> None:
        services = (
            ("candidate_service", candidate_service),
            ("evaluation_service", evaluation_service),
            ("decision_service", decision_service),
            ("application_service", application_service),
            ("verification_service", verification_service),
        )
        for name, service in services:
            if service is None or not self._has_expected_method(name, service):
                raise TypeError(f"{name} must provide its M24 service method")
        self._candidate_service = candidate_service
        self._evaluation_service = evaluation_service
        self._decision_service = decision_service
        self._application_service = application_service
        self._verification_service = verification_service

    @staticmethod
    def _has_expected_method(name: str, service: Any) -> bool:
        method_name = {
            "candidate_service": "propose",
            "evaluation_service": "evaluate",
            "decision_service": "decide",
            "application_service": "apply",
            "verification_service": "verify",
        }[name]
        return callable(getattr(service, method_name, None))

    def dispatch(self, request: InterfaceRequest) -> InterfaceResponse:
        if type(request) is not InterfaceRequest:
            raise TypeError("request must be an interface request")
        handler = {
            InterfaceOperation.PROPOSE: self._propose,
            InterfaceOperation.EVALUATE: self._evaluate,
            InterfaceOperation.DECIDE: self._decide,
            InterfaceOperation.APPLY: self._apply,
            InterfaceOperation.VERIFY: self._verify,
            InterfaceOperation.ROLLBACK: self._rollback,
            InterfaceOperation.STATUS: self._status,
        }[request.operation]
        try:
            artifact = handler(request.payload)
        except (KeyError, TypeError, ValueError, SelfImprovementOrchestrationError) as exc:
            return self._response(request, InterfaceResponseStatus.REJECTED, {"error": str(exc)})
        except Exception as exc:  # pragma: no cover - defensive fail-closed boundary
            return self._response(request, InterfaceResponseStatus.FAILED, {"error": type(exc).__name__})

        expected_type = {
            InterfaceOperation.PROPOSE: ContinuousSelfImprovementCandidate,
            InterfaceOperation.EVALUATE: ImprovementEvaluation,
            InterfaceOperation.DECIDE: ImprovementDecision,
            InterfaceOperation.APPLY: ImprovementApplication,
            InterfaceOperation.VERIFY: ImprovementVerification,
        }.get(request.operation)
        if expected_type is not None and type(artifact) is not expected_type:
            return self._response(
                request,
                InterfaceResponseStatus.FAILED,
                {"error": f"wrong stage result: expected {expected_type.__name__}"},
            )
        return self._response(
            request,
            InterfaceResponseStatus.ACCEPTED,
            {"artifact": artifact},
            extra_metadata={"artifact_type": type(artifact).__name__},
        )

    @staticmethod
    def _response(
        request: InterfaceRequest,
        status: InterfaceResponseStatus,
        payload: Mapping[str, Any],
        *,
        extra_metadata: Mapping[str, Any] | None = None,
    ) -> InterfaceResponse:
        metadata = {"session_id": request.session_id, "actor_id": request.actor_id}
        if extra_metadata:
            metadata.update(extra_metadata)
        return InterfaceResponse(
            request_id=request.request_id,
            operation=request.operation,
            status=status,
            payload=payload,
            metadata=metadata,
        )

    @staticmethod
    def _require(payload: Mapping[str, Any], *names: str) -> None:
        for name in names:
            if name not in payload:
                raise SelfImprovementOrchestrationError(f"missing payload field: {name}")

    @staticmethod
    def _require_type(payload: Mapping[str, Any], field: str, expected_type: type[Any]) -> None:
        if type(payload[field]) is not expected_type:
            raise TypeError(f"{field} must be a {expected_type.__name__}")

    def _propose(self, payload: Mapping[str, Any]) -> ContinuousSelfImprovementCandidate:
        self._require(
            payload,
            "consumption", "candidate_id", "proposer_id", "candidate_purpose",
            "improvement_scope", "proposed_improvement", "rationale",
        )
        self._require_type(
            payload, "consumption", LearningStateExecutionLearningStateValidationIntegrityConsumption
        )
        return self._candidate_service.propose(
            payload["consumption"],
            candidate_id=payload["candidate_id"],
            proposer_id=payload["proposer_id"],
            candidate_purpose=payload["candidate_purpose"],
            improvement_scope=payload["improvement_scope"],
            proposed_improvement=payload["proposed_improvement"],
            rationale=payload["rationale"],
            reasons=payload.get("reasons"),
            lineage=payload.get("lineage"),
        )

    def _evaluate(self, payload: Mapping[str, Any]) -> ImprovementEvaluation:
        self._require(
            payload,
            "candidate", "evaluation_id", "evaluator_id", "evaluation_purpose",
            "evaluation_scope", "criteria", "observations", "assessment",
        )
        self._require_type(payload, "candidate", ContinuousSelfImprovementCandidate)
        return self._evaluation_service.evaluate(
            payload["candidate"],
            evaluation_id=payload["evaluation_id"],
            evaluator_id=payload["evaluator_id"],
            evaluation_purpose=payload["evaluation_purpose"],
            evaluation_scope=payload["evaluation_scope"],
            criteria=payload["criteria"],
            observations=payload["observations"],
            assessment=payload["assessment"],
            reasons=payload.get("reasons"),
            lineage=payload.get("lineage"),
        )

    def _decide(self, payload: Mapping[str, Any]) -> ImprovementDecision:
        self._require(
            payload,
            "evaluation", "decision_id", "decider_id", "decision_purpose",
            "decision_scope", "disposition", "rationale", "factors",
        )
        self._require_type(payload, "evaluation", ImprovementEvaluation)
        return self._decision_service.decide(
            payload["evaluation"],
            decision_id=payload["decision_id"],
            decider_id=payload["decider_id"],
            decision_purpose=payload["decision_purpose"],
            decision_scope=payload["decision_scope"],
            disposition=payload["disposition"],
            rationale=payload["rationale"],
            factors=payload["factors"],
            reasons=payload.get("reasons"),
            lineage=payload.get("lineage"),
        )

    def _apply(self, payload: Mapping[str, Any]) -> ImprovementApplication:
        self._require(
            payload,
            "decision", "applicator_id", "application_scope", "application_purpose",
            "application_result", "status",
        )
        self._require_type(payload, "decision", ImprovementDecision)
        return self._application_service.apply(
            payload["decision"],
            applicator_id=payload["applicator_id"],
            application_scope=payload["application_scope"],
            application_purpose=payload["application_purpose"],
            application_result=payload["application_result"],
            status=payload["status"],
            reasons=payload.get("reasons"),
            lineage=payload.get("lineage"),
        )

    def _verify(self, payload: Mapping[str, Any]) -> ImprovementVerification:
        self._require(
            payload,
            "application", "verification_id", "verifier_id", "verification_purpose",
            "verification_scope", "observed_result", "expected_result",
            "verification_status", "rollback_status", "rollback_result",
        )
        self._require_type(payload, "application", ImprovementApplication)
        return self._verification_service.verify(
            payload["application"],
            verification_id=payload["verification_id"],
            verifier_id=payload["verifier_id"],
            verification_purpose=payload["verification_purpose"],
            verification_scope=payload["verification_scope"],
            observed_result=payload["observed_result"],
            expected_result=payload["expected_result"],
            verification_status=payload["verification_status"],
            rollback_status=payload["rollback_status"],
            rollback_result=payload["rollback_result"],
            reasons=payload.get("reasons"),
            lineage=payload.get("lineage"),
        )

    @staticmethod
    def _rollback(payload: Mapping[str, Any]) -> object:
        del payload
        raise SelfImprovementOrchestrationError(
            "rollback execution is not part of M25.2; M24.5 only records rollback evidence"
        )

    @staticmethod
    def _status(payload: Mapping[str, Any]) -> object:
        del payload
        raise SelfImprovementOrchestrationError(
            "status queries require the runtime state contract introduced after M25.2"
        )

    @property
    def authorizes_execution(self) -> bool:
        return False

    @property
    def executes_capability(self) -> bool:
        return False

    @property
    def mutates_state(self) -> bool:
        return False

    @property
    def persists_state(self) -> bool:
        return False

    @property
    def establishes_truth(self) -> bool:
        return False

    @property
    def establishes_certainty(self) -> bool:
        return False

    @property
    def is_ai_provider(self) -> bool:
        return False


__all__ = ["SelfImprovementOrchestrationError", "SelfImprovementOrchestration"]
