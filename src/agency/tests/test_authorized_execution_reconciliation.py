from unittest import TestCase

from src.agency.authorized_execution_reconciliation import build_authorized_execution_reconciliation
from src.agency.authorized_execution_recovery import AuthorizedExecutionRecovery
from src.agency.authorized_execution_recovery import build_authorized_execution_recovery
from src.agency.recovery_state import reconcile_recovery
from src.agency.tests.test_authorized_execution_recovery import _M58Fixture
from src.agency.work_state import WorkRole, WorkStage, WorkState, WorkStatus


class M59AuthorizedExecutionReconciliationTests(_M58Fixture):
    def _work_state(self):
        return WorkState(
            work_id="work-58",
            objective="recover bounded work",
            stage=WorkStage.EXECUTING,
            status=WorkStatus.ACTIVE,
            role=WorkRole.TECHNICAL_LEAD,
            current_step="deploy change",
        )

    def _recovery(self):
        return build_authorized_execution_recovery(
            self._verification(),
            self._objective(),
            self._cycle(),
        )

    def test_exact_recovery_reconciles_existing_m39_state(self):
        result = build_authorized_execution_reconciliation(self._recovery(), self._work_state())
        self.assertEqual("exec-58", result.execution_id)
        self.assertEqual("auth-58", result.authorization_id)
        self.assertEqual("work-58", result.work_id)
        self.assertEqual("COMPLETED", result.disposition.value)
        self.assertEqual(self._work_state(), result.reconciliation.before)
        self.assertEqual("COMPLETE", result.reconciliation.after.stage.value)

    def test_mismatched_reconciliation_work_identity_is_rejected(self):
        recovery = self._recovery()
        original_state = self._work_state()
        other_state = WorkState(
            work_id="other-work",
            objective="recover bounded work",
            stage=WorkStage.EXECUTING,
            status=WorkStatus.ACTIVE,
            role=WorkRole.TECHNICAL_LEAD,
        )
        other_reconciliation = reconcile_recovery(other_state, recovery.recovery)
        with self.assertRaises(ValueError):
            AuthorizedExecutionReconciliation(
                authorized_recovery=recovery,
                work_state=original_state,
                reconciliation=other_reconciliation,
            )

    def test_non_recovery_input_is_rejected(self):
        with self.assertRaises(TypeError):
            build_authorized_execution_reconciliation(object(), self._work_state())

    def test_reconciliation_exposes_no_authority_or_execution_controls(self):
        payload = build_authorized_execution_reconciliation(self._recovery(), self._work_state()).to_context()
        self.assertFalse(payload["authorization_created"])
        self.assertFalse(payload["execution_requested"])
        self.assertFalse(payload["execution_performed"])
        self.assertNotIn("authorize", payload)
        self.assertNotIn("execute", payload)
