import unittest

from src.core.environment_world_model import EnvironmentWorldModel
from src.core.environment_world_model_rollback_repair_application import (
    EnvironmentWorldModelRollbackRepairApplication,
    EnvironmentWorldModelRollbackRepairApplicationError,
    EnvironmentWorldModelRollbackRepairApplicationService,
)
from src.core.environment_world_model_rollback_repair_decision import (
    EnvironmentWorldModelRollbackRepairDecision,
)
from src.core.environment_world_model_rollback_repair_proposal import (
    EnvironmentWorldModelRollbackRepairProposal,
)
from src.core.environment_world_model_store import InMemoryEnvironmentWorldModelStore


class EnvironmentWorldModelRollbackRepairApplicationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.observed = EnvironmentWorldModel(
            model_id="observed",
            environment_id="env1",
            state_by_domain={"hardware": {"cpu": 1}},
            represented_domains=("hardware",),
            missing_domains=("software",),
            context_ids=("ctx-observed",),
            qualification_ids=("q-observed",),
            provenance_ids=("p-observed",),
            readiness_id="r-observed",
            source_bundle_id="b-observed",
            lineage={"source": "observed"},
        )
        self.expected = EnvironmentWorldModel(
            model_id="expected",
            environment_id="env1",
            state_by_domain={"hardware": {"cpu": 4}},
            represented_domains=("hardware",),
            missing_domains=("software",),
            context_ids=("ctx-expected",),
            qualification_ids=("q-expected",),
            provenance_ids=("p-expected",),
            readiness_id="r-expected",
            source_bundle_id="b-expected",
            lineage={"source": "expected"},
        )
        self.proposal = EnvironmentWorldModelRollbackRepairProposal(
            proposal_id="proposal1",
            environment_id="env1",
            verification_decision_id="verification-decision1",
            expected_model_id="expected",
            observed_model_id="observed",
            recommendation="REPAIR",
            reasons={"status": "repair"},
            lineage={"source": "proposal"},
        )
        self.decision = EnvironmentWorldModelRollbackRepairDecision(
            decision_id="decision1",
            environment_id="env1",
            repair_proposal_id="proposal1",
            expected_model_id="expected",
            observed_model_id="observed",
            decision="ACCEPT",
            reasons={"status": "accept"},
            lineage={"source": "decision"},
        )
        self.store = InMemoryEnvironmentWorldModelStore({"env1": self.observed})
        self.service = EnvironmentWorldModelRollbackRepairApplicationService()

    def test_accept_replaces_observed_with_expected(self) -> None:
        result, application = self.service.apply(
            self.proposal,
            self.decision,
            self.expected,
            self.store,
            application_id="application1",
        )
        self.assertEqual(result, self.expected)
        self.assertEqual(self.store.get("env1"), self.expected)
        self.assertTrue(application.applied)
        self.assertEqual(application.previous_model_id, "observed")
        self.assertEqual(application.resulting_model_id, "expected")

    def test_reject_retains_observed_model(self) -> None:
        rejected = EnvironmentWorldModelRollbackRepairDecision(
            decision_id="decision2",
            environment_id="env1",
            repair_proposal_id="proposal1",
            expected_model_id="expected",
            observed_model_id="observed",
            decision="REJECT",
            reasons={},
            lineage={},
        )
        result, application = self.service.apply(
            self.proposal,
            rejected,
            self.expected,
            self.store,
            application_id="application2",
        )
        self.assertEqual(result, self.observed)
        self.assertEqual(self.store.get("env1"), self.observed)
        self.assertFalse(application.applied)

    def test_compare_and_swap_rejects_stale_current(self) -> None:
        stale = EnvironmentWorldModel(
            model_id="changed",
            environment_id="env1",
            state_by_domain={},
            represented_domains=(),
            missing_domains=("hardware", "software"),
            context_ids=(),
            qualification_ids=(),
            provenance_ids=(),
            readiness_id="r-changed",
            source_bundle_id="b-changed",
            lineage={},
        )
        self.store.put(stale)
        with self.assertRaises(EnvironmentWorldModelRollbackRepairApplicationError):
            self.service.apply(
                self.proposal,
                self.decision,
                self.expected,
                self.store,
                application_id="application1",
            )

    def test_expected_identity_must_match_model(self) -> None:
        foreign_expected = EnvironmentWorldModel(
            model_id="other",
            environment_id="env1",
            state_by_domain={},
            represented_domains=(),
            missing_domains=(),
            context_ids=(),
            qualification_ids=(),
            provenance_ids=(),
            readiness_id="r-other",
            source_bundle_id="b-other",
            lineage={},
        )
        with self.assertRaises(EnvironmentWorldModelRollbackRepairApplicationError):
            self.service.apply(
                self.proposal,
                self.decision,
                foreign_expected,
                self.store,
                application_id="application1",
            )

    def test_observed_identity_must_match_current(self) -> None:
        mismatched_proposal = EnvironmentWorldModelRollbackRepairProposal(
            proposal_id="proposal2",
            environment_id="env1",
            verification_decision_id="verification-decision1",
            expected_model_id="expected",
            observed_model_id="not-current",
            recommendation="REPAIR",
            reasons={},
            lineage={},
        )
        with self.assertRaises(EnvironmentWorldModelRollbackRepairApplicationError):
            self.service.apply(
                mismatched_proposal,
                self.decision,
                self.expected,
                self.store,
                application_id="application1",
            )

    def test_environment_identity_must_match(self) -> None:
        foreign_expected = EnvironmentWorldModel(
            model_id="expected-foreign",
            environment_id="env2",
            state_by_domain={},
            represented_domains=(),
            missing_domains=(),
            context_ids=(),
            qualification_ids=(),
            provenance_ids=(),
            readiness_id="r2",
            source_bundle_id="b2",
            lineage={},
        )
        with self.assertRaises(EnvironmentWorldModelRollbackRepairApplicationError):
            self.service.apply(
                self.proposal,
                self.decision,
                foreign_expected,
                self.store,
                application_id="application1",
            )

    def test_source_objects_are_not_mutated(self) -> None:
        proposal = self.proposal
        decision = self.decision
        observed = self.observed
        expected = self.expected
        self.service.apply(
            proposal,
            decision,
            expected,
            self.store,
            application_id="application1",
        )
        self.assertEqual(proposal.recommendation, "REPAIR")
        self.assertEqual(decision.decision, "ACCEPT")
        self.assertEqual(observed.model_id, "observed")
        self.assertEqual(expected.model_id, "expected")

    def test_nested_result_data_is_immutable(self) -> None:
        _, application = self.service.apply(
            self.proposal,
            self.decision,
            self.expected,
            self.store,
            application_id="application1",
            reasons={"nested": {"value": "x"}},
            lineage={"nested": ["x"]},
        )
        with self.assertRaises(TypeError):
            application.reasons["nested"]["value"] = "y"
        with self.assertRaises(TypeError):
            application.lineage["nested"] = ("y",)

    def test_advisory_and_truth_boundaries_remain_false(self) -> None:
        application = EnvironmentWorldModelRollbackRepairApplication(
            application_id="application1",
            environment_id="env1",
            previous_model_id="observed",
            expected_model_id="expected",
            resulting_model_id="expected",
            decision_id="decision1",
            applied=True,
            reasons={},
            lineage={},
        )
        self.assertFalse(application.mutates_source_objects)
        self.assertFalse(application.establishes_truth)


if __name__ == "__main__":
    unittest.main()
