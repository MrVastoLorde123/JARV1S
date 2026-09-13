from __future__ import annotations

from dataclasses import dataclass

from src.runtime.autonomous_job import AutonomousJob
from src.runtime.autonomous_job_driver import AutonomousCycleDisposition, AutonomousCycleResult
from src.runtime.autonomous_reasoning_action import AutonomousReasoningAction, AutonomousReasoningDisposition
from src.runtime.autonomous_reasoning_worker import AutonomousReasoningWorker
from src.runtime.autonomous_reasoning_tool_gate import AutonomousReasoningToolGate
from src.runtime.autonomous_tool_result_feedback import AutonomousToolResultFeedbackAdapter

@dataclass(frozen=True)
class AutonomousReasoningToolFeedbackCycle:
    cycle: AutonomousCycleResult
    action: AutonomousReasoningAction
    tool_executed: bool
    authorization_required: bool

class AutonomousReasoningToolFeedbackCycleCoordinator:
    def __init__(self, worker: AutonomousReasoningWorker, tool_gate: AutonomousReasoningToolGate, feedback=None):
        if not isinstance(worker, AutonomousReasoningWorker): raise TypeError("worker must be an AutonomousReasoningWorker")
        if not isinstance(tool_gate, AutonomousReasoningToolGate): raise TypeError("tool_gate must be an AutonomousReasoningToolGate")
        self._worker=worker; self._tool_gate=tool_gate; self._feedback=feedback or AutonomousToolResultFeedbackAdapter()

    def run_cycle(self, job: AutonomousJob, *, confirmed: bool=False) -> AutonomousReasoningToolFeedbackCycle:
        if not isinstance(job, AutonomousJob): raise TypeError("job must be an AutonomousJob")
        if not isinstance(confirmed, bool): raise TypeError("confirmed must be a bool")
        action=self._worker.reason_action(job)
        if action.disposition is not AutonomousReasoningDisposition.TOOL_REQUEST:
            return AutonomousReasoningToolFeedbackCycle(self._worker.action_to_cycle_result(action), action, False, False)
        gate=self._tool_gate.evaluate(action, confirmed=confirmed)
        if gate.authorization_required:
            cycle=AutonomousCycleResult(AutonomousCycleDisposition.WAIT_TOOL,"tool_authorization",action.rationale,reason=gate.reason or "tool authorization required",context_delta={"reasoning_action":action.to_dict(),"pending_tool_request":{"tool_name":gate.tool_request.tool_name,"arguments":dict(gate.tool_request.arguments),"invocation_id":gate.tool_request.invocation_id}})
            return AutonomousReasoningToolFeedbackCycle(cycle, action, False, True)
        if gate.tool_result is None:
            cycle=AutonomousCycleResult(AutonomousCycleDisposition.FAIL,"tool_execution","tool gate returned no result after execution",reason="tool execution produced no ToolResult",context_delta={"reasoning_action":action.to_dict()})
            return AutonomousReasoningToolFeedbackCycle(cycle, action, gate.executed, False)
        feedback=self._feedback.adapt(gate.tool_result)
        cycle=AutonomousCycleResult(AutonomousCycleDisposition.CONTINUE,"tool_feedback",f"Tool '{feedback.tool_name}' executed; result is available for the next reasoning cycle.",observation=feedback.observation,context_delta={"reasoning_action":action.to_dict(),**feedback.context_delta})
        return AutonomousReasoningToolFeedbackCycle(cycle, action, gate.executed, False)

__all__=["AutonomousReasoningToolFeedbackCycle","AutonomousReasoningToolFeedbackCycleCoordinator"]