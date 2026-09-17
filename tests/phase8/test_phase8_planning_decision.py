from __future__ import annotations

import unittest

from src.core.planning_decision import (
    CandidatePlan,
    Goal,
    GoalStatus,
    PlanFeasibility,
    PlannedStep,
    PlanningContext,
    PlanningDecisionSystem,
)
from src.core.reasoning import (
    ReasoningContext,
    ReasoningEvaluation,
    ReasoningResult,
)
from src.core.runtime_kernel import JarvisRuntime
from src.core.world_model import WorldSnapshot


_NOW = "2026-09-17T16:00:00+00:00"


def _world(*, ambiguous: bool = False) -> WorldSnapshot:
    from src.core.world_model import WorldConflict

    conflicts = ()
    if ambiguous:
        conflicts = (
            WorldConflict(
                conflict_id="conflict-1",
                subject_id="device-1",
                subject_kind="ENTITY",
                candidate_fingerprints=("a", "b"),
                selected_fingerprint="a",
                observation_ids=("obs-1", "obs-2"),
            ),
        )
    return WorldSnapshot(
        snapshot_id="world-1",
        version=1,
        generated_at=_NOW,
        entities=(),
        relations=(),
        conflicts=conflicts,
        observation_ids=(),
    )


def _reasoning(*, ambiguous: bool = False) -> ReasoningResult:
    context = ReasoningContext(
        request_id="reasoning-1",
        created_at=_NOW,
        question="How should this goal be approached?",
        world_snapshot_id="world-1",
        world_version=1,
    )
    evaluation = ReasoningEvaluation(
        context_id=context.request_id,
        hypothesis_count=0,
        revision_count=0 if not ambiguous else 1,
        conflicted_count=0 if not ambiguous else 1,
        prediction_count=0,
        evidence_count=0,
        trace_count=0,
    )
    if not ambiguous:
        revisions = ()
    else:
        from src.core.reasoning import BeliefRevision, RevisionStatus

        revisions = (
            BeliefRevision(
                revision_id="rev-1",
                hypothesis_id="hyp-1",
                prior=0.5,
                posterior=0.5,
                net_evidence=0.0,
                support_weight=0.4,
                contradiction_weight=0.4,
                evidence_ids=("e1", "e2"),
                status=RevisionStatus.CONFLICTED,
            ),
        )
    return ReasoningResult(
        context=context,
        revisions=revisions,
        predictions=(),
        trace=(),
        evaluation=evaluation,
    )


def _context(*, ambiguous_world: bool = False, ambiguous_reasoning: bool = False, status: GoalStatus = GoalStatus.ACTIVE) -> PlanningContext:
    return PlanningContext(
        context_id="planning-1",
        created_at=_NOW,
        world_snapshot=_world(ambiguous=ambiguous_world),
        reasoning_result=_reasoning(ambiguous=ambiguous_reasoning),
        goal=Goal(
            goal_id="goal-1",
            title="Improve system reliability",
            desired_outcome="Reduce avoidable failures",
            priority=0.8,
            status=status,
        ),
    )


def _plan(plan_id: str, *, blockers: tuple[str, ...] = (), benefit: float = 0.8, effort: float = 0.3, risk: float = 0.2, confidence: float = 0.9) -> CandidatePlan:
    return CandidatePlan(
        plan_id=plan_id,
        goal_id="goal-1",
        steps=(
            PlannedStep(step_id=f"{plan_id}-prepare", description="Prepare diagnostics"),
            PlannedStep(
                step_id=f"{plan_id}-act",
                description="Apply bounded improvement",
                prerequisite_ids=(f"{plan_id}-prepare",),
            ),
        ),
        expected_benefit=benefit,
        effort=effort,
        risk=risk,
        confidence=confidence,
        blockers=blockers,
    )


