import unittest

from src.context.consequence_validation_semantics import (
    ConsequenceValidation,
    ConsequenceValidationStatus,
    ConsequenceViolation,
)
from src.context.policy_input_semantics import (
    ActionCharacteristics,
    ActionEffect,
    PolicyInput,
    PolicyInputProjector,
    PolicyInputProvenance,
)
from src.context.proposed_consequence_semantics import ConsequenceKind
from src.context.reasoning_semantics import ReasoningContext, ReasoningInput


class PolicyInputSemanticsTests(unittest.TestCase):
    def _context(self):
        return ReasoningContext(
            request="inspect config",
            inputs=(ReasoningInput(content="Inspect the configuration.", source_type="REQUEST"),),
        )

    def _valid_validation(self):
        return ConsequenceValidation(
            request="inspect config",
            proposal_id="proposal:0",
            validation_id="validation:0",
            status=ConsequenceValidationStatus.VALID,
        )

    def test_validated_proposal_projects_to_canonical_input(self):
        result = PolicyInputProjector().project(
            self._context(),
            self._valid_validation(),
            ConsequenceKind.PLAN,
            "proposal:0",
        )

        self.assertIsInstance(result, PolicyInput)
        self.assertEqual(result.validation_status, ConsequenceValidationStatus.VALID)
        self.assertEqual(result.provenance.proposal_id, "proposal:0")
        self.assertEqual(result.validation_id, "validation:0")
        self.assertEqual(result.provenance.validation_id, "validation:0")
        self.assertFalse(result.authorized)

    def test_invalid_validation_cannot_enter_policy(self):
        validation = ConsequenceValidation(
            request="inspect config",
            proposal_id="proposal:0",
            validation_id="validation:0",
            status=ConsequenceValidationStatus.INVALID,
            violations=(ConsequenceViolation("bad", "Invalid proposal."),),
        )
        with self.assertRaises(ValueError):
            PolicyInputProjector().project(
                self._context(), validation, ConsequenceKind.PLAN, "proposal:0"
            )

    def test_request_and_proposal_identity_are_enforced(self):
        with self.assertRaises(ValueError):
            PolicyInputProjector().project(
                self._context(), self._valid_validation(), ConsequenceKind.PLAN, "proposal:1"
            )

        mismatched = ConsequenceValidation(
            request="different request",
            proposal_id="proposal:0",
            validation_id="validation:0",
            status=ConsequenceValidationStatus.VALID,
        )
        with self.assertRaises(ValueError):
            PolicyInputProjector().project(
                self._context(), mismatched, ConsequenceKind.PLAN, "proposal:0"
            )

    def test_validation_identity_must_be_preserved(self):
        validation = self._valid_validation()
        with self.assertRaises(ValueError):
            PolicyInput(
                request="inspect config",
                proposal_id="proposal:0",
                validation_id="validation:1",
                proposal_kind=ConsequenceKind.PLAN,
                validation_status=ConsequenceValidationStatus.VALID,
                action=ActionCharacteristics(),
                provenance=PolicyInputProvenance("proposal:0", "validation:0"),
            )

    def test_action_characteristics_are_descriptive(self):
        action = ActionCharacteristics(
            effect=ActionEffect.STATE_CHANGE,
            resource_scope="local_config",
            sensitivity=0.8,
            reversibility=0.4,
        )
        result = PolicyInputProjector().project(
            self._context(), self._valid_validation(), ConsequenceKind.PREPARE, "proposal:0", action
        )
        serialized = result.to_context()
        self.assertEqual(serialized["action"]["effect"], "state_change")
        self.assertEqual(serialized["action"]["sensitivity"], 0.8)
        self.assertFalse(serialized["authorized"])

    def test_policy_input_rejects_authority_controls(self):
        with self.assertRaises(ValueError):
            PolicyInput(
                request="inspect config",
                proposal_id="proposal:0",
                validation_id="validation:0",
                proposal_kind=ConsequenceKind.PLAN,
                validation_status=ConsequenceValidationStatus.VALID,
                action=ActionCharacteristics(),
                provenance=PolicyInputProvenance("proposal:0", "validation:0"),
                metadata={"execute": True},
            )

    def test_policy_input_serialization_is_provider_neutral(self):
        result = PolicyInputProjector().project(
            self._context(), self._valid_validation(), ConsequenceKind.ASK, "proposal:0"
        )
        context = result.to_context()
        self.assertEqual(context["request"], "inspect config")
        self.assertEqual(context["proposal_kind"], "ask")
        self.assertEqual(context["validation_status"], "valid")
        self.assertEqual(context["validation_id"], "validation:0")
        self.assertIn("provenance", context)
        self.assertNotIn("execute", context)


if __name__ == "__main__":
    unittest.main()
