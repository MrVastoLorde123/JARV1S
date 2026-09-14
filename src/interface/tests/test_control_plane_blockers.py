import unittest

from src.core.interface_backend import InterfaceResponseStatus
from src.core.runtime_activity_stream import RuntimeActivityStream
from src.interface.control_host import _blockers_projection
from src.interface.control_plane import ControlPlaneActivityRecorder


class ControlPlaneBlockerProjectionTests(unittest.TestCase):
    def test_pending_confirmation_is_projected_as_runtime_blocker(self):
        stream = RuntimeActivityStream()
        recorder = ControlPlaneActivityRecorder(stream)
        recorder.record_response(
            request_id="req-approval",
            session_id="desktop",
            status=InterfaceResponseStatus.ACCEPTED,
            metadata={
                "route": "CODING_AGENT",
                "stage": "CONFIRMATION",
                "task_id": "task-approval",
                "operation_id": "op-approval",
            },
        )
        blockers = _blockers_projection(stream)
        self.assertEqual(len(blockers), 1)
        self.assertEqual(blockers[0]["type"], "AWAITING_APPROVAL")
        self.assertEqual(blockers[0]["severity"], "MEDIUM")
        self.assertEqual(blockers[0]["operation_id"], "op-approval")

    def test_blocked_tool_is_projected_without_inventing_authority(self):
        stream = RuntimeActivityStream()
        recorder = ControlPlaneActivityRecorder(stream)
        recorder.record_response(
            request_id="req-blocked",
            session_id="desktop",
            status=InterfaceResponseStatus.ACCEPTED,
            metadata={
                "route": "CODING_AGENT",
                "stage": "EXECUTION",
                "success": False,
                "task_id": "task-blocked",
                "operation_id": "op-blocked",
                "blocked_tool": "write_file",
            },
        )
        blockers = _blockers_projection(stream)
        self.assertEqual(len(blockers), 1)
        self.assertEqual(blockers[0]["type"], "TOOL_BLOCKED")
        self.assertEqual(blockers[0]["tool"], "write_file")
        self.assertNotIn("authority_granted", blockers[0])
        self.assertNotIn("permissions_granted", blockers[0])

    def test_failed_verification_is_projected_as_blocker(self):
        stream = RuntimeActivityStream()
        recorder = ControlPlaneActivityRecorder(stream)
        recorder.record_response(
            request_id="req-verify-fail",
            session_id="desktop",
            status=InterfaceResponseStatus.ACCEPTED,
            metadata={
                "route": "CODING_AGENT",
                "stage": "EXECUTION",
                "success": True,
                "task_id": "task-verify-fail",
                "verification": {
                    "state": "FAILED",
                    "runner": "python",
                    "passed": False,
                    "error": "tests failed",
                    "stdout": "PRIVATE LOG",
                },
            },
        )
        blockers = _blockers_projection(stream)
        self.assertEqual(len(blockers), 1)
        self.assertEqual(blockers[0]["type"], "VERIFICATION_FAILED")
        self.assertEqual(blockers[0]["error"], "tests failed")
        self.assertNotIn("stdout", blockers[0])

    def test_successful_execution_has_no_blocker(self):
        stream = RuntimeActivityStream()
        recorder = ControlPlaneActivityRecorder(stream)
        recorder.record_response(
            request_id="req-success",
            session_id="desktop",
            status=InterfaceResponseStatus.ACCEPTED,
            metadata={
                "route": "CODING_AGENT",
                "stage": "EXECUTION",
                "success": True,
            },
        )
        self.assertEqual(_blockers_projection(stream), ())


if __name__ == "__main__":
    unittest.main()
