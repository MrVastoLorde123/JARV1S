from __future__ import annotations

import unittest

from src.core.interface_backend import InterfaceRequest, InterfaceResponse, InterfaceResponseStatus
from src.core.planning_decision import (
    CandidatePlan,
    Goal,
    PlanEvaluation,
    PlanFeasibility,
    PlanRanking,
    PlannedStep,
    PlanningContext,
    PlanningResult,
)
from src.core.proactive_initiative import (
    ProactiveInitiativeContext,
    ProactiveInitiativeSystem,
    ProactiveInitiativeValidationError,
)
from src.core.reasoning import ReasoningContext, ReasoningEvaluation, ReasoningResult
from src.core.runtime_kernel import JarvisRuntime
from src.core.world_model import WorldSnapshot
from src.scheduling import ProactiveSchedule


_NOW = "2026-09-17T16:00:00+00:00"
_LATER = "2026-09-17T17:00:00+00:00"


class _Orchestration:
    def dispatch(self, request: InterfaceRequest) -> InterfaceResponse:
        return InterfaceResponse(
            request_id=request.request_id,
            operation=request.operation,
            status=InterfaceResponseStatus.ACCEPTED,
            payload={},
            metadata={},
        )


def _base_planning(*, ambiguous: bool = False, feasible: bool = True) -> tuple[PlanningContext, PlanningResult, CandidatePlan]:
    goal = Goal(
        goal_id="goal-1",
        title="Improve system reliability",
        desired_outcome="Reduce recurring system failures",
        priority=0.8,
    )
    if ambiguous:
        from src.core.world_model import WorldConflict

        world = WorldSnapshot(
            snapshot_id="world-1",
            version=1,
            generated_at=_NOW,
            entities=(),
            relations=(),
            conflicts=(
                WorldConflict(
                    conflict_id="conflict-1",
                    subject_id="device-1",
                    subject_kind="ENTITY",
                    candidate_fingerprints=("a", "b"),
                    selected_fingerprint="b",
                    observation_ids=("obs-1", "obs-2"),
                ),
            ),
            observation_ids=("obs-1", "obs-2"),
        )
    else:
        world = WorldSnapshot(
            snapshot_id="world-1",
            version=1,
            generated_at=_NOW,
            entities=(),
            relations=(),
            conflicts=(),
            observation_ids=(),
        )
    reasoning_context = ReasoningContext(
        request_id="reason-1",
        created_at=_NOW,
        question="What should be improved?",
        world_snapshot_id="world-1",
        world_version=1,
    )
    reasoning = ReasoningResult(
        context=reasoning_context,
        revisions=(),
        predictions=(),
        trace=(),
        evaluation=ReasoningEvaluation(
            context_id="reason-1",
            hypothesis_count=0,
            revision_count=0,
            conflicted_count=0,
            prediction_count=0,
            evidence_count=0,
            trace_count=0,
        ),
    )
    planning_context = PlanningContext(
        context_id="planning-1",
        created_at=_NOW,
        world_snapshot=world,
        reasoning_result=reasoning,
        goal=goal,
    )
    plan = CandidatePlan(
        plan_id="plan-1",
        goal_id="goal-1",
        steps=(PlannedStep("step-1", "Inspect recurring failures"),),
        expected_benefit=0.9,
        effort=0.2,
        risk=0.1,
        confidence=0.8,
    )
    if feasible and not ambiguous:
        feasibility = PlanFeasibility.FEASIBLE
    elif ambiguous:
        feasibility = PlanFeasibility.REVIEW
    else:
        feasibility = PlanFeasibility.BLOCKED
    evaluation = PlanEvaluation(
        plan_id="plan-1",
        feasibility=feasibility,
        blockers=("blocked by missing input",) if feasibility is PlanFeasibility.BLOCKED else (),
        advisory_score=plan.advisory_score,
        rationale=("fixture",),
    )
    result = PlanningResult(
        context=planning_context,
        evaluations=(evaluation,),
        ranking=PlanRanking(
            ordered_plan_ids=("plan-1",),
            scores={"plan-1": evaluation.advisory_score},
            advisory_selected_plan_id=("plan-1" if feasibility is PlanFeasibility.FEASIBLE else None),
        ),
    )
    return planning_context, result, plan


