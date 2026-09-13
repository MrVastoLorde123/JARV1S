import unittest
from src.runtime.autonomous_reasoning_action import AutonomousReasoningAction, AutonomousReasoningDisposition
from src.runtime.autonomous_reasoning_tool_gate import AutonomousReasoningToolGate
from src.tools.models import RiskLevel, ToolDefinition, ToolResult
from src.tools.protocol import ToolHandler
from src.tools.registry import ToolRegistry
from src.tools.service import ToolService

class EchoTool(ToolHandler):
    def __init__(self, confirm=False): self.confirm=confirm
    def definition(self): return ToolDefinition('echo','Echo','1.0',{}, {}, RiskLevel.LOW, self.confirm)
    def execute(self, request): return ToolResult(True, request.tool_name, request.arguments, invocation_id=request.invocation_id)

class M61Tests(unittest.TestCase):
    def action(self): return AutonomousReasoningAction('a1', AutonomousReasoningDisposition.TOOL_REQUEST, 'inspect', tool_name='echo', arguments={'x':1})
    def gate(self, confirm):
        r=ToolRegistry(); r.register(EchoTool(confirm)); return AutonomousReasoningToolGate(r, ToolService(r))
    def test_confirmation_blocks(self):
        out=self.gate(True).evaluate(self.action()); self.assertTrue(out.authorization_required); self.assertFalse(out.executed)
    def test_confirmation_allows(self):
        out=self.gate(True).evaluate(self.action(), confirmed=True); self.assertTrue(out.executed); self.assertTrue(out.tool_result.success)
    def test_non_confirming_executes(self): self.assertTrue(self.gate(False).evaluate(self.action()).executed)
    def test_non_tool_action_rejected(self):
        a=AutonomousReasoningAction('a1', AutonomousReasoningDisposition.CONTINUE, 'continue')
        with self.assertRaises(ValueError): self.gate(False).evaluate(a)
