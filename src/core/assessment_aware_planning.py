from src.core.execution_assessment import ExecutionAssessment
from src.core.execution_assessment_validator import ExecutionAssessmentValidator
from src.core.execution_plan_models import ExecutionPlan
from src.core.execution_planning import ExecutionPlannerProtocol
from src.core.execution_state import ExecutionState
from src.core.remaining_work import RemainingWork, RemainingWorkResolver
from src.core.task_models import TaskRequest


class AssessmentAwarePlanningService:
    """
    Build an execution plan from validated assessment and grounded remaining work.

    The service is a planning adapter only. It never authorizes, confirms,
    executes, or invokes capabilities.
    """

    def __init__(
        self,
        planner: ExecutionPlannerProtocol,
        assessment_validator: ExecutionAssessmentValidator | None = None,
        remaining_work_resolver: RemainingWorkResolver | None = None,
    ):
        if not hasattr(planner, "plan") or not callable(planner.plan):
            raise TypeError("planner must expose plan(task, ...).")
        if assessment_validator is not None and not isinstance(
            assessment_validator, ExecutionAssessmentValidator
        ):
            raise TypeError(
                "assessment_validator must be an ExecutionAssessmentValidator or None."
            )
        if remaining_work_resolver is not None and not isinstance(
            remaining_work_resolver, RemainingWorkResolver
        ):
            raise TypeError(
                "remaining_work_resolver must be a RemainingWorkResolver or None."
            )

        self.planner = planner
        self.assessment_validator = assessment_validator or ExecutionAssessmentValidator()
        self.remaining_work_resolver = remaining_work_resolver or RemainingWorkResolver()

    def plan(
        self,
        task: TaskRequest,
        state: ExecutionState,
        assessment: ExecutionAssessment,
    ) -> ExecutionPlan:
        if not isinstance(task, TaskRequest):
            raise TypeError("task must be a TaskRequest.")
        if not isinstance(state, ExecutionState):
            raise TypeError("state must be an ExecutionState.")
        if not isinstance(assessment, ExecutionAssessment):
            raise TypeError("assessment must be an ExecutionAssessment.")
        if task.content != state.goal:
            raise ValueError("task objective must match execution state goal.")

        validated = self.assessment_validator.validate(state, assessment)
        remaining = self.remaining_work_resolver.resolve(state, validated)

        return self.planner.plan(
            task,
            progress=None,
            remaining_work=remaining,
        )

    def resolve_remaining_work(
        self,
        state: ExecutionState,
        assessment: ExecutionAssessment,
    ) -> RemainingWork:
        validated = self.assessment_validator.validate(state, assessment)
        return self.remaining_work_resolver.resolve(state, validated)
