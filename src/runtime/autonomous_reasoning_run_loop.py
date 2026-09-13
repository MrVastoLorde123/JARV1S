from dataclasses import dataclass
from src.runtime.autonomous_job import AutonomousJob, AutonomousJobStatus
from src.runtime.autonomous_reasoning_feedback_pulse import AutonomousReasoningFeedbackPulse, AutonomousReasoningFeedbackPulseResult

@dataclass(frozen=True)
class AutonomousReasoningRunResult:
    job: AutonomousJob
    pulses: tuple[AutonomousReasoningFeedbackPulseResult, ...]
    budget_exhausted: bool

class AutonomousReasoningRunLoop:
    def __init__(self, pulse: AutonomousReasoningFeedbackPulse):
        if not isinstance(pulse, AutonomousReasoningFeedbackPulse): raise TypeError("pulse must be an AutonomousReasoningFeedbackPulse")
        self._pulse = pulse
    def run(self, job_id: str, *, max_pulses: int = 32, confirmed: bool = False) -> AutonomousReasoningRunResult:
        if isinstance(max_pulses, bool) or not isinstance(max_pulses, int) or max_pulses <= 0: raise ValueError("max_pulses must be a positive integer")
        if not isinstance(confirmed, bool): raise TypeError("confirmed must be a bool")
        results = []
        for _ in range(max_pulses):
            out = self._pulse.pulse(job_id, confirmed=confirmed)
            results.append(out)
            if out.waiting or out.job.status in {AutonomousJobStatus.COMPLETED, AutonomousJobStatus.FAILED, AutonomousJobStatus.CANCELLED}:
                return AutonomousReasoningRunResult(out.job, tuple(results), False)
            confirmed = False
        return AutonomousReasoningRunResult(results[-1].job, tuple(results), True)

__all__ = ["AutonomousReasoningRunLoop", "AutonomousReasoningRunResult"]