class Phase9ProactiveInitiativeTests(unittest.TestCase):
    def test_feasible_plan_becomes_bounded_initiative_proposal(self) -> None:
        _, planning_result, plan = _base_planning()
        context = ProactiveInitiativeContext(planning_result, {"plan-1": plan})
        result = ProactiveInitiativeSystem().compose(context)
        self.assertIsNotNone(result.proposal)
        self.assertTrue(result.is_ready_for_downstream_validation)
        self.assertFalse(result.to_context()["authority_granted"])
        self.assertFalse(result.to_context()["execution_requested"])

    def test_blocked_plan_does_not_become_proposal(self) -> None:
        _, planning_result, plan = _base_planning(feasible=False)
        context = ProactiveInitiativeContext(planning_result, {"plan-1": plan})
        result = ProactiveInitiativeSystem().compose(context)
        self.assertIsNone(result.proposal)
        self.assertFalse(result.is_ready_for_downstream_validation)
        self.assertEqual(result.detections.detections[0].detection_type.value, "gap")

    def test_ambiguous_planning_requires_review_and_no_selection(self) -> None:
        _, planning_result, plan = _base_planning(ambiguous=True)
        context = ProactiveInitiativeContext(planning_result, {"plan-1": plan})
        result = ProactiveInitiativeSystem().compose(context)
        self.assertIsNone(result.proposal)
        self.assertFalse(result.planning_selection_available)
        self.assertEqual(result.detections.detections[0].detection_type.value, "change")

    def test_candidate_preserves_world_reasoning_and_plan_lineage(self) -> None:
        _, planning_result, plan = _base_planning()
        context = ProactiveInitiativeContext(planning_result, {"plan-1": plan})
        candidate = ProactiveInitiativeSystem().build_candidate(context)
        self.assertIn("world-1", candidate.context_refs)
        self.assertIn("reason-1", candidate.context_refs)
        self.assertIn("plan-1", candidate.context_refs)
        self.assertFalse(candidate.to_dict()["authorization_granted"])

    def test_evaluation_projects_planning_risk_effort_confidence(self) -> None:
        _, planning_result, plan = _base_planning()
        context = ProactiveInitiativeContext(planning_result, {"plan-1": plan})
        system = ProactiveInitiativeSystem()
        candidate = system.build_candidate(context)
        evaluation = system.build_evaluation(context, candidate)
        self.assertEqual(evaluation.risk_score, 0.1)
        self.assertEqual(evaluation.effort_score, 0.2)
        self.assertEqual(evaluation.confidence_score, 0.8)
        self.assertFalse(evaluation.to_dict()["authorization_granted"])

    def test_proposal_requires_confirmation_downstream(self) -> None:
        _, planning_result, plan = _base_planning()
        context = ProactiveInitiativeContext(planning_result, {"plan-1": plan})
        system = ProactiveInitiativeSystem()
        candidate = system.build_candidate(context)
        evaluation = system.build_evaluation(context, candidate)
        proposal = system.build_proposal(context, candidate, evaluation)
        self.assertTrue(proposal.to_dict()["confirmation_required"])
        self.assertFalse(proposal.to_dict()["authorization_granted"])
        self.assertFalse(proposal.to_dict()["execution_requested"])

    def test_optional_schedule_is_only_a_surface_recommendation(self) -> None:
        _, planning_result, plan = _base_planning()
        context = ProactiveInitiativeContext(planning_result, {"plan-1": plan})
        result = ProactiveInitiativeSystem().compose(context, next_at=_LATER)
        self.assertIsInstance(result.schedule, ProactiveSchedule)
        self.assertFalse(result.schedule.to_dict()["scheduling_is_authorization"])
        self.assertFalse(result.schedule.to_dict()["execution_requested"])

    def test_runtime_rejects_wrong_proactive_type(self) -> None:
        with self.assertRaises(TypeError):
            JarvisRuntime(
                orchestration=_Orchestration(),
                session_id="session-proactive-1",
                actor_id="actor-proactive-1",
                proactive_initiative=object(),
            )

    def test_runtime_accepts_proactive_initiative_without_authority(self) -> None:
        system = ProactiveInitiativeSystem()
        runtime = JarvisRuntime(
            orchestration=_Orchestration(),
            session_id="session-proactive-1",
            actor_id="actor-proactive-1",
            proactive_initiative=system,
        )
        self.assertIs(runtime.proactive_initiative, system)
        self.assertFalse(runtime.authorizes_execution)
        self.assertFalse(runtime.executes_capability)
        self.assertFalse(runtime.persists_state)
        self.assertFalse(runtime.establishes_truth)
        self.assertFalse(runtime.establishes_certainty)

    def test_system_authority_surface_is_closed(self) -> None:
        system = ProactiveInitiativeSystem()
        self.assertFalse(system.authorizes_execution)
        self.assertFalse(system.executes_capability)
        self.assertFalse(system.mutates_state)
        self.assertFalse(system.persists_state)
        self.assertFalse(system.establishes_truth)
        self.assertFalse(system.establishes_certainty)
        self.assertFalse(system.selects_provider)

    def test_missing_selected_plan_is_rejected_explicitly(self) -> None:
        _, planning_result, _ = _base_planning()
        with self.assertRaises(ProactiveInitiativeValidationError):
            ProactiveInitiativeContext(planning_result, {})


if __name__ == "__main__":
    unittest.main()
