import json
import unittest

from src.learning.adaptation import AdaptationKind, AdaptationProposal, AdaptationRecord, AdaptationState
from src.learning.consolidation import RetrievalResult
from src.learning.evaluation import Evaluation, EvaluationState
from src.learning.intelligence_integration import IntelligenceContext, IntelligenceIntegrator
from src.learning.reasoning_quality import FeedbackSignal, ReasoningFeedback
from src.learning.reliability import ReliabilityRecord, ReliabilityState


class IntelligenceIntegrationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.integrator = IntelligenceIntegrator()
        self.evaluation = Evaluation(
            evaluation_id="eval-1",
            experience_id="exp-1",
            state=EvaluationState.SUCCESS,
            evidence_ids=("evidence-1",),
            rationale="successful outcome",
            confidence=0.9,
        )
        self.memory = RetrievalResult(
            memory_id="memory-1",
            score=0.8,
            content="use the reliable cached workflow",
            provenance={"source": "m10.4", "memory_id": "memory-1"},
        )
        self.feedback = ReasoningFeedback(
            feedback_id="feedback-1",
            assessment_id="quality-1",
            signal=FeedbackSignal.IMPROVE,
            target="reasoning",
            rationale="reduce unnecessary branching",
            confidence=0.8,
        )
        proposal = AdaptationProposal(
            proposal_id="adapt-1",
            kind=AdaptationKind.BEHAVIOR,
            target="response.detail",
            current_value="normal",
            proposed_value="concise",
            supporting_evaluation_ids=("eval-1",),
            rationale="improve clarity",
        )
        self.accepted_adaptation = AdaptationRecord(
            record_id="adapt-1:record",
            proposal=proposal,
            state=AdaptationState.ACCEPTED,
            acceptance_reference="user-acceptance-1",
        )
        self.rejected_adaptation = AdaptationRecord(
            record_id="adapt-2:record",
            proposal=proposal.__class__(
                proposal_id="adapt-2",
                kind=proposal.kind,
                target=proposal.target,
                current_value=proposal.current_value,
                proposed_value=proposal.proposed_value,
                supporting_evaluation_ids=proposal.supporting_evaluation_ids,
                rationale=proposal.rationale,
            ),
            state=AdaptationState.REJECTED,
            rejection_reference="user-rejection-1",
        )
        self.retained_reliability = ReliabilityRecord(
            record_id="memory-1:reliability:1",
            artifact_id="memory-1",
            state=ReliabilityState.RETAINED,
            assessment_id="reliability-1",
        )
        self.reversed_reliability = ReliabilityRecord(
            record_id="memory-2:reliability:2->reversed",
            artifact_id="memory-2",
            state=ReliabilityState.REVERSED,
            assessment_id="reliability-2",
            predecessor_id="memory-2:reliability:1",
            resolution_reference="reversal-1",
        )
        self.superseded_reliability = ReliabilityRecord(
            record_id="memory-3:reliability:2->superseded",
            artifact_id="memory-3",
            state=ReliabilityState.SUPERSEDED,
            assessment_id="reliability-3",
            predecessor_id="memory-3:reliability:1",
            resolution_reference="supersession-1",
            supersession_reference="memory-3-v2",
        )

    def test_build_context_is_immutable_and_provider_neutral(self) -> None:
        context = self.integrator.build_context("  how should I reason?  ")
        self.assertIsInstance(context, IntelligenceContext)
        self.assertEqual(context.query, "how should I reason?")
        with self.assertRaises(TypeError):
            context.provenance["x"] = "y"

    def test_only_positive_retrieval_evidence_enters_context(self) -> None:
        zero = RetrievalResult("memory-zero", 0.0, "zero score", {})
        context = self.integrator.build_context("query", memory_results=(self.memory, zero))
        self.assertEqual(tuple(item.memory_id for item in context.memories), ("memory-1",))

    def test_reversed_memory_is_excluded_from_context(self) -> None:
        reversed_memory = RetrievalResult("memory-2", 0.9, "reversed lesson", {})
        context = self.integrator.build_context(
            "query",
            memory_results=(self.memory, reversed_memory),
            reliability=(self.reversed_reliability,),
        )
        self.assertEqual(tuple(item.memory_id for item in context.memories), ("memory-1",))

    def test_superseded_memory_is_excluded_from_context(self) -> None:
        superseded = RetrievalResult("memory-3", 0.9, "superseded lesson", {})
        context = self.integrator.build_context(
            "query",
            memory_results=(superseded,),
            reliability=(self.superseded_reliability,),
        )
        self.assertEqual(context.memories, ())

    def test_active_reliability_preserves_nonterminal_history(self) -> None:
        context = self.integrator.build_context(
            "query",
            reliability=(self.retained_reliability, self.reversed_reliability),
        )
        self.assertEqual(context.reliability, (self.retained_reliability,))
        self.assertEqual(context.active_reliability, (self.retained_reliability,))

    def test_only_accepted_adaptations_influence_intelligence_context(self) -> None:
        context = self.integrator.build_context(
            "query",
            adaptations=(self.accepted_adaptation, self.rejected_adaptation),
        )
        self.assertEqual(context.adaptations, (self.accepted_adaptation,))

    def test_feedback_is_preserved_as_feedback_not_authority(self) -> None:
        context = self.integrator.build_context("query", feedback=(self.feedback,))
        self.assertEqual(context.feedback, (self.feedback,))
        self.assertFalse(context.to_dict()["authority_granted"])

    def test_evaluations_are_preserved_without_becoming_truth(self) -> None:
        context = self.integrator.build_context("query", evaluations=(self.evaluation,))
        self.assertEqual(context.evaluations, (self.evaluation,))
        payload = context.to_dict()
        self.assertFalse(payload["truth_guaranteed"])
        self.assertFalse(payload["authorization_granted"])

    def test_provenance_is_deterministic_and_can_carry_caller_context(self) -> None:
        context = self.integrator.build_context(
            "query",
            provenance={"request_id": "req-1"},
        )
        self.assertEqual(context.provenance["source"], "m10.7")
        self.assertEqual(context.provenance["request_id"], "req-1")
        self.assertEqual(context.to_json(), context.to_json())

    def test_serialization_explicitly_denies_authority_and_execution(self) -> None:
        context = self.integrator.build_context(
            "query",
            memory_results=(self.memory,),
            feedback=(self.feedback,),
            adaptations=(self.accepted_adaptation,),
            reliability=(self.retained_reliability,),
            evaluations=(self.evaluation,),
        )
        payload = json.loads(context.to_json())
        self.assertFalse(payload["truth_guaranteed"])
        self.assertFalse(payload["authority_granted"])
        self.assertFalse(payload["authorization_granted"])
        self.assertFalse(payload["execution_requested"])
        self.assertFalse(payload["policy_mutation"])

    def test_unreliable_memory_helper_is_deterministic(self) -> None:
        reversed_memory = RetrievalResult("memory-2", 0.7, "reversed lesson", {})
        results = self.integrator.exclude_unreliable_memory(
            (self.memory, reversed_memory),
            (self.reversed_reliability,),
        )
        self.assertEqual(results, (self.memory,))

    def test_context_does_not_grant_authority_from_rich_learning_inputs(self) -> None:
        context = self.integrator.build_context(
            "query",
            memory_results=(self.memory,),
            feedback=(self.feedback,),
            adaptations=(self.accepted_adaptation,),
            reliability=(self.retained_reliability,),
            evaluations=(self.evaluation,),
        )
        payload = context.to_dict()
        self.assertFalse(payload["authority_granted"])
        self.assertFalse(payload["authorization_granted"])
        self.assertFalse(payload["execution_requested"])

    def test_input_collections_must_be_explicit_tuples(self) -> None:
        with self.assertRaises(TypeError):
            self.integrator.build_context("query", feedback=[self.feedback])
        with self.assertRaises(TypeError):
            self.integrator.exclude_unreliable_memory([self.memory], ())


if __name__ == "__main__":
    unittest.main()
