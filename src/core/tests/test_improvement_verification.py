import unittest
from dataclasses import FrozenInstanceError
from types import MappingProxyType

from src.core.improvement_application import ImprovementApplicationStatus
from src.core.improvement_verification import (
    ImprovementRollbackStatus,
    ImprovementVerificationService,
    ImprovementVerificationStatus,
)
from src.core.tests.test_improvement_application import M24_4ImprovementApplicationTests


class M24_5ImprovementVerificationRollbackTests(unittest.TestCase):
    def _make_application(self):
        return M24_4ImprovementApplicationTests()._apply()

    def _verify(self, application=None, **kwargs):
        values = {
            "verification_id": "improvement-verification-245",
            "verifier_id": "verification-engine",
            "verification_purpose": "verify-applied-candidate",
            "verification_scope": "bounded-target-state",
            "observed_result": {"threshold": 0.95, "health": "reported-healthy"},
            "expected_result": {"threshold": 0.95, "health": "healthy"},
            "verification_status": ImprovementVerificationStatus.VERIFIED,
            "rollback_status": ImprovementRollbackStatus.NOT_REQUIRED,
            "rollback_result": {"action": "none-required"},
        }
        values.update(kwargs)
        return ImprovementVerificationService().verify(application or self._make_application(), **values)

    def test_applied_application_forms_verified_record(self):
        result = self._verify()
        self.assertTrue(result.is_verified)
        self.assertFalse(result.is_invalid)
        self.assertEqual(result.application_id, "application-162")
        self.assertEqual(result.source_status, ImprovementApplicationStatus.APPLIED)
        self.assertEqual(result.rollback_status, ImprovementRollbackStatus.NOT_REQUIRED)

    def test_exact_application_type_is_required(self):
        with self.assertRaises(TypeError):
            self._verify(application=object())

    def test_source_must_be_applied(self):
        source = self._make_application()
        rejected = source.__class__(**{**source.__dict__, "status": ImprovementApplicationStatus.FAILED})
        result = self._verify(rejected)
        self.assertTrue(result.is_invalid)
        self.assertEqual(result.rollback_status, ImprovementRollbackStatus.INVALID)
        self.assertIn("source application is not APPLIED", result.reasons)

    def test_verification_identity_must_be_distinct(self):
        source = self._make_application()
        for identity in (source.application_id, source.decision_id, source.evaluation_id, source.candidate_id):
            with self.subTest(identity=identity):
                with self.assertRaises(ValueError):
                    self._verify(source, verification_id=identity)

    def test_required_metadata_is_enforced(self):
        service = ImprovementVerificationService()
        source = self._make_application()
        common = {
            "verifier_id": "verifier",
            "verification_purpose": "verify",
            "verification_scope": "bounded",
            "observed_result": {"x": 1},
            "expected_result": {"x": 1},
            "verification_status": ImprovementVerificationStatus.VERIFIED,
            "rollback_status": ImprovementRollbackStatus.NOT_REQUIRED,
            "rollback_result": {"action": "none"},
        }
        for field in ("verification_id", "verifier_id", "verification_purpose", "verification_scope"):
            values = dict(common, verification_id="verification-245")
            values[field] = " "
            with self.subTest(field=field):
                with self.assertRaises(ValueError):
                    service.verify(source, **values)
        with self.assertRaises(ValueError):
            service.verify(source, verification_id="verification-245", verifier_id="verifier", verification_purpose="verify", verification_scope="bounded", observed_result=None, expected_result={"x": 1}, verification_status=ImprovementVerificationStatus.VERIFIED, rollback_status=ImprovementRollbackStatus.NOT_REQUIRED, rollback_result={"action": "none"})
        with self.assertRaises(ValueError):
            service.verify(source, verification_id="verification-245", verifier_id="verifier", verification_purpose="verify", verification_scope="bounded", observed_result={"x": 1}, expected_result=None, verification_status=ImprovementVerificationStatus.VERIFIED, rollback_status=ImprovementRollbackStatus.NOT_REQUIRED, rollback_result={"action": "none"})
        with self.assertRaises(ValueError):
            service.verify(source, verification_id="verification-245", verifier_id="verifier", verification_purpose="verify", verification_scope="bounded", observed_result={"x": 1}, expected_result={"x": 1}, verification_status=ImprovementVerificationStatus.VERIFIED, rollback_status=ImprovementRollbackStatus.NOT_REQUIRED, rollback_result=None)

    def test_statuses_are_typed_and_bounded(self):
        service = ImprovementVerificationService()
        source = self._make_application()
        with self.assertRaises(TypeError):
            service.verify(source, verification_id="v-245", verifier_id="v", verification_purpose="p", verification_scope="s", observed_result={"x": 1}, expected_result={"x": 1}, verification_status="VERIFIED", rollback_status=ImprovementRollbackStatus.NOT_REQUIRED, rollback_result={"x": 1})
        with self.assertRaises(TypeError):
            service.verify(source, verification_id="v-245", verifier_id="v", verification_purpose="p", verification_scope="s", observed_result={"x": 1}, expected_result={"x": 1}, verification_status=ImprovementVerificationStatus.VERIFIED, rollback_status="REQUIRED", rollback_result={"x": 1})
        self.assertEqual({item.value for item in ImprovementVerificationStatus}, {"VERIFIED", "FAILED", "INVALID"})
        self.assertEqual({item.value for item in ImprovementRollbackStatus}, {"NOT_REQUIRED", "REQUIRED", "RECORDED", "FAILED", "INVALID"})

    def test_all_verification_statuses_are_recordable(self):
        for status in ImprovementVerificationStatus:
            result = self._verify(verification_id=f"verification-{status.value.lower()}-245", verification_status=status)
            self.assertIs(result.verification_status, status)

    def test_all_rollback_statuses_are_recordable(self):
        for status in ImprovementRollbackStatus:
            result = self._verify(verification_id=f"rollback-{status.value.lower()}-245", rollback_status=status)
            self.assertIs(result.rollback_status, status)

    def test_anchored_lineage_is_rechecked(self):
        source = self._make_application()
        original = source.lineage
        anchors = (
            "application_id", "decision_id", "evaluation_id", "candidate_id", "consumption_id",
            "integrity_id", "validation_id", "transition_id", "evidence_id", "proposal_id",
            "eligibility_id", "source_integrity_id", "source_validation_id",
        )
        for field in anchors:
            tampered = dict(original)
            tampered[field] = "tampered"
            altered = source.__class__(**{**source.__dict__, "lineage": tampered})
            result = self._verify(altered, verification_id=f"verification-{field}-245")
            self.assertTrue(result.is_invalid, msg=field)
            self.assertIn(f"{field} lineage mismatch", result.reasons, msg=field)

    def test_provenance_is_preserved(self):
        result = self._verify()
        for field in (
            "application_id", "decision_id", "evaluation_id", "candidate_id", "consumption_id",
            "integrity_id", "validation_id", "transition_id", "evidence_id", "proposal_id",
            "eligibility_id", "source_integrity_id", "source_validation_id", "state_key",
        ):
            self.assertEqual(getattr(result, field), getattr(self._make_application(), field))

    def test_result_and_lineage_are_recursively_immutable(self):
        result = self._verify(
            observed_result={"steps": ["one", {"ok": True}]},
            expected_result={"steps": ["one", {"ok": True}]},
            rollback_result={"details": [{"stage": 1}]},
            lineage={"chain": ["a", {"depth": 2}]},
        )
        self.assertIsInstance(result.observed_result, MappingProxyType)
        self.assertIsInstance(result.expected_result, MappingProxyType)
        self.assertIsInstance(result.rollback_result, MappingProxyType)
        self.assertIsInstance(result.lineage, MappingProxyType)
        self.assertIsInstance(result.observed_result["steps"], tuple)
        self.assertIsInstance(result.lineage["chain"][1], MappingProxyType)
        with self.assertRaises(TypeError):
            result.lineage["x"] = "y"
        with self.assertRaises((AttributeError, FrozenInstanceError)):
            result.verification_status = ImprovementVerificationStatus.FAILED

    def test_source_is_not_mutated(self):
        source = self._make_application()
        before = source
        self._verify(source)
        self.assertEqual(source, before)

    def test_failed_verification_can_require_rollback_without_executing_it(self):
        result = self._verify(
            verification_id="verification-failed-245",
            verification_status=ImprovementVerificationStatus.FAILED,
            rollback_status=ImprovementRollbackStatus.REQUIRED,
            observed_result={"health": "degraded"},
            expected_result={"health": "healthy"},
            rollback_result={"requested": True, "executed": False},
        )
        self.assertTrue(result.is_failed)
        self.assertTrue(result.requires_rollback)
        self.assertFalse(result.rollback_recorded)
        self.assertFalse(result.executes_rollback)
        self.assertFalse(result.authorizes_rollback)

    def test_recorded_rollback_is_evidence_only(self):
        result = self._verify(
            verification_id="verification-rollback-recorded-245",
            verification_status=ImprovementVerificationStatus.FAILED,
            rollback_status=ImprovementRollbackStatus.RECORDED,
            rollback_result={"reported": "rollback-complete", "executor": "external"},
        )
        self.assertTrue(result.rollback_recorded)
        self.assertFalse(result.executes_rollback)
        self.assertFalse(result.authorizes_rollback)

    def test_execution_and_authority_walls_are_closed(self):
        for result in (
            self._verify(),
            self._verify(verification_id="verification-failed-wall-245", verification_status=ImprovementVerificationStatus.FAILED, rollback_status=ImprovementRollbackStatus.REQUIRED),
        ):
            for name in (
                "executes_rollback", "authorizes_rollback", "executes_improvement", "mutates_model",
                "mutates_memory", "mutates_policy", "mutates_state", "persists_state",
                "establishes_truth", "establishes_certainty",
            ):
                self.assertFalse(getattr(result, name))

    def test_status_properties_are_stable(self):
        verified = self._verify()
        failed = self._verify(verification_id="verification-failed-status-245", verification_status=ImprovementVerificationStatus.FAILED, rollback_status=ImprovementRollbackStatus.REQUIRED)
        invalid = self._verify(verification_id="verification-invalid-status-245")
        self.assertTrue(verified.is_verified)
        self.assertFalse(verified.is_failed)
        self.assertFalse(failed.is_verified)
        self.assertTrue(failed.is_failed)
        self.assertTrue(invalid.is_verified or invalid.is_invalid)


if __name__ == "__main__":
    unittest.main()
