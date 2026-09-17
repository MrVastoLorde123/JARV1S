import unittest

from src.agency.current_context import CurrentContext, CurrentContextFact
from src.agency.information_gain import InformationGainAssessment, InformationGainOpportunity
from src.agency.initiative_evaluation import InitiativeEvaluation, InitiativeEvaluationSet
from src.agency.proactive_proposal import (
    ProactiveProposal,
    build_proactive_proposal_set,
)
from src.agency.world_model import WorldModelFact
from src.agency.world_model_qualification import WorldFactQualification


class M49ProactiveProposalTests(unittest.TestCase):
    def _evaluation_set(self):
        return InitiativeEvaluationSet(
            "eval:set",
            "cand:set",
            (
                InitiativeEvaluation(
                    "candidate:1",
                    "cand:set",
                    0.8,
                    0.7,
                    0.6,
                    "bounded descriptive evaluation",
                ),
            ),
            ("need:more evidence",),
        )

    def _information_gain(self):
        return InformationGainAssessment(
            "ig:set",
            "eval:set",
            (
                InformationGainOpportunity(
                    "ig:1",
                    "eval:set",
                    "need:more evidence",
                    0.75,
                    "evidence would reduce uncertainty",
                    candidate_id="candidate:1",
                ),
            ),
            ("need:more evidence",),
        )

    def test_proposal_must_reference_supplied_boundaries(self):
        evaluation_set = self._evaluation_set()
        information_gain = self._information_gain()
        proposal = ProactiveProposal(
            "proposal:1",
            "eval:set",
            "Consider gathering the missing evidence.",
            "This could reduce a named uncertainty.",
            candidate_id="candidate:1",
            information_gain_opportunity_ids=("ig:1",),
            unresolved_uncertainties=("need:more evidence",),
        )
        result = build_proactive_proposal_set(
            evaluation_set,
            information_gain,
            proposal_set_id="proposal:set",
            proposals=(proposal,),
        )
        self.assertEqual(result.proposal_count, 1)
        self.assertEqual(result.proposals[0].candidate_id, "candidate:1")

    def test_proposal_rejects_unknown_information_gain_reference(self):
        with self.assertRaises(ValueError):
            build_proactive_proposal_set(
                self._evaluation_set(),
                self._information_gain(),
                proposal_set_id="proposal:set",
                proposals=(
                    ProactiveProposal(
                        "proposal:1",
                        "eval:set",
                        "Consider gathering evidence.",
                        "bounded rationale",
                        information_gain_opportunity_ids=("ig:unknown",),
                    ),
                ),
            )

    def test_proposal_rejects_unknown_uncertainty(self):
        with self.assertRaises(ValueError):
            build_proactive_proposal_set(
                self._evaluation_set(),
                self._information_gain(),
                proposal_set_id="proposal:set",
                proposals=(
                    ProactiveProposal(
                        "proposal:1",
                        "eval:set",
                        "Consider gathering evidence.",
                        "bounded rationale",
                        unresolved_uncertainties=("unknown",),
                    ),
                ),
            )

    def test_output_is_not_intent_authority_or_execution(self):
        evaluation_set = self._evaluation_set()
        information_gain = self._information_gain()
        result = build_proactive_proposal_set(
            evaluation_set,
            information_gain,
            proposal_set_id="proposal:set",
        )
        payload = result.to_context()
        self.assertFalse(payload["truth_established"])
        self.assertFalse(payload["intent_established"])
        self.assertFalse(payload["authority_granted"])
        self.assertFalse(payload["scheduling_requested"])
        self.assertFalse(payload["notification_requested"])
        self.assertFalse(payload["authorization_requested"])
        self.assertFalse(payload["execution_requested"])


if __name__ == "__main__":
    unittest.main()
