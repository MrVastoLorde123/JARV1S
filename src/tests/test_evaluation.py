import json
import unittest

from src.evaluation import InitiativeEvaluation, InitiativeEvaluationValidationError
from src.initiative import InitiativeCandidate


class InitiativeEvaluationTests(unittest.TestCase):
    def candidate(self):
        return InitiativeCandidate("init-1", "Review", "Review this.", context_refs=("project:p1",))

    def test_valid_evaluation(self):
        evaluation = InitiativeEvaluation("eval-1", self.candidate(), 0.9, 0.7, 0.8, 0.2, 0.1)
        self.assertEqual(evaluation.evaluation_id, "eval-1")
        self.assertGreater(evaluation.net_signal, 0.0)

    def test_candidate_required(self):
        with self.assertRaises(InitiativeEvaluationValidationError):
            InitiativeEvaluation("eval-1", "bad", 0.5, 0.5, 0.5, 0.5, 0.5)

    def test_scores_are_bounded(self):
        for field in ("value_score", "urgency_score", "confidence_score", "effort_score", "risk_score"):
            values = {name: 0.5 for name in ("value_score", "urgency_score", "confidence_score", "effort_score", "risk_score")}
            values[field] = 1.1
            with self.assertRaises(InitiativeEvaluationValidationError):
                InitiativeEvaluation("eval-1", self.candidate(), **values)

    def test_scores_reject_nan(self):
        with self.assertRaises(InitiativeEvaluationValidationError):
            InitiativeEvaluation("eval-1", self.candidate(), float("nan"), 0.5, 0.5, 0.5, 0.5)

    def test_reasons_are_unique(self):
        with self.assertRaises(InitiativeEvaluationValidationError):
            InitiativeEvaluation("eval-1", self.candidate(), 0.5, 0.5, 0.5, 0.5, 0.5, reasons=("x", "x"))

    def test_metadata_is_frozen(self):
        evaluation = InitiativeEvaluation("eval-1", self.candidate(), 0.5, 0.5, 0.5, 0.5, 0.5, metadata={"a": {"b": 1}})
        with self.assertRaises(TypeError):
            evaluation.metadata["a"]["b"] = 2

    def test_is_immutable(self):
        evaluation = InitiativeEvaluation("eval-1", self.candidate(), 0.5, 0.5, 0.5, 0.5, 0.5)
        with self.assertRaises(Exception):
            evaluation.value_score = 0.1

    def test_net_signal_penalizes_effort_and_risk(self):
        low = InitiativeEvaluation("a", self.candidate(), 0.8, 0.8, 0.8, 0.1, 0.1)
        high = InitiativeEvaluation("b", self.candidate(), 0.8, 0.8, 0.8, 0.9, 0.9)
        self.assertGreater(low.net_signal, high.net_signal)

    def test_zero_scores_are_valid(self):
        evaluation = InitiativeEvaluation("eval-1", self.candidate(), 0, 0, 0, 0, 0)
        self.assertEqual(evaluation.net_signal, 0.4)

    def test_one_scores_are_valid(self):
        evaluation = InitiativeEvaluation("eval-1", self.candidate(), 1, 1, 1, 1, 1)
        self.assertEqual(evaluation.net_signal, 0.6)

    def test_to_dict_is_non_authoritative(self):
        data = InitiativeEvaluation("eval-1", self.candidate(), 0.5, 0.5, 0.5, 0.5, 0.5).to_dict()
        self.assertFalse(data["evaluation_is_authorization"])
        self.assertFalse(data["initiative_is_instruction"])
        self.assertFalse(data["authorization_granted"])
        self.assertFalse(data["policy_authority"])
        self.assertFalse(data["execution_requested"])

    def test_to_json_is_serializable(self):
        data = json.loads(InitiativeEvaluation("eval-1", self.candidate(), 0.5, 0.5, 0.5, 0.5, 0.5).to_json())
        self.assertIsInstance(data, dict)
        self.assertEqual(data["evaluation_id"], "eval-1")

    def test_empty_evaluation_id_rejected(self):
        with self.assertRaises(InitiativeEvaluationValidationError):
            InitiativeEvaluation("", self.candidate(), 0.5, 0.5, 0.5, 0.5, 0.5)

    def test_non_tuple_reasons_rejected(self):
        with self.assertRaises(InitiativeEvaluationValidationError):
            InitiativeEvaluation("eval-1", self.candidate(), 0.5, 0.5, 0.5, 0.5, 0.5, reasons=["x"])

    def test_non_mapping_metadata_rejected(self):
        with self.assertRaises(InitiativeEvaluationValidationError):
            InitiativeEvaluation("eval-1", self.candidate(), 0.5, 0.5, 0.5, 0.5, 0.5, metadata="bad")


if __name__ == "__main__":
    unittest.main()
