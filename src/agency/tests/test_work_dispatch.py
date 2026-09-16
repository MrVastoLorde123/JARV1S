from unittest import TestCase

from src.agency.work_dispatch import DispatchRequest, WorkDispatcher
from src.agency.work_planning import PlanStepKind, WorkPlanStep, build_work_plan
from src.agency.work_state import WorkRole, WorkStage, WorkState, WorkStatus
from src.agency.workforce import WorkerDefinition, WorkerRegistry


class M34WorkDispatchTests(TestCase):
    def _plan(self):
        work = WorkState(
            work_id="work-34",
            objective="dispatch bounded work",
            stage=WorkStage.PLANNING,
            status=WorkStatus.ACTIVE,
            role=WorkRole.TECHNICAL_LEAD,
        )
        return build_work_plan(
            work,
            (
                WorkPlanStep(
                    "implement",
                    "Implement bounded change",
                    PlanStepKind.IMPLEMENT,
                    WorkRole.TECHNICAL_LEAD,
                    requires_capabilities=("code", "tests"),
                ),
            ),
        )

    def _registry(self):
        registry = WorkerRegistry()
        registry.register(
            WorkerDefinition(
                worker_id="coder",
                name="Bounded Coder",
                capabilities=("code", "tests"),
                max_steps=4,
            )
        )
        return registry

    def test_dispatch_binds_selected_step_to_bounded_assignment(self):
        result = WorkDispatcher(self._registry()).dispatch(
            DispatchRequest(self._plan(), "implement", "coder", max_steps=2)
        )
        self.assertEqual("implement", result.step.step_id)
        self.assertEqual("coder", result.assignment.worker_id)
        self.assertEqual("Implement bounded change", result.assignment.objective)
        self.assertEqual(("code", "tests"), result.assignment.allowed_capabilities)

    def test_missing_capability_is_rejected_before_assignment(self):
        registry = WorkerRegistry()
        registry.register(
            WorkerDefinition(
                worker_id="researcher",
                name="Researcher",
                capabilities=("research",),
                max_steps=4,
            )
        )
        with self.assertRaises(ValueError):
            WorkDispatcher(registry).dispatch(DispatchRequest(self._plan(), "implement", "researcher"))

    def test_unknown_step_and_worker_are_rejected(self):
        registry = self._registry()
        with self.assertRaises(ValueError):
            DispatchRequest(self._plan(), "missing", "coder")
        with self.assertRaises(KeyError):
            WorkDispatcher(registry).dispatch(DispatchRequest(self._plan(), "implement", "missing"))

    def test_dispatch_is_not_authorization_or_execution(self):
        result = WorkDispatcher(self._registry()).dispatch(DispatchRequest(self._plan(), "implement", "coder"))
        context = result.to_context()
        self.assertFalse(context["authorization_granted"])
        self.assertFalse(context["execution_requested"])
