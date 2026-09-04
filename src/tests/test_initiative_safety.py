import json
import unittest

from src.evaluation import InitiativeEvaluation
from src.initiative import InitiativeCandidate
from src.proposals import InitiativeProposal
from src.initiative_safety import (
    InitiativeSafetyValidationError,
    InitiativeSafetyResult,
    check_initiative_safety,
)


class InitiativeSafetyTests(unittest.TestCase):
    def _proposal(self):
        candidate = InitiativeCandidate("init-1", "Review", "Review this.")
        evaluation = InitiativeEvaluation(
            "eval-1", candidate, 0.9, 0.7, 0.8, 0.2, 0.1
        )
        return InitiativeProposal(
            "prop-1", evaluation, "Review proposal", "Review this now.", "Review the item"
        )

    def test_valid_result(self):
        result = check_initiative_safety(self._proposal())
        self.assertTrue(result.safe_for_downstream_validation)
        self.assertEqual(result.proposal_id, "prop-1")

    def test_blocks_authority_transitions(self):
        result = check_initiative_safety(self._proposal())
        self.assertIn("proposal_to_instruction", result.blocked_authority_transitions)
        self.assertIn("proposal_to_confirmation", result.blocked_authority_transitions)
        self.assertIn("proposal_to_authorization", result.blocked_authority_transitions)
        self.assertIn("proposal_to_policy", result.blocked_authority_transitions)
        self.assertIn("proposal_to_execution", result.blocked_authority_transitions)

    def test_rejects_non_proposal(self):
        with self.assertRaises(TypeError):
            check_initiative_safety("proposal")

    def test_result_is_immutable(self):
        result = check_initiative_safety(self._proposal())
        with self.assertRaises(Exception):
            result.proposal_id = "changed"

    def test_result_requires_non_empty_id(self):
        with self.assertRaises(InitiativeSafetyValidationError):
            InitiativeSafetyResult("", True, ("x",))

    def test_result_requires_bool(self):
        with self.assertRaises(InitiativeSafetyValidationError):
            InitiativeSafetyResult("p1", 1, ("x",))

    def test_result_requires_tuple_transitions(self):
        with self.assertRaises(InitiativeSafetyValidationError):
            InitiativeSafetyResult("p1", True, ["x"])

    def test_result_rejects_empty_transition(self):
        with self.assertRaises(InitiativeSafetyValidationError):
            InitiativeSafetyResult("p1", True, ("",))

    def test_result_rejects_duplicate_transitions(self):
        with self.assertRaises(InitiativeSafetyValidationError):
            InitiativeSafetyResult("p1", True, ("x", "x"))

    def test_serialization_is_non_authoritative(self):
        data = check_initiative_safety(self._proposal()).to_dict()
        self.assertFalse(data["initiative_is_instruction"])
        self.assertFalse(data["confirmation_granted"])
        self.assertFalse(data["authorization_granted"])
        self.assertFalse(data["policy_authority"])
        self.assertFalse(data["execution_requested"])

    def test_json_is_serializable(self):
        data = json.loads(check_initiative_safety(self._proposal()).to_json())
        self.assertIsInstance(data, dict)

    def test_safety_does_not_change_proposal(self):
        proposal = self._proposal()
        check_initiative_safety(proposal)
        self.assertEqual(proposal.proposal_id, "prop-1")
        self.assertEqual(proposal.proposed_action, "Review the item")

    def test_safety_does_not_grant_authorization(self):
        result = check_initiative_safety(self._proposal())
        self.assertFalse(result.to_dict()["authorization_granted"])

    def test_safety_does_not_grant_confirmation(self):
        result = check_initiative_safety(self._proposal())
        self.assertFalse(result.to_dict()["confirmation_granted"])

    def test_safety_does_not_create_execution_request(self):
        result = check_initiative_safety(self._proposal())
        self.assertFalse(result.to_dict()["execution_requested"])

    def test_safe_only_means_downstream_validation_allowed(self):
        result = check_initiative_safety(self._proposal())
        self.assertTrue(result.safe_for_downstream_validation)
        self.assertNotIn("authorization_granted", result.blocked_authority_transitions)


if __name__ == "__main__":
    unittest.main()
