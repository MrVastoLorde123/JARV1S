import unittest

from src.agency.authorized_execution_admission import AuthorizedExecutionAdmission
from src.agency.authorized_execution_runtime_admission import (
    AuthorizedExecutionRuntimeAdmission,
    create_authorized_execution_runtime_admission,
)
from src.agency.execution_bridge import AgencyExecutionBridgeResult


class _FakePreparation:
    pass


class M55AuthorizedExecutionRuntimeAdmissionTests(unittest.TestCase):
    def test_runtime_result_can_bind_to_exact_admission(self):
        from src.agency.authorization_execution_bridge import AuthorizationExecutionBridge
        from src.agency.authorization_decision import AuthorizationDecision, AuthorizationDisposition
        from src.agency.execution_handoff import ExecutionHandoff
        from src.agency.tests.test_authorized_execution_admission import (
            M54AuthorizedExecutionAdmissionTests,
        )

        helper = M54AuthorizedExecutionAdmissionTests()
        bridge = helper._bridge()
        handoff = helper._handoff()
        admission = AuthorizedExecutionAdmission(bridge, handoff)

        result = AgencyExecutionBridgeResult(
            handoff=handoff,
            agency_result=helper._agency_result(handoff),
        )
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
        from src.agency.tests.test_authorized_execution_admission import M54AuthorizedExecutionAdmissionTests

        helper = M54AuthorizedExecutionAdmissionTests()
        bridge = helper._bridge()
        handoff = helper._handoff()
        admission = AuthorizedExecutionAdmission(bridge, handoff)
        other_handoff = helper._handoff(execution_id="exec-other")
        other_result = AgencyExecutionBridgeResult(
            handoff=other_handoff,
            agency_result=helper._agency_result(other_handoff),
        )
        with self.assertRaises(ValueError):
            create_authorized_execution_runtime_admission(admission, other_result)

    def test_non_bridge_result_is_rejected(self):
        from src.agency.tests.test_authorized_execution_admission import M54AuthorizedExecutionAdmissionTests

        helper = M54AuthorizedExecutionAdmissionTests()
        admission = helper._admission()
        with self.assertRaises(TypeError):
            create_authorized_execution_runtime_admission(admission, object())

    def test_runtime_admission_does_not_create_authority_or_execution_request(self):
        from src.agency.tests.test_authorized_execution_admission import M54AuthorizedExecutionAdmissionTests

        helper = M54AuthorizedExecutionAdmissionTests()
        handoff = helper._handoff()
        admission = helper._admission()
        result = AgencyExecutionBridgeResult(
            handoff=handoff,
            agency_result=helper._agency_result(handoff),
        )
        runtime = create_authorized_execution_runtime_admission(admission, result)
        payload = runtime.to_context()
        self.assertNotIn("authorize", payload)
        self.assertNotIn("execute", payload)
        self.assertFalse(payload["authorization_created"])
        self.assertFalse(payload["execution_requested"])


if __name__ == "__main__":
    unittest.main()
