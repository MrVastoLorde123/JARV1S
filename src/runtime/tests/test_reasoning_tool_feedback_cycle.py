import unittest
from src.runtime.autonomous_job import AutonomousJob
from src.runtime.autonomous_job_driver import AutonomousCycleDisposition
from src.runtime.autonomous_reasoning_action import AutonomousReasoningAction, AutonomousReasoningDisposition
from src.runtime.autonomous_reasoning_tool_feedback_cycle import AutonomousReasoningToolFeedbackCycleCoordinator
from src.runtime.autonomous_reasoning_tool_gate import AutonomousReasoningToolGate
from src.runtime.autonomous_reasoning_worker import AutonomousReasoningWorker
from src.tools.models import RiskLevel, ToolDefinition, ToolResult
from src.tools.protocol import ToolHandler
from src.tools.registry import ToolRegistry
from src.tools.service import ToolService

class EchoTool(ToolHandler):
    def __init__(self, confirm=False): self.confirm=confirm
    def definition(self): return ToolDefinition('echo','Echo','1.0',{}, {}, RiskLevel.LOW, self.confirm)
    def execute(self, request): return ToolResult(True, request.tool_name, request.arguments, invocation_id=request.invocation_id)

class M63Tests(unittest.TestCase):
    def job(self): return AutonomousJob('j','inspect system')
    def coordinator(self, confirm=False, action=None):
        registry=ToolRegistry(); registry.register(EchoTool(confirm)); gate=AutonomousReasoningToolGate(registry, ToolService(registry))
        action=action or AutonomousReasoningAction('a2', AutonomousReasoningDisposition.TOOL_REQUEST, 'inspect', tool_name='echo', arguments={'x':1})
        return AutonomousReasoningToolFeedbackCycleCoordinator(AutonomousReasoningWorker(lambda job: action), gate)
    def test_feedback_reenters_cycle(self):
        out=self.coordinator().run_cycle(self.job()); self.assertTrue(out.tool_executed); self.assertEqual(out.cycle.disposition, AutonomousCycleDisposition.CONTINUE); self.assertEqual(out.cycle.context_delta['tool_result']['content']['x'],1)
    def test_confirmation_waits(self):
        out=self.coordinator(True).run_cycle(self.job()); self.assertFalse(out.tool_executed); self.assertTrue(out.authorization_required); self.assertEqual(out.cycle.disposition, AutonomousCycleDisposition.WAIT_TOOL)
    def test_confirmation_allows_feedback(self):
        out=self.coordinator(True).run_cycle(self.job(), confirmed=True); self.assertTrue(out.tool_executed); self.assertFalse(out.authorization_required)
    def test_non_tool_action_preserves_cycle_contract(self):
        action=AutonomousReasoningAction('a3', AutonomousReasoningDisposition.COMPLETE, 'done', result='finished')
        out=self.coordinator(action=action).run_cycle(self.job()); self.assertEqual(out.cycle.disposition, AutonomousCycleDisposition.COMPLETE); self.assertFalse(out.tool_executed)
