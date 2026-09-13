from dataclasses import dataclass
from src.runtime.autonomous_job import AutonomousJob
from src.runtime.autonomous_job_persistence import AutonomousJobPersistenceService
from src.runtime.autonomous_job_resume import AutonomousJobResumeBoundary, AutonomousJobResumeKind, AutonomousJobResumeRequest, AutonomousJobResumeResult
from src.runtime.autonomous_reasoning_feedback_pulse import AutonomousReasoningFeedbackPulse, AutonomousReasoningFeedbackPulseResult

@dataclass(frozen=True)
class AutonomousResumeReasoningHandoffResult:
    resume: AutonomousJobResumeResult
    pulse: AutonomousReasoningFeedbackPulseResult
    @property
    def job(self) -> AutonomousJob:
        return self.pulse.job

class AutonomousResumeReasoningHandoff:
    def __init__(self, persistence, pulse, resume_boundary=None):
        if not isinstance(persistence, AutonomousJobPersistenceService): raise TypeError("persistence must be an AutonomousJobPersistenceService")
        if not isinstance(pulse, AutonomousReasoningFeedbackPulse): raise TypeError("pulse must be an AutonomousReasoningFeedbackPulse")
        self._resume = resume_boundary or AutonomousJobResumeBoundary(persistence)
        self._pulse = pulse
    def resume_and_pulse(self, request):
        if not isinstance(request, AutonomousJobResumeRequest): raise TypeError("request must be an AutonomousJobResumeRequest")
        resumed = self._resume.resume(request)
        confirmed = request.confirmed if request.kind in {AutonomousJobResumeKind.AUTHORIZATION, AutonomousJobResumeKind.TOOL} else False
        return AutonomousResumeReasoningHandoffResult(resumed, self._pulse.pulse(request.job_id, confirmed=confirmed))

__all__ = ["AutonomousResumeReasoningHandoff", "AutonomousResumeReasoningHandoffResult"]
