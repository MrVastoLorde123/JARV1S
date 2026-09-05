import unittest

from src.core.environment_world_model import EnvironmentWorldModel
from src.core.environment_world_model_change_assessment import (
    EnvironmentWorldModelChangeAssessmentService,
)
from src.core.environment_world_model_revision_proposal import (
    EnvironmentWorldModelRevisionProposal,
    EnvironmentWorldModelRevisionProposalError,
    EnvironmentWorldModelRevisionProposalService,
)


class EnvironmentWorldModelRevisionProposalTests(unittest.TestCase):
    def setUp(self) -> None:
        self.baseline = EnvironmentWorldModel(
            model_id="model-baseline",
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
        self.candidate = EnvironmentWorldModel(
            model_id="model-candidate",
            environment_id="env-1",
            state_by_domain={
                "hardware": {"cpu": "arm64"},
                "software": {"os": "linux"},
            },
            represented_domains=("hardware", "software"),
            missing_domains=("network",),
            context_ids=("ctx-2",),
            qualification_ids=("qual-2",),
            provenance_ids=("prov-2",),
            readiness_id="ready-2",
            source_bundle_id="bundle-2",
        )
        self.assessment_service = EnvironmentWorldModelChangeAssessmentService()
        self.service = EnvironmentWorldModelRevisionProposalService()

    def _assessment(self):
        return self.assessment_service.assess(
            self.baseline,
            self.candidate,
            assessment_id="assessment-1",
        )

    def test_changed_model_produces_consider_revision(self) -> None:
        result = self.service.propose(
            self.baseline,
            self.candidate,
            self._assessment(),
            proposal_id="proposal-1",
        )
        self.assertIsInstance(result, EnvironmentWorldModelRevisionProposal)
        self.assertEqual(result.recommendation, "CONSIDER_REVISION")
        self.assertEqual(result.changed_domains, ("hardware", "software"))
        self.assertTrue(result.is_advisory_only)
        self.assertFalse(result.applies_revision)

    def test_unchanged_model_produces_no_change(self) -> None:
        identical_state = EnvironmentWorldModel(
            model_id="model-same-state",
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
        assessment = self.assessment_service.assess(
            self.baseline,
            identical_state,
            assessment_id="assessment-unchanged",
        )
        result = self.service.propose(
            self.baseline,
            identical_state,
            assessment,
            proposal_id="proposal-unchanged",
        )
        self.assertEqual(result.recommendation, "NO_CHANGE")
        self.assertEqual(result.changed_domains, ())

    def test_assessment_identities_must_align(self) -> None:
        assessment = self._assessment()
        wrong_baseline = EnvironmentWorldModel(
            model_id="model-wrong-baseline",
            environment_id="env-1",
            state_by_domain={"hardware": {"cpu": "x86"}},
            represented_domains=("hardware",),
            missing_domains=("software", "network"),
            context_ids=("ctx-x",),
            qualification_ids=("qual-x",),
            provenance_ids=("prov-x",),
            readiness_id="ready-x",
            source_bundle_id="bundle-x",
        )
        with self.assertRaises(EnvironmentWorldModelRevisionProposalError):
            self.service.propose(
                wrong_baseline,
                self.candidate,
                assessment,
                proposal_id="proposal-invalid",
            )

    def test_wrong_types_are_rejected(self) -> None:
        with self.assertRaises(TypeError):
            self.service.propose(
                object(),
                self.candidate,
                self._assessment(),
                proposal_id="proposal-type",
            )
        with self.assertRaises(TypeError):
            self.service.propose(
                self.baseline,
                self.candidate,
                object(),
                proposal_id="proposal-type-2",
            )

    def test_same_environment_is_required(self) -> None:
        other = EnvironmentWorldModel(
            model_id="model-other-env",
            environment_id="env-2",
            state_by_domain={"hardware": {"cpu": "arm64"}},
            represented_domains=("hardware",),
            missing_domains=("software",),
            context_ids=("ctx-other",),
            qualification_ids=("qual-other",),
            provenance_ids=("prov-other",),
            readiness_id="ready-other",
            source_bundle_id="bundle-other",
        )
        assessment = self._assessment()
        with self.assertRaises(EnvironmentWorldModelRevisionProposalError):
            self.service.propose(
                self.baseline,
                other,
                assessment,
                proposal_id="proposal-env",
            )

    def test_nested_reason_and_lineage_data_are_immutable(self) -> None:
        result = self.service.propose(
            self.baseline,
            self.candidate,
            self._assessment(),
            proposal_id="proposal-immutable",
            reasons={"status": "explicit change", "detail": {"source": "assessment"}},
            lineage={"assessment": {"id": "assessment-1"}},
        )
        with self.assertRaises(TypeError):
            result.reasons["status"] = "changed"
        with self.assertRaises(TypeError):
            result.reasons["detail"]["source"] = "changed"
        with self.assertRaises(TypeError):
            result.lineage["assessment"]["id"] = "changed"

    def test_sources_are_not_mutated(self) -> None:
        baseline_before = dict(self.baseline.state_by_domain["hardware"])
        candidate_before = dict(self.candidate.state_by_domain["hardware"])
        self.service.propose(
            self.baseline,
            self.candidate,
            self._assessment(),
            proposal_id="proposal-no-mutation",
        )
        self.assertEqual(dict(self.baseline.state_by_domain["hardware"]), baseline_before)
        self.assertEqual(dict(self.candidate.state_by_domain["hardware"]), candidate_before)

    def test_authority_fields_are_absent(self) -> None:
        result = self.service.propose(
            self.baseline,
            self.candidate,
            self._assessment(),
            proposal_id="proposal-authority",
        )
        forbidden = {
            "authority_granted",
            "authorization_granted",
            "execution_requested",
            "permission_granted",
            "truth_proven",
            "adaptation_truth_proven",
            "revision_applied",
        }
        self.assertTrue(forbidden.isdisjoint(vars(result)))


if __name__ == "__main__":
    unittest.main()
