"""Focused Phase 10 tests for the typed cognitive runtime composition."""
from __future__ import annotations

import unittest

from src.core.cognitive_runtime import (
    CognitiveEvidenceInput,
    CognitiveHypothesisInput,
    CognitivePredictionInput,
    CognitiveRuntime,
    CognitiveRuntimeRequest,
    CognitiveRuntimeValidationError,
    candidate_plan,
)
from src.core.planning_decision import Goal, PlanningDecisionSystem
from src.core.reasoning import EvidencePolarity, ReasoningSystem
from src.core.proactive_initiative import ProactiveInitiativeSystem
from src.core.world_model import WorldEntity, WorldEntityType, WorldModelSystem, WorldObservation


NOW = "2026-09-17T12:00:00+00:00"


class Phase10CognitiveRuntimeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.runtime = CognitiveRuntime(
            world_model=WorldModelSystem(),
            reasoning_system=ReasoningSystem(),
            planning_system=PlanningDecisionSystem(),
            proactive_initiative=ProactiveInitiativeSystem(),
        )
        self.goal = Goal(
            goal_id="goal-1",
            title="Investigate device state",
            desired_outcome="Determine whether the device requires attention.",
            priority=0.7,
        )
        self.plan = candidate_plan(
            plan_id="plan-1",
            goal_id="goal-1",
            descriptions=("inspect state", "record result"),
            expected_benefit=0.8,
            effort=0.2,
            risk=0.1,
            confidence=0.9,
        )
        self.observation = WorldObservation(
            observation_id="obs-1",
            observed_at=NOW,
            provenance_ids=("prov-1",),
            entity=WorldEntity(
                entity_id="device-1",
                entity_type=WorldEntityType.DEVICE,
                label="Test device",
                attributes={"state": "unknown"},
                confidence=0.9,
                provenance_ids=("prov-1",),
            ),
        )
        self.hypothesis = CognitiveHypothesisInput(
            hypothesis_id="hyp-1",
            statement="The device may require attention.",
            prior=0.5,
            provenance_ids=("prov-1",),
        )
        self.evidence = CognitiveEvidenceInput(
            evidence_id="evidence-1",
            source_id="source-1",
            polarity=EvidencePolarity.SUPPORTS,
            confidence=0.9,
            relevance=0.9,
            likelihood_ratio=2.0,
            summary="The observed state is not normal.",
            provenance_ids=("prov-1",),
            observed_at=NOW,
        )

    def _request(self, **overrides) -> CognitiveRuntimeRequest:
        values = dict(
            request_id="cycle-1",
            created_at=NOW,
            question="What should happen with device-1?",
            world_generated_at=NOW,
            goal=self.goal,
            candidate_plans=(self.plan,),
            world_observations=(self.observation,),
            hypotheses=(self.hypothesis,),
            evidence=(self.evidence,),
            memory_ids=("memory-1",),
            assumptions=("the observation is current",),
        )
        values.update(overrides)
        return CognitiveRuntimeRequest(**values)

    def test_complete_cycle_composes_world_reasoning_planning_and_initiative(self) -> None:
        result = self.runtime.run(self._request())
        self.assertEqual(
            result.stage_trace,
            ("WORLD_MODEL", "REASONING", "PLANNING", "PROACTIVE_INITIATIVE"),
        )
        self.assertEqual(result.selected_plan_id, "plan-1")
        self.assertIsNotNone(result.proposal)
        self.assertTrue(result.ready_for_downstream_validation)

    def test_world_snapshot_lineage_reaches_reasoning_and_planning(self) -> None:
        result = self.runtime.run(self._request())
        self.assertEqual(result.reasoning_result.context.world_snapshot_id, result.world_snapshot.snapshot_id)
        self.assertEqual(
            result.planning_result.context.reasoning_result.context.request_id,
            "cycle-1",
        )
        self.assertEqual(result.planning_result.context.world_snapshot.snapshot_id, result.world_snapshot.snapshot_id)

    def test_prediction_is_derived_from_runtime_revision(self) -> None:
        request = self._request(
            prediction_requests=(
                CognitivePredictionInput(
                    prediction_id="prediction-1",
                    hypothesis_id="hyp-1",
                    outcome="device requires inspection",
                    horizon_start=NOW,
                    horizon_end="2026-09-18T12:00:00+00:00",
                ),
            )
        )
        result = self.runtime.run(request)
        prediction = result.reasoning_result.predictions[0]
        revision = result.reasoning_result.revisions[0]
        self.assertEqual(prediction.revision_id, revision.revision_id)
        self.assertEqual(prediction.prediction_id, "prediction-1")

    def test_missing_prediction_hypothesis_is_rejected(self) -> None:
        request = self._request(
            prediction_requests=(
                CognitivePredictionInput(
                    prediction_id="prediction-1",
                    hypothesis_id="missing",
                    outcome="unknown",
                    horizon_start=NOW,
                    horizon_end="2026-09-18T12:00:00+00:00",
                ),
            )
        )
        with self.assertRaises(CognitiveRuntimeValidationError):
            self.runtime.run(request)

    def test_ambiguous_reasoning_blocks_plan_selection(self) -> None:
        contradictory = CognitiveEvidenceInput(
            evidence_id="evidence-2",
            source_id="source-2",
            polarity=EvidencePolarity.CONTRADICTS,
            confidence=0.9,
            relevance=0.9,
            likelihood_ratio=2.0,
            summary="A second observation contradicts the first interpretation.",
            provenance_ids=("prov-2",),
            observed_at=NOW,
        )
        result = self.runtime.run(self._request(evidence=(self.evidence, contradictory)))
        self.assertTrue(result.reasoning_result.is_ambiguous)
        self.assertIsNone(result.selected_plan_id)
        self.assertIsNone(result.proposal)

    def test_blocked_candidate_never_becomes_proposal(self) -> None:
        blocked = candidate_plan(
            plan_id="plan-blocked",
            goal_id="goal-1",
            descriptions=("blocked action",),
            expected_benefit=1.0,
            effort=0.1,
            risk=0.1,
            confidence=1.0,
        )
        blocked = type(blocked)(
            plan_id=blocked.plan_id,
            goal_id=blocked.goal_id,
            steps=blocked.steps,
            expected_benefit=blocked.expected_benefit,
            effort=blocked.effort,
            risk=blocked.risk,
            confidence=blocked.confidence,
            blockers=("requires confirmation boundary not yet crossed",),
        )
        result = self.runtime.run(self._request(candidate_plans=(blocked,)))
        self.assertEqual(result.planning_result.evaluations[0].feasibility.value, "BLOCKED")
        self.assertIsNone(result.proposal)

    def test_schedule_is_still_only_an_artifact(self) -> None:
        result = self.runtime.run(
            self._request(next_at="2026-09-18T09:00:00+00:00", timezone="America/Paramaribo")
        )
        self.assertIsNotNone(result.initiative_result.schedule)
        self.assertFalse(result.authorizes_execution)
        self.assertFalse(result.executes_capability)

    def test_runtime_does_not_establish_truth_or_certainty(self) -> None:
        result = self.runtime.run(self._request())
        self.assertFalse(result.establishes_truth)
        self.assertFalse(result.establishes_certainty)
        context = result.to_context()
        self.assertFalse(context["truth_established"])
        self.assertFalse(context["authority_granted"])

    def test_memory_ids_are_lineage_only(self) -> None:
        result = self.runtime.run(self._request(memory_ids=("memory-a", "memory-b")))
        self.assertEqual(result.reasoning_result.context.memory_ids, ("memory-a", "memory-b"))
        self.assertFalse(result.persists_state)

    def test_duplicate_observation_ids_are_rejected_at_request_boundary(self) -> None:
        with self.assertRaises(CognitiveRuntimeValidationError):
            self._request(
                world_observations=(self.observation, self.observation),
            )

    def test_duplicate_plan_ids_are_rejected_at_request_boundary(self) -> None:
        with self.assertRaises(CognitiveRuntimeValidationError):
            self._request(candidate_plans=(self.plan, self.plan))

    def test_cycle_is_reusable_without_replacing_the_world_model(self) -> None:
        first = self.runtime.run(self._request())
        second = self.runtime.run(
            self._request(request_id="cycle-2", world_observations=())
        )
        self.assertEqual(first.world_snapshot.snapshot_id, second.world_snapshot.snapshot_id)
        self.assertEqual(second.reasoning_result.context.world_version, first.world_snapshot.version)


if __name__ == "__main__":
    unittest.main()