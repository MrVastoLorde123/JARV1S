import unittest

from src.context.consequence_validation_semantics import (
    ConsequenceValidation,
    ConsequenceValidationEngine,
    ConsequenceValidationStatus,
    ConsequenceValidations,
    ConsequenceViolation,
    ViolationSeverity,
)
from src.context.prioritization_semantics import (
    Prioritization,
    PriorityKind,
    PrioritySignal,
    PriorityTarget,
)
from src.context.proposed_consequence_semantics import (
    ConsequenceKind,
    ProposalSupport,
    ProposedConsequence,
    ProposedConsequences,
)
from src.context.reasoning_semantics import ReasoningContext, ReasoningInput


class ConsequenceValidationSemanticsTests(unittest.TestCase):
    def _context(self):
        return ReasoningContext(
            request="inspect config",
            inputs=(
                ReasoningInput(
                    content="Inspect the configuration file.",
                    source_type="REQUEST",
                ),
            ),
        )

    def _prioritization(self):
        return Prioritization(
            request="inspect config",
            targets=(
                PriorityTarget(
                    "target:0",
                    PriorityKind.INPUT,
                    "Inspect the configuration.",
                    PrioritySignal(relevance=1.0),
                    0,
                ),
            ),
        )

    def test_invalid_proposal_stops_at_validation(self):
        proposal = ProposedConsequence(
            "Inspect the configuration.",
            ConsequenceKind.PLAN,
            (ProposalSupport("prioritization", "missing"),),
        )
        result = ConsequenceValidationEngine().validate(
            self._context(), self._prioritization(), proposal, "proposal:0"
        )

        self.assertEqual(result.status, ConsequenceValidationStatus.INVALID)
        self.assertEqual(result.violations[0].code, "support_reference_unresolved")
        self.assertFalse(result.authorized)

    def test_valid_proposal_does_not_become_authorized(self):
        proposal = ProposedConsequence(
            "Inspect the configuration.",
            ConsequenceKind.PLAN,
            (ProposalSupport("prioritization", "target:0"),),
            priority_target_id="target:0",
        )
        result = ConsequenceValidationEngine().validate(
            self._context(), self._prioritization(), proposal, "proposal:0"
        )

        self.assertEqual(result.status, ConsequenceValidationStatus.VALID)
        self.assertFalse(result.authorized)
        self.assertNotIn("execute", result.to_context())

    def test_forbidden_execution_controls_are_invalidated(self):
        proposal = ProposedConsequence(
            "Inspect the configuration.",
            ConsequenceKind.PLAN,
            metadata={"custom": "ok"},
        )
        object.__setattr__(proposal, "metadata", {"execute": True})
        result = ConsequenceValidationEngine().validate(
            self._context(), self._prioritization(), proposal, "proposal:0"
        )

        self.assertEqual(result.status, ConsequenceValidationStatus.INVALID)
        self.assertEqual(result.violations[0].code, "forbidden_execution_control")

    def test_invalid_status_requires_error(self):
        with self.assertRaises(ValueError):
            ConsequenceValidation(
                "inspect config",
                "proposal:0",
                ConsequenceValidationStatus.INVALID,
                (ConsequenceViolation("note", "warning only", ViolationSeverity.WARNING),),
            )

    def test_valid_status_cannot_carry_error(self):
        with self.assertRaises(ValueError):
            ConsequenceValidation(
                "inspect config",
                "proposal:0",
                ConsequenceValidationStatus.VALID,
                (ConsequenceViolation("bad", "not valid"),),
            )

    def test_collection_is_deterministic_and_preserves_request(self):
        proposal = ProposedConsequence("Inspect the configuration.", ConsequenceKind.PLAN)
        proposals = ProposedConsequences("inspect config", (proposal,))
        results = ConsequenceValidationEngine().validate_all(
            self._context(), self._prioritization(), proposals
        )

        self.assertIsInstance(results, ConsequenceValidations)
        self.assertEqual(results.request, "inspect config")
        self.assertEqual(results.validations[0].proposal_id, "proposal:0")
        self.assertTrue(results.all_valid)
        self.assertEqual(results.to_context()["validations"][0]["status"], "valid")

    def test_request_boundaries_are_enforced(self):
        proposals = ProposedConsequences("different request")
        with self.assertRaises(ValueError):
            ConsequenceValidationEngine().validate_all(
                self._context(), self._prioritization(), proposals
            )

    def test_violation_serialization_is_provider_neutral(self):
        violation = ConsequenceViolation(
            "bad_reference", "The reference does not resolve."
        )
        self.assertEqual(
            violation.to_context(),
            {
                "code": "bad_reference",
                "message": "The reference does not resolve.",
                "severity": "error",
            },
        )


if __name__ == "__main__":
    unittest.main()
