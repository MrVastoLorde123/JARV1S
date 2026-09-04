import json
import unittest

from src.initiative import InitiativeCandidate
from src.evaluation import InitiativeEvaluation
from src.proposals import InitiativeProposal, InitiativeProposalValidationError, MAX_REASONS


class InitiativeProposalTests(unittest.TestCase):
    def _evaluation(self):
        candidate = InitiativeCandidate("init-1", "Review project", "Project may need review.")
        return InitiativeEvaluation(
            "eval-1", candidate, 0.9, 0.8, 0.95, 0.2, 0.1,
            reasons=("high value",), metadata={"source": "context"}
        )

    def test_valid_proposal(self):
        proposal = InitiativeProposal(
            "proposal-1", self._evaluation(), "Review project",
            "The project may benefit from a review.",
            "Review the current project state.", reasons=("high value",)
        )
        self.assertEqual(proposal.candidate_id, "init-1")
        self.assertEqual(proposal.evaluation_id, "eval-1")

    def test_is_immutable(self):
        proposal = InitiativeProposal("p1", self._evaluation(), "Review", "Review it.", "Review it.")
        with self.assertRaises(Exception):
            proposal.title = "Changed"

    def test_requires_evaluation(self):
        with self.assertRaises(InitiativeProposalValidationError):
            InitiativeProposal("p1", "bad", "Review", "Review it.", "Review it.")

    def test_empty_fields_rejected(self):
        evaluation = self._evaluation()
        for kwargs in (
            {"proposal_id": "", "title": "Review", "description": "d", "proposed_action": "a"},
            {"proposal_id": "p", "title": "", "description": "d", "proposed_action": "a"},
            {"proposal_id": "p", "title": "Review", "description": "", "proposed_action": "a"},
            {"proposal_id": "p", "title": "Review", "description": "d", "proposed_action": ""},
        ):
            with self.assertRaises(InitiativeProposalValidationError):
                InitiativeProposal(evaluation=evaluation, **kwargs)

    def test_reasons_must_be_tuple(self):
        with self.assertRaises(InitiativeProposalValidationError):
            InitiativeProposal("p1", self._evaluation(), "Review", "Review it.", "Review it.", reasons=["x"])

    def test_reasons_unique(self):
        with self.assertRaises(InitiativeProposalValidationError):
            InitiativeProposal("p1", self._evaluation(), "Review", "Review it.", "Review it.", reasons=("x", "x"))

    def test_reasons_bounded(self):
        reasons = tuple(f"r{i}" for i in range(MAX_REASONS + 1))
        with self.assertRaises(InitiativeProposalValidationError):
            InitiativeProposal("p1", self._evaluation(), "Review", "Review it.", "Review it.", reasons=reasons)

    def test_metadata_frozen(self):
        proposal = InitiativeProposal("p1", self._evaluation(), "Review", "Review it.", "Review it.", metadata={"a": {"b": 1}})
        with self.assertRaises(TypeError):
            proposal.metadata["a"]["b"] = 2

    def test_metadata_rejects_unsupported_nested_type(self):
        with self.assertRaises(InitiativeProposalValidationError):
            InitiativeProposal("p1", self._evaluation(), "Review", "Review it.", "Review it.", metadata={"bad": object()})

    def test_lineage_is_preserved(self):
        proposal = InitiativeProposal("p1", self._evaluation(), "Review", "Review it.", "Review it.")
        data = proposal.to_dict()
        self.assertEqual(data["candidate_id"], "init-1")
        self.assertEqual(data["evaluation_id"], "eval-1")

    def test_non_authoritative_flags(self):
        data = InitiativeProposal("p1", self._evaluation(), "Review", "Review it.", "Review it.").to_dict()
        self.assertFalse(data["proposal_is_instruction"])
        self.assertFalse(data["proposal_is_authorization"])
        self.assertTrue(data["confirmation_required"])
        self.assertFalse(data["authorization_granted"])
        self.assertFalse(data["policy_authority"])
        self.assertFalse(data["execution_requested"])
        self.assertFalse(data["user_intent_guaranteed"])

    def test_json_shape(self):
        data = json.loads(InitiativeProposal("p1", self._evaluation(), "Review", "Review it.", "Review it.").to_json())
        self.assertEqual(data["proposal_id"], "p1")
        self.assertIsInstance(data, dict)


if __name__ == "__main__":
    unittest.main()
