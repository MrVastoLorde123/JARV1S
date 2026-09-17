from unittest import TestCase

from src.agency.initiative_candidate import (
    InitiativeCandidate,
    build_initiative_candidate_set,
)
from src.agency.initiative_evaluation import (
    InitiativeEvaluation,
    build_initiative_evaluation_set,
)
from src.agency.reasoning import ReasoningHypothesis, build_reasoning_result


class M47InitiativeEvaluationTests(TestCase):
    def _candidate_set(self):
        reasoning = build_reasoning_result(
            self._context(),
            reasoning_id="reasoning:1",
            hypotheses=(
                ReasoningHypothesis(
                    "hypothesis:1",
                    "A bounded candidate may be useful.",
                    0.8,
                    supporting_fact_ids=("fact:1",),
                    uncertainty_reasons=("requires validation",),
                ),
            ),
            unresolved_uncertainties=("value remains uncertain",),
        )
        return build_initiative_candidate_set(
            reasoning,
            candidate_set_id="candidates:1",
            candidates=(
                InitiativeCandidate(
                    "candidate:1",
                    "reasoning:1",
                    "Evaluate a possible initiative.",
                    supporting_hypothesis_ids=("hypothesis:1",),
                    uncertainty_reasons=("requires validation",),
                    rationale="Derived from bounded reasoning.",
                ),
            ),
        )

    @staticmethod
    def _context():
        from src.agency.current_context import CurrentContext, CurrentContextFact
        from src.agency.world_model import WorldModelFact
        from src.agency.world_model_qualification import WorldFactQualification

        return CurrentContext(
            context_id="context:1",
            model_id="model:1",
            assessed_at="2026-09-16T21:00:00+00:00",
            facts=(
                CurrentContextFact(
                    WorldModelFact(
                        "fact:1",
                        "subject:1",
                        "domain:1",
                        "usable",
                        ("observation:1",),
                    ),
                    WorldFactQualification.USABLE,
                ),
            ),
        )

    def test_evaluation_must_reference_supplied_candidate_set(self):
        candidate_set = self._candidate_set()
        result = build_initiative_evaluation_set(
            candidate_set,
            evaluation_set_id="evaluations:1",
            evaluations=(
                InitiativeEvaluation(
                    "candidate:1",
                    "candidates:1",
                    0.8,
                    0.7,
                    0.6,
                    "Descriptive evaluation only.",
                    uncertainty_reasons=("value remains uncertain",),
                ),
            ),
        )
        self.assertEqual(result.candidate_set_id, "candidates:1")
        self.assertEqual(result.evaluation_count, 1)

    def test_unknown_candidate_is_rejected(self):
        candidate_set = self._candidate_set()
        with self.assertRaises(ValueError):
            build_initiative_evaluation_set(
                candidate_set,
                evaluation_set_id="evaluations:1",
                evaluations=(
                    InitiativeEvaluation(
                        "candidate:unknown",
                        "candidates:1",
                        0.8,
                        0.7,
                        0.6,
                        "Descriptive evaluation only.",
                    ),
                ),
            )

    def test_scores_are_bounded_and_evaluation_is_not_authority(self):
        candidate_set = self._candidate_set()
        with self.assertRaises(ValueError):
            InitiativeEvaluation("candidate:1", "candidates:1", 1.1, 0.7, 0.6, "bad")
        evaluation = InitiativeEvaluation("candidate:1", "candidates:1", 0.8, 0.7, 0.6, "ok")
        payload = evaluation.to_context()
        self.assertFalse(payload["authority_granted"])
        self.assertFalse(payload["scheduling_requested"])
        self.assertFalse(payload["execution_requested"])

    def test_uncertainty_is_carried_forward(self):
        result = build_initiative_evaluation_set(
            self._candidate_set(),
            evaluation_set_id="evaluations:1",
        )
        self.assertEqual(result.unresolved_uncertainties, ("value remains uncertain",))
