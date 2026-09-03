import unittest

from src.learning.evaluation import (
    Evidence,
    EvaluationConflictError,
    EvaluationState,
    OutcomeAssessment,
    OutcomeEvaluator,
    EvaluationStore,
)
from src.learning.experience import Experience


class EvaluationTests(unittest.TestCase):
    def experience(self, **overrides):
        values = {"experience_id": "exp-1", "source": "execution", "outcome": "task completed"}
        values.update(overrides)
        return Experience(**values)

    def test_success_from_explicit_positive_evidence(self):
        evaluation = OutcomeEvaluator().evaluate(
            self.experience(),
            OutcomeAssessment("task completed", (Evidence("e1", "observed completion", True),)),
        )
        self.assertEqual(evaluation.state, EvaluationState.SUCCESS)
        self.assertEqual(evaluation.evidence_ids, ("e1",))

    def test_failure_from_explicit_negative_evidence(self):
        evaluation = OutcomeEvaluator().evaluate(
            self.experience(),
            OutcomeAssessment("task failed", (Evidence("e1", "observed failure", False),)),
        )
        self.assertEqual(evaluation.state, EvaluationState.FAILURE)

    def test_conflicting_evidence_is_mixed(self):
        evaluation = OutcomeEvaluator().evaluate(
            self.experience(),
            OutcomeAssessment(
                "partial result",
                (Evidence("e1", "success signal", True), Evidence("e2", "failure signal", False)),
            ),
        )
        self.assertEqual(evaluation.state, EvaluationState.MIXED)

    def test_incomplete_evidence_is_incomplete(self):
        evaluation = OutcomeEvaluator().evaluate(
            self.experience(),
            OutcomeAssessment("still running", (Evidence("e1", "partial", True),), complete=False),
        )
        self.assertEqual(evaluation.state, EvaluationState.INCOMPLETE)

    def test_missing_or_directionless_evidence_is_inconclusive(self):
        evaluator = OutcomeEvaluator()
        self.assertEqual(
            evaluator.evaluate(self.experience(), OutcomeAssessment("completed", ())).state,
            EvaluationState.INCONCLUSIVE,
        )
        self.assertEqual(
            evaluator.evaluate(
                self.experience(),
                OutcomeAssessment("completed", (Evidence("e1", "ambiguous"),)),
            ).state,
            EvaluationState.INCONCLUSIVE,
        )

    def test_missing_outcome_is_incomplete(self):
        evaluation = OutcomeEvaluator().evaluate(self.experience(outcome=""), OutcomeAssessment("", ()))
        self.assertEqual(evaluation.state, EvaluationState.INCOMPLETE)

    def test_evaluation_is_immutable_and_non_authoritative(self):
        evaluation = OutcomeEvaluator().evaluate(
            self.experience(), OutcomeAssessment("done", (Evidence("e1", "done", True),))
        )
        with self.assertRaises(Exception):
            evaluation.rationale = "changed"
        payload = evaluation.to_dict()
        self.assertFalse(payload["truth_guaranteed"])
        self.assertFalse(payload["policy_authority"])
        self.assertFalse(payload["authorization_granted"])
        self.assertFalse(payload["execution_requested"])

    def test_confidence_is_bounded(self):
        evaluator = OutcomeEvaluator()
        with self.assertRaises(ValueError):
            evaluator.evaluate(self.experience(), OutcomeAssessment("done", ()), confidence=1.1)
        with self.assertRaises(ValueError):
            evaluator.evaluate(self.experience(), OutcomeAssessment("done", ()), confidence=-0.1)

    def test_store_is_immutable_and_rejects_duplicates(self):
        evaluation = OutcomeEvaluator().evaluate(
            self.experience(), OutcomeAssessment("done", (Evidence("e1", "done", True),))
        )
        store = EvaluationStore()
        updated = store.append(evaluation)
        self.assertEqual(len(store.list()), 0)
        self.assertEqual(updated.get(evaluation.evaluation_id), evaluation)
        with self.assertRaises(EvaluationConflictError):
            updated.append(evaluation)

    def test_json_serialization_is_deterministic(self):
        evaluation = OutcomeEvaluator().evaluate(
            self.experience(), OutcomeAssessment("done", (Evidence("e1", "done", True),))
        )
        self.assertEqual(evaluation.to_json(), evaluation.to_json())


if __name__ == "__main__":
    unittest.main()
