from __future__ import annotations

import unittest

from src.core.interface_backend import InterfaceRequest, InterfaceResponse, InterfaceResponseStatus
from src.core.reasoning import (
    BeliefRevision,
    EvidencePolarity,
    EvidenceSignal,
    Hypothesis,
    Prediction,
    ReasoningContext,
    ReasoningEvaluation,
    ReasoningResult,
    ReasoningStepKind,
    ReasoningSystem,
    RevisionStatus,
    ReasoningTraceStep,
)
from src.core.runtime_kernel import JarvisRuntime


_NOW = "2026-09-17T16:00:00+00:00"
_LATER = "2026-09-17T17:00:00+00:00"


def _context() -> ReasoningContext:
    return ReasoningContext(
        request_id="reason-1",
        created_at=_NOW,
        question="Will the device remain reachable?",
        world_snapshot_id="world-1",
        world_version=4,
        world_observation_ids=("obs-1",),
        memory_ids=("mem-1",),
        assumptions=("network unchanged",),
    )


def _evidence(
    evidence_id: str,
    polarity: EvidencePolarity,
    *,
    likelihood_ratio: float = 3.0,
    confidence: float = 0.9,
    relevance: float = 0.8,
) -> EvidenceSignal:
    return EvidenceSignal(
        evidence_id=evidence_id,
        source_id=f"source-{evidence_id}",
        polarity=polarity,
        confidence=confidence,
        relevance=relevance,
        likelihood_ratio=likelihood_ratio,
        summary=f"Evidence {evidence_id}",
        provenance_ids=(f"prov-{evidence_id}",),
        observed_at=_NOW,
    )


def _hypothesis() -> Hypothesis:
    return Hypothesis(
        hypothesis_id="hyp-1",
        statement="The device remains reachable.",
        prior=0.5,
        context=_context(),
        provenance_ids=("prov-hyp-1",),
        assumptions=("network unchanged",),
    )


class _Orchestration:
    def dispatch(self, request: InterfaceRequest) -> InterfaceResponse:
        return InterfaceResponse(
            request_id=request.request_id,
            operation=request.operation,
            status=InterfaceResponseStatus.ACCEPTED,
            payload={},
            metadata={},
        )


