from src.ai.models import AIRequest
from src.ai.service import AIService
from src.runtime.autonomous_job import AutonomousJob

class AutonomousAIReasoningProvider:
    def __init__(self, ai_service: AIService, provider_name=None):
        if not isinstance(ai_service, AIService):
            raise TypeError("ai_service must be an AIService")
        self._ai_service = ai_service
        self._provider_name = provider_name

    def reason(self, job: AutonomousJob):
        if not isinstance(job, AutonomousJob):
            raise TypeError("job must be an AutonomousJob")
        request = AIRequest(
            task="Perform one bounded autonomous reasoning cycle and return one AutonomousReasoningAction for: " + job.goal,
            context={
                "job_id": job.job_id,
                "status": job.status.value,
                "step_count": job.step_count,
                "max_steps": job.max_steps,
                "working_context": dict(job.working_context),
                "previous_steps": [step.to_dict() for step in job.steps[-8:]],
            },
            metadata={"runtime": "autonomous_reasoning", "job_id": job.job_id},
        )
        return self._ai_service.generate(request, provider_name=self._provider_name, required_capabilities=("structured_output",)).content
