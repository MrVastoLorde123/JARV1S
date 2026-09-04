import json
import unittest

from src.context.goal_project import (
    GoalContext,
    GoalProjectContext,
    GoalProjectContextValidationError,
    GoalStatus,
    ProjectContext,
    ProjectStatus,
)


class GoalProjectContextTests(unittest.TestCase):
    def goal(self, goal_id="goal-1", project_id="project-1", status=GoalStatus.ACTIVE):
        return GoalContext(
            goal_id=goal_id,
            name="Build JARVIS",
            status=status,
            project_id=project_id,
            metadata={"priority": 1},
            source_refs=(f"source-{goal_id}",),
        )

    def project(self, project_id="project-1", goal_ids=("goal-1",), status=ProjectStatus.ACTIVE):
        return ProjectContext(
            project_id=project_id,
            name="JARVIS",
            status=status,
            goal_ids=goal_ids,
            metadata={"domain": "ai"},
            source_refs=(f"source-{project_id}",),
        )

    def test_goal_context_accepts_status_string(self):
        goal = self.goal(status="active")
        self.assertIs(goal.status, GoalStatus.ACTIVE)

    def test_project_context_accepts_status_string(self):
        project = self.project(status="active")
        self.assertIs(project.status, ProjectStatus.ACTIVE)

    def test_goal_project_context_requires_referenced_project(self):
        with self.assertRaises(GoalProjectContextValidationError):
            GoalProjectContext(goals=(self.goal(),), projects=())

    def test_goal_project_context_requires_referenced_goal(self):
        with self.assertRaises(GoalProjectContextValidationError):
            GoalProjectContext(
                goals=(),
                projects=(self.project(),),
            )

    def test_goal_and_project_lookup(self):
        context = GoalProjectContext(goals=(self.goal(),), projects=(self.project(),))
        self.assertIs(context.for_goal("goal-1"), context.goals[0])
        self.assertIs(context.for_project("project-1"), context.projects[0])
        self.assertIsNone(context.for_goal("missing"))

    def test_active_filters(self):
        goals = (self.goal("goal-1"), self.goal("goal-2", status=GoalStatus.PAUSED))
        projects = (self.project("project-1"), self.project("project-2", goal_ids=("goal-2",), status=ProjectStatus.PAUSED))
        context = GoalProjectContext(goals=goals, projects=projects)
        self.assertEqual(tuple(item.goal_id for item in context.active_goals()), ("goal-1",))
        self.assertEqual(tuple(item.project_id for item in context.active_projects()), ("project-1",))

    def test_goal_ids_are_unique(self):
        with self.assertRaises(GoalProjectContextValidationError):
            GoalProjectContext(goals=(self.goal("goal-1"), self.goal("goal-1")), projects=(self.project(),))

    def test_project_ids_are_unique(self):
        with self.assertRaises(GoalProjectContextValidationError):
            GoalProjectContext(goals=(self.goal(),), projects=(self.project("project-1"), self.project("project-1")))

    def test_metadata_is_frozen(self):
        goal = self.goal()
        with self.assertRaises(TypeError):
            goal.metadata["new"] = "value"

    def test_context_is_immutable(self):
        context = GoalProjectContext(goals=(self.goal(),), projects=(self.project(),))
        with self.assertRaises(AttributeError):
            context.goals = ()

    def test_serialization_is_deterministic(self):
        context = GoalProjectContext(goals=(self.goal(),), projects=(self.project(),))
        self.assertEqual(context.to_json(), context.to_json())
        self.assertEqual(json.loads(context.to_json())["goals"][0]["goal_id"], "goal-1")

    def test_goal_and_project_do_not_become_instructions(self):
        context = GoalProjectContext(goals=(self.goal(),), projects=(self.project(),))
        payload = context.to_dict()
        self.assertFalse(payload["goal_is_instruction"])
        self.assertFalse(payload["project_is_instruction"])
        self.assertFalse(payload["authorization_granted"])
        self.assertFalse(payload["policy_authority"])
        self.assertFalse(payload["execution_requested"])

    def test_goal_context_reference_and_project_goal_reference_are_bounded(self):
        with self.assertRaises(GoalProjectContextValidationError):
            self.goal(goal_id="x" * 257)
        with self.assertRaises(GoalProjectContextValidationError):
            ProjectContext(project_id="p", name="P", goal_ids=("x" * 257,))

    def test_goal_context_is_immutable(self):
        goal = self.goal()
        with self.assertRaises(AttributeError):
            goal.name = "changed"

    def test_project_context_is_immutable(self):
        project = self.project()
        with self.assertRaises(AttributeError):
            project.name = "changed"


if __name__ == "__main__":
    unittest.main()
