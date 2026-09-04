import unittest

from src.change_impact import (
    ChangeImpactAssessment,
    ChangeImpactValidationError,
    ImpactDomain,
    ImpactLevel,
)
from src.self_development import SelfDevelopmentProposal


class ChangeImpactAssessmentTests(unittest.TestCase):
    def setUp(self) -> None:
        self.proposal = SelfDevelopmentProposal(
            proposal_id="proposal-1",
            title="Improve planner",
            description="Refine planner behavior.",
            target="planner",
            rationale="Reduce unnecessary work.",
            expected_change="Better prioritization.",
            affected_paths=("src/planner.py",),
            validation_requirements=("run planner tests",),
            rollback_plan="Restore the previous implementation.",
            reversible=True,
        )

    def make_assessment(self, **overrides):
        values = dict(
            assessment_id="impact-1",
            proposal=self.proposal,
            overall_impact=ImpactLevel.LOW,
            affected_domains=(ImpactDomain.CODE,),
            reasons=("Single component change.",),
            dependency_impact=ImpactLevel.NONE,
            compatibility_impact=ImpactLevel.LOW,
            rollback_feasibility=ImpactLevel.HIGH,
            confidence=0.9,
        )
        values.update(overrides)
        return ChangeImpactAssessment(**values)

    def test_constructs_bounded_assessment(self):
        assessment = self.make_assessment()
        self.assertEqual(assessment.proposal_id, "proposal-1")
        self.assertFalse(assessment.change_is_authorized)
        self.assertFalse(assessment.execution_requested)

    def test_authority_impact_requires_authority_domain(self):
        with self.assertRaises(ChangeImpactValidationError):
            self.make_assessment(authority_scope_impact=True, requires_authority_review=True)

    def test_authority_impact_requires_review(self):
        with self.assertRaises(ChangeImpactValidationError):
            self.make_assessment(
                affected_domains=(ImpactDomain.CODE, ImpactDomain.AUTHORITY),
                authority_scope_impact=True,
            )

    def test_identity_impact_requires_identity_domain(self):
        with self.assertRaises(ChangeImpactValidationError):
            self.make_assessment(identity_scope_impact=True, requires_authority_review=True)

    def test_identity_impact_requires_review(self):
        with self.assertRaises(ChangeImpactValidationError):
            self.make_assessment(
                affected_domains=(ImpactDomain.CODE, ImpactDomain.IDENTITY),
                identity_scope_impact=True,
            )

    def test_authority_review_does_not_authorize(self):
        assessment = self.make_assessment(
            affected_domains=(ImpactDomain.CODE, ImpactDomain.AUTHORITY),
            authority_scope_impact=True,
            requires_authority_review=True,
        )
        self.assertTrue(assessment.requires_authority_review)
        self.assertFalse(assessment.change_is_authorized)

    def test_identity_review_does_not_authorize(self):
        assessment = self.make_assessment(
            affected_domains=(ImpactDomain.CODE, ImpactDomain.IDENTITY),
            identity_scope_impact=True,
            requires_authority_review=True,
        )
        self.assertFalse(assessment.change_is_authorized)

    def test_confidence_is_bounded(self):
        with self.assertRaises(ChangeImpactValidationError):
            self.make_assessment(confidence=1.1)
        with self.assertRaises(ChangeImpactValidationError):
            self.make_assessment(confidence=-0.1)

    def test_with_reason_is_immutable(self):
        assessment = self.make_assessment()
        updated = assessment.with_reason("Rollback is straightforward.")
        self.assertEqual(assessment.reasons, ("Single component change.",))
        self.assertEqual(len(updated.reasons), 2)

    def test_duplicate_reason_rejected(self):
        with self.assertRaises(ChangeImpactValidationError):
            self.make_assessment().with_reason("Single component change.")

    def test_with_domain_is_immutable(self):
        assessment = self.make_assessment()
        updated = assessment.with_domain(ImpactDomain.RUNTIME)
        self.assertEqual(assessment.affected_domains, (ImpactDomain.CODE,))
        self.assertEqual(updated.affected_domains[-1], ImpactDomain.RUNTIME)

    def test_duplicate_domain_rejected(self):
        with self.assertRaises(ChangeImpactValidationError):
            self.make_assessment().with_domain(ImpactDomain.CODE)

    def test_serialization_preserves_lineage_and_walls(self):
        payload = self.make_assessment().to_dict()
        self.assertEqual(payload["proposal_id"], "proposal-1")
        self.assertTrue(payload["impact_assessment"])
        self.assertFalse(payload["change_is_authorized"])
        self.assertFalse(payload["instruction_granted"])
        self.assertFalse(payload["execution_requested"])
        self.assertFalse(payload["policy_authority"])
        self.assertFalse(payload["authority_scope_change_authorized"])
        self.assertFalse(payload["identity_change_authorized"])

    def test_metadata_is_frozen(self):
        assessment = self.make_assessment(metadata={"source": {"kind": "static"}})
        with self.assertRaises(TypeError):
            assessment.metadata["source"] = "changed"
        with self.assertRaises(TypeError):
            assessment.metadata["source"]["kind"] = "changed"

    def test_non_finite_confidence_rejected(self):
        with self.assertRaises(ChangeImpactValidationError):
            self.make_assessment(confidence=float("nan"))
        with self.assertRaises(ChangeImpactValidationError):
            self.make_assessment(confidence=float("inf"))

    def test_unsupported_domain_rejected(self):
        with self.assertRaises(ChangeImpactValidationError):
            self.make_assessment(affected_domains=("code",))

    def test_unsupported_proposal_rejected(self):
        with self.assertRaises(ChangeImpactValidationError):
            self.make_assessment(proposal=object())

    def test_long_reason_rejected(self):
        with self.assertRaises(ChangeImpactValidationError):
            self.make_assessment(reasons=("x" * 513,))


if __name__ == "__main__":
    unittest.main()