class Phase8PlanningDecisionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.system = PlanningDecisionSystem()

    def test_goal_is_bounded_and_non_authoritative(self) -> None:
        goal = _context().goal
        self.assertEqual(goal.goal_id, "goal-1")
        self.assertFalse(goal.to_context()["authorization_granted"])
        with self.assertRaises(Exception):
            Goal("goal-2", "Bad", "Outcome", priority=1.1)

    def test_planned_step_requires_known_prerequisites(self) -> None:
        with self.assertRaises(ValueError):
            CandidatePlan(
                plan_id="bad",
                goal_id="goal-1",
                steps=(PlannedStep("step-1", "Do it", ("missing",)),),
                expected_benefit=0.5,
                effort=0.5,
                risk=0.5,
                confidence=0.5,
            )

    def test_candidate_plan_score_is_bounded(self) -> None:
        plan = _plan("plan-1")
        self.assertGreaterEqual(plan.advisory_score, 0.0)
        self.assertLessEqual(plan.advisory_score, 1.0)
        self.assertFalse(plan.to_context()["authorization_granted"])

    def test_blocked_plan_is_not_feasible(self) -> None:
        evaluation = self.system.evaluate(
            _context(),
            _plan("plan-1", blockers=("required input missing",)),
        )
        self.assertEqual(evaluation.feasibility, PlanFeasibility.BLOCKED)
        self.assertIn("required input missing", evaluation.blockers)

    def test_non_active_goal_blocks_candidate(self) -> None:
        evaluation = self.system.evaluate(
            _context(status=GoalStatus.PAUSED),
            _plan("plan-1"),
        )
        self.assertEqual(evaluation.feasibility, PlanFeasibility.BLOCKED)

    def test_ambiguous_reasoning_requires_review(self) -> None:
        evaluation = self.system.evaluate(
            _context(ambiguous_reasoning=True),
            _plan("plan-1"),
        )
        self.assertEqual(evaluation.feasibility, PlanFeasibility.REVIEW)

    def test_ambiguous_world_requires_review(self) -> None:
        evaluation = self.system.evaluate(
            _context(ambiguous_world=True),
            _plan("plan-1"),
        )
        self.assertEqual(evaluation.feasibility, PlanFeasibility.REVIEW)

    def test_wrong_goal_is_rejected(self) -> None:
        plan = _plan("plan-1")
        wrong_goal = CandidatePlan(
            plan_id=plan.plan_id,
            goal_id="other-goal",
            steps=plan.steps,
            expected_benefit=plan.expected_benefit,
            effort=plan.effort,
            risk=plan.risk,
            confidence=plan.confidence,
        )
        with self.assertRaises(ValueError):
            self.system.evaluate(_context(), wrong_goal)

    def test_ranking_is_deterministic(self) -> None:
        context = _context()
        evaluations = (
            self.system.evaluate(context, _plan("b", benefit=0.8)),
            self.system.evaluate(context, _plan("a", benefit=0.8)),
        )
        ranking = self.system.rank(evaluations)
        self.assertEqual(ranking.ordered_plan_ids, ("a", "b"))
        self.assertEqual(ranking.advisory_selected_plan_id, "a")

    def test_blocked_plan_never_beats_feasible_plan(self) -> None:
        context = _context()
        evaluations = (
            self.system.evaluate(context, _plan("blocked", blockers=("x",), benefit=1.0)),
            self.system.evaluate(context, _plan("good", benefit=0.6)),
        )
        ranking = self.system.rank(evaluations)
        self.assertEqual(ranking.advisory_selected_plan_id, "good")
        self.assertEqual(ranking.ordered_plan_ids[0], "good")

    def test_empty_candidate_set_has_no_selection(self) -> None:
        result = self.system.plan(_context(), ())
        self.assertEqual(result.evaluations, ())
        self.assertIsNone(result.ranking.advisory_selected_plan_id)

    def test_planning_result_reports_ambiguity(self) -> None:
        result = self.system.plan(_context(ambiguous_world=True), (_plan("plan-1"),))
        self.assertTrue(result.is_ambiguous)
        self.assertEqual(result.evaluations[0].feasibility, PlanFeasibility.REVIEW)

    def test_summary_closes_authority_surface(self) -> None:
        summary = self.system.summary()
        self.assertFalse(summary["authorizes_execution"])
        self.assertFalse(summary["executes_capability"])
        self.assertFalse(summary["mutates_external_state"])
        self.assertFalse(summary["persists_state"])
        self.assertFalse(summary["establishes_truth"])
        self.assertFalse(summary["establishes_certainty"])
        self.assertFalse(summary["selection_is_authorization"])
        self.assertFalse(self.system.authorizes_execution)
        self.assertFalse(self.system.executes_capability)

    def test_runtime_accepts_planning_without_authority(self) -> None:
        class _Orchestration:
            def dispatch(self, request):
                return None

        runtime = JarvisRuntime(
            orchestration=_Orchestration(),
            session_id="planning-session",
            actor_id="planner",
            planning_system=self.system,
        )
        self.assertIs(runtime.planning_system, self.system)
        self.assertFalse(runtime.authorizes_execution)
        self.assertFalse(runtime.executes_capability)
        self.assertFalse(runtime.establishes_truth)
        self.assertFalse(runtime.establishes_certainty)

    def test_runtime_rejects_wrong_planning_type(self) -> None:
        class _Orchestration:
            def dispatch(self, request):
                return None

        with self.assertRaises(TypeError):
            JarvisRuntime(
                orchestration=_Orchestration(),
                session_id="planning-session",
                actor_id="planner",
                planning_system=object(),
            )


if __name__ == "__main__":
    unittest.main()
