import unittest

from src.core.environment_world_model import EnvironmentWorldModel
from src.core.environment_world_model_revision_application import (
    EnvironmentWorldModelRevisionApplication,
    EnvironmentWorldModelRevisionApplicationService,
)
from src.core.environment_world_model_revision_decision import (
    EnvironmentWorldModelRevisionDecision,
)


class EnvironmentWorldModelRevisionApplicationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.baseline = EnvironmentWorldModel(
            model_id="model-1",
            environment_id="env-1",
            state_by_domain={"hardware": {"cpu": "x86"}},
            represented_domains=("hardware",),
            missing_domains=("software",),
            context_ids=("ctx-1",),
            qualification_ids=("qual-1",),
            provenance_ids=("prov-1",),
            readiness_id="ready-1",
            source_bundle_id="bundle-1",
        )
        self.candidate = EnvironmentWorldModel(
            model_id="model-2",
            environment_id="env-1",
            state_by_domain={"hardware": {"cpu": "arm64"}},
            represented_domains=("hardware",),
            missing_domains=("software",),
            context_ids=("ctx-2",),
            qualification_ids=("qual-2",),
            provenance_ids=("prov-2",),
            readiness_id="ready-2",
            source_bundle_id="bundle-2",
        )
        self.service = EnvironmentWorldModelRevisionApplicationService()

    def decision(self, value: str) -> EnvironmentWorldModelRevisionDecision:
        return EnvironmentWorldModelRevisionDecision(
            decision_id="decision-1",
            environment_id="env-1",
            baseline_model_id="model-1",
            candidate_model_id="model-2",
            proposal_id="proposal-1",
            assessment_id="assessment-1",
            decision=value,
            changed_domains=("hardware",),
            unchanged_domains=(),
        )

    def test_accept_returns_candidate_and_applied_record(self) -> None:
        result, application = self.service.apply(
            self.baseline,
            self.candidate,
            self.decision("ACCEPT"),
            application_id="application-1",
        )
        self.assertIs(result, self.candidate)
        self.assertIsInstance(application, EnvironmentWorldModelRevisionApplication)
        self.assertTrue(application.applied)
        self.assertEqual(application.resulting_model_id, "model-2")

    def test_reject_retains_baseline(self) -> None:
        result, application = self.service.apply(
            self.baseline,
            self.candidate,
            self.decision("REJECT"),
            application_id="application-2",
        )
        self.assertIs(result, self.baseline)
        self.assertFalse(application.applied)
        self.assertEqual(application.resulting_model_id, "model-1")

    def test_defer_retains_baseline(self) -> None:
        result, application = self.service.apply(
            self.baseline,
            self.candidate,
            self.decision("DEFER"),
            application_id="application-3",
        )
        self.assertIs(result, self.baseline)
        self.assertFalse(application.applied)

    def test_environment_identity_must_align(self) -> None:
        other = EnvironmentWorldModel(
            model_id="model-3",
            environment_id="env-2",
            state_by_domain={"hardware": {"cpu": "arm64"}},
            represented_domains=("hardware",),
            missing_domains=("software",),
            context_ids=("ctx-3",),
            qualification_ids=("qual-3",),
            provenance_ids=("prov-3",),
            readiness_id="ready-3",
            source_bundle_id="bundle-3",
        )
        with self.assertRaisesRegex(RuntimeError, "share an environment"):
            self.service.apply(
                self.baseline,
                other,
                self.decision("ACCEPT"),
                application_id="application-4",
            )
        mismatched = EnvironmentWorldModelRevisionDecision(
            decision_id="decision-2",
            environment_id="env-2",
            baseline_model_id="model-1",
            candidate_model_id="model-2",
            proposal_id="proposal-2",
            assessment_id="assessment-2",
            decision="ACCEPT",
            changed_domains=("hardware",),
            unchanged_domains=(),
        )
        with self.assertRaisesRegex(RuntimeError, "share an environment"):
            self.service.apply(
                self.baseline,
                self.candidate,
                mismatched,
                application_id="application-5",
            )

    def test_decision_model_identities_must_match_sources(self) -> None:
        mismatched = EnvironmentWorldModelRevisionDecision(
            decision_id="decision-3",
            environment_id="env-1",
            baseline_model_id="wrong-baseline",
            candidate_model_id="model-2",
            proposal_id="proposal-3",
            assessment_id="assessment-3",
            decision="ACCEPT",
            changed_domains=("hardware",),
            unchanged_domains=(),
        )
        with self.assertRaisesRegex(RuntimeError, "baseline identity"):
            self.service.apply(
                self.baseline,
                self.candidate,
                mismatched,
                application_id="application-6",
            )

    def test_source_objects_are_not_mutated(self) -> None:
        baseline_state = dict(self.baseline.state_by_domain["hardware"])
        candidate_state = dict(self.candidate.state_by_domain["hardware"])
        self.service.apply(
            self.baseline,
            self.candidate,
            self.decision("ACCEPT"),
            application_id="application-7",
        )
        self.assertEqual(dict(self.baseline.state_by_domain["hardware"]), baseline_state)
        self.assertEqual(dict(self.candidate.state_by_domain["hardware"]), candidate_state)

    def test_application_record_is_immutable(self) -> None:
        _, application = self.service.apply(
            self.baseline,
            self.candidate,
            self.decision("ACCEPT"),
            application_id="application-8",
            reasons={"status": "manual review"},
            lineage={"decision": {"id": "decision-1"}},
        )
        with self.assertRaises(TypeError):
            application.reasons["status"] = "changed"
        with self.assertRaises(TypeError):
            application.lineage["decision"]["id"] = "changed"
        with self.assertRaises(AttributeError):
            application.application_id = "changed"

    def test_lineage_and_reasons_are_preserved(self) -> None:
        _, application = self.service.apply(
            self.baseline,
            self.candidate,
            self.decision("ACCEPT"),
            application_id="application-9",
            reasons={"status": "approved candidate"},
            lineage={"decision_id": "decision-1"},
        )
        self.assertEqual(application.reasons["status"], "approved candidate")
        self.assertEqual(application.lineage["decision_id"], "decision-1")

    def test_authority_fields_are_absent(self) -> None:
        _, application = self.service.apply(
            self.baseline,
            self.candidate,
            self.decision("ACCEPT"),
            application_id="application-10",
        )
        forbidden = {
            "authority_granted",
            "authorization_granted",
            "permission_granted",
            "truth_proven",
            "execution_requested",
            "adaptation_truth_proven",
        }
        self.assertTrue(forbidden.isdisjoint(vars(application)))
        self.assertFalse(application.is_mutation_of_source_objects)

    def test_wrong_types_are_rejected(self) -> None:
        with self.assertRaises(TypeError):
            self.service.apply(
                object(),
                self.candidate,
                self.decision("ACCEPT"),
                application_id="application-11",
            )
        with self.assertRaises(TypeError):
            self.service.apply(
                self.baseline,
                object(),
                self.decision("ACCEPT"),
                application_id="application-12",
            )
        with self.assertRaises(TypeError):
            self.service.apply(
                self.baseline,
                self.candidate,
                object(),
                application_id="application-13",
            )


if __name__ == "__main__":
    unittest.main()
