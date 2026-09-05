import unittest

from src.core.environment_world_model import EnvironmentWorldModel
from src.core.environment_world_model_change_assessment import (
    EnvironmentWorldModelChangeAssessmentService,
)
from src.core.environment_world_model_revision_decision import (
    EnvironmentWorldModelRevisionDecision,
    EnvironmentWorldModelRevisionDecisionError,
    EnvironmentWorldModelRevisionDecisionService,
)
from src.core.environment_world_model_revision_proposal import (
    EnvironmentWorldModelRevisionProposalService,
)


class EnvironmentWorldModelRevisionDecisionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.baseline = EnvironmentWorldModel(
            model_id="model-1",
            environment_id="env-1",
            state_by_domain={"hardware": {"cpu": "x86"}},
            represented_domains=("hardware",),
            missing_domains=("software", "network"),
            context_ids=("ctx-1",),
            qualification_ids=("qual-1",),
            provenance_ids=("prov-1",),
            readiness_id="ready-1",
            source_bundle_id="bundle-1",
        )
        self.changed = EnvironmentWorldModel(
            model_id="model-2",
            environment_id="env-1",
            state_by_domain={"hardware": {"cpu": "arm64"}},
            represented_domains=("hardware",),
            missing_domains=("software", "network"),
            context_ids=("ctx-2",),
            qualification_ids=("qual-2",),
            provenance_ids=("prov-2",),
            readiness_id="ready-2",
            source_bundle_id="bundle-2",
        )
        self.unchanged = EnvironmentWorldModel(
            model_id="model-3",
            environment_id="env-1",
            state_by_domain={"hardware": {"cpu": "x86"}},
            represented_domains=("hardware",),
            missing_domains=("software", "network"),
            context_ids=("ctx-3",),
            qualification_ids=("qual-3",),
            provenance_ids=("prov-3",),
            readiness_id="ready-3",
            source_bundle_id="bundle-3",
        )
        self.assessor = EnvironmentWorldModelChangeAssessmentService()
        self.proposer = EnvironmentWorldModelRevisionProposalService()
        self.service = EnvironmentWorldModelRevisionDecisionService()

    def _proposal(self, candidate: EnvironmentWorldModel, proposal_id: str):
        assessment = self.assessor.assess(
            self.baseline,
            candidate,
            assessment_id=f"assessment-{proposal_id}",
        )
        return self.proposer.propose(
            self.baseline,
            candidate,
            assessment,
            proposal_id=proposal_id,
        )

    def test_changed_proposal_produces_accept(self) -> None:
        result = self.service.decide(
            self._proposal(self.changed, "proposal-changed"),
            decision_id="decision-1",
        )
        self.assertIsInstance(result, EnvironmentWorldModelRevisionDecision)
        self.assertEqual(result.decision, "ACCEPT")
        self.assertEqual(result.changed_domains, ("hardware",))
        self.assertTrue(result.is_advisory_only)
        self.assertFalse(result.applies_revision)

    def test_unchanged_proposal_produces_reject(self) -> None:
        result = self.service.decide(
            self._proposal(self.unchanged, "proposal-unchanged"),
            decision_id="decision-2",
        )
        self.assertEqual(result.decision, "REJECT")
        self.assertEqual(result.changed_domains, ())

    def test_proposal_identity_and_lineage_are_preserved(self) -> None:
        proposal = self._proposal(self.changed, "proposal-lineage")
        result = self.service.decide(
            proposal,
            decision_id="decision-lineage",
            lineage={"proposal_id": proposal.proposal_id, "stage": "revision-decision"},
        )
        self.assertEqual(result.proposal_id, proposal.proposal_id)
        self.assertEqual(result.assessment_id, proposal.assessment_id)
        self.assertEqual(result.lineage["proposal_id"], "proposal-lineage")
        self.assertEqual(result.lineage["stage"], "revision-decision")

    def test_reasons_are_preserved(self) -> None:
        result = self.service.decide(
            self._proposal(self.changed, "proposal-reason"),
            decision_id="decision-reason",
            reasons={"status": "reviewed model change"},
        )
        self.assertEqual(result.reasons["status"], "reviewed model change")

    def test_result_and_nested_data_are_immutable(self) -> None:
        result = self.service.decide(
            self._proposal(self.changed, "proposal-immutable"),
            decision_id="decision-immutable",
            reasons={"nested": "evidence"},
            lineage={"source": {"stage": "proposal"}},
        )
        with self.assertRaises(TypeError):
            result.reasons["nested"] = "changed"
        with self.assertRaises(TypeError):
            result.lineage["source"]["stage"] = "changed"
        with self.assertRaises(AttributeError):
            result.decision_id = "changed"

    def test_authority_fields_are_absent(self) -> None:
        result = self.service.decide(
            self._proposal(self.changed, "proposal-authority"),
            decision_id="decision-authority",
        )
        forbidden = {
            "authorization_granted",
            "execution_requested",
            "permission_granted",
            "truth_proven",
            "revision_applied",
            "adaptation_truth_proven",
        }
        self.assertTrue(forbidden.isdisjoint(vars(result)))

    def test_source_proposal_is_not_mutated(self) -> None:
        proposal = self._proposal(self.changed, "proposal-source")
        before = dict(proposal.reasons)
        self.service.decide(proposal, decision_id="decision-source")
        self.assertEqual(dict(proposal.reasons), before)

    def test_wrong_type_is_rejected(self) -> None:
        with self.assertRaises(TypeError):
            self.service.decide(object(), decision_id="decision-type")

    def test_invalid_decision_value_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            EnvironmentWorldModelRevisionDecision(
                decision_id="decision-invalid",
                environment_id="env-1",
                baseline_model_id="model-1",
                candidate_model_id="model-2",
                proposal_id="proposal-1",
                assessment_id="assessment-1",
                decision="INVALID",
                changed_domains=("hardware",),
                unchanged_domains=(),
            )

    def test_model_identities_must_differ(self) -> None:
        with self.assertRaises(ValueError):
            EnvironmentWorldModelRevisionDecision(
                decision_id="decision-same",
                environment_id="env-1",
                baseline_model_id="model-1",
                candidate_model_id="model-1",
                proposal_id="proposal-1",
                assessment_id="assessment-1",
                decision="ACCEPT",
                changed_domains=("hardware",),
                unchanged_domains=(),
            )

    def test_unsupported_recommendation_fails_closed(self) -> None:
        proposal = self._proposal(self.changed, "proposal-unsupported")
        object.__setattr__(proposal, "recommendation", "UNSUPPORTED")
        with self.assertRaises(EnvironmentWorldModelRevisionDecisionError):
            self.service.decide(proposal, decision_id="decision-unsupported")


if __name__ == "__main__":
    unittest.main()
