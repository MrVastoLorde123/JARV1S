from typing import Callable, Any
from src.runtime.autonomous_job import AutonomousJob
from src.runtime.autonomous_job_driver import AutonomousCycleDisposition, AutonomousCycleResult
from src.runtime.autonomous_reasoning_action import AutonomousReasoningAction, AutonomousReasoningDisposition

class AutonomousReasoningWorker:
    def __init__(self, reason: Callable[[AutonomousJob], Any]):
        if not callable(reason): raise TypeError('reason must be callable')
        self._reason = reason
    def run_cycle(self, job: AutonomousJob) -> AutonomousCycleResult:
        value=self._reason(job)
        action=value if isinstance(value, AutonomousReasoningAction) else AutonomousReasoningAction.from_mapping(value)
        d=action.disposition
        base={'reasoning_action':action.to_dict()}
        if d is AutonomousReasoningDisposition.CONTINUE: return AutonomousCycleResult(AutonomousCycleDisposition.CONTINUE,'reasoning',action.rationale,context_delta=base)
        if d is AutonomousReasoningDisposition.TOOL_REQUEST: return AutonomousCycleResult(AutonomousCycleDisposition.WAIT_TOOL,'reasoning_action',action.rationale,reason=f'tool request pending: {action.tool_name}',context_delta={**base,'pending_tool_request':action.to_dict()})
        if d is AutonomousReasoningDisposition.WAIT_AUTHORIZATION: return AutonomousCycleResult(AutonomousCycleDisposition.WAIT_AUTHORIZATION,'reasoning',action.rationale,reason=action.wait_reason,context_delta=base)
        if d is AutonomousReasoningDisposition.WAIT_INPUT: return AutonomousCycleResult(AutonomousCycleDisposition.WAIT_INPUT,'reasoning',action.rationale,reason=action.wait_reason,context_delta=base)
        if d is AutonomousReasoningDisposition.WAIT_TOOL: return AutonomousCycleResult(AutonomousCycleDisposition.WAIT_TOOL,'reasoning',action.rationale,reason=action.wait_reason,context_delta=base)
        if d is AutonomousReasoningDisposition.COMPLETE: return AutonomousCycleResult(AutonomousCycleDisposition.COMPLETE,'reasoning',action.rationale,result=str(action.result),context_delta=base)
        return AutonomousCycleResult(AutonomousCycleDisposition.FAIL,'reasoning',action.rationale,reason=action.wait_reason or 'reasoning failed',context_delta=base)