class Phase7ReasoningTests(unittest.TestCase):
    def setUp(self) -> None:
        self.system = ReasoningSystem()

    def test_reasoning_context_requires_timezone_and_bounded_world_version(self) -> None:
        context = _context()
        self.assertEqual(context.world_version, 4)
        with self.assertRaises(ValueError):
            ReasoningContext(
                request_id="x",
                created_at="2026-09-17T16:00:00",
                question="q",
                world_snapshot_id="world",
                world_version=1,
            )

    def test_reasoning_context_rejects_duplicate_source_ids(self) -> None:
        with self.assertRaises(ValueError):
            ReasoningContext(
                request_id="reason-2",
                created_at=_NOW,
                question="q",
                world_snapshot_id="world",
                world_version=1,
                world_observation_ids=("obs-1", "obs-1"),
            )

    def test_evidence_requires_provenance(self) -> None:
        with self.assertRaises(ValueError):
            EvidenceSignal(
                evidence_id="e-1",
                source_id="s-1",
                polarity=EvidencePolarity.SUPPORTS,
                confidence=0.8,
                relevance=0.8,
                likelihood_ratio=2.0,
                summary="evidence",
                provenance_ids=(),
                observed_at=_NOW,
            )

    def test_evidence_bounds_confidence_relevance_and_likelihood_ratio(self) -> None:
        for kwargs in (
            {"confidence": 1.1},
            {"relevance": -0.1},
            {"likelihood_ratio": 101.0},
        ):
            with self.assertRaises(ValueError):
                _evidence("bad", EvidencePolarity.SUPPORTS, **kwargs)

    def test_evidence_weight_is_zero_for_context_only(self) -> None:
        signal = _evidence("context", EvidencePolarity.CONTEXT)
        self.assertEqual(signal.weighted_log_likelihood, 0.0)

    def test_hypothesis_requires_bounded_prior(self) -> None:
        with self.assertRaises(ValueError):
            Hypothesis(
                hypothesis_id="hyp-bad",
                statement="bad",
                prior=1.0,
                context=_context(),
            )

    def test_belief_revision_with_support_increases_posterior(self) -> None:
        revision = self.system.revise_belief(
            _hypothesis(),
            (_evidence("support-1", EvidencePolarity.SUPPORTS),),
        )
        self.assertIsInstance(revision, BeliefRevision)
        self.assertGreater(revision.posterior, revision.prior)
        self.assertEqual(revision.status, RevisionStatus.REVISED)
        self.assertFalse(revision.to_context()["truth_established"])

    def test_belief_revision_with_contradiction_decreases_posterior(self) -> None:
        revision = self.system.revise_belief(
            _hypothesis(),
            (_evidence("contra-1", EvidencePolarity.CONTRADICTS),),
        )
        self.assertLess(revision.posterior, revision.prior)
        self.assertEqual(revision.status, RevisionStatus.REVISED)

    def test_belief_revision_retains_explicit_conflict(self) -> None:
        revision = self.system.revise_belief(
            _hypothesis(),
            (
                _evidence("support-1", EvidencePolarity.SUPPORTS),
                _evidence("contra-1", EvidencePolarity.CONTRADICTS),
            ),
        )
        self.assertEqual(revision.status, RevisionStatus.CONFLICTED)
        self.assertGreater(revision.support_weight, 0.0)
        self.assertGreater(revision.contradiction_weight, 0.0)

    def test_empty_evidence_leaves_prior_unchanged(self) -> None:
        revision = self.system.revise_belief(_hypothesis(), ())
        self.assertEqual(revision.posterior, revision.prior)
        self.assertEqual(revision.status, RevisionStatus.UNCHANGED)

    def test_prediction_is_bounded_and_advisory(self) -> None:
        revision = self.system.revise_belief(
            _hypothesis(),
            (_evidence("support-1", EvidencePolarity.SUPPORTS),),
        )
        prediction = self.system.predict(
            revision,
            prediction_id="pred-1",
            outcome="device remains reachable",
            horizon_start=_NOW,
            horizon_end=_LATER,
        )
        self.assertIsInstance(prediction, Prediction)
        self.assertTrue(prediction.to_context()["is_advisory"])
        self.assertFalse(prediction.to_context()["truth_established"])

    def test_prediction_rejects_invalid_horizon(self) -> None:
        revision = self.system.revise_belief(_hypothesis(), ())
        with self.assertRaises(ValueError):
            self.system.predict(
                revision,
                prediction_id="pred-bad",
                outcome="x",
                horizon_start=_LATER,
                horizon_end=_NOW,
            )

    def test_prediction_adjustment_is_bounded(self) -> None:
        revision = self.system.revise_belief(_hypothesis(), ())
        with self.assertRaises(ValueError):
            self.system.predict(
                revision,
                prediction_id="pred-bad",
                outcome="x",
                horizon_start=_NOW,
                horizon_end=_LATER,
                adjustment=0.3,
            )

    def test_reasoning_orders_predictions_deterministically(self) -> None:
        context = _context()
        hypothesis = _hypothesis()
        revision = self.system.revise_belief(
            hypothesis,
            (_evidence("support-1", EvidencePolarity.SUPPORTS),),
        )
        low = self.system.predict(
            revision,
            prediction_id="pred-b",
            outcome="B",
            horizon_start=_NOW,
            horizon_end=_LATER,
            adjustment=-0.1,
        )
        high = self.system.predict(
            revision,
            prediction_id="pred-a",
            outcome="A",
            horizon_start=_NOW,
            horizon_end=_LATER,
        )
        result = self.system.reason(context, (hypothesis,), (_evidence("support-1", EvidencePolarity.SUPPORTS),), (low, high))
        self.assertIsInstance(result, ReasoningResult)
        self.assertEqual(result.predictions[0].prediction_id, "pred-a")
        self.assertGreaterEqual(result.evaluation.trace_count, 1)

    def test_reasoning_requires_matching_hypothesis_context(self) -> None:
        context = _context()
        mismatched = ReasoningContext(
            request_id="other",
            created_at=_NOW,
            question="same",
            world_snapshot_id="world-2",
            world_version=5,
        )
        hypothesis = Hypothesis(
            hypothesis_id="hyp-2",
            statement="another",
            prior=0.5,
            context=mismatched,
        )
        with self.assertRaises(ValueError):
            self.system.reason(context, (hypothesis,), ())

    def test_reasoning_result_is_ambiguous_when_revision_is_conflicted(self) -> None:
        context = _context()
        hypothesis = _hypothesis()
        evidence = (
            _evidence("support-1", EvidencePolarity.SUPPORTS),
            _evidence("contra-1", EvidencePolarity.CONTRADICTS),
        )
        result = self.system.reason(context, (hypothesis,), evidence)
        self.assertTrue(result.is_ambiguous)
        self.assertFalse(result.to_context()["truth_established"])

    def test_trace_steps_are_typed_and_immutable(self) -> None:
        step = ReasoningTraceStep(
            step_id="step-1",
            kind=ReasoningStepKind.CONTEXT,
            input_ids=("world-1",),
            output_ids=("reason-1",),
            summary="context accepted",
        )
        self.assertEqual(step.kind, ReasoningStepKind.CONTEXT)
        with self.assertRaises((AttributeError, TypeError)):
            step.summary = "changed"  # type: ignore[misc]

    def test_reasoning_evaluation_rejects_impossible_conflict_count(self) -> None:
        with self.assertRaises(ValueError):
            ReasoningEvaluation(
                context_id="reason-1",
                hypothesis_count=1,
                revision_count=0,
                conflicted_count=1,
                prediction_count=0,
                evidence_count=0,
                trace_count=0,
            )

    def test_reasoning_summary_closes_authority_surface(self) -> None:
        summary = self.system.summary()
        self.assertFalse(summary["truth_established"])
        self.assertFalse(summary["authority_granted"])
        self.assertFalse(summary["execution_requested"])
        self.assertFalse(summary["provider_selected"])
        self.assertFalse(self.system.authorizes_execution)
        self.assertFalse(self.system.executes_capability)
        self.assertFalse(self.system.mutates_external_state)
        self.assertFalse(self.system.persists_state)
        self.assertFalse(self.system.establishes_truth)
        self.assertFalse(self.system.establishes_certainty)
        self.assertFalse(self.system.selects_provider)

    def test_reasoning_context_is_provider_neutral(self) -> None:
        projected = _context().to_context()
        self.assertEqual(projected["world_snapshot_id"], "world-1")
        self.assertNotIn("provider", projected)
        self.assertFalse(projected["authority_granted"])

    def test_runtime_accepts_reasoning_without_gaining_authority(self) -> None:
        reasoning = ReasoningSystem()
        runtime = JarvisRuntime(
            orchestration=_Orchestration(),
            session_id="session-reasoning-1",
            actor_id="actor-reasoning-1",
            reasoning_system=reasoning,
        )
        self.assertIs(runtime.reasoning_system, reasoning)
        self.assertFalse(runtime.authorizes_execution)
        self.assertFalse(runtime.executes_capability)
        self.assertFalse(runtime.establishes_truth)
        self.assertFalse(runtime.establishes_certainty)

    def test_runtime_rejects_wrong_reasoning_type(self) -> None:
        with self.assertRaises(TypeError):
            JarvisRuntime(
                orchestration=_Orchestration(),
                session_id="session-reasoning-1",
                actor_id="actor-reasoning-1",
                reasoning_system=object(),
            )


if __name__ == "__main__":
    unittest.main()