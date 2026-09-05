import unittest
from datetime import datetime, timezone
from types import MappingProxyType

from src.core.environment_world_model_rollback_repair_follow_up_action_decision import (
    EnvironmentWorldModelRollbackRepairFollowUpActionDecision,
)
from src.core.environment_world_model_rollback_repair_retry_eligibility import (
    EnvironmentWorldModelRollbackRepairRetryEligibility,
    EnvironmentWorldModelRollbackRepairRetryEligibilityError,
    EnvironmentWorldModelRollbackRepairRetryEligibilityService,
    EnvironmentWorldModelRollbackRepairRetryPolicy,
)


class EnvironmentWorldModelRollbackRepairRetryEligibilityTests(unittest.TestCase):
    def setUp(self) -> None:
        self.accepted = EnvironmentWorldModelRollbackRepairFollowUpActionDecision(
            decision_id="action-decision1",
            environment_id="env1",
            proposal_id="action-proposal1",
            follow_up_decision_id="follow-up-decision1",
            expected_model_id="expected",
            observed_model_id="observed",
            decision="ACCEPT",
            reasons={"status": "accepted"},
            lineage={"source": "action-decision"},
        )
        self.rejected = EnvironmentWorldModelRollbackRepairFollowUpActionDecision(
            decision_id="action-decision2",
            environment_id="env1",
            proposal_id="action-proposal2",
            follow_up_decision_id="follow-up-decision2",
            expected_model_id="expected",
            observed_model_id="observed",
            decision="REJECT",
            reasons={},
            lineage={},
        )
        self.deferred = EnvironmentWorldModelRollbackRepairFollowUpActionDecision(
            decision_id="action-decision3",
            environment_id="env1",
            proposal_id="action-proposal3",
            follow_up_decision_id="follow-up-decision3",
            expected_model_id="expected",
            observed_model_id="observed",
            decision="DEFER",
            reasons={},
            lineage={},
        )
        self.policy = EnvironmentWorldModelRollbackRepairRetryPolicy(
            max_retries=3,
            base_backoff_seconds=10.0,
            backoff_multiplier=2.0,
            max_backoff_seconds=25.0,
        )
        self.now = datetime(2026, 9, 5, 20, 0, tzinfo=timezone.utc)
        self.service = EnvironmentWorldModelRollbackRepairRetryEligibilityService()

    def test_accepted_decision_is_eligible_within_limit(self) -> None:
        result = self.service.evaluate(
            self.accepted,
            self.policy,
            eligibility_id="eligibility1",
            retry_count=1,
            evaluated_at=self.now,
        )
        self.assertTrue(result.eligible)
        self.assertEqual(result.backoff_seconds, 20.0)
        self.assertEqual(
            result.next_eligible_at,
            datetime(2026, 9, 5, 20, 0, 20, tzinfo=timezone.utc),
        )
        self.assertTrue(result.is_advisory_only)
        self.assertFalse(result.authorizes_retry)
        self.assertFalse(result.executes_retry)

    def test_backoff_is_capped(self) -> None:
        result = self.service.evaluate(
            self.accepted,
            self.policy,
            eligibility_id="eligibility2",
            retry_count=2,
            evaluated_at=self.now,
        )
        self.assertEqual(result.backoff_seconds, 25.0)

    def test_retry_limit_is_fail_closed(self) -> None:
        result = self.service.evaluate(
            self.accepted,
            self.policy,
            eligibility_id="eligibility3",
            retry_count=3,
            evaluated_at=self.now,
        )
        self.assertFalse(result.eligible)
        self.assertIsNone(result.next_eligible_at)
        self.assertEqual(result.backoff_seconds, 0.0)

    def test_rejected_action_is_not_eligible(self) -> None:
        result = self.service.evaluate(
            self.rejected,
            self.policy,
            eligibility_id="eligibility4",
            retry_count=0,
            evaluated_at=self.now,
        )
        self.assertFalse(result.eligible)
        self.assertIsNone(result.next_eligible_at)

    def test_deferred_action_is_not_eligible(self) -> None:
        result = self.service.evaluate(
            self.deferred,
            self.policy,
            eligibility_id="eligibility5",
            retry_count=0,
            evaluated_at=self.now,
        )
        self.assertFalse(result.eligible)
        self.assertIsNone(result.next_eligible_at)

    def test_policy_zero_retries_never_allows_retry(self) -> None:
        policy = EnvironmentWorldModelRollbackRepairRetryPolicy(max_retries=0)
        result = self.service.evaluate(
            self.accepted,
            policy,
            eligibility_id="eligibility6",
            retry_count=0,
            evaluated_at=self.now,
        )
        self.assertFalse(result.eligible)

    def test_policy_rejects_invalid_limits_and_backoff(self) -> None:
        with self.assertRaises(ValueError):
            EnvironmentWorldModelRollbackRepairRetryPolicy(max_retries=-1)
        with self.assertRaises(ValueError):
            EnvironmentWorldModelRollbackRepairRetryPolicy(
                max_retries=1, backoff_multiplier=0.5
            )
        with self.assertRaises(ValueError):
            EnvironmentWorldModelRollbackRepairRetryPolicy(
                max_retries=1,
                base_backoff_seconds=20,
                max_backoff_seconds=10,
            )

    def test_invalid_retry_count_and_timestamp_are_rejected(self) -> None:
        with self.assertRaises(ValueError):
            self.service.evaluate(
                self.accepted,
                self.policy,
                eligibility_id="eligibility7",
                retry_count=-1,
                evaluated_at=self.now,
            )
        with self.assertRaises(ValueError):
            self.service.evaluate(
                self.accepted,
                self.policy,
                eligibility_id="eligibility8",
                retry_count=0,
                evaluated_at=datetime(2026, 9, 5, 20, 0),
            )

    def test_wrong_upstream_types_fail_closed(self) -> None:
        with self.assertRaises(TypeError):
            self.service.evaluate(
                object(),
                self.policy,
                eligibility_id="eligibility9",
                retry_count=0,
                evaluated_at=self.now,
            )
        with self.assertRaises(TypeError):
            self.service.evaluate(
                self.accepted,
                object(),
                eligibility_id="eligibility10",
                retry_count=0,
                evaluated_at=self.now,
            )

    def test_lineage_and_identity_are_preserved(self) -> None:
        result = self.service.evaluate(
            self.accepted,
            self.policy,
            eligibility_id="eligibility11",
            retry_count=0,
            evaluated_at=self.now,
            lineage={"nested": {"source": "test"}},
        )
        self.assertEqual(result.action_decision_id, "action-decision1")
        self.assertEqual(result.environment_id, "env1")
        self.assertEqual(result.expected_model_id, "expected")
        self.assertEqual(result.observed_model_id, "observed")
        self.assertEqual(result.lineage["nested"]["source"], "test")

    def test_nested_evidence_is_immutable(self) -> None:
        result = self.service.evaluate(
            self.accepted,
            self.policy,
            eligibility_id="eligibility12",
            retry_count=0,
            evaluated_at=self.now,
            reasons={"nested": {"value": "x"}},
            lineage={"nested": ["x"]},
        )
        self.assertIsInstance(result.reasons, MappingProxyType)
        with self.assertRaises(TypeError):
            result.reasons["nested"]["value"] = "y"
        with self.assertRaises(TypeError):
            result.lineage["nested"] = ("y",)

    def test_policy_backoff_is_deterministic(self) -> None:
        self.assertEqual(self.policy.backoff_seconds_for_retry(0), 10.0)
        self.assertEqual(self.policy.backoff_seconds_for_retry(1), 20.0)
        self.assertEqual(self.policy.backoff_seconds_for_retry(2), 25.0)
        with self.assertRaises(ValueError):
            self.policy.backoff_seconds_for_retry(-1)

    def test_result_is_the_only_artifact_no_execution_occurs(self) -> None:
        result = self.service.evaluate(
            self.accepted,
            self.policy,
            eligibility_id="eligibility13",
            retry_count=0,
            evaluated_at=self.now,
        )
        self.assertIsInstance(result, EnvironmentWorldModelRollbackRepairRetryEligibility)
        self.assertFalse(result.authorizes_retry)
        self.assertFalse(result.executes_retry)

    def test_unsupported_decision_artifact_fails_closed(self) -> None:
        invalid = object.__new__(EnvironmentWorldModelRollbackRepairFollowUpActionDecision)
        object.__setattr__(invalid, "decision_id", "bad")
        object.__setattr__(invalid, "environment_id", "env1")
        object.__setattr__(invalid, "proposal_id", "proposal")
        object.__setattr__(invalid, "follow_up_decision_id", "follow-up")
        object.__setattr__(invalid, "expected_model_id", "expected")
        object.__setattr__(invalid, "observed_model_id", "observed")
        object.__setattr__(invalid, "decision", "RETRY")
        object.__setattr__(invalid, "reasons", MappingProxyType({}))
        object.__setattr__(invalid, "lineage", MappingProxyType({}))
        with self.assertRaises(EnvironmentWorldModelRollbackRepairRetryEligibilityError):
            self.service.evaluate(
                invalid,
                self.policy,
                eligibility_id="eligibility14",
                retry_count=0,
                evaluated_at=self.now,
            )


if __name__ == "__main__":
    unittest.main()
