import unittest

from src.agents.coding_service import CodingAgentService
from src.agents.consequence_execution_attempt import ConsequenceExecutionAttemptService
from src.agents.consequence_execution_outcome import ConsequenceExecutionOutcomeStatus
from src.tools.models import ToolResult
from src.agents.tests.test_consequence_execution_attempt import RecordingExecutor
from src.agents.tests.test_consequence_execution_outcome import M35ConsequenceExecutionOutcomeTests


class M35CodingServiceConsequenceExecutionOutcomeTests(unittest.TestCase):
    def test_service_requires_explicit_outcome_binding(self):
        service = CodingAgentService(planner=object(), worker=object())
        with self.assertRaises(RuntimeError):
            service.evaluate_execution_outcome(object())

    def test_service_evaluates_an_attempt_through_bound_outcome_service(self):
        source = M35ConsequenceExecutionOutcomeTests()
        source.setUp()
        attempt = source._attempt(
            source.__class__.__dict__["_attempt"].__globals__["ConsequenceExecutionAttemptStatus"].ATTEMPTED_COMPLETED,
            result=ToolResult(success=True, tool_name="write_file", invocation_id="invocation-35"),
        )
        service = CodingAgentService(planner=object(), worker=object())
        service.bind_consequence_execution_outcome()
        result = service.evaluate_execution_outcome(attempt)
        self.assertEqual(result.status, ConsequenceExecutionOutcomeStatus.COMPLETED_SUCCESS)

    def test_outcome_binding_does_not_execute_or_retry(self):
        service = CodingAgentService(planner=object(), worker=object())
        service.bind_consequence_execution_outcome()
        source = M35ConsequenceExecutionOutcomeTests()
        source.setUp()
        attempt = source._attempt(
            source.__class__.__dict__["_attempt"].__globals__["ConsequenceExecutionAttemptStatus"].ATTEMPTED_FAILED,
            reason="executor unavailable",
        )
        result = service.evaluate_execution_outcome(attempt)
        self.assertEqual(result.status, ConsequenceExecutionOutcomeStatus.COMPLETED_FAILURE)
        self.assertFalse(result.to_context()["retry_requested"])


if __name__ == "__main__":
    unittest.main()
