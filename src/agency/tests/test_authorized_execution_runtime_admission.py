import unittest
from unittest.mock import Mock

from src.agency.authorization_execution_bridge import create_authorization_execution_bridge
from src.agency.authorized_execution_admission import create_authorized_execution_admission
from src.agency.authorized_execution_runtime_admission import (
    AuthorizedExecutionRuntimeAdmission,
    create_authorized_execution_runtime_admission,
)
from src.agency.controlled_agency import AgencyStopReason, ControlledAgencyResult
from src.agency.execution_bridge import AgencyExecutionBridgeResult
from src.agency.tests.test_authorized_execution_admission import M54AuthorizedExecutionAdmissionTests
from src.context.working_context import WorkingContext


class M55AuthorizedExecutionRuntimeAdmissionTests(unittest.TestCase):
    def _admission(self):
        helper = M54AuthorizedExecutionAdmissionTests()
        preparation = helper._preparation()
        bridge = create_authorization_execution_bridge(helper._authorization(), preparation)
        return create_authorized_execution_admission(bridge, helper._handoff(preparation))

    def _execution_result(self, admission):
        result = ControlledAgencyResult(
            observations=(),
            lifecycles=(),
            working_context=Mock(spec=WorkingContext),
            stop_reason=AgencyStopReason.COMPLETED,
        )
        return AgencyExecutionBridgeResult(
            handoff=admission.execution_handoff,
            agency_result=result,
        )

    def test_runtime_result_can_bind_to_exact_admission(self):
        admission = self._admission()
        result = self._execution_result(admission)
        runtime = create_authorized_execution_runtime_admission(admission, result)
        self.assertIsInstance(runtime, AuthorizedExecutionRuntimeAdmission)
        self.assertEqual(runtime.execution_id, admission.execution_id)
        self.assertEqual(runtime.authorization_id, admission.authorization_id)
        self.assertEqual(runtime.steps_executed, result.steps_executed)
        self.assertEqual(runtime.succeeded, result.succeeded)
        payload = runtime.to_context()
        self.assertFalse(payload["authorization_created"])
        self.assertFalse(payload["execution_requested"])
        self.assertTrue(payload["execution_performed"])

    def test_mismatched_execution_result_is_rejected(self):
        helper = M54AuthorizedExecutionAdmissionTests()
        admission = self._admission()
        other_preparation = helper._preparation()
        other_preparation = type(other_preparation)(
            request=other_preparation.request,
            execution_id="exec-other",
            status=other_preparation.status,
            execution_request=type(other_preparation.execution_request)(
                execution_id="exec-other",
                request=other_preparation.execution_request.request,
                proposal_id=other_preparation.execution_request.proposal_id,
                validation_id=other_preparation.execution_request.validation_id,
                policy_decision_id=other_preparation.execution_request.policy_decision_id,
                confirmation_id=other_preparation.execution_request.confirmation_id,
                authorization_id=other_preparation.execution_request.authorization_id,
                operation=other_preparation.execution_request.operation,
            ),
        )
        other_handoff = helper._handoff(other_preparation)
        other_result = AgencyExecutionBridgeResult(
            handoff=other_handoff,
            agency_result=ControlledAgencyResult(
                observations=(),
                lifecycles=(),
                working_context=Mock(spec=WorkingContext),
                stop_reason=AgencyStopReason.COMPLETED,
            ),
        )
        with self.assertRaises(ValueError):
            create_authorized_execution_runtime_admission(admission, other_result)

    def test_non_bridge_result_is_rejected(self):
        admission = self._admission()
        with self.assertRaises(TypeError):
            create_authorized_execution_runtime_admission(admission, object())

    def test_runtime_admission_does_not_create_authority_or_execution_request(self):
        admission = self._admission()
        runtime = create_authorized_execution_runtime_admission(admission, self._execution_result(admission))
        payload = runtime.to_context()
        self.assertNotIn("authorize", payload)
        self.assertNotIn("execute", payload)
        self.assertFalse(payload["authorization_created"])
        self.assertFalse(payload["execution_requested"])


if __name__ == "__main__":
    unittest.main()
