"""M127-M134: bounded cognitive runtime composition.

Phase 10 composes the already-verified persistent-intelligence, world-model,
reasoning, planning, and proactive-initiative boundaries into one typed
cognitive cycle. The runtime produces inspectable advisory artifacts; it does
not validate policy, confirm, authorize, execute, select providers, establish
truth, or establish certainty.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Mapping

from src.core.planning_decision import (
    CandidatePlan,
    Goal,
    PlanningContext,
    PlanningDecisionSystem,
    PlanningResult,
    PlannedStep,
)
from src.core.proactive_initiative import (
    ProactiveInitiativeContext,
    ProactiveInitiativeResult,
    ProactiveInitiativeSystem,
)
from src.core.reasoning import (
    EvidencePolarity,
    EvidenceSignal,
    Hypothesis,
    Prediction,
    ReasoningContext,
    ReasoningResult,
    ReasoningSystem,
)
from src.core.world_model import WorldModelSystem, WorldObservation, WorldSnapshot


class CognitiveRuntimeValidationError(ValueError):
    """Raised when a cognitive-cycle contract cannot be composed safely."""


@dataclass(frozen=True)
class CognitiveHypothesisInput:
    """Provider-neutral hypothesis specification before reasoning context exists."""

    hypothesis_id: str
    statement: str
    prior: float
    provenance_ids: tuple[str, ...] = ()
    assumptions: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not isinstance(self.hypothesis_id, str) or not self.hypothesis_id.strip():
            raise CognitiveRuntimeValidationError("hypothesis_id must be non-empty")
        if not isinstance(self.statement, str) or not self.statement.strip():
            raise CognitiveRuntimeValidationError("hypothesis statement must be non-empty")
        if not isinstance(self.provenance_ids, tuple) or any(
            not isinstance(item, str) or not item.strip() for item in self.provenance_ids
        ):
            raise CognitiveRuntimeValidationError("hypothesis provenance_ids must be non-empty strings")
        if not isinstance(self.assumptions, tuple) or any(
            not isinstance(item, str) or not item.strip() for item in self.assumptions
        ):
            raise CognitiveRuntimeValidationError("hypothesis assumptions must be non-empty strings")


@dataclass(frozen=True)
class CognitiveEvidenceInput:
    """Provider-neutral evidence specification consumed by the reasoning boundary."""

    evidence_id: str
    source_id: str
    polarity: EvidencePolarity
    confidence: float
    relevance: float
    likelihood_ratio: float
    summary: str
    provenance_ids: tuple[str, ...]
    observed_at: str

    def __post_init__(self) -> None:
        if not isinstance(self.evidence_id, str) or not self.evidence_id.strip():
            raise CognitiveRuntimeValidationError("evidence_id must be non-empty")
        if not isinstance(self.source_id, str) or not self.source_id.strip():
            raise CognitiveRuntimeValidationError("source_id must be non-empty")
        if not isinstance(self.summary, str) or not self.summary.strip():
            raise CognitiveRuntimeValidationError("evidence summary must be non-empty")
        if not isinstance(self.polarity, EvidencePolarity):
            raise TypeError("polarity must be an EvidencePolarity")
        if not isinstance(self.provenance_ids, tuple) or any(
            not isinstance(item, str) or not item.strip() for item in self.provenance_ids
        ):
            raise CognitiveRuntimeValidationError("evidence provenance_ids must be non-empty strings")
        if not self.provenance_ids:
            raise CognitiveRuntimeValidationError("evidence requires at least one provenance id")


@dataclass(frozen=True)
class CognitivePredictionInput:
    """Prediction request linked to a hypothesis before revision identity exists."""

    prediction_id: str
    hypothesis_id: str
    outcome: str
    horizon_start: str
    horizon_end: str
    assumptions: tuple[str, ...] = ()
    adjustment: float = 0.0

    def __post_init__(self) -> None:
        for name in ("prediction_id", "hypothesis_id", "outcome"):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise CognitiveRuntimeValidationError(f"{name} must be non-empty")
        if not isinstance(self.assumptions, tuple) or any(
            not isinstance(item, str) or not item.strip() for item in self.assumptions
        ):
            raise CognitiveRuntimeValidationError("prediction assumptions must be non-empty strings")


@dataclass(frozen=True)
class CognitiveRuntimeRequest:
    """Complete typed input for one deterministic cognitive-cycle composition."""

    request_id: str
    created_at: str
    question: str
    world_generated_at: str
    goal: Goal
    candidate_plans: tuple[CandidatePlan, ...]
    world_observations: tuple[WorldObservation, ...] = ()
    hypotheses: tuple[CognitiveHypothesisInput, ...] = ()
    evidence: tuple[CognitiveEvidenceInput, ...] = ()
    prediction_requests: tuple[CognitivePredictionInput, ...] = ()
    memory_ids: tuple[str, ...] = ()
    assumptions: tuple[str, ...] = ()
    additional_constraints: tuple[str, ...] = ()
    next_at: str | None = None
    timezone: str = "UTC"
    metadata: Mapping[str, object] = field(default_factory=dict)

    def __post_init__(self) -> None:
        for name in ("request_id", "question", "created_at", "world_generated_at", "timezone"):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise CognitiveRuntimeValidationError(f"{name} must be non-empty")
        if not isinstance(self.goal, Goal):
            raise TypeError("goal must be a Goal")
        if not isinstance(self.candidate_plans, tuple) or any(
            not isinstance(item, CandidatePlan) for item in self.candidate_plans
        ):
            raise TypeError("candidate_plans must be a tuple of CandidatePlan")
        if not isinstance(self.world_observations, tuple) or any(
            not isinstance(item, WorldObservation) for item in self.world_observations
        ):
            raise TypeError("world_observations must be a tuple of WorldObservation")
        if not isinstance(self.hypotheses, tuple) or any(
            not isinstance(item, CognitiveHypothesisInput) for item in self.hypotheses
        ):
            raise TypeError("hypotheses must be a tuple of CognitiveHypothesisInput")
        if not isinstance(self.evidence, tuple) or any(
            not isinstance(item, CognitiveEvidenceInput) for item in self.evidence
        ):
            raise TypeError("evidence must be a tuple of CognitiveEvidenceInput")
        if not isinstance(self.prediction_requests, tuple) or any(
            not isinstance(item, CognitivePredictionInput) for item in self.prediction_requests
        ):
            raise TypeError("prediction_requests must be a tuple of CognitivePredictionInput")
        for name, values in (
            ("memory_ids", self.memory_ids),
            ("assumptions", self.assumptions),
            ("additional_constraints", self.additional_constraints),
        ):
            if not isinstance(values, tuple) or any(not isinstance(item, str) or not item.strip() for item in values):
                raise CognitiveRuntimeValidationError(f"{name} must be a tuple of non-empty strings")
        if not isinstance(self.metadata, Mapping):
            raise TypeError("metadata must be a mapping")
        if len({item.observation_id for item in self.world_observations}) != len(self.world_observations):
            raise CognitiveRuntimeValidationError("world observation ids must be unique")
        if len({item.hypothesis_id for item in self.hypotheses}) != len(self.hypotheses):
            raise CognitiveRuntimeValidationError("hypothesis ids must be unique")
        if len({item.evidence_id for item in self.evidence}) != len(self.evidence):
            raise CognitiveRuntimeValidationError("evidence ids must be unique")
        if len({item.plan_id for item in self.candidate_plans}) != len(self.candidate_plans):
            raise CognitiveRuntimeValidationError("candidate plan ids must be unique")


@dataclass(frozen=True)
class CognitiveRuntimeResult:
    """Inspectably composed output of one cognitive cycle."""

    request: CognitiveRuntimeRequest
    world_snapshot: WorldSnapshot
    reasoning_result: ReasoningResult
    planning_result: PlanningResult
    initiative_result: ProactiveInitiativeResult
    stage_trace: tuple[str, ...]

    def __post_init__(self) -> None:
        if not isinstance(self.request, CognitiveRuntimeRequest):
            raise TypeError("request must be a CognitiveRuntimeRequest")
        for name, expected in (
            ("world_snapshot", WorldSnapshot),
            ("reasoning_result", ReasoningResult),
            ("planning_result", PlanningResult),
            ("initiative_result", ProactiveInitiativeResult),
        ):
            if not isinstance(getattr(self, name), expected):
                raise TypeError(f"{name} must be a {expected.__name__}")
        if not isinstance(self.stage_trace, tuple) or any(not isinstance(item, str) or not item.strip() for item in self.stage_trace):
            raise TypeError("stage_trace must contain non-empty strings")

    @property
    def selected_plan_id(self) -> str | None:
        return self.planning_result.ranking.advisory_selected_plan_id

    @property
    def proposal(self):
        return self.initiative_result.proposal

    @property
    def ready_for_downstream_validation(self) -> bool:
        return self.initiative_result.is_ready_for_downstream_validation

    def to_context(self) -> dict[str, object]:
        return {
            "request_id": self.request.request_id,
            "world_snapshot": self.world_snapshot.to_context(),
            "reasoning": self.reasoning_result.to_context(),
            "planning": self.planning_result.to_context(),
            "initiative": self.initiative_result.to_context(),
            "stage_trace": self.stage_trace,
            "selected_plan_id": self.selected_plan_id,
            "ready_for_downstream_validation": self.ready_for_downstream_validation,
            "truth_established": False,
            "authority_granted": False,
            "execution_requested": False,
        }

    @property
    def authorizes_execution(self) -> bool:
        return False

    @property
    def executes_capability(self) -> bool:
        return False

    @property
    def mutates_external_state(self) -> bool:
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
    def selects_provider(self) -> bool:
        return False


class CognitiveRuntime:
    """Compose world, reasoning, planning, and proactive initiative exactly once per cycle."""

    def __init__(
        self,
        *,
        world_model: WorldModelSystem,
        reasoning_system: ReasoningSystem,
        planning_system: PlanningDecisionSystem,
        proactive_initiative: ProactiveInitiativeSystem,
    ) -> None:
        for name, value, expected in (
            ("world_model", world_model, WorldModelSystem),
            ("reasoning_system", reasoning_system, ReasoningSystem),
            ("planning_system", planning_system, PlanningDecisionSystem),
            ("proactive_initiative", proactive_initiative, ProactiveInitiativeSystem),
        ):
            if type(value) is not expected:
                raise TypeError(f"{name} must be a {expected.__name__}")
        self._world_model = world_model
        self._reasoning_system = reasoning_system
        self._planning_system = planning_system
        self._proactive_initiative = proactive_initiative

    @property
    def world_model(self) -> WorldModelSystem:
        return self._world_model

    @property
    def reasoning_system(self) -> ReasoningSystem:
        return self._reasoning_system

    @property
    def planning_system(self) -> PlanningDecisionSystem:
        return self._planning_system

    @property
    def proactive_initiative(self) -> ProactiveInitiativeSystem:
        return self._proactive_initiative

    def run(self, request: CognitiveRuntimeRequest) -> CognitiveRuntimeResult:
        if type(request) is not CognitiveRuntimeRequest:
            raise TypeError("request must be a CognitiveRuntimeRequest")

        for observation in request.world_observations:
            self._world_model.observe(observation)
        snapshot = self._world_model.snapshot(generated_at=request.world_generated_at)

        reasoning_context = ReasoningContext(
            request_id=request.request_id,
            created_at=request.created_at,
            question=request.question,
            world_snapshot_id=snapshot.snapshot_id,
            world_version=snapshot.version,
            world_observation_ids=snapshot.observation_ids,
            memory_ids=request.memory_ids,
            assumptions=request.assumptions,
            metadata=request.metadata,
        )
        hypotheses = tuple(
            Hypothesis(
                hypothesis_id=item.hypothesis_id,
                statement=item.statement,
                prior=item.prior,
                context=reasoning_context,
                provenance_ids=item.provenance_ids,
                assumptions=item.assumptions,
            )
            for item in request.hypotheses
        )
        evidence = tuple(
            EvidenceSignal(
                evidence_id=item.evidence_id,
                source_id=item.source_id,
                polarity=item.polarity,
                confidence=item.confidence,
                relevance=item.relevance,
                likelihood_ratio=item.likelihood_ratio,
                summary=item.summary,
                provenance_ids=item.provenance_ids,
                observed_at=item.observed_at,
            )
            for item in request.evidence
        )

        revisions = tuple(
            self._reasoning_system.revise_belief(hypothesis, evidence)
            for hypothesis in hypotheses
        )
        revision_by_hypothesis = {item.hypothesis_id: item for item in revisions}
        predictions: list[Prediction] = []
        for item in request.prediction_requests:
            revision = revision_by_hypothesis.get(item.hypothesis_id)
            if revision is None:
                raise CognitiveRuntimeValidationError(
                    f"prediction {item.prediction_id!r} references unknown hypothesis {item.hypothesis_id!r}"
                )
            predictions.append(
                self._reasoning_system.predict(
                    revision,
                    prediction_id=item.prediction_id,
                    outcome=item.outcome,
                    horizon_start=item.horizon_start,
                    horizon_end=item.horizon_end,
                    assumptions=item.assumptions,
                    adjustment=item.adjustment,
                )
            )
        reasoning_result = self._reasoning_system.reason(
            reasoning_context,
            hypotheses,
            evidence,
            tuple(predictions),
        )

        planning_context = PlanningContext(
            context_id=f"planning-{request.request_id}",
            created_at=request.created_at,
            world_snapshot=snapshot,
            reasoning_result=reasoning_result,
            goal=request.goal,
            additional_constraints=request.additional_constraints,
        )
        planning_result = self._planning_system.plan(planning_context, request.candidate_plans)
        candidate_map = {item.plan_id: item for item in request.candidate_plans}
        initiative_context = ProactiveInitiativeContext(
            planning_result=planning_result,
            candidate_plans=candidate_map,
        )
        initiative_result = self._proactive_initiative.compose(
            initiative_context,
            next_at=request.next_at,
            timezone=request.timezone,
        )

        return CognitiveRuntimeResult(
            request=request,
            world_snapshot=snapshot,
            reasoning_result=reasoning_result,
            planning_result=planning_result,
            initiative_result=initiative_result,
            stage_trace=(
                "WORLD_MODEL",
                "REASONING",
                "PLANNING",
                "PROACTIVE_INITIATIVE",
            ),
        )

    @property
    def authorizes_execution(self) -> bool:
        return False

    @property
    def executes_capability(self) -> bool:
        return False

    @property
    def mutates_external_state(self) -> bool:
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
    def selects_provider(self) -> bool:
        return False


def candidate_plan(
    *,
    plan_id: str,
    goal_id: str,
    descriptions: tuple[str, ...],
    expected_benefit: float,
    effort: float,
    risk: float,
    confidence: float,
) -> CandidatePlan:
    """Small helper for callers/tests that need deterministic plan construction."""
    steps = tuple(
        PlannedStep(step_id=f"{plan_id}-step-{index}", description=text)
        for index, text in enumerate(descriptions)
    )
    return CandidatePlan(
        plan_id=plan_id,
        goal_id=goal_id,
        steps=steps,
        expected_benefit=expected_benefit,
        effort=effort,
        risk=risk,
        confidence=confidence,
    )


__all__ = [
    "CognitiveEvidenceInput",
    "CognitiveHypothesisInput",
    "CognitivePredictionInput",
    "CognitiveRuntime",
    "CognitiveRuntimeRequest",
    "CognitiveRuntimeResult",
    "CognitiveRuntimeValidationError",
    "candidate_plan",
]